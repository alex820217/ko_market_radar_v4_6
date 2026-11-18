def metrics(rows):
 closed=openp=invested=0.0;closed_n=open_n=wins=0
 for r in rows:
  e=float(r.get('certificate_entry') or 0);q=float(r.get('quantity') or 0);invested+=e*q
  if r.get('status')=='CLOSED' and r.get('certificate_exit') is not None:
   p=(float(r['certificate_exit'])-e)*q;closed+=p;closed_n+=1;wins+=p>0
  else:
   cur=float(r.get('last_price') or e);openp+=(cur-e)*q;open_n+=1
 total=closed+openp
 return dict(total=total,closed=closed,open=openp,trades=len(rows),closed_n=closed_n,open_n=open_n,win_rate=wins/closed_n*100 if closed_n else 0,return_pct=total/invested*100 if invested else 0)
