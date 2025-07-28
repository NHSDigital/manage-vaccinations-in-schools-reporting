from http import HTTPStatus
import requests
import urllib.parse
import werkzeug

from flask import redirect

from mavis_reporting.helpers import auth_helper


def mavis_url(current_app, path, params={}):
    url = urllib.parse.urljoin(current_app.config["MAVIS_ROOT_URL"], path)
    if params != {}:
        parsed_url = urllib.parse.urlsplit(url)
        query_string = urllib.parse.urlencode(params)
        url_with_params = parsed_url._replace(query=query_string)
        url = urllib.parse.urlunsplit(url_with_params)

    return url


def verify_auth_code(code, current_app):
    url = mavis_url(current_app, "/tokens/authorize")
    body = {
        "client_id": current_app.config["CLIENT_ID"],
        "code": code,
        "grant_type": "authorization_code",
    }
    headers = {
        "Accept": "application/json; charset=utf-8",
        "Content-type": "application/json; charset=utf-8",
    }

    r = post_request(url, body=body, headers=headers)

    auth_code_response_data = r.json()
    jwt_data = auth_helper.decode_jwt(auth_code_response_data["jwt"], current_app)
    return jwt_data["data"]


def api_call(current_app, session, path, params={}):
    url = mavis_url(current_app, path, params)
    headers = {
        "Authorization": "Bearer " + session["jwt"],
        "Accept": "application/json; charset=utf-8",
        "Content-type": "application/json; charset=utf-8",
    }
    response = get_request(url, headers=headers)
    if response.status_code in [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN]:
        session.clear()
        raise (werkzeug.exceptions.Unauthorized)

    return response


def login_and_return_after(current_app, return_url):
    target_url = mavis_url(
        current_app,
        "/start?redirect_uri=" + urllib.parse.quote_plus(return_url),
    )
    current_app.logger.warning("REDIRECTING TO %s", target_url)
    return redirect(target_url)


def get_request(url, headers={}):
    return requests.get(url, headers=headers)


def post_request(url, body={}, headers={}):
    return requests.post(url, json=body, headers=headers)
