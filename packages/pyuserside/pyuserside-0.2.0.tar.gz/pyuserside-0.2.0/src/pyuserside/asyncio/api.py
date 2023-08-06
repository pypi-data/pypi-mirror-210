import json.decoder
import httpx
from ..exceptions import UsersideException
from ..parser import parse_response


class UsersideAPI:
    def __init__(self, url: str, key: str, session: httpx.AsyncClient = None):
        self.url = url
        self.key = key
        self.session = session or httpx.AsyncClient()

    def __getattr__(self, category):
        return UsersideCategory(self, category)


class UsersideCategory:
    def __init__(self, api: UsersideAPI, category: str):
        self.api = api
        self.category = category

    async def _request(self, action, **kwargs):
        params = {'key': self.api.key,
                  'cat': self.category,
                  'action': action}
        params = params | kwargs
        response = await self.api.session.get(self.api.url, params=params)
        try:
            content = response.json()
        except json.decoder.JSONDecodeError:
            raise UsersideException('Not a valid JSON response')
        if not response.status_code == 200:
            raise UsersideException(
                content.get('error', 'No error description provided'))
        return parse_response(content)

    def __getattr__(self, action):
        async def _action(**kwargs):
            return await self._request(action, **kwargs)
        return _action
