# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface


class IImioWebspellcheckerLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IIWebspellcheckerControlPanelSettings(Interface):
    """
    Settings for Document Generator.
    """
