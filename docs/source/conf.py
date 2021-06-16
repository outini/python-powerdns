#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join('..', '..')))
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode'
]
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = 'python-powerdns'
copyright = '2018, Denis \'jawa\' Pompilio'
author = 'Denis \'jawa\' Pompilio'


version_file = os.path.join(os.path.dirname(__file__), "..", "..", "VERSION")
release = open(version_file).read()
version = ".".join(release.split('.')[0:2])

language = None

exclude_patterns = []
pygments_style = 'friendly'
todo_include_todos = False
html_theme = "python_docs_theme"
html_style = 'custom.css'
htmlhelp_basename = 'python-powerdns-doc'

intersphinx_mapping = {'https://docs.python.org/3/': None,
'http://docs.python-requests.org/en/master/': None}
