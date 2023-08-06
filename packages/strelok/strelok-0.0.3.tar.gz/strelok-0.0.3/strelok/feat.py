import numpy as np
import pandas as pd
from scipy import stats

from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

from sklearn.feature_selection import SelectKBest, SelectPercentile, RFE, SelectFromModel
from sklearn.linear_model import LassoCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from scipy.stats import boxcox
from scipy.stats import skew
from itertools import combinations



class Pipeline:
    def __init__(self, target_col):
        self.target_col = target_col
        self.feature_defs = []
        self.feature_selector = None

    def add_feature(self, feature):
        self.feature_defs.append(feature)

    def set_feature_selector(self, feature_selector, not_X_col=[], y_col=[]):
        self.feature_selector = feature_selector
        self.not_X_col = not_X_col + y_col
        self.y_col = y_col

    def generate_features(self, data):
        transformed_data = data.copy()  # Make a copy of the input data

        for feature in self.feature_defs:
            transformed_feature = feature.generate(transformed_data, self)  # Only generate the new feature

            if feature.name in transformed_data.columns:
                transformed_data[feature.name] = transformed_feature[feature.name]  # Overwrite existing column
            else:
                transformed_data = pd.concat([transformed_data, transformed_feature], axis=1)  # Create new column

        if self.feature_selector is not None:
            X = transformed_data.drop(columns=self.not_X_col)
            y = data[self.y_col]
            transformed_data = self.feature_selector.fit_transform(X, y)
        return transformed_data
    
    def get_target_col(self):
        return self.target_col



class Feature:
    def __init__(self, name):
        self.name = name

    def generate(self, data):
        # Placeholder method for feature generation
        pass


class MathematicalTransformation(Feature):
    def __init__(self, name, transformation_type, diff_col = None, **kwargs):
        super().__init__(name)
        self.transformation_type = transformation_type
        self.kwargs = kwargs
        self.diff_col - diff_col
        

    def generate(self, data, pipeline):
        if self.diff_col == None:
            target_col = pipeline.get_target_col()
        else:
            target_col = self.diff_col
        transformed_data = pd.DataFrame(data.copy()[target_col])  # Initialize with the target column
        transformed_data = pd.DataFrame(index=data.index)  # Initialize an empty DataFrame with the same index as data
        transformed_data[self.name] = 1  # Initialize the new column with 1


        if self.transformation_type == 'logarithmic':
            transformed_data[self.name] = np.log1p(data[target_col])

        elif self.transformation_type == 'square_root':
            transformed_data[self.name] = np.sqrt(data[target_col])

        elif self.transformation_type == 'exponential':
            power = self.kwargs.get('power', 1)
            transformed_data[self.name] = np.power(data[target_col], power)

        elif self.transformation_type == 'box_cox':
            transformed_data[self.name], _ = stats.boxcox(data[target_col])

        elif self.transformation_type == 'reciprocal':
            transformed_data[self.name] = 1 / (data[target_col] + 1e-10)  # Adding a small constant to avoid division by zero

        elif self.transformation_type == 'power':
            power = self.kwargs.get('power', 2)  # Default to 2 if no power is provided
            transformed_data[self.name] = np.power(data[target_col], power)

        elif self.transformation_type == 'binning':
            num_bins = self.kwargs.get('num_bins', 10)
            transformed_data[self.name] = pd.cut(data[target_col], bins=num_bins, labels=False)

        elif self.transformation_type == 'standardization':
            mean = self.kwargs.get('mean', data[target_col].mean())
            std = self.kwargs.get('std', data[target_col].std())

            transformed_data[self.name] = (data[target_col] - mean) / std


        elif self.transformation_type == 'rank':
            transformed_data[self.name] = data[target_col].rank()

        elif self.transformation_type == 'difference':
            other_feature = self.kwargs.get('other_feature') 
            transformed_data[self.name] = data[target_col] - data[other_feature]

        elif self.transformation_type == 'relative_difference':
            other_value = self.kwargs.get('other_value')
            transformed_data[self.name] = (data[target_col] - other_value) / other_value


        return transformed_data[[self.name]]


        
class MissingValueImputation(Feature):
    def __init__(self, name, imputation_strategy, diff_col = None, **kwargs):
        super().__init__(name)
        self.imputation_strategy = imputation_strategy
        self.diff_col = diff_col

        self.kwargs = kwargs

    def generate(self, data, pipeline):
        if self.diff_col == None:
            target_col = pipeline.get_target_col()
        else:
            target_col = self.diff_col

        
        if self.imputation_strategy == 'mean':
            imputed_data = data.copy()
            imputed_data[self.name] = imputed_data[target_col].fillna(imputed_data[target_col].mean())
        elif self.imputation_strategy == 'median':
            imputed_data = data.copy()
            imputed_data[self.name] = imputed_data[target_col].fillna(imputed_data[target_col].median())
        elif self.imputation_strategy == 'mode':
            imputed_data = data.copy()
            imputed_data[self.name] = imputed_data[target_col].fillna(imputed_data[target_col].mode().iloc[0])
        elif self.imputation_strategy == 'constant':
            imputed_data = data.copy()
            imputed_data[self.name] = imputed_data[target_col].fillna(0)
        elif self.imputation_strategy == 'forward_fill':
            imputed_data = data.copy()
            imputed_data[self.name] = imputed_data[target_col].ffill()
        elif self.imputation_strategy == 'backward_fill':
            imputed_data = data.copy()
            imputed_data[self.name] = imputed_data[target_col].bfill()
        elif self.imputation_strategy == 'interpolation':
            imputed_data = data.copy()
            imputed_data[self.name] = imputed_data[target_col].interpolate()
        elif self.imputation_strategy == 'knn':
            self.n_neighbors = self.kwargs.get('n_neighbors')
            imputer = KNNImputer(n_neighbors=self.n_neighbors)
            imputed_data = data.copy()
            imputed_data.loc[:, target_col] = imputer.fit_transform(data)[:, data.columns.get_loc(target_col)]
            imputed_data = imputed_data.rename(columns={target_col: self.name})
        elif self.imputation_strategy == 'multiple':
            imputer = IterativeImputer(max_iter=10, random_state=0)
            imputed_values = imputer.fit_transform(data[[target_col]])  # Impute only the target column
            imputed_data = data.copy()
            imputed_data[self.name] = imputed_values  # Add the new column to the data frame
        elif self.imputation_strategy == 'missing_indicator':
            imputed_data = data.copy()
            imputed_data[self.name] = imputed_data[target_col].isnull().astype(int)

        else:
            raise ValueError('Invalid imputation strategy')

        return imputed_data[[self.name]]
    

