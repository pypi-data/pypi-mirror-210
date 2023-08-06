import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.exponential_smoothing import ExponentialSmoothing
from statsmodels.nonparametric.smoothers_lowess import lowess
from statsmodels.tsa.stattools import adfuller
from sklearn.preprocessing import MinMaxScaler, StandardScaler

class DataPreprocessing:
    """
    This class provides methods to preprocess the time series data before feeding it to the models.
    smoothen(data: pd.Series, method: str)
    This static method smoothes the given time series data using one of the following methods:
    Moving Average Smoothing (MAS) - method='MAS'
    Exponential Smoothing (ES) - method='ES'
    LOcally WEighted Scatterplot Smoothing (LOWESS) - method='LOWESS'
    difference(data: pd.Series, lag: int)
    This static method calculates the first-difference of the given time series data and returns the differenced data along with the optimal lag value determined using the Augmented Dickey-Fuller (ADF) test.
    make_sequence(data: pd.Series, n_features: int)
    This static method converts the given time series data into a sequence of input-output pairs of a fixed length n_features.
    scale(data: pd.Series, **kwargs)
    This static method scales the given time series data to the range [0, 1] using the Min-Max scaling technique and returns the scaler object along with the scaled data.
    """
    @staticmethod
    def smoothen(data: pd.Series, method):
        """
        Apply smoothing to a time series using a given method.
        Args:
            data: The time series to be smoothed.
            method: The method of smoothing to be applied. It can be 'MAS' (moving average smoothing),
                    'ES' (exponential smoothing), or 'LOWESS' (locally weighted scatterplot smoothing).
        Returns:
            The smoothed time series.
        Raises:
            ValueError: If an inappropriate method value is provided.
        """
        try:
            if method == 'MAS':
                out = data.rolling(5).mean()
            elif method == 'ES':
                out = ExponentialSmoothing(data).fit().fittedvalues
            elif method == 'LOWESS':
                _ = lowess(data.values.ravel(), np.arange(len(data)), frac=0.05)[:, 1]
                out = pd.DataFrame(data={f'{data.name}':_})
                out.index = data.index
                out = out[data.name]
            else:
                print('Inappropriate `method` value, choose from; MAS, ES, LOWESS')

            return out
        except UnboundLocalError as ue:
            pass
    
    @staticmethod
    def difference(data: pd.Series, lag=1):
        """
        Compute first-order difference of a time series.
        Args:
            data: The time series to be differenced.
            lag: The number of lags to be used for the differencing.
        Returns:
            The differenced time series and the selected lag.
        Raises:
            ValueError: If the p-value for the Augmented Dickey-Fuller test is not significant for any lag value.
        """
        diff_data = np.log(data).diff(lag)
        p_val = adfuller(diff_data.dropna())[1]
        while p_val > 0.05:
            lag += 1
            diff_data = np.log(data).diff(lag)
            p_val = adfuller(diff_data.dropna())[1]
        return diff_data, lag

    @staticmethod
    def make_sequence(data: pd.Series, n_features):
        """
        Create input and output sequences from a given time series for training a LSTM model.
        Args:
            data: The time series to be used for creating the sequences.
            n_features: The number of input features for each sequence.
        Returns:
            The input and output sequences as numpy arrays.
        """
        X, y = [],[]
        for i in range(len(data)):
            end_ix = i + n_features
            if end_ix > len(data)-1:
                break
            seq_x, seq_y = data[i:end_ix], data[end_ix]
            X.append(seq_x)
            y.append(seq_y)
        return np.array(X), np.array(y)
    
    @staticmethod
    def scale(data: pd.Series, scaler_type: str = "minmax", **kwargs):
        """
        Scale a time series using either MinMax scaler or Standard scaler.
        Args:
            data: The time series to be scaled.
            scaler_type: A string indicating the type of scaler to use. Can be either "minmax" (default) or "standard".
            **kwargs: Additional arguments to be passed to the scaler constructor.
        Returns:
            The fitted scaler object and the scaled time series.
        """
        if scaler_type == "minmax":
            scaler_ = MinMaxScaler(**kwargs)
        elif scaler_type == "standard":
            scaler_ = StandardScaler(**kwargs)
        else:
            raise ValueError(f"Scaler type {scaler_type} is not supported.")

        scaled_data = scaler_.fit_transform(data.values.reshape(-1,1))
        scaled_data = pd.Series(scaled_data.reshape(-1), name=data.name, index=data.index)

        return scaler_, scaled_data