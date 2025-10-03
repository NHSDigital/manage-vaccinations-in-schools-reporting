from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse


def url_without_param(url: str, param: str) -> str:
    parsed_url = urlparse(url)
    query_param_pairs = parse_qsl(parsed_url.query, keep_blank_values=True)
    filtered_pairs = [(p, v) for (p, v) in query_param_pairs if p != param]

    if len(filtered_pairs) == len(query_param_pairs):
        return url

    new_query = urlencode(filtered_pairs)
    return urlunparse(parsed_url._replace(query=new_query))


def externalise_current_url(current_app, request) -> str:
    return urljoin(
        current_app.config["ROOT_URL"] or request.host_url, request.full_path
    )
