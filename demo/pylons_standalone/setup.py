#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) # only for demo app
sys.path.append('../../')

from agatsuma.setup_helpers import (getEntryPoints,
                                    runSetuptools,
                                    getDeps,
                                    groupsPredicate,
                                    out,
                                    nl,
                                    )

from pylons_demo import make_core
make_core({}, appMode = 'setup', appName = "demo")

entryPoints = getEntryPoints()
dependencies = getDeps(groupsPredicate(sys.argv))

nl()
out("Continuing with Distribute...")
nl()
from setuptools import find_packages

runSetuptools(
    name='pylons_standalone',
    version='0.1',
    description='agatsuma demo app for pylons under paster',
    author='fei wong reed',
    author_email='',
    url='',
    packages=find_packages(exclude=['distribute_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,

    paster_plugins=['PasteScript', 'Pylons'],
    setup_requires=["PasteScript>=1.6.3"],

    install_requires=dependencies,

    entry_points=entryPoints,
 )
