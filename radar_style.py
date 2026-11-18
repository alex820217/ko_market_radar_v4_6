"""Robust radar presentation using emoji badges instead of pandas CSS.
Works consistently in Streamlit Cloud tables.
"""
def signal_label(signal):
    v=str(signal).upper()
    if "CONFIRMED LONG" in v:return "🟢🟢 CONFIRMED LONG"
    if "EARLY LONG" in v:return "🟢 EARLY LONG"
    if "CONFIRMED SHORT" in v:return "🔴🔴 CONFIRMED SHORT"
    if "EARLY SHORT" in v:return "🔴 EARLY SHORT"
    if "PRE-LONG" in v:return "🟡 PRE-LONG"
    if "PRE-SHORT" in v:return "🟡 PRE-SHORT"
    if "WATCH LONG" in v:return "🟡 WATCH LONG"
    if "WATCH SHORT" in v:return "🟡 WATCH SHORT"
    if "LATE ENTRY" in v:return "⛔ LATE ENTRY"
    if "HOT ENTRY" in v:return "🔥 HOT ENTRY"
    if "CONTEXT CONFLICT" in v:return "⚠️ CONTEXT CONFLICT"
    if "NO TRADE" in v:return "⛔ NO TRADE"
    return "⚪ WAIT"
def grade_label(v):
    return {"A+":"🟢 A+","A":"🟢 A","B":"🟡 B","C":"🟠 C","-":"⚪ -"}.get(str(v),str(v))
def entry_label(v):
    u=str(v).upper()
    if "OPTIMAL" in u:return "🟢 OPTIMAL"
    if "AKZEPTABEL" in u:return "🟡 AKZEPTABEL"
    if "SPÄT" in u:return "🔴 SPÄT"
    return str(v)
def regime_label(v):
    u=str(v).upper()
    return "🟢 LONG" if u=="LONG" else "🔴 SHORT" if u=="SHORT" else "⚪ NEUTRAL"
def prepare_radar(df):
    d=df.copy()
    if "Signal" in d:d["Signal"]=d["Signal"].map(signal_label)
    if "Grade" in d:d["Grade"]=d["Grade"].map(grade_label)
    if "Entry Status" in d:d["Entry Status"]=d["Entry Status"].map(entry_label)
    for c in ["60m Regime","15m Bias"]:
        if c in d:d[c]=d[c].map(regime_label)
    return d
