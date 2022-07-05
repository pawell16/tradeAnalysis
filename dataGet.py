import yfinance as yf

def getData(a0name,a1name,time,update):
    price=[]
    if a0name=='USD':
        data1 = yf.download(tickers=a1name, period=time, interval=update)
        initialPrice=data1['Close'][0]
        for x in data1['Close']: price.append(x/initialPrice)
    else:
        data0 = yf.download(tickers=a0name, period=time, interval=update)
        data1 = yf.download(tickers=a1name, period=time, interval=update)
        if len(data0)<len(data1):
            data0fix=0
            data1fix=len(data1)-len(data0)
            dataMin=len(data0)
        else:
            data0fix=len(data0)-len(data1)
            data1fix=0
            dataMin=len(data1)
        initialPrice=data1['Close'][data1fix]/data0['Close'][data0fix]
        for i in range(0,dataMin): price.append(data1['Close'][i+data1fix]/data0['Close'][i+data0fix]/initialPrice)
    dataIndex=[]
    for i in range(len(data1)): dataIndex.append(str(data1.index[i]))
    print('data downloaded')
    return dataIndex,price
