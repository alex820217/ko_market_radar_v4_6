import time as tm
import pandas as pd,streamlit as st
from market_universe import MARKET_GROUPS,build_universe,all_assets
from scanner_engine import scan_asset,market_open
from radar_style import prepare_radar,signal_label
from trade_journal import create_trade,update_trade,close_trade,delete_trade,update_trade_metadata,load,enriched_df,statistics,export_bytes,backup_bytes,restore_bytes
from portfolio_summary import metrics
from position_manager import evaluate
st.set_page_config(page_title='KO Market Radar V4.6',page_icon='📡',layout='wide')
st.title('📡 KO Market Radar V4.6')
st.caption('Farbsignale · freie Basiswertauswahl · nachträgliche Korrektur · Open Position Manager · Gesamtbilanz · Lernjournal')
ASSETS=all_assets();LABELS=[f'{n} ({t})' for n,t,g in ASSETS];BY={f'{n} ({t})':(n,t) for n,t,g in ASSETS}
def eur(x):return f'{x:+.2f} €'
def default_label(ticker):return next((k for k,v in BY.items() if v[1]==ticker),LABELS[0])
def balance():
 m=metrics(load());st.subheader('💶 Gesamtbilanz');c=st.columns(7);c[0].metric('Gesamt P/L',eur(m['total']),f"{m['return_pct']:+.2f}%");c[1].metric('Realisiert',eur(m['closed']));c[2].metric('Offen',eur(m['open']));c[3].metric('Trades',m['trades']);c[4].metric('Offen',m['open_n']);c[5].metric('Geschlossen',m['closed_n']);c[6].metric('Trefferquote',f"{m['win_rate']:.1f}%")
balance();tabs=st.tabs(['🔥 Radar','💼 Open Position Manager','📓 Journal & Lernen','💾 Backup'])
scan=pd.DataFrame()
with tabs[0]:
 st.sidebar.header('Marktuniversum');groups=st.sidebar.multiselect('Gruppen',list(MARKET_GROUPS),default=['Deutschland','US Tech','Indizes']);maxa=st.sidebar.slider('Max Assets',10,50,30);only=st.sidebar.checkbox('Geschlossene Märkte überspringen',True)
 if st.sidebar.button('Cache leeren'):st.cache_data.clear();st.rerun()
 items=build_universe(groups)[:maxa];items=[x for x in items if not(only and not market_open(x['ticker']))];rows=[];errs=[];bar=st.progress(0);start=tm.time()
 for i,m in enumerate(items,1):
  try:rows.append(scan_asset(m))
  except Exception as e:errs.append({'Asset':m['name'],'Fehler':str(e)})
  bar.progress(i/max(1,len(items)))
 bar.empty()
 if rows:
  scan=pd.DataFrame(rows);scan=scan.sort_values(['Score','ADX'],ascending=False);st.caption(f'{len(scan)} analysiert · {tm.time()-start:.1f}s');cols=['Asset','Signal','Grade','Score','60m Regime','15m Bias','5m Setup','3m Trigger','Entry Status','Setup-Hinweis'];st.dataframe(prepare_radar(scan[cols]),use_container_width=True,hide_index=True)
  sel=st.selectbox('Radar-Setup für Signal-Snapshot',scan.Asset.tolist());r=scan[scan.Asset==sel].iloc[0];st.subheader(f"{r.Asset} · {signal_label(r.Signal)}")
  with st.form('new'):
   wanted=st.selectbox('Basiswert des gekauften Produkts',LABELS,index=LABELS.index(default_label(r.Ticker)),help='Diese Auswahl ist unabhängig vom Radar-Setup.');name,ticker=BY[wanted]
   c=st.columns(5);wkn=c[0].text_input('WKN').upper();direction=c[1].selectbox('Richtung',['LONG','SHORT'],index=0 if 'LONG' in r.Signal else 1);entry=c[2].number_input('Kaufpreis',.0001,value=1.22,format='%.4f');qty=c[3].number_input('Stück',1,value=1000);stop=c[4].number_input('Stop',.0001,value=1.1495,format='%.4f');notes=st.text_input('Notiz');save=st.form_submit_button('Trade speichern',type='primary')
  if save:
   snap={k:(v.item() if hasattr(v,'item') else v) for k,v in r.to_dict().items()};create_trade(wkn,name,ticker,direction,entry,stop,qty,snap,{},notes);st.success(f'{wkn} auf {name} gespeichert.');st.rerun()
 if errs:
  with st.expander(f'Fehler ({len(errs)})'):st.dataframe(pd.DataFrame(errs),hide_index=True)
