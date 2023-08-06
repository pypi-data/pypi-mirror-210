# -*- coding: utf-8 -*-
#
# dqsegdb2 documentation build configuration file

import glob
import os.path
import re
from importlib import metadata

# -- metadata

project = "dqsegdb2"
copyright = "2018-2022, Cardiff University"
author = "Duncan Macleod"
release = metadata.version(project).split("+")[0]
version = re.split(r"[\w-]", release)[0]

# -- config

default_role = 'obj'

# -- extensions

extensions = [
    "sphinx.ext.ifconfig",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_automodapi.automodapi",
    "sphinx_immaterial",
]

# Intersphinx directory
intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
    "ligo-segments": ("https://lscsoft.docs.ligo.org/ligo-segments/", None),
    "igwn-auth-utils": (
        "https://igwn-auth-utils.readthedocs.io/en/stable/",
        None,
    ),
}

# don't inherit in automodapi
automodapi_inherited_members = False

# -- theme

html_theme = "sphinx_immaterial"
html_theme_options = {
    # metadata
    "edit_uri": "blob/main/docs",
    "repo_name": "dqsegdb2",
    "repo_url": "https://git.ligo.org/duncanmmacleod/dqsegdb2",
    "repo_type": "gitlab",
    "site_url": "https://dqsegdb2.readthedocs.io/",
    # features
    "features": [
        "navigation.expand",
        "navigation.sections",
    ],
    # colour palette
    "palette": [
        {
            "media": "(prefers-color-scheme: light)",
            "scheme": "default",
            "primary": "indigo",
            "accent": "light-blue",
            "toggle": {
                "icon": "material/eye-outline",
                "name": "Switch to dark mode",
            },
        },
        {
            "media": "(prefers-color-scheme: dark)",
            "scheme": "slate",
            "primary": "orange",
            "accent": "orange",
            "toggle": {
                "icon": "material/eye",
                "name": "Switch to light mode",
            },
        },
    ],
}

html_last_updated_fmt = ""
