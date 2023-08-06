import http.client


def iap_http_request(method: str, api_url: str, request_url: str, body: str, headers: dict[str, str]):
    conn = http.client.HTTPSConnection(api_url)
    conn.request(method=method, url=request_url,
                 body=body, headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return data.decode("utf-8")
