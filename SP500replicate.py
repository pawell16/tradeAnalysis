import yfinance as yf
def f1(e):
    return e[1]
stock=['AAPL','MSFT','AMZN','TSLA','GOOGL','NVDA','FB']
shares=[134935338, 65249358, 3808674, 7286163, 5000000, 21758920, 20097212]
weight=[6.94843,5.867116,3.562516,2.262093,4.074216,1.522961,1.353449]
price = yf.download(stock, period='1d',interval='1d')['Close']
cash=16700
mode='shares'
s=0
for i in range(len(stock)):
    if mode=='shares': mcap=price[stock[i]][0]*shares[i]
    elif mode=='marketCap': mcap=yf.Ticker(stock[i]).info['marketCap']
    elif mode=='weight': mcap=weight[i]
    else: exit()
    stock[i]=(stock[i],mcap)
    s+=mcap
for i in range(len(stock)): stock[i]=(stock[i][0],int(cash*stock[i][1]/s))
stock.sort(reverse=True,key=f1)
print(len(stock))
print(stock)