import re
from base64 import b64decode

from .. import http
from . import base

import logging  # isort:skip
_log = logging.getLogger(__name__)


class SrrdbApi(base.PredbApiBase):
    name = 'srrdb'
    label = 'srrDB'

    default_config = {}

    _url_base = b64decode('YXBpLnNycmRiLmNvbQ==').decode('ascii')
    _search_url = f'https://{_url_base}/v1/search'
    _details_url = f'https://{_url_base}/v1/details'

    _keyword_separators_regex = re.compile(r'[^a-zA-Z0-9]')

    # We can skip over 50_000 results and get 1000 results per request
    # https://www.srrdb.com/help
    _page_size = 1000
    _max_skip = 50_000

    async def _search(self, keywords, group):
        combined_results = []
        for skip in range(0, self._max_skip + 1, self._page_size):
            keywords_path = self._get_keywords_path(keywords, group, skip)
            results = await self._request_search_page(keywords_path)
            combined_results.extend(results)
            if len(results) < self._page_size:
                # We didn't get a full page, so we assume this is the last page
                break

        return combined_results

    async def _request_search_page(self, keywords_path):
        search_url = f'{self._search_url}/{keywords_path}'
        _log.debug('Search URL: %s', search_url)
        response = (await http.get(search_url, cache=True)).json()
        results = response.get('results', [])
        return tuple(r['release'] for r in results)

    def _get_keywords_path(self, keywords, group, skip):
        def sanitize_keyword(kw):
            return kw.lower()

        keywords_sanitized = [
            sanitize_keyword(kw)
            for keyword in keywords
            for kw in self._keyword_separators_regex.split(keyword)
        ]
        if group:
            keywords_sanitized.append(f'group:{sanitize_keyword(group)}')

        # Get most recent results
        keywords_sanitized.append('order:date-desc')

        # Skip over `skip` results
        assert (isinstance(skip, int) and 0 <= skip <= self._max_skip), skip
        keywords_sanitized.append(f'skipr:{skip}.{self._page_size}')

        return '/'.join(keywords_sanitized)

    async def _release_files(self, release_name):
        """
        Map file names to dictionaries with the keys ``release_name``,
        ``file_name``, ``size`` and ``crc``

        If no files for `release_name` are found, return an empty :class:`dict`.

        :param str release_name: Exact name of the release

        :raise RequestError: if request fails
        """
        details_url = f'{self._details_url}/{release_name}'
        _log.debug('Details URL: %s', details_url)
        response = await http.get(details_url, cache=True)
        # Response may be empty string
        if response:
            # Response may be empty list
            info = response.json()
            if info:
                # If info is not an empty list, it should be a dictionary
                files = info['archived-files']
                release_name = info['name']
                return {
                    f['name']: {
                        'release_name': release_name,
                        'file_name': f['name'],
                        'size': f['size'],
                        'crc': f['crc'],
                    }
                    for f in sorted(files, key=lambda f: f['name'].casefold())
                }

        return {}
