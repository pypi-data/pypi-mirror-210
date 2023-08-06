import pandas as pd


class ColumnExtractor(object):
    """Simple Class for extracting columns from a database.

    To be used in pipeline to apply the feature selection or elimination results.
    """

    def __init__(self, cols):
        """Initialize the class with colums to keep."""
        self.cols = cols

    def transform(self, X):
        """Apply to a pd.DataFrame."""
        return X[self.cols]

    def fit(self, X, y=None):
        """No Fitter."""
        return self

    def fit_transform(self, X, y=None):
        """Apply the the transform."""
        return self.transform(X)


class ColumnRenamer(object):
    """Simple Class for rename columns from a database.

    To be used in pipeline after transformers to allow further steps.
    """

    def __init__(self, col_names):
        """Initialize the class with columns name."""
        self.col_names = col_names

    def transform(self, X):
        """Apply to a np.array or pd.DataFrame."""
        X = pd.DataFrame(X, columns=self.col_names)
        return X

    def fit(self, X, y=None):
        """No Fitter."""
        return self

    def fit_transform(self, X, y=None):
        """Apply the the transform."""
        return self.transform(X)


class Categorizer:
    """Simple Class for trasform columns from a database from object dtype to category.

    To be used in pipeline before the feature elimination if the selected model used categorical features.
    """

    def __init__(self, feat_to_check=None):
        """Initialize the class with the columns to be considered. If None all are checked."""
        self.feat_to_check = None
        self._fitted = False
        return

    def fit(self, X, y=None):
        """Identify the columns with dtypes object from the input pd.DataFrame."""
        self._fitted = True
        if self.feat_to_check is None:
            self.feat_to_check = X.columns

        self._cols_to_categorize = [x for x in X[self.feat_to_check].columns if X[x].dtype == "O"]
        return

    def transform(self, X):
        """Transform the columns identified of a pd.DataFrame in type category."""
        if not self._fitted:
            raise ValueError("Categorizer not fitted. Run fit method before.")

        for x in self._cols_to_categorize:
            X[x] = X[x].astype("category")

        return X

    def fit_transform(self, X, y=None):
        """Identify and trasform the columns with dtypes object to category for the input pd.DataFrame."""
        self._fitted = True

        if self.feat_to_check is None:
            self.feat_to_check = X.columns

        self._cols_to_categorize = [x for x in X[self.feat_to_check].columns if X[x].dtype == "O"]

        for x in self._cols_to_categorize:
            X[x] = X[x].astype("category")

        return X
