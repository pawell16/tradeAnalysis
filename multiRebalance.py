import plotly.graph_objs as go
import dataGet
time='5y'
update='1d'
asset=['AAPL','MSFT','GOOGL','AMZN','TSLA','FB','NVDA']
th=1.02
lever=1
levUpdate=100
price,hold,equity,lev=[],[],[],[]
L=len(asset)
lendPos=[(lever-1)/L/lever for _ in range(L)]
pos=[1/L for _ in range(L)]
C=1/L**L
posV=[(0,0)for _ in range(L)]
levM=lever
info='MultiRebalance, threshold '+str(th)+' '
if lever!=1: info+='lever '+str(lever)+' update '+str(levUpdate)+' '
dataIndex,trash=dataGet.getData('USD',asset[0],time,update)
for a in asset:
    trash,p=dataGet.getData('USD',a,time,update)
    price.append(p)
def f1(e): return e[1]
levFail=False
for i in range(min([len(e) for e in price])):
    p=[e[i] for e in price]
    s=0
    for e in p: s+=e
    hold.append(s/L)
    s=0
    for j in range(L):
        v=pos[j]*p[j]
        posV[j]=(j,v)
        s+=v
    equity.append(s)
    s/=L
    posV.sort(key=f1)
    dif=[s-posV[j][1] for j in range(L)]
    trade=[0 for _ in range(L)]
    j,k=0,L-1
    while j<k:
        if posV[k][1]/posV[j][1]<th: break
        if dif[j]+dif[k]>0:
            trade[k]+=dif[k]
            trade[j]-=dif[k]
            dif[j]+=dif[k]
            k-=1
        else:
            trade[j]+=dif[j]
            trade[k]-=dif[j]
            dif[k]+=dif[j]
            j+=1
    for j in range(L):
        k=posV[j][0]
        pos[k]+=trade[j]/p[k]
    if lever!=1:
        s=0
        for j in range(L):
            realPos=pos[j]-lendPos[j]
            if realPos<0: levFail=True
            s+=realPos*p[j]
        lev.append(s*levM)
        if (i+1)%levUpdate==0:
            lendPos=[(lever-1)/lever*pos[j] for j in range(L)]
            levM=lev[i]/equity[i]*lever
i=1
for v in pos: i*=v
info+='fluctuation profit: '+str((i/C)**0.5*100-100)[:4]+'% '
zwrot=int((equity[-1]/hold[-1]-1)*10000)/100
info+='return to holding: '+str(zwrot)+'% '
if levFail: info+=' leverage outside!'
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=dataIndex,
    y=hold,
    name='hold',
    mode='lines',
    marker=dict(size=[0, 0, 0, 30, 0, 0],
            color=[0, 0, 0, 10, 10, 0])
))
fig.add_trace(go.Scatter(
    x=dataIndex,
    y=equity,
    name='equity',
    mode='lines',
    marker=dict(size=[0, 0, 0, 30, 0, 0],
            color=[0, 0, 0, 10, 10, 0])
))
for i in range(L): fig.add_trace(go.Scatter(
    x=dataIndex,
    y=price[i],
    name=asset[i],
    mode='lines',
    marker=dict(size=[0, 0, 0, 10, 0, 0],
            color=[0, 0, 0, 10, 10, 0])
))
if lever!=1: fig.add_trace(go.Scatter(
    x=dataIndex,
    y=lev,
    name='lever',
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
