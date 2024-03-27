#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "3.0")

import logging
from os import environ

from gi.repository import Gtk
from rtoml import load

from gui import ZeeveeSwitcherGui
from switcher import ZeeveeSwitcher

LOGLEVELS = {
    "debug": logging.DEBUG,
    "error": logging.ERROR,
    "info": logging.INFO,
    "warn": logging.WARNING,
}


def main():
    with open(environ.get("SWITCHER_CONFIG", "config.toml")) as f:
        config = load(f)

    settings = Gtk.Settings.get_default()
    for k, v in config.get("gtk-settings").items():
        settings.set_property(
            k, v
        )  # TODO find out if we can just pass a dict somewhere

    logging.basicConfig(**config.get("logging", {}))

    switcher = ZeeveeSwitcher(config)

    gui = ZeeveeSwitcherGui(config, switcher)
    gui.main_loop()


if __name__ == "__main__":
    main()
