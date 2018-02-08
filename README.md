[![PythonSupport][1]][1l][![License][2]][2l]

# python-powerdns -- PowerDNS web api python client and interface

| **Contact:** Denis 'jawa' Pompilio <dpompilio@vente-privee.com>
| **Sources:** https://github.com/vente-privee/python-powerdns

## About

This package provides intuitive and easy to use python client and interface
for the PowerDNS web API.

## Installation

```bash
python setup.py install
```

## Exemples

Basic initialization:
```python
import powerdns

PDNS_API = "https://my.pdns.api.domain.tld/api/v1"
PDNS_KEY = "mysupersecretbase64key"

api_client = powerdns.PDNSApiClient(api_endpoint=PDNS_API, api_key=PDNS_KEY)
api = powerdns.PDNSEndpoint(api_client)
```

Creation and deletion of zones:
```python
from datetime import date

# Creating new zone on first PowerDNS server
serial = date.today().strftime("%Y%m%d00")
soa = "ns0.domain.tld. admin.domain.tld. %s 28800 7200 604800 86400" % serial
soa_r = powerdns.RRSet(name='test.python-powerdns.domain.tld.',
                       rtype="SOA",
                       records=[(soa, False)],
                       ttl=86400)
zone = api.servers[0].create_zone(name="test.python-powerdns.domain.tld.",
                                  kind="Native",
                                  rrsets=[soa_r],
                                  nameservers=["ns1.domain.tld.",
                                               "ns2.domain.tld."])

# Getting new zone info
print(zone)
print(zone.details)

# Deleting newly created zone
api.servers[0].delete_zone(zone.name)
```

Creation and deletion of DNS records:
```python
zone = api.server[0].get_zone("test.python-powerdns.domain.tld.")

zone.create_records([
    powerdns.RRSet('a', 'A', [('1.1.1.1', False)]),
    powerdns.RRSet('b', 'A', ['1.1.1.2', '1.1.1.3']),
    powerdns.RRSet('c', 'A', [('1.1.1.4', False)]),
    powerdns.RRSet('d', 'CNAME', ['a'])
])

zone.delete_record([
    powerdns.RRSet('a', 'A', [('1.1.1.1', False)]),
    powerdns.RRSet('d', 'CNAME', ['a'])
])
```

Backup and restoration of zones:
```python
# Backup every zone of every PowerDNS server
for server in api.servers:
    backup_dir = "backups/%s" % server.name
    for zone in server.zones:
        zone.backup(backup_dir)

# Restore a single zone on first PowerDNS server
zone_file = "backups/pdns-server-01/my.domain.tld.json"
api.servers[0].restore_zone(zone_file)
```

## License

MIT LICENSE *(see LICENSE file)*

[1]: https://img.shields.io/badge/python-2.7,3.4+-blue.svg
[1l]: https://github.com/vente-privee/python-powerdns
[2]: https://img.shields.io/badge/license-MIT-blue.svg
[2l]: https://github.com/vente-privee/python-powerdns
