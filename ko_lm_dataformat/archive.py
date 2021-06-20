import os
import time
from typing import Dict, List, Union

import ujson as json
import zstandard


class Archive:
    def __init__(self, out_dir: str, threads: int = -1):
        """
        Archive for save lm data. Save as `.jsonl.zst`

        Args:
            out_dir (str): Output directory path
            threads (int, optional):
                Number of threads for compressing.
                0 will disable multithread.
                -1 will set the number of threads to the numbert of detected logical CPUs.
                Defaults to -1.
        """
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)
        self.commit_cnt = 0  # count number of commit

        self.fh = open(self.out_dir + "/current_chunk_incomplete", "wb")
        self.cctx = zstandard.ZstdCompressor(level=3, threads=threads)
        self.compressor = self.cctx.stream_writer(self.fh)

    def add_data(self, data: Union[str, List[str]], meta: Dict = {}):
        """
        Args:
            data (Union[str, List[str]]):
                - Simple text
                - List of text (multiple document)
            meta (Dict, optional): [description]. Defaults to {}.
        """
        self.compressor.write(json.dumps({"text": data, "meta": meta}, ensure_ascii=False).encode("UTF-8") + b"\n")

    def commit(self, archive_name="default"):
        fname = (
            self.out_dir
            + "/data_"
            + str(self.commit_cnt)
            + "_time"
            + str(int(time.time()))
            + "_"
            + archive_name
            + ".jsonl.zst"
        )
        self.compressor.flush(zstandard.FLUSH_FRAME)

        self.fh.flush()
        self.fh.close()
        os.rename(self.out_dir + "/current_chunk_incomplete", fname)

        # Make new file for temporary writer
        self.fh = open(self.out_dir + "/current_chunk_incomplete", "wb")
        self.compressor = self.cctx.stream_writer(self.fh)

        self.commit_cnt += 1


class DatArchive:
    def __init__(self, out_dir: str):
        """
        Archive for save lm data. Save as `.dat.zst`

        Args:
            out_dir (str): Output directory path
        """
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

        self.commit_cnt = 0
        if os.path.exists(out_dir) and len(os.listdir(out_dir)) > 0:
            self.commit_cnt = max(map(lambda x: int(x.split("_")[1].split(".")[0]), os.listdir(out_dir))) + 1

        self.data = []

    def add_data(self, data):
        self.data.append(data)

    def commit(self, archive_name=None):
        cctx = zstandard.ZstdCompressor(level=3)

        if archive_name is None:
            archive_name = str(int(time.time()))

        res = b"".join(
            map(lambda x: ("%016d" % len(x)).encode("UTF-8") + x, map(lambda x: x.encode("UTF-8"), self.data))
        )
        cdata = cctx.compress(res)

        with open(self.out_dir + "/data_" + str(self.commit_cnt) + "_" + archive_name + ".dat.zst", "wb") as fh:
            fh.write(cdata)

        self.commit_cnt += 1
        self.data = []


class JSONArchive:
    def __init__(self, out_dir: str):
        """
        Archive for save lm data. Save as `.json.zst`

        Args:
            out_dir (str): Output directory path
        """
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

        self.commit_cnt = 0
        if os.path.exists(out_dir) and len(os.listdir(out_dir)) > 0:
            self.commit_cnt = max(map(lambda x: int(x.split("_")[1].split(".")[0]), os.listdir(out_dir))) + 1

        self.data = []

    def add_data(self, data):
        self.data.append(data)

    def commit(self):
        cctx = zstandard.ZstdCompressor(level=3)

        cdata = cctx.compress(json.dumps(self.data).encode("UTF-8"))
        with open(
            self.out_dir + "/data_" + str(self.commit_cnt) + "_" + str(int(time.time())) + ".json.zst", "wb"
        ) as fh:
            fh.write(cdata)

        self.commit_cnt += 1
        self.data = []
