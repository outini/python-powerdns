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

import os
import setuptools


if __name__ == '__main__':
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    release = "1.0.0"
    setuptools.setup(
        name="python-powerdns",
        version=release,
        url="https://github.com/outini/python-powerdns",
        author="Denis Pompilio (jawa)",
        author_email="denis.pompilio@gmail.com",
        maintainer="Denis Pompilio (jawa)",
        maintainer_email="denis.pompilio@gmail.com",
        description="PowerDNS web api python client and interface",
        long_description=open(readme_file).read(),
        long_description_content_type='text/markdown',
        license="MIT",
        platforms=['UNIX'],
        scripts=['bin/pdns-create-zone'],
        packages=['powerdns'],
        package_dir={'powerdns': 'powerdns'},
        data_files=[
            ('share/doc/python-powerdns', ['README.md', 'LICENSE', 'CHANGES']),
        ],
        keywords=['dns', 'powerdns', 'api'],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Operating System :: POSIX :: BSD',
            'Operating System :: POSIX :: Linux',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Environment :: Web Environment',
            'Topic :: Utilities',
            ],
        requires=['urllib3', 'requests']
    )
