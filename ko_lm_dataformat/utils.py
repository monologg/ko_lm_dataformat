import datetime
import mmap
import os
import sys
from functools import reduce
from math import ceil

# The package importlib_metadata is in a different place, depending on the python version.
if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata


def listdir_or_file(x):
    if isinstance(x, list):
        return reduce(lambda x, y: x + y, map(listdir_or_file, sorted(x)))
    return [x] if os.path.isfile(x) else [x + "/" + fn for fn in sorted(os.listdir(x))]


def tarfile_reader(file, streaming=False):
    # we need our own tarfile parser because `tarfile` doesn't work well for
    # big tarfiles; it seems to be reading the entire file to get a list of
    # where all the files are - but we don't need that because we just need
    # to see each file once. surprisingly, `tarfile` doesn't expose any
    # facilities for this. the only options are 1. load the entire tarfile
    # and then query by filename or 2. extract to disk - and neither of
    # these is what we want.

    offset = 0
    paxfilesize = None
    while True:
        hdr = file.read(512)
        offset += 512

        # https://www.gnu.org/software/tar/manual/html_node/Standard.html
        # end at 135 not 136 because of \0 terminator
        if hdr[124:135] == b"\0" * 11:
            # end of record
            break

        # fname = hdr[:100].split(b"\0")[0]

        # if the file is too big to fit in the size field, tarfiles will actually
        # include a PaxHeader with the size in it, applicable to the immediate next file.
        if paxfilesize is not None:
            size = paxfilesize
            paxfilesize = None
        else:
            size = int(hdr[124:135], 8)

        padded_size = ceil(size / 512) * 512

        # for handling PaxHeader files (which contain extra metadata about file size) and directories
        # https://pubs.opengroup.org/onlinepubs/9699919799/utilities/pax.html#tag_20_92_13_03
        type = chr(hdr[156])

        if type == "x":
            meta = file.read(padded_size)[:size]

            def kv(x):
                return x.decode("utf-8").split(" ")[1].split("=")

            paxfileattrs = {kv(x)[0]: kv(x)[1] for x in meta.split(b"\n") if x}
            paxfilesize = int(paxfileattrs["size"])

            offset += padded_size
            continue
        elif type != "0" and type != "\0":
            if streaming:
                file.seek(padded_size, os.SEEK_CUR)
            else:
                file.read(padded_size)
            offset += padded_size
            continue

        if streaming:
            # skip directory entries
            if size != 0:
                mmo = mmap.mmap(file.fileno(), length=offset + size, access=mmap.ACCESS_READ)
                mmo.seek(offset)
                yield mmo

            file.seek(padded_size, os.SEEK_CUR)
        else:
            yield file.read(padded_size)[:size]
        offset += padded_size


def handle_jsonl(
    jsonl_reader, get_meta: bool = False, autojoin_sentences: bool = False, sent_joiner: str = " ", key: str = "text"
):
    for ob in jsonl_reader:
        text = ob[key]

        # if data is List[str], concatenate multiple sentence.
        if autojoin_sentences and isinstance(text, list):
            text = sent_joiner.join(text)

        if get_meta:
            yield text, (ob["meta"] if "meta" in ob else {})
        else:
            yield text


def get_version():
    version_txt = os.path.join(os.path.dirname(__file__), "version.txt")
    with open(version_txt) as f:
        return f.read().strip()


def get_datetime_timestamp():
    """Get current datetime timestamp, based on Korea Timezone"""
    KST = datetime.timezone(datetime.timedelta(hours=9))
    return datetime.datetime.now(tz=KST).strftime("%Y%m%d%H%M%S")[2:]
