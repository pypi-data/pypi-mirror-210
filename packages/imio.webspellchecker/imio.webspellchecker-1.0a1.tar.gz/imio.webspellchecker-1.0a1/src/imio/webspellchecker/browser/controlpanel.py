from Products.CMFCore.utils import getToolByName
from Products.ResourceRegistries.tools.JSRegistry import JSRegistryTool
from imio.webspellchecker import _
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.registry.browser.controlpanel import RegistryEditForm, ControlPanelFormWrapper
from z3c.form import button
from zope import schema
from zope.interface import implementer
from zope.interface import Interface

from plone import api
from imio.webspellchecker.interfaces import IIWebspellcheckerControlPanelSettings



class IWebspellcheckerControlPanelSchema(Interface):
    """
    """

    enabled = schema.Bool(
        title=_(u"Enabled"),
        description=_(u"Enable or disable Webspellchecker."),
        required=False,
        default=False,
    )
    hide_branding = schema.Bool(
        title=_(u"Hide branding"),
        description=_(u"Note: only available for server version."),
        required=False,
        default=False,
    )
    enable_grammar = schema.Bool(
        title=_(u"Enable grammar"),
        description=_(u""),
        required=False,
        default=True,
    )
    theme = schema.Choice(
        title=_(u"Theme"),
        description=_(u""),
        required=True,
        vocabulary="imio.webspellchecker.vocabularies.Themes",
        default=u"default",
    )
    js_bundle_url = schema.TextLine(
        title=_(u"WSC JS bundle URL"),
        description=_(u""),
        required=True,
        default=u"",
    )
    service_url = schema.TextLine(
        title=_(u"WSC service URL"),
        description=_(u""),
        required=True,
        default=u"",
    )
    service_id = schema.TextLine(
        title=_(u"Service ID"), description=_(u""), required=False, default=u"",
    )


@implementer(IIWebspellcheckerControlPanelSettings)
class WebspellcheckerControlPanelEditForm(RegistryEditForm):
    schema = IWebspellcheckerControlPanelSchema
    label = _(u"Webspellchecker settings")
    description = _(u"Webspellchecker settings control panel")


class WebspellcheckerSettings(ControlPanelFormWrapper):
    form = WebspellcheckerControlPanelEditForm
