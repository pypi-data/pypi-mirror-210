from AnyQt.QtWidgets import QApplication, QGridLayout, QLabel

from Orange.widgets import settings
from orangecontrib.text.corpus import Corpus
from orangecontrib.text.vectorization import BowVectorizer
from orangecontrib.text.widgets.utils import owbasevectorizer, widgets
from orangecontrib.text.i18n_config import *


def __(key):
    return i18n.t('text.owbagofwords.' + key)


class OWTBagOfWords(owbasevectorizer.OWBaseVectorizer):
    name = __("name")
    description = __("desc")
    icon = 'icons/BagOfWords.svg'
    priority = 300
    keywords = ["BOW"]

    Method = BowVectorizer

    # Settings
    wlocal = settings.Setting(BowVectorizer.COUNT)
    wglobal = settings.Setting(BowVectorizer.NONE)
    normalization = settings.Setting(BowVectorizer.NONE)

    def create_configuration_layout(self):
        layout = QGridLayout()
        layout.setSpacing(10)
        row = 0
        combo = widgets.ComboBox(self, 'wlocal',
                                 items=tuple(BowVectorizer.wlocals.keys()))
        combo.currentIndexChanged.connect(self.on_change)
        layout.addWidget(QLabel(__("row_term_frequency")))
        layout.addWidget(combo, row, 1)

        row += 1
        combo = widgets.ComboBox(self, 'wglobal',
                                 items=tuple(BowVectorizer.wglobals.keys()))

        combo.currentIndexChanged.connect(self.on_change)
        layout.addWidget(QLabel(__("row_document_frequency")))
        layout.addWidget(combo, row, 1)

        row += 1
        combo = widgets.ComboBox(self, 'normalization',
                                 items=tuple(BowVectorizer.norms.keys()))

        combo.currentIndexChanged.connect(self.on_change)
        layout.addWidget(QLabel(__("row_regular")))
        layout.addWidget(combo, row, 1)

        return layout

    def update_method(self):
        self.method = self.Method(norm=self.normalization,
                                  wlocal=self.wlocal,
                                  wglobal=self.wglobal)


if __name__ == '__main__':
    app = QApplication([])
    widget = OWTBagOfWords()
    widget.show()
    corpus = Corpus.from_file('book-excerpts')
    widget.set_data(corpus)
    app.exec()
