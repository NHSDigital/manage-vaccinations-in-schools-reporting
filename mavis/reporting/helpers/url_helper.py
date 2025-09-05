from urllib.parse import parse_qs, parse_qsl, urlencode, urljoin, urlparse, urlunparse


def url_without_param(url: str, param: str) -> str:
    parsed_url = urlparse(url)
    query_params_as_dict = parse_qs(parsed_url.query)
    if param in query_params_as_dict:
        query_param_pairs = parse_qsl(parsed_url.query)
        query_pairs_without_param = [
            (p, v) for (p, v) in query_param_pairs if p != param
        ]

        parsed_url = parsed_url._replace(query=urlencode(query_pairs_without_param))
        return urlunparse(parsed_url)
    else:
        return url


def externalise_current_url(current_app, request) -> str:
    return urljoin(
        current_app.config["ROOT_URL"] or request.host_url, request.full_path
    )
