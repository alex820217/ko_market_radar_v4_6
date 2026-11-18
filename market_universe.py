MARKET_GROUPS={
"Deutschland":{"DAX":"^GDAXI","SAP":"SAP.DE","Siemens":"SIE.DE","Allianz":"ALV.DE","Deutsche Telekom":"DTE.DE","Airbus":"AIR.DE","Rheinmetall":"RHM.DE","Mercedes-Benz":"MBG.DE","BMW":"BMW.DE","BASF":"BAS.DE","Infineon":"IFX.DE","Deutsche Bank":"DBK.DE","Commerzbank":"CBK.DE","Adidas":"ADS.DE","Vonovia":"VNA.DE","DHL Group":"DHL.DE"},
"US Tech":{"Microsoft":"MSFT","Apple":"AAPL","NVIDIA":"NVDA","Amazon":"AMZN","Meta":"META","Alphabet":"GOOGL","Tesla":"TSLA","AMD":"AMD","Broadcom":"AVGO","Netflix":"NFLX","Palantir":"PLTR","Micron":"MU"},
"Indizes":{"Nasdaq 100":"^NDX","S&P 500":"^GSPC","Dow Jones":"^DJI","Euro Stoxx 50":"^STOXX50E"},
"Metalle":{"Gold":"GC=F","Silber":"SI=F","Kupfer":"HG=F","Platin":"PL=F"},
"Energie":{"WTI Öl":"CL=F","Brent Öl":"BZ=F","Natural Gas":"NG=F"}}
def build_universe(groups):
 out=[];seen=set()
 for g in groups:
  for n,t in MARKET_GROUPS[g].items():
   if t not in seen:out.append({'group':g,'name':n,'ticker':t});seen.add(t)
 return out
def all_assets():
 return sorted([(n,t,g) for g,a in MARKET_GROUPS.items() for n,t in a.items()],key=lambda x:x[0].casefold())
