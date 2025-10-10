import requests
from flask import Response, current_app, request


def proxy_to_mavis(path):
    backend_url = current_app.config["MAVIS_BACKEND_URL"]
    proxy_url = request.host_url.rstrip("/")

    url = f"{backend_url}/{path}"
    if request.query_string:
        url += f"?{request.query_string.decode()}"

    headers = {k: v for k, v in request.headers if k.lower() != "host"}

    # Rewrite Origin and Referer headers for Rails CSRF validation
    if "Origin" in headers:
        headers["Origin"] = backend_url
    if "Referer" in headers:
        headers["Referer"] = headers["Referer"].replace(proxy_url, backend_url)

    resp = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        stream=True,
    )

    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    response_headers = [
        (k, v)
        for k, v in resp.raw.headers.items()
        if k.lower() not in excluded_headers
    ]

    return Response(resp.content, resp.status_code, response_headers)
