import plotly.graph_objs as go
from numpy import sign
import dataGet
a0name='AAPL'
a1name='MSFT'
time='5y'
update='1d'
strategy='infgrid'
step=1.04
fee=0.0
feeFix=1.0+fee/2
tradeFix=1.0-fee
funds=1000000

def volatility(t):
    n=min(10,len(t))
    s=0
    prev=t[0]
    for i in range(1,n):
        s+=abs(t[i]/prev-1)
        prev=t[i]
    return s/(n-1)


if a0name=='USD': usd=True
else : usd=False
price=[]
price2=[]
eguity=[]
hold50=[]
a1hold=[]
dataIndex,price=dataGet.getData(a0name,a1name,time,update)
p0=price[0]
hold=funds/p0
info=strategy+' '+time+' '+update+' '
asset0=funds/2
asset1=asset0/p0
C=asset0*asset1
outside0=False
outside1=False
if strategy=='rebalance':
    up=p0*step
    low=p0/step
    for p in price:
        eguity.append((asset0+asset1*p)/funds)
        hold50.append((p+1)/2)
        if p>=up or p<=low:
            up=p*step
            low=p/step
            trade=feeFix*(asset1*p-asset0)/2
            if trade>0:
                asset0+=trade*tradeFix
                asset1-=trade/p
            else:
                asset0+=trade
                asset1-=tradeFix*trade/p
    info+='fluctuation profit: '+str((asset0*asset1/C)**0.5*100-100)[:4]+'% '
elif strategy=='infgrid':
    up=p0*step
    low=p0/step
    A=asset0
    for p in price:
        cap=asset0+asset1*p
        eguity.append((cap)/funds)
        hold50.append((p+1)/2)
        if p>=up or p<=low:
            up=p*step
            low=p/step
            if cap>A:
                asset1=A/p
                asset0=cap-A
    info+='fluctuation profit: '+str((asset0*asset1/C)**0.5*100-100)[:4]+'% '
            
elif strategy=='grid':
 print('set grid range %: ')
 s=input()
 info+='grid range: '+s+'% '
 r=1.0+float(s)/100
 a=(step-1)/(1-1/r)
 up=p0*step
 low=p0/step
 a0less=True
 trade=a*asset0/price[0]
 tradeM=trade*tradeFix
 for p in price:
  eguity.append((asset0+asset1*p)/funds)
  hold50.append((p+1)/2)
  while p>=up:
   up*=step
   low*=step
   if a0less:
    asset0+=tradeM*p*tradeFix
    asset1-=tradeM
    if asset0>asset1*p:
     a0less=False
     trade=a*asset1*p
     tradeM=trade*tradeFix
   elif asset1>=trade/p:
    asset1-=trade/p
    asset0+=tradeM
   else: outside1=True
  while p<=low:
   up/=step
   low/=step
   if not a0less:
    asset1+=tradeM/p*tradeFix
    asset0-=tradeM
    if asset0<asset1*p:
     a0less=True
     trade=a*asset0/p
     tradeM=trade*tradeFix
   elif asset0>=trade*p:
    asset0-=trade*p
    asset1+=tradeM
   else: outside0=True
elif strategy=='gridS':
    s=input('set grid range %: ')
    info+='grid range:'+s+'% '
    efr=0
    pom1=1.0+float(s)/100
    pom2=1.0
    while pom2<pom1:
        efr+=1
        pom2*=step
    efr=1/efr
    s=input('return difference: ')
    rdif=float(s)
    rdif=rdif**(1/len(price))
    up=p0*step
    low=p0/step
    refPrice=1
    for p in price:
        eguity.append((asset0+asset1*p)/funds)
        hold50.append((p+1)/2)
        a1hold.append((asset1*p)/(asset0+asset1*p))
        trade=(asset0+asset1*p)*efr
        flag=True
        while p>=up:
            if asset1-trade/p>=0:
                up*=step
                low*=step
                asset0+=trade
                asset1-=trade/p
            else:
                outside1=True
                break
        while p<=low:
            if asset0-trade>=0:
                up/=step
                low/=step
                asset0-=trade
                asset1+=trade/p
            else:
                flag=False
                outside0=True
                break
        if flag:
            up*=rdif
            low*=rdif
