# -*- coding: utf-8 -*-
#
#  PowerDNS web api python client and interface (python-powerdns)
#
#  Copyright (C) 2018 Denis Pompilio (jawa) <denis.pompilio@gmail.com>
#
#  This file is part of python-powerdns
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the MIT License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  MIT License for more details.
#
#  You should have received a copy of the MIT License along with this
#  program; if not, see <https://opensource.org/licenses/MIT>.

"""
powerdns.client - PowerDNS API client
"""

import json
import logging
from functools import partial
import requests
from .exceptions import PDNSError


LOG = logging.getLogger(__name__)


class PDNSApiClient(object):
    """Powerdns API client

    It implements common HTTP methods GET, POST, PUT, PATCH and DELETE

    This client is using :mod:`requests` package. Please see
    http://docs.python-requests.org/ for more information.

    :param str api_endpoint: Powerdns API endpoint
    :param str api_key: API key
    :param bool verify: Control SSL certificate validation
    :param int timeout: Request timeout in seconds

    .. method:: get(self, path, data=None, **kwargs)

        Partial method invoking :meth:`~PDNSApiClient.request` with
        http method *GET*.

    .. method:: post(self, path, data=None, **kwargs)

        Partial method invoking :meth:`~PDNSApiClient.request` with
        http method *POST*.

    .. method:: put(self, path, data=None, **kwargs)

        Partial method invoking :meth:`~PDNSApiClient.request` with
        http method *PUT*.

    .. method:: patch(self, path, data=None, **kwargs)

        Partial method invoking :meth:`~PDNSApiClient.request` with
        http method *PATCH*.

    .. method:: delete(self, path, data=None, **kwargs)

        Partial method invoking :meth:`~PDNSApiClient.request` with
        http method *DELETE*.
    """
    def __init__(self, api_endpoint, api_key, verify=True, timeout=None):
        """Initialization"""
        self._api_endpoint = api_endpoint
        self._api_key = api_key
        self._verify = verify
        self._timeout = timeout

        if not verify:
            LOG.debug("removing insecure https connection warnings")
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.request_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Directly expose common HTTP methods
        self.get = partial(self.request, method='GET')
        self.post = partial(self.request, method='POST')
        self.put = partial(self.request, method='PUT')
        self.patch = partial(self.request, method='PATCH')
        self.delete = partial(self.request, method='DELETE')

    def __repr__(self):
        return "PDNSApiClient(%s, %s, verify=%s, timeout=%s)" % (
            repr(self._api_endpoint), repr(self._api_key),
            repr(self._verify), repr(self._timeout)
        )

    def __str__(self):
        return self._api_endpoint

    def request(self, path, method, data=None, **kwargs):
        """Handle requests to API

        :param str path: API endpoint's path to request
        :param str method: HTTP method to use
        :param dict data: Data to send (optional)
        :return: Parsed json response as :class:`dict`

        Additional named argument may be passed and are directly transmitted
        to :meth:`request` method of :class:`requests.Session` object.

        :raise PDNSError: If request's response is an error.
        """
        if self._api_key:
            self.request_headers['X-API-Key'] = self._api_key

        LOG.debug("request: original path is %s", path)
        if not path.startswith('http://') and not path.startswith('https://'):
            if path.startswith('/'):
                path = path.lstrip('/')
            url = "%s/%s" % (self._api_endpoint, path)
        else:
            url = path

        if data is None:
            data = {}
        data = json.dumps(data)

        LOG.info("request: %s %s", method, url)
        LOG.debug("headers: %s", self.request_headers)
        LOG.debug("data: %s", data)
        response = requests.request(method, url,
                                    data=data,
                                    headers=self.request_headers,
                                    timeout=self._timeout,
                                    verify=self._verify,
                                    **kwargs)

        LOG.info("request response code: %d", response.status_code)
        LOG.debug("response: %s", response.text)

        # Try to handle basic return
        if response.status_code in [200, 201]:
            return response.json()
        elif response.status_code == 204:
            return ""
        elif response.status_code == 404:
            error_message = 'Not found'
        else:
            try:
                error_message = self._get_error(response=response.json())
            except Exception:
                error_message = response.text

        LOG.error("raising error code %d", response.status_code)
        LOG.debug("error response: %s", error_message)
        raise PDNSError(url=response.url,
                        status_code=response.status_code,
                        message=error_message)

    @staticmethod
    def _get_error(response):
        """Get error message from API response

        :param dict response: API response
        :return: Error message as :func:`str`
        """
        if 'error' in response:
            err = response.get('error')
        elif 'errors' in response:
            err = response.get('errors')
        else:
            err = 'No error message found'
        return err
