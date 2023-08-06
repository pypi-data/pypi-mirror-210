from numpy import float64
from gensim.models import LsiModel

from .topics import GensimWrapper
from orangecontrib.text.i18n_config import *


def __(key):
    return i18n.t('text.common.' + key)


class LsiModelProxy(LsiModel):
    update = LsiModel.add_documents

    def add_documents(self, corpus, chunksize=None, decay=None):
        """
        add_documents calls update which is equal to super().add_documents

        It is made because of mechanism in topics.py which disables update in
        some cases. In case of Lsi disabling update must results in disabling
        add_documents.
        """
        self.update(corpus, chunksize, decay)


class LsiWrapper(GensimWrapper):
    name = __("lsi_wrapper")
    Model = LsiModelProxy
    has_negative_weights = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs, dtype=float64)
