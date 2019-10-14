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
powerdns.exceptions - PowerDNS API interface exceptions
"""


class PDNSCanonicalError(SyntaxError):
    """PowerDNS Canonical Error
    """
    def __init__(self, name):
        """Initialization"""
        self.name = name
        self.message = "'%s' is not canonical" % name
        super(PDNSCanonicalError, self).__init__()


class PDNSError(Exception):
    """PowerDNS API Exception
    """
    def __str__(self):
        return "code=%d %s: %s" % (self.status_code, self.url, self.message)

    def __repr__(self):
        return "PDNSError(\"%s\", %d, \"%s\")" % (self.url,
                                                  self.status_code,
                                                  self.message)

    def __init__(self, url, status_code, message):
        """Initialization"""
        self.url = url
        self.status_code = status_code
        self.message = message
        super(PDNSError, self).__init__()
