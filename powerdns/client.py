# -*- coding: utf-8 -*-
#
#  PowerDNS web api python client and interface (python-powerdns)
#
#  Copyright (C) 2018 Denis Pompilio (jawa) <dpompilio@vente-privee.com>
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

import json
import requests
import logging
from functools import partial
from .exceptions import PDNSError


logger = logging.getLogger(__name__)


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
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.verify = verify
        self.timeout = timeout

        if not verify:
            logger.debug("removing insecure https connection warnings")
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
        if self.api_key:
            self.request_headers['X-API-Key'] = self.api_key

        logger.debug("request: original path is %s" % path)
        if not path.startswith('http://') and not path.startswith('https://'):
            if path.startswith('/'):
                path = path.lstrip('/')
            url = "%s/%s" % (self.api_endpoint, path)
        else:
            url = path

        if data is None:
            data = {}
        data = json.dumps(data)

        logger.info("request: %s %s" % (method, url))
        logger.debug("headers: %s" % self.request_headers)
        logger.debug("data: %s" % data)
        response = requests.request(method, url,
                                    data=data,
                                    headers=self.request_headers,
                                    timeout=self.timeout,
                                    verify=self.verify,
                                    **kwargs)

        logger.info("request response code: %d" % response.status_code)
        logger.debug("response: %s" % response.text)

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

        logger.error("raising error code %d" % response.status_code)
        logger.debug("error response: %s" % error_message)
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
