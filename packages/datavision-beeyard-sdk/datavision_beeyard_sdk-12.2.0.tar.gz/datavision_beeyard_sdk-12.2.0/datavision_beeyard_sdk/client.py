import httpx
import base64
import datetime


class AuthenticatedClient:
    def __init__(
        self,
        base_url,
        username="",
        password="",
        grant_type="password",
        max_waiting_time_ms=0,
        client_id="byard",
        client_secret="",
        login_url=None,
        use_token=False,
        token=None,
    ):
        self.base_url = base_url[:-1] if base_url.endswith("/") else base_url
        self.username = username
        self.password = password
        self.grant_type = grant_type
        self.delay = max_waiting_time_ms
        self.endpoint_auth: str = "/oauth/token/"
        self.client_id = client_id
        self.client_secret = client_secret
        self.login_url = login_url
        if use_token:
            if isinstance(token, dict):
                self.token_headers = token
            elif "Authorization" in token:
                self.token_headers = {"Authorization": f"Bearer {token.split(' ')[2]}"}
            else:
                self.token_headers = {"Authorization": f"Bearer {token}"}
        else:
            self.authenticate()

    def authenticate(self):
        if self.grant_type == "password":
            data = {
                "grant_type": self.grant_type,
                "username": self.username,
                "password": self.password,
            }
            credentials = self.client_id + ":" + self.client_secret
            message_bytes = credentials.encode("ascii")
            base64_bytes = base64.b64encode(message_bytes)
            base64_credentials = base64_bytes.decode("ascii")
            header = {"Authorization": "Basic " + base64_credentials}
        elif self.grant_type == "client_credentials":
            data = {
                "grant_type": self.grant_type,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            header = {}
        else:
            raise Exception(f"Grant type '{self.grant_type}' not recognized")
        if self.login_url is None:
            response = httpx.post(
                f"{self.base_url}{self.endpoint_auth}".replace("hive", "id"),
                data=data,
                headers=header,
            )
        else:
            response = httpx.post(
                f"{self.login_url}{self.endpoint_auth}",
                data=data,
                headers=header,
            )
        if response.status_code not in range(200, 300):
            raise Exception("Bad authenticate response")
        auth = "Bearer " + response.json()["access_token"]
        self.token_headers = {"Authorization": auth}
        return True

    def check_response(self, response):
        if response.status_code in range(200, 300):
            return True
        if response.status_code in range(400, 500):
            raise Exception("Bad response: client exception -> %s" % response.text)
        if response.status_code in range(500, 600):
            raise Exception("Bad response: server exception -> %s" % response.text)

    def get(self, *args, **kwargs):
        try:
            response = httpx.get(*args, **kwargs, timeout=None)
        except httpx.ConnectError:
            t1 = datetime.datetime.now()
            while ((datetime.datetime.now() - t1).total_seconds() * 1000) < self.delay:
                try:
                    httpx.get(*args, **kwargs, timeout=None)
                    break
                except httpx.ConnectError:
                    continue
            response = httpx.get(*args, **kwargs, timeout=None)
        if response.status_code == 401:
            self.authenticate()
            kwargs["headers"]["Authorization"] = self.token_headers["Authorization"]
            try:
                response = httpx.get(*args, **kwargs, timeout=None)
            except httpx.ConnectError:
                t1 = datetime.datetime.now()
                while (
                    (datetime.datetime.now() - t1).total_seconds() * 1000
                ) < self.delay:
                    try:
                        httpx.get(*args, **kwargs, timeout=None)
                        break
                    except httpx.ConnectError:
                        continue
                response = httpx.get(*args, **kwargs, timeout=None)
        self.check_response(response)
        return response

    def post(self, *args, **kwargs):
        try:
            response = httpx.post(*args, **kwargs, timeout=None)
        except httpx.ConnectError:
            t1 = datetime.datetime.now()
            while ((datetime.datetime.now() - t1).total_seconds() * 1000) < self.delay:
                try:
                    httpx.post(*args, **kwargs, timeout=None)
                    break
                except httpx.ConnectError:
                    continue
            response = httpx.post(*args, **kwargs, timeout=None)
        if response.status_code == 401:
            self.authenticate()
            kwargs["headers"]["Authorization"] = self.token_headers["Authorization"]
            try:
                response = httpx.post(*args, **kwargs, timeout=None)
            except httpx.ConnectError:
                t1 = datetime.datetime.now()
                while (
                    (datetime.datetime.now() - t1).total_seconds() * 1000
                ) < self.delay:
                    try:
                        httpx.post(*args, **kwargs, timeout=None)
                        break
                    except httpx.ConnectError:
                        continue
                response = httpx.post(*args, **kwargs, timeout=None)
        self.check_response(response)
        return response

    def patch(self, *args, **kwargs):
        try:
            response = httpx.patch(*args, **kwargs, timeout=None)
        except httpx.ConnectError:
            t1 = datetime.datetime.now()
            while ((datetime.datetime.now() - t1).total_seconds() * 1000) < self.delay:
                try:
                    httpx.patch(*args, **kwargs, timeout=None)
                    break
                except httpx.ConnectError:
                    continue
            response = httpx.patch(*args, **kwargs, timeout=None)
        if response.status_code == 401:
            self.authenticate()
            kwargs["headers"]["Authorization"] = self.token_headers["Authorization"]
            try:
                response = httpx.patch(*args, **kwargs, timeout=None)
            except httpx.ConnectError:
                t1 = datetime.datetime.now()
                while (
                    (datetime.datetime.now() - t1).total_seconds() * 1000
                ) < self.delay:
                    try:
                        httpx.patch(*args, **kwargs, timeout=None)
                        break
                    except httpx.ConnectError:
                        continue
                response = httpx.patch(*args, **kwargs, timeout=None)
        self.check_response(response)
        return response

    def delete(self, *args, **kwargs):
        try:
            response = httpx.delete(*args, **kwargs, timeout=None)
        except httpx.ConnectError:
            t1 = datetime.datetime.now()
            while ((datetime.datetime.now() - t1).total_seconds() * 1000) < self.delay:
                try:
                    httpx.delete(*args, **kwargs, timeout=None)
                    break
                except httpx.ConnectError:
                    continue
            response = httpx.delete(*args, **kwargs, timeout=None)
        if response.status_code == 401:
            self.authenticate()
            kwargs["headers"]["Authorization"] = self.token_headers["Authorization"]
            try:
                response = httpx.delete(*args, **kwargs, timeout=None)
            except httpx.ConnectError:
                t1 = datetime.datetime.now()
                while (
                    (datetime.datetime.now() - t1).total_seconds() * 1000
                ) < self.delay:
                    try:
                        httpx.delete(*args, **kwargs, timeout=None)
                        break
                    except httpx.ConnectError:
                        continue
                response = httpx.delete(*args, **kwargs, timeout=None)
        self.check_response(response)
        return response

    def put(self, *args, **kwargs):
        try:
            response = httpx.put(*args, **kwargs, timeout=None)
        except httpx.ConnectError:
            t1 = datetime.datetime.now()
            while ((datetime.datetime.now() - t1).total_seconds() * 1000) < self.delay:
                try:
                    httpx.put(*args, **kwargs, timeout=None)
                    break
                except httpx.ConnectError:
                    continue
            response = httpx.put(*args, **kwargs, timeout=None)
        if response.status_code == 401:
            self.authenticate()
            kwargs["headers"]["Authorization"] = self.token_headers["Authorization"]
            try:
                response = httpx.put(*args, **kwargs, timeout=None)
            except httpx.ConnectError:
                t1 = datetime.datetime.now()
                while (
                    (datetime.datetime.now() - t1).total_seconds() * 1000
                ) < self.delay:
                    try:
                        httpx.put(*args, **kwargs, timeout=None)
                        break
                    except httpx.ConnectError:
                        continue
                response = httpx.put(*args, **kwargs, timeout=None)
        self.check_response(response)
        return response
