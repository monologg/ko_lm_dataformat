import importlib
import logging
import sys
from typing import List

from .sentence_cleaner import clean_sentence

# The package importlib_metadata is in a different place, depending on the python version.
if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata

logger = logging.getLogger(__name__)


class SentenceSplitterBase:
    """Base Class for sentence splitter"""

    def __init__(self, clean_sentence=False):
        self.splitter = None
        self.clean_sentence = clean_sentence

    def split(self, document: str) -> List[str]:
        raise NotImplementedError


class KssSentenceSplitter(SentenceSplitterBase):
    def __init__(self, clean_sentence=False):
        super().__init__(clean_sentence=clean_sentence)
        try:
            self.splitter = importlib.import_module("kss")
            assert importlib_metadata.version("kss") == "1.3.1"
        except ImportError:
            logger.warning("You need to install kss to use KssSentenceSplitter")

    def split(self, document: str) -> List[str]:
        if not self.clean_sentence:
            return self.splitter.split_sentences(document)
        else:
            cleaned_output = []
            for sent in self.splitter.split_sentences(document):
                cleaned_output.append(clean_sentence(sent))
            return cleaned_output
