import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin
from parametro.services import get_parametro_cliente, get_sufixo_api_jira

class JiraAPIError(Exception):
    pass

class JiraClient:
    def __init__(self, base_url: str, email: str, api_token: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/") + "/"
        self.auth = HTTPBasicAuth(email, api_token)
        self.timeout = timeout
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcwNjQxMjQ2LCJpYXQiOjE3NzA2Mzk0NDYsImp0aSI6ImFmMmFlYjBjMzc3MTQ1NDhiNDJkMjYxMGFmMDU3YjkzIiwidXNlcl9pZCI6IjEifQ.lP5rzZ-7vDw9BXSOW25MWfolQilZ5bU1BYsYW6gkzo8"
        print("Access token: " + str(access_token))
        self.headers = {
            "Authorization": f"Bearer {access_token}",  # ✅ OAuth2
            "Accept": "application/json",
            "Content-Type": "application/json",
        }


    def _get(self, path: str, params: dict | None = None):
        url = urljoin(self.base_url, path.lstrip("/"))
        print(f"GET {url} params={params}")

        r = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )

        print(f"Response: {r.status_code} {r.text[:300]}")
        if r.status_code >= 400:
            raise JiraAPIError(f"Jira GET {url} -> {r.status_code}: {r.text[:500]}")
        return r.json()

    def iter_projects(self, start_at=0, max_results=50):
        while True:
            sufixo_url = get_sufixo_api_jira(1, "PROJ_CLIENTES", default="/rest/api/3")
            data = self._get(sufixo_url, {
                "startAt": start_at,
                "maxResults": max_results,
            })
            values = data.get("values") or []
            for p in values:
                yield p

            start_at += len(values)
            total = data.get("total") or 0
            if not values or start_at >= total:
                break

    def iter_issues(self, jql: str, start_at=0, max_results=50):
        while True:
            data = self._get("/rest/api/3/search", {
                "jql": jql,
                "startAt": start_at,
                "maxResults": max_results,
            })
            issues = data.get("issues") or []
            for it in issues:
                yield it

            start_at += len(issues)
            total = data.get("total") or 0
            if not issues or start_at >= total:
                break
