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

from unittest import TestCase

from . import API_CLIENT, PDNS_API, PDNS_KEY


class TestClient(TestCase):

    def test_client_repr_and_str(self):
        repr_str = "PDNSApiClient('%s', '%s', verify=False, timeout=None)" % (
            PDNS_API, PDNS_KEY
        )
        self.assertEqual(repr(API_CLIENT), repr_str)
        self.assertEqual(str(API_CLIENT), PDNS_API)

    def test_client_full_uri(self):
        self.assertIsInstance(API_CLIENT.get(PDNS_API + "/servers"), list)
