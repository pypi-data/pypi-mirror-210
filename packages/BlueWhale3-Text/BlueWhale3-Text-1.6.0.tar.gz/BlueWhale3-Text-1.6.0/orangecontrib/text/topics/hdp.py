from gensim import models

from .topics import GensimWrapper
from orangecontrib.text.i18n_config import *


def __(key):
    return i18n.t('text.common.' + key)

class HdpWrapper(GensimWrapper):
    name = __("hdp_wrapper")
    Model = models.HdpModel

    @property
    def num_topics(self):
        return self.model.m_lambda.shape[0] if self.model else 0
