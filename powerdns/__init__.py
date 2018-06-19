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

"""
powerdns - PowerDNS API client and interface
"""

import logging
from logging.handlers import SysLogHandler
from .client import PDNSApiClient
from .interface import PDNSEndpoint, RRSet


#: Current version of the package as :class:`str`.
__version__ = "0.2.1"

LOG_LEVELS = [
    logging.ERROR,
    logging.WARN,
    logging.INFO,
    logging.DEBUG
]


def basic_logger(name=None, clevel=2, slevel=1):
    """Configure a basic logger

    :param str name: Logger name
    :param int clevel: Console log level
    :param int slevel: Syslog log level
    :return: Logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVELS[clevel])
    fmt_syslog = logging.Formatter('%(name)s %(levelname)s: %(message)s')
    fmt_stream = logging.Formatter('%(name)s %(levelname)s: %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt_stream)
    logger.addHandler(stream_handler)
    syslog_handler = SysLogHandler(address='/dev/log')
    syslog_handler.setFormatter(fmt_syslog)
    syslog_handler.setLevel(LOG_LEVELS[slevel])
    logger.addHandler(syslog_handler)
    return logger
