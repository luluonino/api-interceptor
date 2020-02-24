from flask import request, Response
import requests


def proxy(origin):
    def _proxy(*args, **kwargs):
        r = requests.request(
            method=request.method,
            url=request.url.replace(request.host_url, origin + "/"),
            headers={key: value for (key, value) in request.headers if key != "Host"},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
        )

        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        ]
        headers = [
            (name, value)
            for (name, value) in r.raw.headers.items()
            if name.lower() not in excluded_headers
        ]

        return Response(
            r.iter_content(chunk_size=10 * 1024),
            r.status_code,
            headers,
            content_type=r.headers["Content-Type"]
        )

    return _proxy
