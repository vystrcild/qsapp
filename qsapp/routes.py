from flask import request, redirect, session, url_for, render_template
from flask import current_app as app
import requests
import os
from requests_oauthlib import OAuth2Session
import logging.config

from qsapp.models import Body, withings_daily_summary

logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger("debugLogger")

logger.debug("Module routes.py loaded")

CLIENT_ID_OURA = app.config["CLIENT_ID_OURA"]
CLIENT_SECRET_OURA = app.config["CLIENT_SECRET_OURA"]
AUTH_URL_OURA = app.config["AUTH_URL_OURA"]
TOKEN_URL_OURA = app.config["TOKEN_URL_OURA"]

CLIENT_ID_WITHINGS = app.config["CLIENT_ID_WITHINGS"]
CLIENT_SECRET_WITHINGS = app.config["CLIENT_SECRET_WITHINGS"]
AUTH_URL_WITHINGS = app.config["AUTH_URL_WITHINGS"]
CALLBACK_WITHINGS = app.config["CALLBACK_WITHINGS"]
WBS_API_URL = app.config["WBS_API_URL"]


@app.route("/", methods=['GET', 'POST'])
def index():
    # Check what is the last row in DB and ask Withings API for call
    logger.debug("Start loading - Index page")
    last_in_db = Body.load_df().date.max()
    data = withings_daily_summary(str(last_in_db))
    # If Withings API returns data return success status and automaticaly start uploading newest data to DB
    # TODO - Bad design, insert should be only when data > last_in_db, else pass
    if isinstance(data, list):
        last_in_API = data[-1]['date']
        status = f"Last record in API: {last_in_API}"
        icon = "green"
        Body.body_insert(str(last_in_db))
    # If Withing API token is invalid return Error message
    else:
        status = data
        icon = ""
    return render_template("index.html", status=status, icon=icon, last_in_db=last_in_db)


@app.route("/body")
def body():
    logger.debug("Start loading - Body page")
    return render_template("body.html")


@app.route("/test")
def test():
    logger.debug("Start loading - Test page")
    return render_template("test.html")


@app.route('/oura_login')
def oura_login():
    """Redirect to the OAuth provider login page.
    """
    oura_session = OAuth2Session(CLIENT_ID_OURA)
    # URL for Oura's authorization page.
    authorization_url, state = oura_session.authorization_url(AUTH_URL_OURA)
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route("/withings_login")
def withings_login():
    """Redirect to the OAuth provider login page.
    """
    withings_session = OAuth2Session(CLIENT_ID_WITHINGS)
    authorization_url, state = withings_session.authorization_url(AUTH_URL_WITHINGS)
    session["oauth_state"] = state
    scope = ['user.metrics', 'user.info', 'user.activity']

    payload = {'response_type': 'code',
               'client_id': CLIENT_ID_WITHINGS,
               'state': session["oauth_state"],
               'scope': ",".join(scope),
               'redirect_uri': CALLBACK_WITHINGS,
               }
    r_auth = requests.get(f'{AUTH_URL_WITHINGS}', params=payload)
    return redirect(r_auth.url)


@app.route('/callback')
def callback():
    """Retrieve acces_token from Oura response url. Redirect to profile page.
    """
    oura_session = OAuth2Session(CLIENT_ID_OURA, state=session['oauth_state'])
    session['oauth'] = oura_session.fetch_token(
        TOKEN_URL_OURA,
        client_secret=CLIENT_SECRET_OURA,
        authorization_response=request.url)

    token = session['oauth']['access_token']
    os.environ['TOKEN_OURA'] = token
    return redirect(url_for('.index'))


@app.route("/callback_withings")
def callback_withings():
    code = request.args.get('code')
    payload = {'action': 'requesttoken',
               'grant_type': 'authorization_code',
               'client_id': CLIENT_ID_WITHINGS,
               'client_secret': CLIENT_SECRET_WITHINGS,
               'code': code,
               'redirect_uri': CALLBACK_WITHINGS
               }

    token = requests.post(WBS_API_URL, payload).json()
    token = token["body"]["access_token"]
    os.environ['TOKEN_WITHINGS'] = token
    return redirect(url_for('.index'))
