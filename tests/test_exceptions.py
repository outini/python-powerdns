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
from powerdns import exceptions


class TestExceptions(TestCase):

    def test_exception_pdns_error(self):
        exc = exceptions.PDNSError("/fake-url", 404, "Not found.")
        self.assertEqual(exc.url, "/fake-url")
        self.assertEqual(exc.status_code, 404)
        self.assertEqual(exc.message, "Not found.")
        self.assertEqual(repr(exc), 'PDNSError("/fake-url", 404, "Not found.")')
        self.assertEqual(str(exc), 'code=404 /fake-url: Not found.')

    def test_exception_pdns_canonical_error(self):
        self.assertTrue(issubclass(exceptions.PDNSCanonicalError, SyntaxError))
        exc = exceptions.PDNSCanonicalError("fake-name.tld")
        self.assertEqual(repr(exc), "PDNSCanonicalError('fake-name.tld')")
        self.assertEqual(str(exc), "fake-name.tld")
        self.assertEqual(exc.name, "fake-name.tld")
        self.assertEqual(exc.message, "'fake-name.tld' is not canonical")
