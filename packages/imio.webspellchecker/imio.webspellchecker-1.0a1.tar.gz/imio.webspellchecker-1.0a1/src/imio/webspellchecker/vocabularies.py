from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.interface import provider


@provider(IVocabularyFactory)
class WebspellcheckerHttpProtocolsVocabulary(object):
    """Vocabulary factory for http protocols
    """

    def __call__(self, context):
        return SimpleVocabulary([SimpleTerm("http", "HTTP"), SimpleTerm("https", "HTTPS")])


WebspellcheckerHttpProtocolsVocabularyFactory = WebspellcheckerHttpProtocolsVocabulary()


@provider(IVocabularyFactory)
class WebspellcheckerThemesVocabulary(object):
    """Vocabulary factory for http protocols
    """

    def __call__(self, context):
        return SimpleVocabulary(
            [
                SimpleTerm("default", "Default"),
                SimpleTerm("gray", "Gray"),
                SimpleTerm("dark", "Dark"),
                SimpleTerm("custom", "Custom"),
            ]
        )


WebspellcheckerThemesVocabularyFactory = WebspellcheckerThemesVocabulary()
