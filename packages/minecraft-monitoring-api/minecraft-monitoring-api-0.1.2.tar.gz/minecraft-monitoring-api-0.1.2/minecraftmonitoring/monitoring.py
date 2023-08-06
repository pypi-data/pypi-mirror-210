from .models import AddServerResponse

from .version import version_list

import requests

import re

import logging

_logger = logging.getLogger('minecraftmonitoring')

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'


def retryable_request(method, *args, **kwargs) -> requests.Response:
    attempts = kwargs.get('attempts', 5)
    url = args[0]
    for retry in range(attempts):
        try:
            response = method(*args, **kwargs)
            if response.status_code == 200:
                return response
            _logger.warn(
                f'Server returned a status code of {response.status_code} while downloading {url}. Retrying ({retry + 1}/{attempts})...'
            )
        except requests.exceptions.ConnectionError:
            _logger.warn(
                f'ConnectionError while downloading {url}. Retrying ({retry + 1}/{attempts})...'
            )
            continue

    raise RuntimeError(f'Failed to download {url} too many times.')


class Client:
    url = 'https://monitoringminecraft.ru'

    def __init__(
        self,
        authautologin: str,
        user_agent: str = user_agent
    ):
        self.__user_agent = user_agent

        self.session = requests.Session()

        self.session.cookies.set(
            'authautologin',
            authautologin,
            domain='monitoringminecraft.ru'
        )
        self.session.headers.update({
            'user-agent': self.__user_agent
        })

        self.__auth()

    def __auth(self):
        response = retryable_request(
            self.session.get,
            self.url + '/acc'
        )

        if '<title>Авторизация</title>' in response.text:
            raise RuntimeError('Invalid token')

        return response

    def add_server(
        self,
        address: str,
        port: str = 25565,
        params: list[str] = [],
        forced_title: str = '',
        lure: str = '',
        site_url: str = '',
        description: str = '',
        public_contacts: str = '',
        client_url: str = '',
        map_url: str = '',
        show_plugins: bool = True,
        server_version: str = '',
        banner_path: str = ''
    ) -> AddServerResponse:
        response = retryable_request(
            self.session.post,
            self.url + '/add-server',
            headers={
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data=f'address={address}:{port}&right=1'
        )

        server = AddServerResponse.parse_obj(response.json())

        self.edit_server(
            id=server.id,
            params=params,
            forced_title=forced_title,
            lure=lure,
            forced_address=address,
            forced_port=port,
            site_url=site_url,
            description=description,
            public_contacts=public_contacts,
            client_url=client_url,
            map_url=map_url,
            show_plugins=show_plugins,
            server_version=server_version,
            banner_path=banner_path
        )

        return server

    def remove_server(
        self,
        id: str
    ):
        response = retryable_request(
            self.session.post,
            self.url + '/acc/remove-server-' + str(id)
        )

        return response

    def servers(self):
        response = retryable_request(
            self.session.get,
            self.url + '/acc/servers'
        )

        pattern = r'<a href="/server/(\d+)">(.*?)</a>'
        matches = re.findall(pattern, response.text)

        return {title: id for id, title in matches}

    def edit_server(
        self,
        id: str,
        params: list[str] = [],
        forced_title: str = '',
        lure: str = '',
        forced_address: str = '',
        forced_port: str = 25565,
        site_url: str = '',
        description: str = '',
        public_contacts: str = '',
        client_url: str = '',
        map_url: str = '',
        show_plugins: bool = True,
        server_version: str = '',
        address: str = '',
        banner_path: str = ''
    ):
        files = []

        if banner_path:
            files.append(('banner', (
                'file',
                open(banner_path, 'rb'),
                'application/octet-stream'
            )))

        for param in params:
            files.append(('tags[]', (None, param)))

        response = retryable_request(
            self.session.post,
            self.url + '/acc/edit-server-' + str(id),
            data={
                'forced_title': forced_title,
                'lure': lure,
                'forced_address': str(forced_address + ':' + str(forced_port)) if forced_address else '',
                'site_url': site_url,
                'description': description,
                'public_contacts': public_contacts,
                'client_url': client_url,
                'map_url': map_url,
                'show_plugins': 'on' if show_plugins else 'off',
                'forced_version_tag': version_list[server_version] if server_version else '',
                'address': address,
                'submit': 'Обновить'
            },
            files=files
        )

        return response
