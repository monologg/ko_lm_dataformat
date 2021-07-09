import shutil

import ko_lm_dataformat as kldf

from .testing_utils import TMP_DIR_NAME, get_tests_dir, remove_tmp_dir


def test_kowiki_archive():
    remove_tmp_dir()
    archive = kldf.Archive(TMP_DIR_NAME)
    with open(get_tests_dir(append_path="assets/kowiki_sample.txt"), "r", encoding="utf-8") as f:
        for line in f:
            archive.add_data(line.strip())
    shutil.rmtree(TMP_DIR_NAME)


def test_kor_str_is_same():
    remove_tmp_dir()
    archive = kldf.Archive(TMP_DIR_NAME)
    text = open(get_tests_dir(append_path="assets/kowiki_sample.txt"), "r", encoding="utf-8").read()
    archive.add_data(text)
    archive.commit()

    reader = kldf.Reader(TMP_DIR_NAME)
    data = list(reader.stream_data())
    assert data[0] == text


# TODO how to install kss in github workflows
def test_archive_kss_sent_split():
    remove_tmp_dir()
    archive = kldf.Archive(TMP_DIR_NAME, sentence_splitter=kldf.KssV1SentenceSplitter())
    with open(get_tests_dir(append_path="assets/kowiki_sample.txt"), "r", encoding="utf-8") as f:
        for line in f:
            archive.add_data(line.strip(), split_sent=True, clean_sent=False)
    shutil.rmtree(TMP_DIR_NAME)
