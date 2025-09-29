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
powerdns.interface - PowerDNS API interface
"""

import logging
import os
import json
import time

from .exceptions import PDNSCanonicalError


LOG = logging.getLogger(__name__)


# pylint: disable=useless-object-inheritance
# pylint: disable=too-few-public-methods
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

    .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#api-spec
    """
    def __init__(self, api_client):
        """Initialization method"""
        self._servers = None
        super(PDNSEndpoint, self).__init__(api_client)

    def __repr__(self):
        return 'PDNSEndpoint(%s)' % repr(self.api_client)

    def __str__(self):
        return str(self.api_client)

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

    .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#servers
    """
    def __init__(self, api_client, api_data):
        """Initialization method"""
        self._api_client = api_client
        self._api_data = api_data
        self.sid = api_data['id']
        self.version = api_data['version']
        self.daemon_type = api_data['daemon_type']
        self.url = '/servers/%s' % self.sid
        self._zones = None
        super(PDNSServer, self).__init__(api_client)

    def __repr__(self):
        return 'PDNSServer(%s, %s)' % (
            repr(self._api_client), repr(self._api_data)
        )

    def __str__(self):
        return self.sid

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
        :return: Zone as :class:`PDNSZone` object or :obj:`None`
        """
        LOG.info("suggesting zone for: %s", r_name)
        if not r_name.endswith('.'):
            raise PDNSCanonicalError(r_name)
        best_match = None
        for zone in self.zones:
            if r_name.endswith('.' + zone.name):
                if not best_match:
                    best_match = zone
                if best_match and len(zone.name) > len(best_match.name):
                    best_match = zone
        LOG.info("zone best match: %s", best_match)
        return best_match

    # pylint: disable=inconsistent-return-statements
    # pylint: disable=too-many-arguments
    # TODO: Full implementation of zones endpoint
    def create_zone(self, name, kind, nameservers, masters=None, servers=None,
                    rrsets=None, update=False):
        """Create or update a (new) zone

        :param str name: Name of zone
        :param str kind: Type of zone
        :param list nameservers: Name servers
        :param list masters: Zone masters
        :param list servers: List of forwarded-to servers (recursor only)
        :param list rrsets: Resource records sets
        :param bool update: If the zone need to be updated or created
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

        if update is True:
            LOG.info("update of zone: %s", name)
            get_zone = self.get_zone(name).details
            zone_id = get_zone['id']
            zone_data = self._patch("{}/zones/{}".format(self.url,
                                                         zone_id),
                                    data=zone_data)

        else:
            LOG.info("creation of zone: %s", name)
            zone_data = self._post("%s/zones" % self.url, data=zone_data)

        if zone_data:
            # reset server object cache
            self._zones = None
            LOG.info("zone %s successfully processed", name)
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

    :param PDNSApiClient api_client: Cachet API client instance
    :param PDNSServer server: PowerDNS server instance
    :param dict api_data: PowerDNS API zone data
    """
    def __init__(self, api_client, server, api_data):
        """Initialization method"""
        self._api_client = api_client
        self._api_data = api_data
        self.server = server
        self.name = api_data['name']
        self.url = '%s/zones/%s' % (self.server.url, self.name)
        self._details = None
        super(PDNSZone, self).__init__(api_client)

    def __repr__(self):
        return "PDNSZone(%s, %s, %s)" % (
            repr(self._api_client), repr(self.server), repr(self._api_data)
        )

    def __str__(self):
        return self.name

    @property
    def details(self):
        """Get zone's detailed data"""
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

    def get_record(self, name):
        """Get record data

        :param str name: Record name
        :return: Records data as :func:`list`
        """
        records = []
        LOG.info("getting zone record: %s", name)
        for record in self.details['rrsets']:
            if name == record['name']:
                LOG.info("record found: %s", name)
                records.append(record)

        if not records:
            LOG.info("record not found: %s", name)

        return records

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

    def delete_records(self, rrsets):
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
        :param bool pretty_json: Enable pretty json display

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

    def notify(self):
        """Trigger notification for zone updates"""
        LOG.info("notify of zone: %s", self.name)
        return self._put(self.url + '/notify')


# pylint: disable=line-too-long
# pylint: disable=too-many-arguments
class RRSet(dict):
    """Resource record data for PowerDNS API

    :param str changetype: API keyword DELETE or REPLACE
    :param str name: Record name
    :param str rtype: Record type
    :param list records: List of Str or Tuple(content_str, disabled_bool)
                         or Dict with the keys "content" and optionally
                         "disabled".
    :param int ttl: Record time to live
    :param list comments: list of Comments instances for this RRSet

    .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#url-apiv1serversserver95idzoneszone95id
    """
    def __init__(self, name, rtype, records, ttl=3600, changetype='REPLACE',
                 comments=None):
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
            if isinstance(record, dict):
                if set(record.keys()) > {"content", "disabled"}:
                    raise ValueError(f"Dictionary { records } has more keys than 'content' and 'disabled'")
                if "content" not in record.keys():
                    raise ValueError(f"Dictionary { records } does not have the 'content' key.")
                if "disabled" not in record.keys():
                    record["disabled"] = False

                self['records'].append(record)
                continue

            if isinstance(record, (list, tuple)):
                disabled = record[1]
                record = record[0]
            self['records'].append({'content': record, 'disabled': disabled})
        if comments is None:
            self["comments"] = list()
        else:
            self["comments"] = comments

    def __repr__(self):
        return "RRSet(%s, %s, %s, %s, %s, %s)" % (
            repr(self['name']),
            repr(self['type']),
            repr(self.raw_records),
            repr(self['ttl']),
            repr(self['changetype']),
            repr(self['comments']),
        )

    def __str__(self):
        records = []

        for record in self.raw_records:
            if isinstance(record, (list, tuple)):
                records += [record[0]]
            else:
                records += [record]

        return "(ttl=%d) %s  %s  %s %s)" % (self['ttl'],
                                            self['name'],
                                            self['type'],
                                            records,
                                            self['comments'],)

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


class Comment(dict):
    """Comment data for PowerDNS API RRSets

    :param str content: the content of the comment
    :param str account: the account
    :param int modified_at: Unix timestamp at which the comment was last
                            modified. Will be set to the current timestamp if
                            None.

    .. seealso:: https://doc.powerdns.com/md/httpapi/api_spec/#zone95collection
    """

    def __init__(self, content, account="", modified_at=None):
        """Initialization"""
        super(Comment, self).__init__(content=content, account=account)

        if modified_at is None:
            self["modified_at"] = int(time.time())
        else:
            self["modified_at"] = modified_at

    def __repr__(self):
        return "Comment(%s, %s, %s)" % (
            repr(self["content"]),
            repr(self["account"]),
            repr(self["modified_at"]),
        )