elif strategy=='100fluct' or strategy=='100trend':
    catchTrend=False
    prevUp=False
    if strategy=='100trend':
        catchTrend=True
        prevUp=True
    print('set step range %: ')
    s=input()
    info+='step: '+s+'% '
    step=1.0+float(s)/100
    asset0=0.0
    asset1=funds/p0
    up=p0*step
    low=p0/step
    for i in range(len(price)):
        p=price[i]
        eguity.append((asset0+asset1*p)/funds)
        hold50.append((p+1)/2)
        if p>=up:
            up=p*step
            low=p/step
            if not prevUp:
                prevUp=True
                if catchTrend:
                    asset1=asset0/p
                    asset0=0.0
                else:
                    asset0=asset1*p
                    asset1=0.0
        if p<=low:
            up=p*step
            low=p/step
            if prevUp:
                prevUp=False
                if catchTrend:
                    asset0=asset1*p
                    asset1=0.0
                else:
                    asset1=asset0/p
                    asset0=0.0
elif strategy=='stepStreak':
    up=p0*step
    low=p0/step
    streakUp=[0 for _ in range(20)]
    streakDown=[0 for _ in range(20)]
    streak=0
    Up=True
    for p in price:
        if p>=up or p<=low:
            if p>=up:
                if Up: streak+=1
                else:
                    Up=True
                    streakDown[min(19,streak)]+=1
                    streak=1
            else:
                if not Up: streak+=1
                else:
                    Up=False
                    streakUp[min(19,streak)]+=1
                    streak=1
            up=p*step
            low=p/step
    print(' \tUp\tDown\t')
    for i in range(1,20): print(i,streakUp[i],streakDown[i],sep='\t')
    exit()
elif strategy=='buypower':
    prev=1
    power=0
    balance=1
    inflow=0.5
    edge=20
    clock=0
    pos='none'
    m=1/volatility(price)
    for p in price:
        chg=(1-p/prev)*m
        if clock==0:
            pos=0
            if abs(power)>edge:
                pos=sign(power)
                clock=2
        else: clock-=1
        balance+=pos*balance*(p/prev-1)
        eguity.append(balance)
        hold50.append(power/100)
        power-=chg
        power-=sign(power)*inflow
        prev=p

else: print('no stategy selected')
if len(hold50)>1:
    zwrot=int((eguity[-1]/hold50[-1]-1)*10000)/100
    info+=' return to holding: '+str(zwrot)+'% '
if outside0:
 print('not enough',a0name,'to run grid')
 info+=' not enough '+a0name
if outside1:
 print('not enough',a1name,'to run grid')
 info+=' not enough '+a1name
fig = go.Figure()

#Candlestick
"""fig.add_trace(go.Candlestick(x=data0.index,
                open=data0['Open'],
                high=data0['High'],
                low=data0['Low'],
                close=data0['Close'], name = a0name))"""
fig.add_trace(go.Scatter(
    x=dataIndex,
    y=price,
    name=a1name+'/'+a0name,
    mode='lines',
    marker=dict(size=[0, 0, 0, 30, 0, 0],
            color=[0, 0, 0, 10, 0, 0])
))
if len(hold50)>1: fig.add_trace(go.Scatter(
    x=dataIndex,
    y=hold50,
    name='hold 50/50',
    mode='lines',
    marker=dict(size=[0, 0, 0, 30, 0, 0],
            color=[0, 0, 0, 10, 10, 0])
))
fig.add_trace(go.Scatter(
    x=dataIndex,
    y=eguity,
    name=strategy+' '+str(int(100*asset0/funds/eguity[-1]))+'%'+a0name,
    mode='lines',
    marker=dict(size=[0, 0, 0, 30, 0, 0],
            color=[0, 0, 0, 10, 10, 0])
))
if len(a1hold)>1: fig.add_trace(go.Scatter(
    x=dataIndex,
    y=a1hold,
    name=a1name+'% in portfolio',
    mode='lines',
    marker=dict(size=[0, 0, 0, 30, 0, 0],
            color=[0, 0, 0, 10, 10, 0])
))
fig.update_layout(
    title=info,
    yaxis_title='Price fluctuations + strategy performance')
fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1d", step="day", stepmode="todate"),
            dict(count=30, label="30d", step="day", stepmode="backward"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(count=5, label="5y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    )
)
fig.show()