class FeatureSelection:
    def __init__(self, method=None, k=None, percentile=None,
                 correlation_threshold=None, box_cox_threshold=1e-10, **kwargs):
        self.method = method
        self.k = k
        self.percentile = percentile
        self.correlation_threshold = correlation_threshold
        self.box_cox_threshold = box_cox_threshold
        self.kwargs = kwargs
        self.selected_features = None

    def fit_transform(self, X, y):
        X_transformed = X.copy()

        if self.method == 'univariate':
            self.univariate_selection(X, y)
        elif self.method == 'rfe':
            self.rfe_selection(X, y)
        elif self.method == 'lasso':
            self.lasso_selection(X, y)
        elif self.method == 'random_forest':
            self.random_forest_importance_selection(X, y)
        elif self.method == 'pearson_correlation':
            self.pearson_correlation_selection(X, y)
        elif self.method == 'spearman_correlation':
            self.spearman_correlation_selection(X, y)
        elif self.method == 'box_cox':
            self.box_cox_selection(X, y)

        if self.selected_features is not None:
            X_transformed = X_transformed[self.selected_features]

        return X_transformed

    def univariate_selection(self, X, y):
        selector = SelectKBest(k=self.k) if self.k else SelectPercentile(percentile=self.percentile)
        selector.fit(X, y)
        self.selected_features = X.columns[selector.get_support(indices=True)].tolist()
        print(self.selected_features)

    def rfe_selection(self, X, y):
        estimator = RandomForestClassifier()
        selector = RFE(estimator, n_features_to_select=self.k, **self.kwargs)
        selector.fit(X, y)
        self.selected_features = X.columns[selector.support_].tolist()

    def lasso_selection(self, X, y):
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        selector = SelectFromModel(LassoCV(), max_features=self.k, **self.kwargs)
        selector.fit(X_scaled, y)
        self.selected_features = X.columns[selector.get_support(indices=True)].tolist()

    def random_forest_importance_selection(self, X, y):
        selector = SelectFromModel(RandomForestClassifier(), max_features=self.k, **self.kwargs)
        selector.fit(X, y)
        self.selected_features = X.columns[selector.get_support(indices=True)].tolist()

    def pearson_correlation_selection(self, X, y):
        # Create a DataFrame from X with columns 
        df = pd.DataFrame(X, columns = X.columns)
        # Add the target variable to df
        df['Target'] = y

        # Calculate the correlation matrix
        corr_matrix = df.corr(method='pearson')

        # Select the features that have a correlation above the threshold with the target
        self.selected_features = [column for column in corr_matrix.columns 
                                  if abs(corr_matrix['Target'][column]) > self.correlation_threshold]
        # remove the 'Target' as it's not an original feature in X
        self.selected_features.remove('Target')

    def spearman_correlation_selection(self, X, y):
        # Create a DataFrame from X with columns 
        df = pd.DataFrame(X, columns = X.columns)
        # Add the target variable to df
        df['Target'] = y

        # Calculate the correlation matrix
        corr_matrix = df.corr(method='spearman')

        # Select the features that have a correlation above the threshold with the target
        self.selected_features = [column for column in corr_matrix.columns 
                                  if abs(corr_matrix['Target'][column]) > self.correlation_threshold]
        # remove the 'Target' as it's not an original feature in X
        self.selected_features.remove('Target')



    def box_cox_selection(self, X, y):
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        skewed_feats = X[numeric_cols].apply(lambda x: skew(x)).sort_values(ascending=False)
        skewness = pd.DataFrame({'Skew': skewed_feats})
        skewness = skewness[abs(skewness['Skew']) > self.box_cox_threshold]
        self.selected_features = skewness.index[:self.k].tolist()


class InteractionFeature(Feature):
    def __init__(self, method, columns, name=0):
        self.method = method
        self.columns = columns

        if name == 0:
            self.name = method
        else:
            self.name = name
        
    def generate(self, data, pipeline):

        transformed_data = pd.DataFrame(index=data.index)  # Initialize an empty DataFrame with the same index as data

        for i in range(2, len(self.columns) + 1):
            for combination in combinations(self.columns, i):
                interaction_name = self.name + '_' + '_'.join(combination)
                transformed_data[interaction_name] = data[combination[0]]

                # Perform the interaction operation on the selected columns
                for column in combination[1:]:
                    if self.method == 'multiply':
                        transformed_data[interaction_name] *= data[column]
                    elif self.method == 'add':
                        transformed_data[interaction_name] += data[column]
                    elif self.method == 'subtract':
                        transformed_data[interaction_name] -= data[column]
                    elif self.method == 'divide':
                        transformed_data[interaction_name] /= (data[column] + 1e-10)

        return transformed_data