"""
redirects.py  -  the rules that used to live in nginx, now inside Python.

It wraps your website app (WSGI middleware), so it works whether the app is Flask,
Django or anything else that Waitress can run.  Put it in the SAME folder as app.py.

What it does, in this order:
  1. blocks SEO crawler bots
  2. www.aarogyahastha.com  ->  https://aarogyahastha.com
  3. cleans double slashes (//) in the URL
  4. old Google search URL  /search?q={search_term_string}  ->  home page
  5. the 55 old-URL redirects below (exact match, CASE-SENSITIVE like nginx "location =")
  6. serves robots.txt, sitemap.xml, llms.txt straight from this folder
  7. any other /page.html  ->  /page
  8. any other *.php  ->  404 page
  Everything else is handed to your app untouched.
"""
import os
import re
from urllib.parse import quote

# >>> CHANGE THIS to your real domain: no "www", no "https://"
DOMAIN = "aarogyahastha.com"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BOTS = re.compile(
    r"AhrefsBot|SemrushBot|MJ12bot|DotBot|SeekBot|Barkrowler|Baiduspider|YandexBot", re.I
)

# One line per old URL:  "old path": "new path".
# To add another redirect, add another line here.  Nothing else to touch.
REDIRECTS = {
    '/about-us': '/about',
    '/appointment': '/appointments',
    '/services': '/',
    '/index.php': '/',
    '/index.html': '/',
    '/contact.php': '/contact',
    '/appointment.php': '/',
    '/about.php': '/about',
    '/health_packages': '/health-packages',
    '/sports_packages': '/sports-packages',
    '/departments.php': '/departments/',
    '/index': '/',
    '/None': '/',
    '/none': '/',
    '/submit-review': '/',
    '/request_callback': '/',
    '/career': '/',
    '/service': '/',
    '/doctors/dr.-santhosh-r': '/doctors/dr-santosh',
    '/doctors/dr.-santhosh': '/doctors/dr-santosh',
    '/doctors/dr.-santhosh-r-1': '/doctors/dr-santosh',
    '/departments/Urology': '/departments/urology',
    '/departments/Orthopaedics': '/departments/orthopaedics',
    '/departments/Cardiology': '/departments/cardiology',
    '/departments/Neurology': '/departments/neurology',
    '/departments/Physiotherapy': '/departments/physiotherapy',
    '/departments/Dermatology': '/departments/dermatology',
    '/departments/pain_medicine': '/departments/pain-medicine',
    '/departments/medical_gastroenterology': '/departments/medical-gastroenterology',
    '/departments/surgical_gastroenterology': '/departments/surgical-gastroenterology',
    '/departments/general_surgery': '/departments/general-surgery',
    '/departments/lab_medicine': '/departments/lab-medicine',
    '/departments/emergency_medicine': '/departments/emergency-medicine',
    '/departments/general_medicine': '/departments/general-medicine',
    '/departments/minimal_access_surgery': '/departments/minimal-access-surgery',
    '/departments/plastic_surgery': '/departments/plastic-surgery',
    '/departments/paediatric': '/departments/paediatrics',
    '/departments-new/orthopaedics': '/departments/orthopaedics',
    '/privacy_policy': '/privacy-policy',
    '/terms_and_conditions': '/terms-and-conditions',
    '/doctors/dr-geetha': '/doctors/dr-geetha-r',
    '/doctors/dr': '/doctors',
    '/doctors/dr-janaki-ram': '/doctors',
    '/doctors/dr.-sowmya': '/doctors/dr-soumya',
    '/doctors/dr-saraswathi-m': '/doctors/dr.-saraswathi-m',
    '/doctors/Dt Neelima Sharma': '/doctors/dt-neelima-sharma',
    '/doctors/dr magesh b': '/doctors/dr-magesh-b',
    '/foundations.php': '/',
    '/career.php': '/',
    '/best-physiotherapy-rehabilitation-center-in-hsrlayout-bangalore': '/physiotherapy-in-hsr-layout-bangalore',
    '/best-hospital-in-electronic-city-bangalore/': '/best-hospital-in-electronic-city-bangalore',
    '/best-hospital-in-hosa-road-bangalore/': '/best-hospital-in-hosa-road-bangalore',
    '/best-hospital-in-hsr-bangalore/': '/best-hospital-in-hsr-bangalore',
    '/best-hospital-in-sarjapur-road-bangalore/': '/best-hospital-in-sarjapur-road-bangalore',
    '/best-plastic-surgeon-in-bangalore/': '/best-plastic-surgeon-in-bangalore',
}

# Files served straight from the website folder (the old nginx "location = /robots.txt" blocks)
STATIC_FILES = {
    "/robots.txt": "text/plain; charset=utf-8",
    "/sitemap.xml": "application/xml; charset=utf-8",
    "/llms.txt": "text/plain; charset=utf-8",
}

# .html files that must NOT be redirected (error pages, Google verification file)
HTML_KEEP = re.compile(r"^/(404|50x)\.html$|^/google[0-9a-f]+\.html$")


def _redirect(start_response, location):
    start_response(
        "301 Moved Permanently",
        [("Location", location), ("Content-Type", "text/plain"), ("Content-Length", "0")],
    )
    return [b""]


def _not_found(start_response):
    try:
        with open(os.path.join(BASE_DIR, "templates", "404.html"), "rb") as f:
            body = f.read()
    except OSError:
        body = b"<h1>404 Not Found</h1>"
    start_response(
        "404 Not Found",
        [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(body)))],
    )
    return [body]


def _full_path(environ):
    """The requested path + query string, safely encoded again for a Location header."""
    raw = environ.get("PATH_INFO", "/").encode("latin-1", "replace")
    path = quote(raw, safe="/:@!$&'()*+,;=-._~")
    query = environ.get("QUERY_STRING", "")
    return path + ("?" + query if query else "")


class SiteRules:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "/")
        query = environ.get("QUERY_STRING", "")
        host = environ.get("HTTP_HOST", "").split(":")[0].lower()

        # 1. bots
        if BOTS.search(environ.get("HTTP_USER_AGENT", "")):
            start_response("403 Forbidden", [("Content-Type", "text/plain"), ("Content-Length", "0")])
            return [b""]

        # 2. www -> non-www
        if host == "www." + DOMAIN:
            return _redirect(start_response, "https://" + DOMAIN + _full_path(environ))

        # 3. double slashes
        if "//" in path:
            clean = re.sub(r"/{2,}", "/", path)
            return _redirect(start_response, clean + ("?" + query if query else ""))

        # 4. old Google search URL
        if path == "/search" and query in ("q=%7Bsearch_term_string%7D", "q={search_term_string}"):
            return _redirect(start_response, "/")

        # 5. page-specific redirects (query string dropped, like nginx)
        target = REDIRECTS.get(path)
        if target is not None:
            return _redirect(start_response, target)

        # 6. robots.txt / sitemap.xml / llms.txt from the website folder
        if path in STATIC_FILES:
            try:
                with open(os.path.join(BASE_DIR, path.lstrip("/")), "rb") as f:
                    body = f.read()
                start_response(
                    "200 OK",
                    [("Content-Type", STATIC_FILES[path]), ("Content-Length", str(len(body)))],
                )
                return [body]
            except OSError:
                pass  # file not in the folder: let the app answer

        # 7. any other /page.html -> /page
        if path.endswith(".html") and not HTML_KEEP.match(path):
            return _redirect(start_response, path[:-5] or "/")

        # 8. any other .php -> 404
        if path.endswith(".php"):
            return _not_found(start_response)

        # everything else: your normal website app
        return self.app(environ, start_response)

