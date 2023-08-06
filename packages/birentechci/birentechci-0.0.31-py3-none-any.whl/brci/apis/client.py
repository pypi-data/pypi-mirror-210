from requests import Request, Session


class Client(object):
    def __init__(self, host=None, port=None) -> None:
        self.base_url = None
        self.session = Session()
        if host and port:
            self.base_url = f"http://{host}:{port}"

    def _send(
        self,
        method=None,
        url=None,
        headers=None,
        files=None,
        data=None,
        params=None,
        auth=None,
        cookies=None,
        hooks=None,
        json=None,
    ):
        if self.base_url:
            url = f"{self.base_url}{url}"
        preq = Request(
            method=method,
            url=url,
            headers=headers,
            files=files,
            data=data,
            params=params,
            auth=auth,
            cookies=cookies,
            hooks=hooks,
            json=json,
        ).prepare()
        try:
            resp = self.session.send(preq)
            if resp.status_code == 200:
                return resp
        except Exception as e:
            print(f"网络异常\n  request:    {preq.__dict__}\n  error:   {e}")
            exit(1)
        else:
            print(
                f"请求失败\n  request:    {preq.__dict__}\n  response:    {resp.__dict__}"
            )
            exit(1)

    def get(self, url, **kwargs):
        return self._send("GET", url=url, **kwargs)

    def post(self, url, **kwargs):
        return self._send("POST", url=url, **kwargs)

    def patch(self, url, **kwargs):
        return self._send("PATCH", url=url, **kwargs)

    def put(self, url, **kwargs):
        return self._send("PUT", url=url, **kwargs)
