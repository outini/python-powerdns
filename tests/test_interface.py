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

from datetime import date
from unittest import TestCase

from powerdns.client import PDNSApiClient
from powerdns.interface import PDNSEndpoint, PDNSServer, PDNSZone
from powerdns.interface import RRSet, Comment
from powerdns.exceptions import PDNSError

from . import API_CLIENT


API = PDNSEndpoint(API_CLIENT)
SERVER = API.servers[0]
ZONE = API.servers[0].get_zone("test.outini.net.")


class TestEndpoint(TestCase):

    def test_endpoint_attributes(self):
        self.assertIsInstance(API.api_client, PDNSApiClient)
        self.assertTrue(hasattr(API, "servers"))

    def test_endpoint_repr_and_str(self):
        api_client_repr = repr(API.api_client)
        api_repr = "PDNSEndpoint(%s)" % (api_client_repr,)
        self.assertEqual(repr(API), api_repr)
        self.assertEqual(str(API), str(API.api_client))

    def test_endpoint_servers_list(self):
        self.assertIsInstance(API.servers, list)
        self.assertIsInstance(API.servers[0], PDNSServer)


class TestServers(TestCase):

    def test_server_object(self):
        # server_repr = "PDNSServer(%s, %s)"
        # self.assertEqual(repr(SERVER), server_repr)
        self.assertEqual(str(SERVER), "localhost")
        self.assertEqual(SERVER.sid, "localhost")
        self.assertTrue(isinstance(SERVER.version, str))

    def test_server_config(self):
        self.assertIsInstance(SERVER.config, list)
        self.assertIsInstance(SERVER.config[0], dict)

    def test_server_zones(self):
        self.assertIsInstance(SERVER.zones, list)
        self.assertIsInstance(SERVER.zones[0], PDNSZone)

    def test_server_create_zone(self):
        zone_name = "test.outini.net."
        serial = date.today().strftime("%Y%m%d00")
        timers = "28800 7200 604800 86400"
        soa = "ns01.test.outini.net. admin.outini.net. %s %s" % (serial, timers)
        comments = [Comment("test comment", "admin")]
        soa_r = RRSet(name=zone_name, rtype="SOA", ttl=86400,
                      records=[(soa, False)], comments=comments)
        zone_data = dict(name=zone_name,
                         kind="Master",
                         rrsets=[soa_r],
                         nameservers=["ns01.test.outini.net.",
                                      "ns02.test.outini.net."])

        zone = SERVER.create_zone(**zone_data)
        self.assertIsInstance(zone, PDNSZone)
        with self.assertRaises(PDNSError):
            SERVER.create_zone(**zone_data)

    def test_server_get_zone(self):
        self.assertIs(SERVER.get_zone("nonexistent"), None)
        self.assertIsInstance(SERVER.get_zone("test.outini.net."), PDNSZone)

    def test_server_suggest_zone(self):
        zone = SERVER.suggest_zone("a.b.c.test.outini.net.")
        self.assertIsInstance(zone, PDNSZone)
        self.assertEqual(zone.name, "test.outini.net.")


# class TestZones(TestCase):
#
#     def test_zone_object(self):
#         # zone_repr = "PDNSZone(%s, %s)"
#         # self.assertEqual(repr(ZONE), zone_repr)
#         self.assertEqual(str(ZONE), "test.outini.net.")
#         print(dir(ZONE))


class TestRRSetRecords(TestCase):

    def test_dict_correct(self):
        rrset = RRSet("test", "TXT", [{"content": "foo"},
                                      {"content": "bar", "disabled": False},
                                      {"content": "baz", "disabled": True}])

        self.assertEqual(rrset["records"][0],
                         {"content": "foo", "disabled": False})
        self.assertEqual(rrset["records"][1],
                         {"content": "bar", "disabled": False})
        self.assertEqual(rrset["records"][2],
                         {"content": "baz", "disabled": True})

    def test_dict_additional_key(self):
        with self.assertRaises(ValueError):
            RRSet("test", "TXT", [{"content": "baz",
                                   "disabled": False,
                                   "foo": "bar"}])

    def test_dict_missing_key(self):
        with self.assertRaises(ValueError):
            RRSet("test", "TXT", [{"content": "baz",
                                   "disabled": False,
                                   "foo": "bar"}])
