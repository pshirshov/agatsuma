#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from agatsuma.core import Core
from agatsuma.setup_helpers import (getEntryPoints,
                                    runSetuptools,
                                    getDeps,
                                    groupsPredicate,
                                    out,
                                    nl,
                                    )
def main():
    nl()
    out("Agatsuma: Distribute mode")
    nl()

    Core(None, None, appMode = 'setup')

    spellsFilter = lambda x: True # consider internal spells too
    entryPoints = getEntryPoints(spellsFilter)
    dependencies = getDeps(groupsPredicate(sys.argv), spellsFilter)

    nl()
    out("Continuing with Distribute...")
    nl()
    from setuptools import find_packages
    runSetuptools(
        install_requires = dependencies,
        entry_points = entryPoints,
        version = Core.versionString,

        packages = find_packages(exclude=['distribute_setup']),
        zip_safe=False,
        include_package_data = True,
        #test_suite = 'nose.collector',
        #scripts = ['say_hello.py'],
        package_data = {
            # If any package contains *.txt or *.rst files, include them:
            '': ['*.txt', '*.rst'],
            # And include any *.msg files found in the 'hello' package, too:
            #'hello': ['*.msg'],
        },

        # metadata for upload to PyPI
        name = "Agatsuma",
        author = "Fei Wong Reed",
        author_email = "feiwreed@gmail.com",
        description = "Flexible modular metaframework, mostly intended for web but not only",
        license = "GPL3",
        keywords = "agatsuma modularity web framework dynamic imports tornado pylons",
        url = "http://agatsuma.ritsuka.org/",
    )

if __name__ == '__main__':
    main()
