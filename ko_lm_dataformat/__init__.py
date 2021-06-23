from .archive import Archive, DatArchive, JSONArchive
from .reader import Reader
from .sentence_splitter import KssSentenceSplitter
from .utils import get_version, tarfile_reader

__version__ = get_version()
