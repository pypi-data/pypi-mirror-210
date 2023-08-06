import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

class InverseTransform:
    
    def __init__(self, data):
        self.data = data
    
    def differenced(self, last_obs):
        inverse_data = np.exp(self.data.cumsum()) * last_obs
        inverse_series = pd.Series(inverse_data, 
                                   name=self.data.name, 
                                   index=self.data.index)
        return inverse_series
    
    def scaled(self, scaler_):
        inverse_data = scaler_.inverse_transform(self.data.values.reshape(-1,1))
        inverse_series = pd.Series(inverse_data.reshape(-1), 
                                   name=self.data.name, 
                                   index=self.data.index)
        return inverse_series
    
def analyze_data(data, show_graph=True, **kwargs):
        """
        Genrates correlogram plots for a given time series data.
        
        Args:
            data: a pandas.DataFrame object.
            show_graph: (bool, optional).
            kwargs: Additional arguments to be passed to plot_pacf.
            
        Returns: 
            None
        """
        data = data.dropna()

        values = []
        means = []
        variance = []
        for idx in data:
            values.append(idx)
            means.append(np.mean(values))
            variance.append(np.var(values))

        sum_stat = pd.DataFrame({'Means':means, 'Variance':variance})
        sum_stat.index = data.index
        result = adfuller(data)
        test_statistic, p_value, lags, _, _, _ = result

        if show_graph:
            fig = plt.figure(figsize=(10, 8))
            gs = fig.add_gridspec(3, 2)

            ax1 = fig.add_subplot(gs[0, :])
            ax1.plot(data)
            ax1.set_title(data.name)

            ax2 = fig.add_subplot(gs[1, 0])
            plot_acf(data, ax=ax2, **kwargs)

            ax3 = fig.add_subplot(gs[1, 1])
            plot_pacf(data, ax=ax3, method='ywm', **kwargs)

            ax4 = fig.add_subplot(gs[2, 0])
            ax4.plot(sum_stat['Means'])
            ax4.axhline(np.mean(data), linestyle='--', label='Actual Usage Mean', color='red')
            ax4.legend()
            ax4.set_title('Mean Over Time')

            ax5 = fig.add_subplot(gs[2, 1])
            ax5.plot(sum_stat['Variance'])
            ax5.axhline(np.var(data), linestyle='--', label='Actual Usage Variance', color='red')
            ax5.legend()
            ax5.set_title('Variance Over Time')

            fig.tight_layout(pad=3.0)
            plt.show()

            frame = pd.DataFrame({' ':['Test Statistic', 'p-value', 'lags'], "value":[test_statistic, p_value, lags]})
            frame.set_index(' ', inplace=True)
            display(frame)

        if p_value < 0.05:
            out = 'STATIONARY'
        else:
            out = 'NONE STATIONARY'
        print(out)
        
def evaluate_forecast(y_test, y_pred):
    """
    Evaluate a time series forecast using common metrics.
    
    Parameters:
    y_test (numpy.ndarray): Array of true values with shape (n_samples,).
    y_pred (numpy.ndarray): Array of predicted values with shape (n_samples,).
    
    Returns:
    dict: Dictionary containing metrics and their values.
    """
    # Calculate metrics
    mse = np.mean((y_test - y_pred)**2)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    mae = np.mean(np.abs(y_test - y_pred))
    mase = np.mean(np.abs(y_test - y_pred)) / np.mean(np.abs(np.diff(y_test)))
    
    # Store metrics in dictionary
    metrics = {'MSE': mse, 'RMSE': rmse, 'MAPE': mape, 'MAE': mae, 'MASE': mase}
    
    return metrics