import importlib
import logging
from typing import List

from .sentence_cleaner import clean_sentence
from .utils import importlib_metadata

logger = logging.getLogger(__name__)


class SentenceSplitterBase:
    """Base Class for sentence splitter"""

    def __init__(self):
        self.splitter = None

    def split(self, document: str) -> List[str]:
        raise NotImplementedError


class KssSentenceSplitter(SentenceSplitterBase):
    def __init__(self):
        super().__init__()
        try:
            self.splitter = importlib.import_module("kss")
            assert importlib_metadata.version("kss") == "1.3.1"
        except ImportError:
            logger.warning(
                "You need to install kss to use KssSentenceSplitter \n"
                "pip install cython\n"
                "pip install kss==1.3.1\n"
            )

    def split(self, document: str, clean_sent: bool = False) -> List[str]:
        if not clean_sent:
            return self.splitter.split_sentences(document)
        else:
            cleaned_output = []
            for sent in self.splitter.split_sentences(document):
                cleaned_output.append(clean_sentence(sent))
            return cleaned_output
