from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 1 - Planning',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

desc = """Time Series Binder is a Python library for time series analysis and forecasting. It offers a comprehensive set of tools and models, including Pandas integration, statistical methods, neural networks with Keras, and the NeuralProphet library. With Time Series Binder, you can easily manipulate, visualize, and predict time series data, making it an essential toolkit for researchers and analysts."""
 
dependencies = ['pandas', 
                'numpy', 
                'matplotlib', 
                'statsmodels', 
                'keras', 
                'neuralprophet', 
                'scikit-learn', 
                'tqdm', 
                'tabulate']

setup(
  name='time_series_binder',
  version='1.0.2',
  description=desc,
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Jhun Brian Andam',
  author_email='brianandam123@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords=['Time Series Analysis', 'Forecasting'], 
  packages=find_packages(),
  install_requires=dependencies
)