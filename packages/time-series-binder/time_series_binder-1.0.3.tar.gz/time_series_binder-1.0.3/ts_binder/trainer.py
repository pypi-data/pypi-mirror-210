import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from ts_binder.data_processing import DataPreprocessing

from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.statespace.exponential_smoothing import ExponentialSmoothing
from statsmodels.tsa.holtwinters import ExponentialSmoothing as holtwinters_ES
from keras.models import Sequential
from keras.layers import LSTM, Dense
from neuralprophet import NeuralProphet

from neuralprophet.utils import set_random_seed
import tensorflow as tf
from tensorflow.keras import layers
import random

from keras.metrics import RootMeanSquaredError, MeanAbsolutePercentageError, MeanAbsoluteError

class Trainer:
    """
    This class provides methods to train the time series forecasting models.
    train_sarimax(show_summary: bool, **kwargs)
    This method trains a SARIMAX model on the preprocessed time series data and returns the trained model object. show_summary flag can be set to True to print the model summary.
    train_lstm(n_steps: int, n_target: int, epochs: int, batch: int, optimizer: str, **kwargs)
    This method trains a Long Short-Term Memory (LSTM) model on the preprocessed time series data and returns the last sequence of input data along with the trained model object. n_steps and n_target represent the number of time steps and input features respectively, epochs and batch are the number of training epochs and batch size, and optimizer is the name of the optimizer to use.
    train_neural_prophet(**kwargs)
    This method trains a NeuralProphet model on the preprocessed time series data and returns the trained model object.
    """
    def __init__(self, data: pd.Series):
        """
        Constructor for TimeSeriesModel class.
        Args:
            data (pd.Series): The time series data to be used for training and prediction.
        """
        self.data = data
    
    def train_sarimax(self, show_summary=True, **kwargs):
        """
        Trains a SARIMAX model on the data.
        Args:
            show_summary (bool, optional): Whether to print a summary of the model after training. Defaults to True.
            **kwargs: Additional arguments to be passed to SARIMAX.
        Returns:
            A trained SARIMAX model.
        """
        model = SARIMAX(self.data, simple_differencing=False, **kwargs).fit(disp=False)
        if show_summary:
            print(model.summary())
        return model
    
    def train_exponential_smoothing(self, model='additive' ,show_summary=True, **kwargs):
        """
        Trains a exponential smoothing model: If model == 'additive' then the model will be built using ExponentialSmoothing from 
        statsmodels.tsa.statespace.exponential_smoothing else if model == 'multiplicative' then the model will be built in 
        statsmodels.tsa.holtwinters.
        #latest update
        """
        
        if model == 'additive':
            model_obj = ExponentialSmoothing(self.data, **kwargs).fit(optimized=True)
            
        elif model == 'multiplicative':
            model_obj = holtwinters_ES(self.data, **kwargs).fit(optimized=True)
            
        else:
            raise ValueError(f"Invalid model: {model}")
        
        if show_summary:
            print(model_obj.summary())
            
        return model_obj

    def train_lstm(self, n_steps: int, n_target: int, epochs=200, batch_size=None, optimizer='adam', neurons=50, activation='relu', show_graph=True, **kwargs):
        """
        Trains an LSTM model on the data.
        Args:
            n_steps (int): The number of time steps to use for each input sequence.
            n_target (int): The number of features in each input sequence.
            epochs (int, optional): The number of epochs to train the model for. Defaults to 200.
            batch (int, optional): The batch size for training. If None, the default batch size is used. Defaults to None.
            optimizer (str or optimizer object, optional): The optimizer to use for training. Defaults to 'adam'.
            **kwargs: Additional arguments to be passed to the LSTM model.
        Returns:
            last_sequence (np.ndarray): The last input sequence used for training.
            model (keras.models.Sequential): The trained LSTM model.
        """
        np.random.seed(143)
        tf.random.set_seed(143)
        random.seed(143)
        
        sequencer = DataPreprocessing()
        X, y = sequencer.make_sequence(self.data, n_steps)
        last_sequence = X[-1]

        model = Sequential()
        model.add(LSTM(neurons, activation=activation, return_sequences=True, input_shape=(n_steps, n_target)))
        model.add(LSTM(neurons, activation=activation))
        model.add(Dense(1))
        metrics = [RootMeanSquaredError(name='rmse'),
                   MeanAbsolutePercentageError(name='mape'), 
                   MeanAbsoluteError(name='mae')]
        model.compile(optimizer=optimizer, loss='mse', metrics=metrics)
        history = model.fit(X, y, batch_size=batch_size, epochs=epochs, **kwargs)
        result_df =  pd.DataFrame(history.history)
        
        if show_graph:
            for col in result_df:
                plt.figure(figsize=(9,3))
                plt.plot(result_df[col])
                plt.title(f'Validation {str.upper(col)} per Epoch')
                plt.show()
                
        return last_sequence, model

    def train_prophet(self, **kwargs):
        """
        Trains a NeuralProphet model on the data.
        Args:
            **kwargs: Additional arguments to be passed to NeuralProphet.
        Returns:
            A trained NeuralProphet model.
        """
        
        set_random_seed(143)
        np.random.seed(143)
        random.seed(143)
        
        df = self.data.reset_index()
        df.columns = ['ds', 'y']
        df = df.drop_duplicates(subset=['ds'])
        model = NeuralProphet(**kwargs)
        model.fit(df)
        return model