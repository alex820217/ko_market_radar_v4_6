from dataclasses import dataclass
@dataclass
class Advice:action:str;score:int;recommended_stop:float;reasons:list

def _n(v):
 try:return int(str(v).split('/')[0])
 except:return 0
def trail(entry,perf):
 if perf<5:return None
 locked=max(0,(int(perf//5)-1)*5);return entry*(1+locked/100)
def evaluate(trade,market,current):
 entry=float(trade['certificate_entry']);stop=float(trade['certificate_stop']);qty=float(trade['quantity']);perf=(current/entry-1)*100;pnl=(current-entry)*qty
 if current<=stop:return Advice('⛔ STOP ERREICHT',0,stop,[f'Geldkurs {current:.4f} <= Stop {stop:.4f}'])
 t=trail(entry,perf)
 if not market:return Advice('⚪ MANUELL PRÜFEN',50,t or stop,[f'P/L {perf:+.2f}% / {pnl:+.2f} €','Keine Basiswertanalyse verfügbar'])
 direction=trade.get('direction','LONG');score=0;reasons=[]
 for key,pts in [('60m Regime',25),('15m Bias',25)]:
  ok=market.get(key)==direction;score+=pts if ok else 0;reasons.append(f'{key}: {market.get(key)}')
 s5=_n(market.get('5m Setup'));s3=_n(market.get('3m Trigger'));score+=min(20,s5*5)+min(10,s3*3);adx=float(market.get('ADX') or 0);score+=10 if adx>=20 else 5 if adx>=15 else 0;score+=10 if perf>=0 else 5 if perf>-3 else 0
 reasons += [f"5m {market.get('5m Setup')}",f"3m {market.get('3m Trigger')}",f'ADX {adx:.1f}',f'Zertifikat {perf:+.2f}%']
 conflict=sum([market.get('60m Regime') not in {direction,'NEUTRAL'},market.get('15m Bias')!=direction,s5<2,adx<15])
 if conflict>=3 or score<50:act='🔴 EXIT PRÜFEN'
 elif perf>=5 and conflict>=2:act='🟠 GEWINN ABSICHERN'
 elif t and t>stop:act='🟡 STOP NACHZIEHEN'
 elif score>=80:act='🟢 HALTEN'
 elif score>=65:act='🟡 BEOBACHTEN'
 else:act='🟠 GEWINN ABSICHERN'
 return Advice(act,max(0,min(100,score)),t or stop,reasons)
