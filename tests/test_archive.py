import json
import shutil

import pytest

import ko_lm_dataformat as kldf

from .testing_utils import TMP_DIR_NAME, get_tests_dir, remove_tmp_dir


def test_kowiki_archive():
    remove_tmp_dir()
    archive = kldf.Archive(TMP_DIR_NAME)
    with open(get_tests_dir(append_path="assets/kowiki_sample.txt"), "r", encoding="utf-8") as f:
        for line in f:
            archive.add_data(line.strip())

    # close the archive's file handles to avoid Windows permission issues
    archive.compressor.close()
    archive.fh.close()

    shutil.rmtree(TMP_DIR_NAME)


def test_archive_json_data():
    remove_tmp_dir()
    archive = kldf.Archive(TMP_DIR_NAME)
    with open(get_tests_dir(append_path="assets/sample.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    archive.add_data(data)

    # close the archive's file handles to avoid Windows permission issues
    archive.compressor.close()
    archive.fh.close()

    shutil.rmtree(TMP_DIR_NAME)


def test_archive_json_data_is_same():
    remove_tmp_dir()
    archive = kldf.Archive(TMP_DIR_NAME)
    with open(get_tests_dir(append_path="assets/sample.json"), "r", encoding="utf-8") as f:
        orig_data = json.load(f)
    archive.add_data(orig_data)
    archive.commit()

    # Close the archive's file handles to avoid Windows permission issues
    archive.compressor.close()
    archive.fh.close()

    reader = kldf.Reader(TMP_DIR_NAME)
    kldf_data = list(reader.stream_data())
    assert kldf_data[0] == orig_data


def test_kor_str_is_same():
    remove_tmp_dir()
    archive = kldf.Archive(TMP_DIR_NAME)
    with open(get_tests_dir(append_path="assets/kowiki_sample.txt"), "r", encoding="utf-8") as f:
        text = f.read()
    archive.add_data(text)
    archive.commit()

    # Close the archive's file handles to avoid Windows permission issues
    archive.compressor.close()
    archive.fh.close()

    reader = kldf.Reader(TMP_DIR_NAME)
    data = list(reader.stream_data())
    assert data[0] == text


@pytest.mark.skip("Kss install makes error on github actions")
def test_archive_kss_sent_split():
    remove_tmp_dir()
    archive = kldf.Archive(TMP_DIR_NAME, sentence_splitter=kldf.KssV1SentenceSplitter())
    with open(get_tests_dir(append_path="assets/kowiki_sample.txt"), "r", encoding="utf-8") as f:
        for line in f:
            archive.add_data(line.strip(), split_sent=True, clean_sent=False)

    # Close the archive's file handles to avoid Windows permission issues
    archive.compressor.close()
    archive.fh.close()

    shutil.rmtree(TMP_DIR_NAME)
