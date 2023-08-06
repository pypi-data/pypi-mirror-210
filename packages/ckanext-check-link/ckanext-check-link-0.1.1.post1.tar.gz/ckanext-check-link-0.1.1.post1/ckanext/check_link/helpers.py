from __future__ import annotations

import ckan.plugins.toolkit as tk

from ckanext.toolbelt.decorators import Collector

CONFIG_HEADER_LINK = "ckanext.check_link.show_header_link"
DEFAULT_HEADER_LINK = False

helper, get_helpers = Collector("check_link").split()


@helper
def show_header_link() -> bool:
    return tk.asbool(tk.config.get(CONFIG_HEADER_LINK, DEFAULT_HEADER_LINK))
