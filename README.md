[![PythonSupport][1]][1l] [![License][2]][2l] [![PyPI version][3]][3l]

# python-powerdns -- PowerDNS web api python client and interface

**Contact:** Denis 'jawa' Pompilio <denis.pompilio@gmail.com>

**Sources:** <https://github.com/outini/python-powerdns>

## About

This package provides intuitive and easy to use python client and interface
for the PowerDNS web API.

## Installation

```bash
python setup.py install
```

or

```bash
pip install python-powerdns
```

## Helpers

### pdns-zone-creator

```bash
usage: pdns-create-zone [-h] -A API -K APIKEY -z ZONE -o ORIGIN -c ZONE -d DNS
                        [-t TIMERS]

PowerDNS zone creator

optional arguments:
  -h, --help            show this help message and exit
  -A API, --api API     PowerDNS api (eg. https://api.domain.tld/api/v1
  -K APIKEY, --key APIKEY
                        PowerDNS api key
  -z ZONE, --zone ZONE  Zone name (canonical)
  -o ORIGIN, --origin ORIGIN
                        Zone origin (for SOA)
  -c ZONE, --contact ZONE
                        Zone contact (for SOA)
  -d DNS, --dns DNS     Zone nameservers comma separated
  -t TIMERS, --timers TIMERS
                        Zone timers (eg. '28800 7200 604800 86400')
```

```bash
./bin/pdns-create-zone -A "https://api.domain.tld/api/v1" -K "xxxxxxxxx" \
                       -z "myzone.domain.tld." \
                       -o "ns01.domain.tld." -c "admin.domain.tld." \
                       -d "nsd01.domain.tld.,nsd02.domain.tld."
powerdns.interface INFO: listing available PowerDNS servers
powerdns.interface INFO: getting available servers from API
powerdns.client INFO: request: GET https://api.domain.tld/api/v1/servers
powerdns.client INFO: request response code: 200
powerdns.interface INFO: 1 server(s) listed
powerdns.interface INFO: creation of zone: myzone.domain.tld.
powerdns.client INFO: request: POST https://api.domain.tld/api/v1/servers/localhost/zones
powerdns.client INFO: request response code: 201
powerdns.interface INFO: zone myzone.domain.tld. successfully created
```

## Examples

### Basic initialization

```python
import powerdns

PDNS_API = "https://my.pdns.api.domain.tld/api/v1"
PDNS_KEY = "mysupersecretbase64key"

api_client = powerdns.PDNSApiClient(api_endpoint=PDNS_API, api_key=PDNS_KEY)
api = powerdns.PDNSEndpoint(api_client)
```

### Creation and deletion of zones

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

### Creation and deletion of DNS records

```python
zone = api.servers[0].get_zone("test.python-powerdns.domain.tld.")

comments = [powerdns.Comment("test comment", "admin")]

zone.create_records([
    powerdns.RRSet('a', 'A', [('1.1.1.1', False)], comments=comments),
    powerdns.RRSet('b', 'A', ['1.1.1.2', '1.1.1.3']),
    powerdns.RRSet('c', 'A', [('1.1.1.4', False)]),
    powerdns.RRSet('d', 'CNAME', ['a'])
])

zone.delete_records([
    powerdns.RRSet('a', 'A', [('1.1.1.1', False)]),
    powerdns.RRSet('d', 'CNAME', ['a'])
])
```

Where (for the first RRSet):

* `a` is the NAME of the record
* `A` is the TYPE of the record
* `[('1.1.1.1', False)]` is a list of RDATA entries (tuples or just strings), where:
  * `'1.1.1.1'` is the RDATA
  * `False` tells that this RDATA entry is NOT disabled

### Backup and restoration of zones

```python
# Backup every zone of every PowerDNS server
for server in api.servers:
    backup_dir = "backups/%s" % server.id
    for zone in server.zones:
        zone.backup(backup_dir)

# Restore a single zone on first PowerDNS server
zone_file = "backups/pdns-server-01/my.domain.tld.json"
api.servers[0].restore_zone(zone_file)
```

## Tests

### PowerDNS service

A simple [Dockerfile] is provided to spawn a basic powerdns service for tests
purposes. The container is built using:

```bash
docker build --tag pdns .
```

And started using:

```bash
docker run --rm -it pdns
```

### Python Unit-Tests

Python unit-tests are available in the [tests] directory. Based on [unittests],
those are run using `coverage run -m unittest discover` or integrated in your
IDE for development purposes. Those tests require a PDNS service to connect to
(see _PowerDNS service_ section above).

Those tests are very limited at the moment and will be improved in the future.

## License

MIT LICENSE *(see LICENSE file)*

## Miscellaneous

```
    ╚⊙ ⊙╝
  ╚═(███)═╝
 ╚═(███)═╝
╚═(███)═╝
 ╚═(███)═╝
  ╚═(███)═╝
   ╚═(███)═╝
```

[1]: https://img.shields.io/badge/python-2.7,3.4+-blue.svg
[1l]: https://github.com/outini/python-powerdns
[2]: https://img.shields.io/badge/license-MIT-blue.svg
[2l]: https://github.com/outini/python-powerdns
[3]: https://badge.fury.io/py/python-powerdns.svg
[3l]: https://pypi.org/project/python-powerdns
[Dockerfile]: files/Dockerfile
[tests]: tests
[unittests]: https://docs.python.org/3/library/unittest.html
