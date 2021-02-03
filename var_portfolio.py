# var_portfolio.py

#Importing all required libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_datareader as web
from matplotlib.ticker import FuncFormatter
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from matplotlib.ticker import FuncFormatter

tickers = ['GOOGL','FB','AAPL','NFLX','AMZN']
thelen = len(tickers)
price_data = []
for ticker in range(thelen):   
    prices = web.DataReader(tickers[ticker], start='2018-06-20', end = '2020-06-20', data_source='yahoo')   
    price_data.append(prices[['Adj Close']])
df_stocks = pd.concat(price_data, axis=1)
df_stocks.columns=tickers
df_stocks.tail()

#Annualized Return
mu = expected_returns.mean_historical_return(df_stocks)
#Sample Variance of Portfolio
Sigma = risk_models.sample_cov(df_stocks)#Max Sharpe Ratio - Tangent to the EF
from pypfopt import objective_functions, base_optimizer
ef = EfficientFrontier(mu, Sigma, weight_bounds=(0,1)) #weight bounds in negative allows shorting of stocks
sharpe_pfolio=ef.max_sharpe() #May use add objective to ensure minimum zero weighting to individual stocks
sharpe_pwt=ef.clean_weights()
print(sharpe_pwt)

#VaR Calculation
ticker_rx2 = []#Convert Dictionary to list of asset weights from Max Sharpe Ratio Portfolio
sh_wt = list(sharpe_pwt.values())
sh_wt=np.array(sh_wt)

for a in range(thelen):  
    ticker_rx = df_stocks[[tickers[a]]].pct_change()
    ticker_rx = (ticker_rx+1).cumprod()
    ticker_rx2.append(ticker_rx[[tickers[a]]])
    ticker_final = pd.concat(ticker_rx2,axis=1)
ticker_final

#Plot graph of Cumulative/HPR of all stocks
for i, col in enumerate(ticker_final.columns):
    ticker_final[col].plot()
plt.title('Cumulative Returns')
plt.xticks(rotation=80)
plt.legend(ticker_final.columns)#Saving the graph into a JPG file
plt.savefig('CR.png', bbox_inches='tight')

#Taking Latest Values of Return
pret = []
pre1 = []
price =[]
for x in range(thelen):
  pret.append(ticker_final.iloc[[-1],[x]])
  price.append((df_stocks.iloc[[-1],[x]]))
pre1 = pd.concat(pret,axis=1)
pre1 = np.array(pre1)
price = pd.concat(price,axis=1)
varsigma = pre1.std()
ex_rtn=pre1.dot(sh_wt)
print('The weighted expected portfolio return for selected time period is'+ str(ex_rtn))
#ex_rtn = (ex_rtn)**0.5-(1) 
#Annualizing the cumulative return (will not affect outcome)
price=price.dot(sh_wt) #Calculating weighted value
print(ex_rtn, varsigma, price)

from scipy.stats import norm
import math
Time=1440 #No of days(steps or trading days in this case)
lt_price=[]
final_res=[]
for i in range(1000): #10000 runs of simulation
    if i%100==0:
        print(i)
    daily_return=(np.random.normal(ex_rtn/Time,varsigma/math.sqrt(Time),Time))
    plt.plot(daily_return)
plt.axhline(np.percentile(daily_return,5), color='r', linestyle='dashed', linewidth=1)
plt.axhline(np.percentile(daily_return,95), color='g', linestyle='dashed', linewidth=1)
plt.axhline(np.mean(daily_return), color='b', linestyle='solid', linewidth=1)
plt.show()

plt.hist(daily_return,bins=15)
plt.axvline(np.percentile(daily_return,5), color='r', linestyle='dashed', linewidth=2)
plt.axvline(np.percentile(daily_return,95), color='r', linestyle='dashed', linewidth=2)
plt.show()
plt.savefig('daily_r_histogram.png', bbox_inches='tight')

print(np.percentile(daily_return,5),np.percentile(daily_return,95)) #VaR - Minimum loss of 5.7% at a 5% probability, also a gain can be higher than 15% with a 5 % probability
pvalue = 1000 #portfolio value
print('$Amount required to cover minimum losses for one day is ' + str(pvalue* - np.percentile(daily_return,5)))