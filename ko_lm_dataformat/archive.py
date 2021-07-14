import os
import time
from glob import glob
from typing import Dict, List, Optional, Union

import ujson as json
import zstandard

from .sentence_cleaner import clean_sentence
from .sentence_splitter import SentenceSplitterBase
from .utils import get_datetime_timestamp, get_version

CURRENT_CHUNK_INCOMPLETE = "current_chunk_incomplete"


class Archive:
    def __init__(
        self, out_dir: str, sentence_splitter: Optional[SentenceSplitterBase] = None, threads: int = -1, level: int = 3
    ):
        """
        Archive for save lm data. Save as `.jsonl.zst`

        Args:
            out_dir (str): Output directory path
            sentence_splitter (SentenceSplitterBase, optional): Sentence Splitter. Defaults to None.
            threads (int, optional):
                Number of threads for compressing.
                0 will disable multi-thread.
                -1 will set the number of threads to the number of detected logical CPUs.
                Defaults to -1.
            level (int, optional): Integer compression level. Valid values are all negative integers through 22.
        """
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.commit_cnt = 0  # count number of commit

        self.chunk_path = self.set_chunk_name()
        self.fh = open(self.chunk_path, "wb")
        self.cctx = zstandard.ZstdCompressor(level=level, threads=threads)
        self.compressor = self.cctx.stream_writer(self.fh)

        self.sentence_splitter = sentence_splitter

    def set_chunk_name(self):
        # check whether the incomplete chunks exist
        chunk_list = glob(os.path.join(self.out_dir, CURRENT_CHUNK_INCOMPLETE + "_*"))
        # sort the names of chunks by numerical order
        chunk_list = sorted(chunk_list, key=lambda name: int(name.split("_")[-1]))
        # give a unique name of the current chunk
        chunk_num = 0
        if chunk_list and chunk_list[-1]:
            chunk_num = int(chunk_list[-1].split("_")[-1]) + 1

        return os.path.join(self.out_dir, f"{CURRENT_CHUNK_INCOMPLETE}_{chunk_num}")

    def add_data(
        self,
        data: Union[str, List[str]],
        meta: Optional[Dict] = None,
        split_sent: bool = False,
        clean_sent: bool = False,
    ):
        """
        Args:
            data (Union[str, List[str]]):
                - Simple text
                - List of text (multiple sentences)
            meta (Dict, optional): metadata. Defaults to None.
            split_sent (bool): Whether to split text into sentences
            clean_sent (bool): Whether to clean text (NFC, remove control char etc.)
        """
        if meta is None:
            meta = {}
        if split_sent:
            assert self.sentence_splitter
            assert type(data) != list  # Shouldn't be List[str]
            data = self.sentence_splitter.split(data, clean_sent=clean_sent)

        if clean_sent and type(data) == str:
            data = clean_sentence(data)

        self.compressor.write(json.dumps({"text": data, "meta": meta}, ensure_ascii=False).encode("UTF-8") + b"\n")

    def commit(self, archive_name="default"):
        fname = (
            self.out_dir
            + "/data_"
            + str(self.commit_cnt)
            + "_"
            + f"{get_datetime_timestamp()}"
            + "_"
            + f"v{get_version()}"
            + "_"
            + archive_name
            + ".jsonl.zst"
        )
        self.compressor.flush(zstandard.FLUSH_FRAME)

        self.fh.flush()
        self.fh.close()
        os.rename(self.chunk_path, fname)

        # Make new file for temporary writer
        self.chunk_path = self.set_chunk_name()
        self.fh = open(self.chunk_path, "wb")
        self.compressor = self.cctx.stream_writer(self.fh)

        self.commit_cnt += 1

    def set_sentence_splitter(self, sentence_splitter: SentenceSplitterBase):
        self.sentence_splitter = sentence_splitter


class DatArchive:
    def __init__(self, out_dir: str, sentence_splitter: Optional[SentenceSplitterBase] = None, level: int = 3):
        """
        Archive for save lm data. Save as `.dat.zst`

        Args:
            out_dir (str): Output directory path
            sentence_splitter (SentenceSplitterBase, optional): Sentence Splitter. Defaults to None.
            level (int, optional): Integer compression level. Valid values are all negative integers through 22.
        """
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.level = level

        self.commit_cnt = 0
        if os.path.exists(out_dir) and len(os.listdir(out_dir)) > 0:
            self.commit_cnt = max(map(lambda x: int(x.split("_")[1].split(".")[0]), os.listdir(out_dir))) + 1

        self.data = []

        self.sentence_splitter = sentence_splitter

    def add_data(self, data: Union[str, List[str]], split_sent: bool = False, clean_sent: bool = False):
        if split_sent:
            assert self.sentence_splitter
            assert type(data) == str  # Shouldn't be List[str]
            data = self.sentence_splitter.split(data, clean_sent=clean_sent)

        self.data.append(data)

    def commit(self, archive_name=None):
        cctx = zstandard.ZstdCompressor(level=self.level)

        if archive_name is None:
            archive_name = str(int(time.time()))

        res = b"".join(
            map(lambda x: ("%016d" % len(x)).encode("UTF-8") + x, map(lambda x: x.encode("UTF-8"), self.data))
        )
        cdata = cctx.compress(res)

        with open(
            self.out_dir
            + "/data_"
            + str(self.commit_cnt)
            + "_"
            + f"v{get_version()}"
            + "_"
            + archive_name
            + ".dat.zst",
            "wb",
        ) as fh:
            fh.write(cdata)

        self.commit_cnt += 1
        self.data = []


class JSONArchive:
    def __init__(self, out_dir: str, sentence_splitter: Optional[SentenceSplitterBase] = None, level: int = 3):
        """
        Archive for save lm data. Save as `.json.zst`

        Args:
            out_dir (str): Output directory path
            sentence_splitter (SentenceSplitterBase, optional): Sentence Splitter. Defaults to None.
            level (int, optional): Integer compression level. Valid values are all negative integers through 22.
        """
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.level = level

        self.commit_cnt = 0
        if os.path.exists(out_dir) and len(os.listdir(out_dir)) > 0:
            self.commit_cnt = max(map(lambda x: int(x.split("_")[1].split(".")[0]), os.listdir(out_dir))) + 1

        self.data = []

        self.sentence_splitter = sentence_splitter

    def add_data(self, data: Union[str, List[str]], split_sent: bool = False, clean_sent: bool = False):
        if split_sent:
            assert self.sentence_splitter
            assert type(data) == str  # Shouldn't be List[str]
            data = self.sentence_splitter.split(data, clean_sent=clean_sent)

        self.data.append(data)

    def commit(self):
        cctx = zstandard.ZstdCompressor(level=self.level)

        cdata = cctx.compress(json.dumps(self.data).encode("UTF-8"))
        with open(
            self.out_dir
            + "/data_"
            + str(self.commit_cnt)
            + "_"
            + str(int(time.time()))
            + "_"
            + f"v{get_version()}"
            + "_"
            + ".json.zst",
            "wb",
        ) as fh:
            fh.write(cdata)

        self.commit_cnt += 1
        self.data = []