with tabs[1]:
 st.subheader('💼 Open Position Manager');st.caption('Basiswert, WKN und Richtung können hier jederzeit korrigiert werden.')
 for t in load('OPEN'):
  with st.container(border=True):
   entry=float(t['certificate_entry']);current=float(t.get('last_price') or entry);market=None
   try:market=scan_asset({'name':t['asset'],'ticker':t['ticker']})
   except Exception as e:st.caption(f'Basiswertanalyse nicht verfügbar: {e}')
   adv=evaluate(t,market,current);pnl=(current-entry)*float(t['quantity']);st.markdown(f"### {t['wkn']} · {t['asset']} · {t['direction']}");c=st.columns(5);c[0].metric('Aktion',adv.action);c[1].metric('Position Score',f'{adv.score}/100');c[2].metric('Geldkurs',f'{current:.4f} €');c[3].metric('P/L',eur(pnl));c[4].metric('Empf. Stop',f'{adv.recommended_stop:.4f} €')
   with st.expander('✏️ Basiswert / WKN / Richtung korrigieren'):
    with st.form('meta'+t['id']):
     lab=st.selectbox('Korrekter Basiswert',LABELS,index=LABELS.index(default_label(t['ticker'])),key='bl'+t['id']);n,tk=BY[lab];a,b=st.columns(2);ww=a.text_input('WKN',value=t['wkn'],key='w'+t['id']);dd=b.selectbox('Richtung',['LONG','SHORT'],index=0 if t['direction']=='LONG' else 1,key='d'+t['id']);nn=st.text_input('Notiz',value=t.get('notes') or '',key='n'+t['id']);ok=st.form_submit_button('Korrektur speichern')
    if ok:update_trade_metadata(t['id'],n,tk,dd,ww,nn);st.success('Korrigiert.');st.rerun()
   with st.form('upd'+t['id']):
    a,b=st.columns(2);cp=a.number_input('Aktueller Geldkurs',.0001,value=current,format='%.4f',key='cp'+t['id']);ns=b.number_input('Neuer Stop',.0001,value=float(t['certificate_stop']),format='%.4f',key='ns'+t['id']);up=st.form_submit_button('Kurs und Stop aktualisieren')
   if up:update_trade(t['id'],cp,ns);st.rerun()
   with st.expander('Technische Gründe'):
    for x in adv.reasons:st.write('• '+x)
   with st.form('close'+t['id']):
    a,b=st.columns(2);ep=a.number_input('Verkaufskurs',.0001,value=current,format='%.4f',key='ep'+t['id']);reason=b.selectbox('Exitgrund',['Stop','Trailing-Stop','Gewinnziel','Trendbruch','Manuell','Handelsschluss'],key='rs'+t['id']);cl=st.form_submit_button('Trade schließen')
   if cl:close_trade(t['id'],ep,reason);st.rerun()
   with st.expander('🗑️ Trade löschen'):
    sure=st.checkbox('Dauerhaftes Löschen bestätigen',key='sure'+t['id']);
    if st.button('Endgültig löschen',disabled=not sure,key='del'+t['id']):delete_trade(t['id']);st.rerun()
with tabs[2]:
 df=enriched_df();summary,groups=statistics();
 if summary.get('trades',0):
  c=st.columns(5);c[0].metric('Geschlossen',summary['trades']);c[1].metric('Trefferquote',f"{summary['win_rate']:.1f}%");c[2].metric('P/L',eur(summary['total_pnl']));c[3].metric('Profit Factor',f"{summary['profit_factor']:.2f}");c[4].metric('Ø R',f"{summary['avg_r']:+.2f}R");st.dataframe(groups,use_container_width=True,hide_index=True)
 st.subheader('Alle Trades');st.dataframe(df,use_container_width=True,hide_index=True)
 if not df.empty:
  opts={f"{r['wkn']} · {r['asset']} · {r['status']} · {r['id'][:8]}":r['id'] for _,r in df.iterrows()};lab=st.selectbox('Journal-Eintrag bearbeiten',list(opts));tid=opts[lab];row=df[df.id==tid].iloc[0]
  with st.form('editjournal'):
   bl=st.selectbox('Basiswert korrigieren',LABELS,index=LABELS.index(default_label(row['ticker'])));n,tk=BY[bl];a,b=st.columns(2);ww=a.text_input('WKN',value=row['wkn']);dd=b.selectbox('Richtung',['LONG','SHORT'],index=0 if row['direction']=='LONG' else 1);edit=st.form_submit_button('Korrektur speichern')
  if edit:update_trade_metadata(tid,n,tk,dd,ww,row.get('notes') or '');st.rerun()
 st.download_button('CSV herunterladen',export_bytes(),'trade_journal.csv','text/csv')
with tabs[3]:
 st.warning('SQLite auf Streamlit Cloud ist nicht garantiert dauerhaft. Backup regelmäßig herunterladen.');st.download_button('SQLite Backup',backup_bytes(),'trade_journal.sqlite3','application/octet-stream');up=st.file_uploader('Backup wiederherstellen',type=['sqlite3','db']);
 if up and st.button('Backup einspielen'):restore_bytes(up.read());st.rerun()
st.caption('Technische Entscheidungshilfe. Keine automatische Order und keine Gewinngarantie.')
