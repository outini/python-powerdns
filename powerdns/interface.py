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
powerdns.interface - PowerDNS API interface
"""

import logging
import os
import json
from .exceptions import PDNSCanonicalError


LOG = logging.getLogger(__name__)


class PDNSEndpointBase(object):
    """Powerdns API Endpoint Base

    :param PDNSApiClient api_client: Cachet API client instance
    """
    def __init__(self, api_client):
        """Initialization method"""
        self.api_client = api_client
        self._get = api_client.get
        self._post = api_client.post
        self._patch = api_client.patch
        self._put = api_client.put
        self._delete = api_client.delete


class PDNSEndpoint(PDNSEndpointBase):
    """PowerDNS API Endpoint

    :param PDNSApiClient api_client: Cachet API client instance

    The :class:`~PDNSEndpoint` class defines the following attributes:

    .. autoattribute:: servers

    .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#api-spec
    """
    def __init__(self, api_client):
        """Initialization method"""
        self._servers = None
        super(PDNSEndpoint, self).__init__(api_client)

    def __repr__(self):
        return 'PDNSEndpoint(%s)' % self.api_client

    def __str__(self):
        return 'PDNSEndpoint:%s' % self.api_client.api_endpoint

    @property
    def servers(self):
        """List PowerDNS servers

        PowerDNS API is queried and results are cached. Received
        data is converted to :class:`PDNSServer` instances.

        .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#servers
        """
        LOG.info("listing available PowerDNS servers")
        if not self._servers:
            LOG.info("getting available servers from API")
            self._servers = [PDNSServer(self.api_client, data)
                             for data in self._get('/servers')]
        LOG.info("%d server(s) listed", len(self._servers))
        LOG.debug("listed servers: %s", self._servers)
        return self._servers


class PDNSServer(PDNSEndpointBase):
    """Powerdns API Server Endpoint

    :param PDNSApiClient api_client: Cachet API client instance
    :param str api_data: PowerDNS API server data

    api_data structure is received from API, here an example structure::

        {
          "type": "Server",
          "id": "localhost",
          "url": "/api/v1/servers/localhost",
          "daemon_type": "recursor",
          "version": "VERSION",
          "config_url": "/api/v1/servers/localhost/config{/config_setting}",
          "zones_url": "/api/v1/servers/localhost/zones{/zone}",
        }

    The :class:`~PDNSServer` class defines the following attributes:

    .. autoattribute:: config
    .. autoattribute:: zones

    .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#servers
    """
    def __init__(self, api_client, api_data):
        """Initialization method"""
        self._api_data = api_data
        self.sid = api_data['id']
        self.version = api_data['version']
        self.daemon_type = api_data['daemon_type']
        self.url = '/servers/%s' % self.sid
        self._zones = None
        super(PDNSServer, self).__init__(api_client)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'PDNSServer:%s' % self.sid

    @property
    def config(self):
        """Server configuration from PowerDNS API

        .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#url-apiv1serversserver95idconfig
        """
        LOG.info("getting server configuration")
        return self._get('%s/config' % self.url)

    @property
    def zones(self):
        """List of DNS zones on a PowerDNS server

        PowerDNS API is queried and results are cached in object. This cache is
        resetted in case of zone creation, deletion, or restoration. Received
        data is converted to :class:`PDNSZone` instances.

        .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#zone95collection
        """
        LOG.info("listing available zones")
        if not self._zones:
            LOG.info("getting available zones from API")
            self._zones = [PDNSZone(self.api_client, self, data)
                           for data in self._get('%s/zones' % self.url)]
        LOG.info("%d zone(s) listed", len(self._zones))
        LOG.debug("listed zones: %s", self._zones)
        return self._zones

    def search(self, search_term, max_result=100):
        """Search term using API search endpoint

        :param str search_term:
        :param int max_result:
        :return: Query results as :func:`list`

        API response is a list of one or more of the following objects:

        For a zone::

            {
              "name": "<zonename>",
              "object_type": "zone",
              "zone_id": "<zoneid>"
            }

        For a record::

            {
              "content": "<content>",
              "disabled": <bool>,
              "name": "<name>",
              "object_type": "record",
              "ttl": <ttl>,
              "type": "<type>",
              "zone": "<zonename>,
              "zone_id": "<zoneid>"
            }

        For a comment::

            {
              "object_type": "comment",
              "name": "<name>",
              "content": "<content>"
              "zone": "<zonename>,
              "zone_id": "<zoneid>"
            }
        """
        LOG.info("api search terms: %s", search_term)
        results = self._get('%s/search-data?q=%s&max=%d' % (
            self.url,
            search_term,
            max_result
        ))
        LOG.info("%d search result(s)", len(results))
        LOG.debug("search results: %s", results)
        return results

    # pylint: disable=inconsistent-return-statements
    def get_zone(self, name):
        """Get zone by name

        :param str name: Zone name (canonical)
        :return: Zone as :class:`PDNSZone` instance or :obj:`None`

        .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#zone95collection
        """
        LOG.info("getting zone: %s", name)
        for zone in self.zones:
            if zone.name == name:
                LOG.debug("found zone: %s", zone)
                return zone
        LOG.info("zone not found: %s", name)

    def suggest_zone(self, r_name):
        """Suggest best matching zone from existing zone

        Proposal is done on longer zone names matching the record suffix.
        Example::

            record: a.test.sub.domain.tld.
            zone:              domain.tld.
            zone:          sub.domain.tld.   <== best match
            zone:      another.domain.tld.

        :param str r_name: Record canonical name
        :return: Zone as :class:`PDNSZone` object
        """
        LOG.info("suggesting zone for: %s", r_name)
        if not r_name.endswith('.'):
            raise PDNSCanonicalError(r_name)
        best_match = ""
        for zone in self.zones:
            if r_name.endswith(zone.name):
                if not best_match:
                    best_match = zone
                if len(zone.name) > len(best_match.name):
                    best_match = zone
        LOG.info("zone best match: %s", best_match)
        return best_match

    # pylint: disable=inconsistent-return-statements
    # TODO: Full implementation of zones endpoint
    def create_zone(self, name, kind, nameservers, masters=None, servers=None,
                    rrsets=None):
        """Create a new zone

        :param str name: Name of zone
        :param str kind: Type of zone
        :param list nameservers: Name servers
        :param list masters: Zone masters
        :param list servers: List of forwarded-to servers (recursor only)
        :param list rrsets: Resource records sets
        :return: Created zone as :class:`PDNSZone` instance or :obj:`None`

        .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#url-apiv1serversserver95idzones
        """
        zone_data = {
            "name": name,
            "kind": kind,
            "nameservers": nameservers,
        }
        if masters:
            zone_data['masters'] = masters
        if servers:
            zone_data['servers'] = servers
        if rrsets:
            zone_data['rrsets'] = rrsets

        LOG.info("creation of zone: %s", name)
        zone_data = self._post("%s/zones" % self.url, data=zone_data)

        if zone_data:
            # reset server object cache
            self._zones = None
            LOG.info("zone %s successfully created", name)
            return PDNSZone(self.api_client, self, zone_data)

    def delete_zone(self, name):
        """Delete a zone

        :param str name: Zone name
        :return: :class:`PDNSApiClient` response
        """
        # reset server object cache
        self._zones = None
        LOG.info("deletion of zone: %s", name)
        return self._delete("%s/zones/%s" % (self.url, name))

    # pylint: disable=inconsistent-return-statements
    def restore_zone(self, json_file):
        """Restore a zone from a json file produced by :meth:`PDNSZone.backup`

        :param str json_file: Backup file
        :return: Restored zone as :class:`PDNSZone` instance or :obj:`None`
        """
        with open(json_file) as backup_fp:
            zone_data = json.load(backup_fp)
        self._zones = None
        zone_name = zone_data['name']
        zone_data['nameservers'] = []
        LOG.info("restoration of zone: %s", zone_name)
        zone_data = self._post("%s/zones" % self.url, data=zone_data)
        if zone_data:
            LOG.info("zone successfully restored: %s", zone_data['name'])
            return PDNSZone(self.api_client, self, zone_data)
        LOG.info("%s zone restoration failed", zone_name)


class PDNSZone(PDNSEndpointBase):
    """Powerdns API Zone Endpoint

    .. autoattribute:: details
    .. autoattribute:: records

    :param PDNSApiClient api_client: Cachet API client instance
    :param PDNSServer server: PowerDNS server instance
    :param dict api_data: PowerDNS API zone data
    """
    def __init__(self, api_client, server, api_data):
        """Initialization method"""
        self._api_data = api_data
        self.server = server
        self.name = api_data['name']
        self.url = '%s/zones/%s' % (self.server.url, self.name)
        self._details = None
        super(PDNSZone, self).__init__(api_client)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'PDNSZone:%s:%s' % (self.server.sid, self.name)

    @property
    def details(self):
        """Get zone's detailled data"""
        LOG.info("getting %s zone details", self.name)
        if not self._details:
            LOG.info("getting %s zone details from api", self.name)
            self._details = self._get(self.url)
        return self._details

    @property
    def records(self):
        """Get zone's records"""
        LOG.info("getting %s zone records", self.name)
        return self.details['rrsets']

    # pylint: disable=inconsistent-return-statements
    def get_record(self, name):
        """Get record data

        :param str name: Record name
        :return: Record data as :class:`dict` or :obj:`None`
        """
        LOG.info("getting zone record: %s", name)
        for record in self.details['rrsets']:
            if name == record['name']:
                LOG.info("record found: %s", name)
                return record
        LOG.info("record not found: %s", name)

    def create_records(self, rrsets):
        """Create resource record sets

        :param list rrsets: Resource record sets
        :return: Query response
        """
        LOG.info("creating %d record(s) to %s", len(rrsets), self.name)
        LOG.debug("records: %s", rrsets)
        for rrset in rrsets:
            rrset.ensure_canonical(self.name)
            rrset['changetype'] = 'REPLACE'

        # reset zone object cache
        self._details = None
        return self._patch(self.url, data={'rrsets': rrsets})

    def delete_record(self, rrsets):
        """Delete resource record sets

        :param list rrsets: Resource record sets
        :return: Query response
        """
        LOG.info("deletion of %d records from %s", len(rrsets), self.name)
        LOG.debug("records: %s", rrsets)
        for rrset in rrsets:
            rrset.ensure_canonical(self.name)
            rrset['changetype'] = 'DELETE'

        # reset zone object cache
        self._details = None
        return self._patch(self.url, data={'rrsets': rrsets})

    def backup(self, directory, filename=None, pretty_json=False):
        """Backup zone data to json file

        :param str directory: Directory to store json file
        :param str filename: Json file name

        If filename is not provided, destination file is generated with zone
        name (stripping the last dot) and extension `.json`.
        """
        LOG.info("backup of zone: %s", self.name)
        if not filename:
            filename = self.name.rstrip('.') + ".json"
        json_file = os.path.join(directory, filename)
        LOG.info("backup file is %s", json_file)

        with open(json_file, "w") as backup_fp:
            if pretty_json:
                json.dump(self.details,
                          backup_fp,
                          ensure_ascii=True,
                          indent=2,
                          sort_keys=True)
            else:
                json.dump(self.details, backup_fp)
        LOG.info("zone %s successfully saved", self.name)


