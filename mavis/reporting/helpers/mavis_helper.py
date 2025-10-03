import urllib.parse
from http import HTTPStatus

import requests
from flask import redirect
from werkzeug.exceptions import Unauthorized

from mavis.reporting.helpers import auth_helper


class MavisApiError(Exception):
    def __init__(self, message, status_code=None, response_body=None):
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(self.message)


def mavis_url(current_app, path, params={}):
    url = urllib.parse.urljoin(current_app.config["MAVIS_ROOT_URL"], path)
    if params != {}:
        parsed_url = urllib.parse.urlsplit(url)

        encoded_params = []
        for key, value in params.items():
            if isinstance(value, list):
                for item in value:
                    encoded_params.append((f"{key}[]", item))
            else:
                encoded_params.append((key, value))

        query_string = urllib.parse.urlencode(encoded_params)
        url_with_params = parsed_url._replace(query=query_string)
        url = urllib.parse.urlunsplit(url_with_params)

    return url


def parse_json_response(response, context="API response"):
    if not response.content:
        raise MavisApiError(
            f"{context}: Empty response body",
            status_code=response.status_code,
            response_body="",
        )

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError as e:
        raise MavisApiError(
            f"{context}: Invalid JSON - {str(e)}",
            status_code=response.status_code,
            response_body=response.text[:500],
        )


def validate_http_response(response, session=None, context="API response"):
    if response.status_code in [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN]:
        if session:
            session.clear()
        raise Unauthorized()

    if not response.ok:
        raise MavisApiError(
            f"{context}: {response.status_code}",
            status_code=response.status_code,
            response_body=response.text[:500],
        )

    return response


def verify_auth_code(code, current_app):
    url = mavis_url(current_app, "/api/reporting/authorize")
    body = {
        "client_id": current_app.config["CLIENT_ID"],
        "code": code,
        "grant_type": "authorization_code",
    }
    headers = {
        "Accept": "application/json; charset=utf-8",
        "Content-type": "application/json; charset=utf-8",
    }

    context = "Authorization response"

    r = post_request(url, body=body, headers=headers)
    validate_http_response(r, session=None, context=context)

    auth_code_response_data = parse_json_response(r, context)

    if "jwt" not in auth_code_response_data:
        raise MavisApiError(
            f"{context}: missing 'jwt' field",
            status_code=r.status_code,
            response_body=str(auth_code_response_data),
        )

    jwt_data = auth_helper.decode_jwt(auth_code_response_data["jwt"], current_app)
    user_nav = auth_code_response_data.get("user_nav", "")
    return {"jwt_data": jwt_data["data"], "user_nav": user_nav}


def api_call(current_app, session, path, params={}):
    url = mavis_url(current_app, path, params)
    headers = {
        "Authorization": "Bearer " + session["jwt"],
        "Accept": "application/json; charset=utf-8",
        "Content-type": "application/json; charset=utf-8",
    }
    response = get_request(url, headers=headers)
    validate_http_response(response, session=session)

    return response


def login_and_return_after(current_app, return_url):
    target_url = mavis_url(
        current_app,
        "/start?redirect_uri=" + urllib.parse.quote_plus(return_url),
    )
    current_app.logger.warning("REDIRECTING TO %s", target_url)
    return redirect(str(target_url))


def get_request(url, headers={}):
    return requests.get(url, headers=headers)


def post_request(url, body={}, headers={}):
    return requests.post(url, json=body, headers=headers)
