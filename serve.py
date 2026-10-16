# serve.py  -  starts your website WITH the redirect rules switched on.
# Put it in the SAME folder as app.py and redirects.py  (D:\website).
#
# Your existing app is not touched: this file just wraps it.
from app import app as _site          # app.py -> the object called  app
from redirects import SiteRules

app = SiteRules(_site)                # Waitress now runs  serve:app  instead of  app:app
