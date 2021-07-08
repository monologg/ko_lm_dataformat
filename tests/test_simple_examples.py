import hashlib
import shutil

import ko_lm_dataformat as kldf

from .testing_utils import TMP_DIR_NAME, get_tests_dir, remove_tmp_dir


def sha256str(s):
    h = hashlib.sha256()
    h.update(s)
    return h.hexdigest()


def test_dat():
    remove_tmp_dir()
    archive = kldf.DatArchive(TMP_DIR_NAME)
    blns = open(get_tests_dir(append_path="assets/blns.txt")).read()
    archive.add_data(blns)
    archive.add_data("testing 123")
    archive.add_data(blns)
    archive.add_data("testing 123456789")
    archive.commit()

    reader = kldf.Reader(TMP_DIR_NAME)

    data = list(reader.stream_data())

    assert data[0] == blns
    assert data[1] == "testing 123"
    assert data[2] == blns
    assert data[3] == "testing 123456789"
    shutil.rmtree(TMP_DIR_NAME)


def test_json():
    remove_tmp_dir()
    archive = kldf.JSONArchive(TMP_DIR_NAME)
    blns = open(get_tests_dir(append_path="assets/blns.txt")).read()
    archive.add_data(blns)
    archive.add_data("testing 123")
    archive.add_data(blns)
    archive.add_data("testing 123456789")
    archive.commit()

    reader = kldf.Reader(TMP_DIR_NAME)

    data = list(reader.stream_data())

    assert data[0] == blns
    assert data[1] == "testing 123"
    assert data[2] == blns
    assert data[3] == "testing 123456789"
    shutil.rmtree(TMP_DIR_NAME)


def test_jsonl():
    remove_tmp_dir()
    archive = kldf.Archive(TMP_DIR_NAME)
    blns = open(get_tests_dir(append_path="assets/blns.txt")).read()
    archive.add_data(blns)
    archive.add_data("testing 123", meta={"testing": 123})
    archive.add_data(blns, meta={"testing2": 456, "testing": ["a", "b"]})
    archive.add_data("testing 123456789")
    archive.commit()

    reader = kldf.Reader(TMP_DIR_NAME)

    data = list(reader.stream_data(get_meta=True))

    assert data[0] == (blns, {})
    assert data[1] == ("testing 123", {"testing": 123})
    assert data[2] == (blns, {"testing2": 456, "testing": ["a", "b"]})
    assert data[3] == ("testing 123456789", {})
    shutil.rmtree(TMP_DIR_NAME)


def test_naughty_string():
    remove_tmp_dir()
    archive = kldf.Archive(TMP_DIR_NAME)
    naughty_text = "  Today a::: : \t\t \x00I \x00a  朝 三暮四 [MASK] m \na fool \n\nbecause I am a fool. \n [SEP][CLS]  "
    archive.add_data(naughty_text, clean_sent=True)
    archive.commit()

    reader = kldf.Reader(TMP_DIR_NAME)

    data = list(reader.stream_data())
    assert data[0] == "Today a::: : I a 朝 三暮四 [MASK] m a fool because I am a fool. [SEP][CLS]"


def test_jsonl_sentences():
    remove_tmp_dir()
    archive = kldf.Archive(TMP_DIR_NAME)
    blns = open(get_tests_dir(append_path="assets/blns.txt")).read()
    archive.add_data(blns)
    archive.add_data(["testing 123", "testing 345"], meta={"testing": 123})
    archive.add_data(blns, meta={"testing2": 456, "testing": ["a", "b"]})
    archive.add_data("testing 123456789")
    archive.commit()

    reader = kldf.Reader(TMP_DIR_NAME)

    data = list(reader.stream_data(get_meta=True, autojoin_sentences=True, sent_joiner="\n"))

    assert data[0] == (blns, {})
    assert data[1] == ("testing 123\ntesting 345", {"testing": 123})
    assert data[2] == (blns, {"testing2": 456, "testing": ["a", "b"]})
    assert data[3] == ("testing 123456789", {})
    shutil.rmtree(TMP_DIR_NAME)


def test_jsonl_tar():
    blns = open(get_tests_dir(append_path="assets/blns.txt")).read()
    reader = kldf.Reader(get_tests_dir(append_path="assets/blns.jsonl.zst.tar"))

    data = list(reader.stream_data(get_meta=True, autojoin_sentences=True, sent_joiner="\n"))

    assert data[0] == (blns, {})
    assert data[1] == ("testing 123\ntesting 345", {"testing": 123})
    assert data[2] == (blns, {"testing2": 456, "testing": ["a", "b"]})
    assert data[3] == ("testing 123456789", {})

    assert data[4] == (blns, {})
    assert data[5] == ("testing 123\ntesting 345", {"testing": 123})
    assert data[6] == (blns, {"testing2": 456, "testing": ["a", "b"]})
    assert data[7] == ("testing 123456789", {})


def test_txt_read():
    reader = kldf.Reader(get_tests_dir(append_path="assets/blns.txt"))
    blns = open(get_tests_dir(append_path="assets/blns.txt")).read()

    data = list(reader.stream_data(get_meta=False))

    assert data[0] == blns
    assert len(data) == 1


def test_zip_read():
    reader = kldf.Reader(get_tests_dir(append_path="assets/blns.txt.zip"))
    blns = open(get_tests_dir(append_path="assets/blns.txt")).read()

    data = list(reader.stream_data(get_meta=False))

    assert data[0] == blns
    assert len(data) == 1


def test_tgz_read():
    reader = kldf.Reader(get_tests_dir(append_path="assets/blns.txt.tar.gz"))
    blns = open(get_tests_dir(append_path="assets/blns.txt")).read()

    data = list(reader.stream_data(get_meta=False))

    assert data[0] == blns
    assert len(data) == 1


def test_tarfile_reader():
    rdr = kldf.tarfile_reader(open(get_tests_dir(append_path="assets/testtarfile.tar"), "rb"), streaming=True)

    hashes = map(lambda doc: sha256str(doc.read()), rdr)

    expected = [
        "782588d891b1a836fcbd0bcd43227f83bf066d90245dd91d061f1b2c0e72fc9d",
        "dc666c65cd421c688ed8542223c24d9e4a2e5276944f1e7cc296d43a57245498",
        "c38af4ad8a9b901ea75d7cf60d452a233949f9e88b5fea04f80acde29d513d3e",
        "fb3ecc0ad0b851dd3e9f0955805530b4946080f6e2a8e6aa0f67ba8209c2f779",
    ]

    assert all(map(lambda x: x[0] == x[1], zip(hashes, expected)))
