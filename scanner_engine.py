from datetime import datetime,time
from zoneinfo import ZoneInfo
import pandas as pd,numpy as np,streamlit as st,yfinance as yf,ta

def _series(d,c):
 x=d[c];x=x.iloc[:,0] if isinstance(x,pd.DataFrame) else x;return pd.to_numeric(x,errors='coerce')
@st.cache_data(ttl=240,show_spinner=False)
def download(ticker,interval='5m',period='5d'):
 d=yf.download(ticker,interval=interval,period=period,auto_adjust=True,prepost=False,progress=False,threads=False)
 if d.empty:return d
 o=pd.DataFrame(index=d.index)
 for c in ['Open','High','Low','Close','Volume']:o[c]=_series(d,c)
 return o.dropna(subset=['Open','High','Low','Close'])
def indicators(d):
 d=d.copy();c,h,l,v=d.Close,d.High,d.Low,d.Volume.fillna(0)
 for n in [9,20,50,200]:d[f'EMA{n}']=ta.trend.EMAIndicator(c,n).ema_indicator()
 d['RSI']=ta.momentum.RSIIndicator(c,14).rsi();d['ATR']=ta.volatility.AverageTrueRange(h,l,c,14).average_true_range();d['ADX']=ta.trend.ADXIndicator(h,l,c,14).adx();d['MACD']=ta.trend.MACD(c).macd_diff()
 typ=(h+l+c)/3;day=pd.Series(d.index.date,index=d.index);cv=v.groupby(day).cumsum();d['VWAP']=((typ*v).groupby(day).cumsum()/cv.replace(0,np.nan)).fillna(d.EMA20)
 return d.dropna()
def market_open(t):
 if t.endswith('.DE') or t in {'^GDAXI','^STOXX50E'}:
  n=datetime.now(ZoneInfo('Europe/Berlin'));return n.weekday()<5 and time(9)<=n.time()<time(17,30)
 if t.startswith('^') or t.isalpha():
  n=datetime.now(ZoneInfo('America/New_York'));return n.weekday()<5 and time(9,30)<=n.time()<time(16)
 return True
def _score_side(r):
 L=sum([r.Close>r.EMA20,r.EMA20>r.EMA50,r.RSI>50,r.MACD>0]);S=sum([r.Close<r.EMA20,r.EMA20<r.EMA50,r.RSI<50,r.MACD<0]);return ('LONG' if L>=S else 'SHORT'),L,S
def scan_asset(meta):
 d5=indicators(download(meta['ticker'],'5m','5d').iloc[:-1]);d15=indicators(download(meta['ticker'],'15m','30d').iloc[:-1])
 if len(d5)<60 or len(d15)<80:raise ValueError('zu wenig bestätigte Daten')
 r5=d5.iloc[-1];r15=d15.iloc[-1];side,L,S=_score_side(r15)
 reg='LONG' if r15.Close>r15.EMA20 and r15.EMA20>r15.EMA50 else 'SHORT' if r15.Close<r15.EMA20 and r15.EMA20<r15.EMA50 else 'NEUTRAL'
 setup=sum([r5.Close>r5.VWAP,r5.EMA9>r5.EMA20,r5.RSI>50,r5.MACD>0]) if side=='LONG' else sum([r5.Close<r5.VWAP,r5.EMA9<r5.EMA20,r5.RSI<50,r5.MACD<0])
 p=d5.iloc[-2];trig=sum([r5.Close>r5.EMA9,r5.RSI>52,r5.Close>p.High]) if side=='LONG' else sum([r5.Close<r5.EMA9,r5.RSI<48,r5.Close<p.Low])
 dist=abs(r5.Close-r5.EMA20)/r5.ATR;score=min(100,(L if side=='LONG' else S)*10+setup*10+trig*7)
 late=dist>1;hot=(side=='LONG' and r5.RSI>72) or (side=='SHORT' and r5.RSI<28)
 if late and setup>=3:signal='LATE ENTRY'
 elif hot and setup>=3:signal='HOT ENTRY'
 elif reg not in {side,'NEUTRAL'}:signal='CONTEXT CONFLICT'
 elif setup>=3 and trig>=2 and score>=80:signal=('CONFIRMED ' if score>=88 else 'EARLY ')+side
 elif setup>=3:signal='PRE-'+side
 else:signal='WATCH '+side if reg==side else 'WAIT'
 entry_status='OPTIMAL' if dist<=.75 else 'AKZEPTABEL' if dist<=1 else 'SPÄT';grade='A+' if score>=92 else 'A' if score>=85 else 'B' if score>=75 else 'C' if score>=65 else '-'
 if late or hot or 'CONFLICT' in signal:grade='-'
 risk=1.2*r5.ATR;entry=float(r5.Close);stop=float(entry-risk if side=='LONG' else entry+risk)
 hint=[]
 if r5.ADX<20:hint.append(f'ADX nur {r5.ADX:.1f}')
 if dist>.75:hint.append(f'Entry {dist:.2f} ATR von EMA20')
 if hot:hint.append('RSI überhitzt')
 return {'Asset':meta['name'],'Ticker':meta['ticker'],'Signal':signal,'Grade':grade,'Score':int(score),'60m Regime':reg,'15m Bias':side,'5m Setup':f'{setup}/4','3m Trigger':f'{trig}/3','Entry Status':entry_status,'Setup-Hinweis':'; '.join(hint) or 'Setup technisch sauber','ADX':float(r5.ADX),'RSI':float(r5.RSI),'Entry':entry,'Stop':stop,'TP1':float(entry+1.8*risk if side=='LONG' else entry-1.8*risk),'TP2':float(entry+2.8*risk if side=='LONG' else entry-2.8*risk),'CRV':1.8}
