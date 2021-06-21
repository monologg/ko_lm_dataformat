import gzip
import io
import multiprocessing as mp
from zipfile import ZipFile

import jsonlines
import ujson as json
import zstandard

from .utils import handle_jsonl, listdir_or_file, tarfile_reader


class Reader:
    def __init__(self, in_path: str):
        """
        Read data which is archive with ko_lm_dataformat

        Args:
            in_path (str): Input directory path
        """
        self.in_path = in_path

    def stream_data(self, get_meta=False, autojoin_sentences=False, sent_joiner=" ", threaded=False):
        if not threaded:
            yield from self._stream_data(
                get_meta=get_meta, autojoin_sentences=autojoin_sentences, sent_joiner=sent_joiner
            )
            return

        q = mp.Queue(1000)
        p = mp.Process(target=self._stream_data_threaded, args=(q, get_meta, autojoin_sentences, sent_joiner))
        p.start()
        while p.is_alive():
            res = q.get()
            if res is None:
                break
            yield res

    def _stream_data_threaded(self, q, get_meta=False):
        for data in self._stream_data(get_meta):
            q.put(data)
        q.put(None)

    def _stream_data(self, get_meta=False, autojoin_sentences=False, sent_joiner=" ", jsonl_key="text"):
        """
        - Support format: jsonl.zst, json, dat, txt, zip, tar.gz

        Args:
            get_meta (bool, optional): Whether to get meta data. Only jsonl file has metadata. Defaults to False.
            jsonl_key (str, optional): Key name for text. Defaults to "text".

        Yields:
            if get_meta:
                text: str
            else:
                (text: str, meta: dict)
        """
        self.f_name = ""
        for f in listdir_or_file(self.in_path):
            self.f_name = f
            if f.endswith(".jsonl.zst"):
                yield from self.read_jsonl(
                    f, get_meta=get_meta, autojoin_sentences=autojoin_sentences, sent_joiner=sent_joiner, key=jsonl_key
                )
            elif f.endswith(".dat.zst"):
                assert not get_meta
                yield from self.read_dat(f)
            elif f.endswith(".jsonl.zst.tar"):
                yield from self.read_jsonl_tar(
                    f, get_meta=get_meta, autojoin_sentences=autojoin_sentences, sent_joiner=sent_joiner, key=jsonl_key
                )
            elif f.endswith(".json.zst"):
                assert not get_meta
                yield from self.read_json(f)
            elif f.endswith(".txt"):
                assert not get_meta
                yield from self.read_txt(f)
            elif f.endswith(".zip"):
                assert not get_meta
                yield from self.read_zip(f)
            elif f.endswith(".tar.gz"):
                assert not get_meta
                yield from self.read_tgz(f)

    def read_txt(self, file):
        with open(file, "r") as fh:
            yield fh.read()

    def read_zip(self, file):
        archive = ZipFile(file, "r")
        for f in archive.namelist():
            yield archive.read(f).decode("UTF-8")

    def read_tgz(self, file):
        gz = gzip.open(file)
        yield from (x.decode("utf-8") for x in tarfile_reader(gz, streaming=False))

    def read_json(self, file):
        with open(file, "rb") as fh:
            cctx = zstandard.ZstdDecompressor()
            reader = cctx.stream_reader(fh)
            ob = json.load(reader)
            yield from ob

    def read_dat(self, file):
        with open(file, "rb") as fh:
            cctx = zstandard.ZstdDecompressor()
            reader = cctx.stream_reader(fh)
            while True:
                ln = reader.read(16).decode("UTF-8")
                if not ln:
                    break

                ln = int(ln)

                yield reader.read(ln).decode("UTF-8")

    def read_jsonl(
        self,
        file_path: str,
        get_meta: bool = False,
        autojoin_sentences: bool = True,
        sent_joiner: str = " ",
        key: str = "text",
    ):
        """
        Read Jsonl data.

        Args:
            file_path (str): input file path
            get_meta (bool, optional): return metadata. Defaults to False.
            autojoin_sentences (bool, optional): Join sentences if data consists of multiple texts (=paragraph). Defaults to True.
            sent_joiner (str, optional): Seperator for joining multiple sentences. Defaults to "\n\n".
            key (str, optional): Json key name for text. Defaults to "text".
        """
        with open(file_path, "rb") as fh:
            cctx = zstandard.ZstdDecompressor()
            reader = io.BufferedReader(cctx.stream_reader(fh))
            rdr = jsonlines.Reader(reader)
            yield from handle_jsonl(rdr, get_meta, autojoin_sentences, sent_joiner, key)

    def read_jsonl_tar(
        self,
        file_path,
        get_meta=False,
        autojoin_sentences: bool = True,
        sent_joiner: str = " ",
        key="text",
    ):
        with open(file_path, "rb") as fh:
            for f in tarfile_reader(fh, streaming=True):
                cctx = zstandard.ZstdDecompressor()
                reader = io.BufferedReader(cctx.stream_reader(f))
                rdr = jsonlines.Reader(reader)
                yield from handle_jsonl(rdr, get_meta, autojoin_sentences, sent_joiner, key)
                f.close()