# pylint: disable=line-too-long
class RRSet(dict):
    """Resource record data for PowerDNS API

    :param str changetype: API keyword DELETE or REPLACE
    :param str name: Record name
    :param str rtype: Record type
    :param list records: List of Str or Tuple(content_str, disabled_bool)
    :param int ttl: Record time to live

    .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#url-apiv1serversserver95idzoneszone95id
    """
    def __init__(self, name, rtype, records, ttl=3600, changetype='REPLACE'):
        """Initialization"""
        LOG.debug("new rrset object for %s", name)
        super(RRSet, self).__init__()
        self.raw_records = records
        self['name'] = name
        self['type'] = rtype
        self['changetype'] = changetype
        self['ttl'] = ttl
        self['records'] = []
        for record in records:
            disabled = False
            if isinstance(record, tuple):
                disabled = record[1]
                record = record[0]
            self['records'].append({'content': record, 'disabled': disabled})

    def __str__(self):
        return "(ttl=%d) %s  %s  %s)" % (self['ttl'], self['name'],
                                         self['type'],
                                         [r[0] for r in self.raw_records])

    def __repr__(self):
        return "powerdns.RRSet(\"%s\", \"%s\", \"%s\", %d, \"%s\")" % (
            self['name'],
            self['type'],
            self.raw_records,
            self['ttl'],
            self['changetype'])

    def ensure_canonical(self, zone):
        """Ensure every record names are canonical

        :param str zone: Zone name to build canonical names

        In case of CNAME records, records content is also checked.

        .. warning::

            This method update :class:`RRSet` data to ensure the use of
            canonical names. It is actually not possible to revert values.
        """
        LOG.debug("ensuring rrset %s is canonical", self['name'])
        if not zone.endswith('.'):
            raise PDNSCanonicalError(zone)
        if not self['name'].endswith('.'):
            LOG.debug("transforming %s with %s", self['name'], zone)
            self['name'] += ".%s" % zone
        if self['type'] == 'CNAME':
            for record in self['records']:
                if not record['content'].endswith('.'):
                    LOG.debug("transforming %s with %s",
                              record['content'], zone)
                    record['content'] += ".%s" % zone
