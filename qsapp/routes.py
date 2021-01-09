from flask import request, redirect, session, url_for, render_template
from flask import current_app as app
import requests
import os
import datetime
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
    last_in_db = Body.get_last_date()
    data = withings_daily_summary(str(last_in_db))

    # If Withings API returns data return success status
    if isinstance(data, list):
        last_in_API = data[-1]['date']
        last_in_API = datetime.datetime.strptime(last_in_API, "%Y-%m-%d")
        status = datetime.datetime.strftime(last_in_API, "%Y-%m-%d")
        icon = "green"
        # If outdated data, insert them in DB
        if last_in_API > last_in_db:
            Body.body_insert(str(last_in_db))

    # If Withings API token is invalid return Error message
    else:
        status = data
        icon = ""
    last_in_db = datetime.datetime.strftime(last_in_db, "%Y-%m-%d") # Format to date
    return render_template("index.html", status=status, icon=icon, last_in_db=last_in_db)


@app.route("/fitness")
def fitness():
    logger.debug("Start loading - Fitness page")
    return render_template("fitness.html")

@app.route("/heart")
def heart():
    logger.debug("Start loading - Heart page")
    return render_template("heart.html")

@app.route("/sleep")
def sleep():
    logger.debug("Start loading - Sleep page")
    return render_template("sleep.html")


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
