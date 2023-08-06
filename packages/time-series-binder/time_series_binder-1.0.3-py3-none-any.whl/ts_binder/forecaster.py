import pandas as pd
import numpy as np

from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from tensorflow.keras.models import Sequential
from neuralprophet import NeuralProphet

class Forecaster:
    """
    Forecaster class
    This class provides methods to make forecasts using the trained models.
    forecast_sarimax(model: SARIMAX) -> pd.Series
    This method uses the given SARIMAX model to make future predictions for a fixed number of time steps and returns the predicted values as a Pandas series.
    forecast_lstm(model: Sequential, last_sequence: np.ndarray, n_features: int) -> pd.Series
    This method uses the given LSTM model to make future predictions for a fixed number of time steps using the last sequence of input data, and returns the predicted values as a Pandas series.
    forecast_neural_prophet(model, df_future) -> pd.DataFrame
    This method uses the given NeuralProphet model to make future predictions and returns the predicted values along with their associated uncertainty intervals as a Pandas dataframe. The df_future argument is a Pandas dataframe that specifies the future time steps for which predictions are to be made.
    """
    def __init__(self, time_steps: int):
        """
        Initialize a Forecaster object.
        Args:
            time_steps: The number of time steps to forecast.
        """
        self.time_steps = time_steps
    
    def forecast_sarimax(self, model: SARIMAX) -> pd.Series:
        """
        Generate forecasts using a fitted SARIMAX model.
        Args:
            model: A fitted SARIMAX model object.
        Returns:
            A pandas Series containing the forecast values.
        """
        return model.forecast(self.time_steps).reset_index(drop=True)
    
    def forecast_exponential_smoothing(self, model: ExponentialSmoothing) -> pd.Series:
        """
        Generate forecasts using a fitted Exponential Smoothing model.
        
        Args:
            model: a fitted ExponentialSmoothing model object.
        
        Returns:
            A pandas Series containing the forecast values.
        """
        return model.forecast(self.time_steps).reset_index(drop=True)

    def forecast_lstm(self, model: Sequential, last_sequence: np.ndarray, n_target: int) -> pd.Series:
        """
        Generate forecasts using a fitted LSTM model.
        Args:
            model: A fitted LSTM model object.
            last_sequence: The last sequence of the input data used to fit the model.
            n_target: The number of features in the input data.
        Returns:
            A pandas Series containing the forecast values.
        """
        n_steps = last_sequence.shape[0]
        temp_input = list(last_sequence.reshape(-1))
        lst_output = []
        i = 0
        while i < self.time_steps:
            if len(temp_input) > n_steps * n_target:
                x_input = np.array(temp_input[-n_steps * n_target:]).reshape((1, n_steps, n_target))
                yhat = model.predict(x_input, verbose=0)
                temp_input.append(yhat[0][0])
                lst_output.append(yhat[0][0])
                i += 1
            else:
                x_input = np.array(temp_input[-n_steps * n_target:]).reshape((1, n_steps, n_target))
                yhat = model.predict(x_input, verbose=0)
                temp_input.append(yhat[0][0])
                lst_output.append(yhat[0][0])
                i += 1
        return pd.Series(lst_output)

    def forecast_prophet(self, model: NeuralProphet, data: pd.DataFrame) -> pd.Series:
        """
        Generate forecasts using a fitted NeuralProphet model.
        Args:
            model: A fitted NeuralProphet model object.
            data: The input data used to fit the model as a pandas DataFrame.
        Returns:
            A pandas Series containing the forecast values.
        """
        df = data.reset_index()
        df.columns = ['ds', 'y']
        df = df.drop_duplicates(subset=['ds'])

        future = model.make_future_dataframe(df, periods=self.time_steps)
        forecast = model.predict(future)
        forecast_values = forecast['yhat1'].tail(self.time_steps)
        return forecast_values