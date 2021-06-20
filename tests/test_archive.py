import shutil

import ko_lm_dataformat as klmd

from .testing_utils import TMP_DIR_NAME, get_tests_dir, remove_tmp_dir


def test_archive_single_sentence():
    remove_tmp_dir()
    archive = klmd.Archive(TMP_DIR_NAME)
    with open(get_tests_dir(append_path="assets/kowiki_sample.txt"), "r", encoding="utf-8") as f:
        for line in f:
            archive.add_data(line.strip())
    shutil.rmtree(TMP_DIR_NAME)


# TODO how to install kss in github workflows
# def test_archive_kss_sent_split():
#     remove_tmp_dir()
#     archive = klmd.Archive(TMP_DIR_NAME, sentence_splitter=klmd.KssSentenceSplitter(clean_sentence=False))
#     with open(get_tests_dir(append_path="assets/kowiki_sample.txt"), "r", encoding="utf-8") as f:
#         for line in f:
#             archive.add_data(line.strip(), split_sent=True)
#     shutil.rmtree(TMP_DIR_NAME)
