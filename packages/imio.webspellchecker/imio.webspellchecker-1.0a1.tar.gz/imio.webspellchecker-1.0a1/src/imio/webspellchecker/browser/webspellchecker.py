import json
import os

from Products.Five import BrowserView
from plone import api
from imio.webspellchecker.browser.controlpanel import IWebspellcheckerControlPanelSchema
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from six.moves.urllib.parse import urlparse


class WebspellcheckerInitJS(BrowserView):
    JS_SCRIPT_TEMPLATE = """
$.ajax({{
     type: "GET",
     url: "{js_bundle_url}",
     success: function() {{
        window.WEBSPELLCHECKER_CONFIG = {wsc_config};
     }},
     dataType: "script",
     cache: true
}});
"""

    def __call__(self):
        """
        Get the current webspellchecker settings and create the init script
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IWebspellcheckerControlPanelSchema)
        if settings.enabled:
            language = api.portal.get_current_language()
            return self.JS_SCRIPT_TEMPLATE.format(
                js_bundle_url=settings.js_bundle_url,
                wsc_config=self.format_json_settings(settings, language)
            )

    def format_json_settings(self, settings, language):
        service_url = urlparse(settings.service_url)
        service_port = service_url.port
        if not service_port:
            service_port = 443 if service_url.scheme == "https" else 80
        return json.dumps({
            "autoSearch": True,
            "lang": 'auto',
            "localization": language,
            "theme": settings.theme,
            "removeBranding": settings.hide_branding,
            "serviceProtocol": service_url.scheme,
            "serviceHost": service_url.hostname,
            "servicePort": service_port,
            "servicePath": service_url.path,
            "disableDictionariesPreferences": True,
        })
