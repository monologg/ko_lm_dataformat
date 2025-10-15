# ko_lm_dataformat

[![PyPI](https://img.shields.io/pypi/v/ko_lm_dataformat)](https://pypi.org/project/ko_lm_dataformat/)
[![License](https://img.shields.io/github/license/monologg/ko_lm_dataformat)](https://github.com/monologg/ko_lm_dataformat/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

- **한국어 언어모델용 학습 데이터를 저장, 로딩**하기 위한 유틸리티

  - [`zstandard`](https://github.com/facebook/zstd), [`ultrajson`](https://github.com/ultrajson/ultrajson) 을 사용하여 **데이터 로딩, 압축 속도 개선**
  - 문서에 대한 **메타 데이터**도 함께 저장

- 코드는 EleutherAI에서 사용하는 [lm_dataformat](https://github.com/leogao2/lm_dataformat)를 참고하여 제작
  - 일부 버그 수정
  - 한국어에 맞게 기능 추가 및 수정 (sentence splitter, text cleaner)

## Installation

0.3.1 이후의 버전은 Python 3.9 이상을 지원합니다.

```bash
pip3 install ko_lm_dataformat
```

## Usage

### 1. Write Data

#### 1.1. Archive

- [kss v1 sentence splitter](https://github.com/likejazz/korean-sentence-splitter) 사용 가능

```python
import ko_lm_dataformat as kldf

ar = kldf.Archive("output_dir")
ar = kldf.Archive("output_dir", sentence_splitter=kldf.KssV1SentenceSplitter()) # Use sentence splitter
```

#### 1.2. Adding data

- `meta` 데이터를 추가할 수 있음 (e.g. 제목, url)
- 하나의 document가 들어온다고 가정 (`str` 이 아닌 `List[str]` 로 들어오게 되면 여러 개의 sentence가 들어오는 걸로 취급)
- `split_sent=True`이면 **document를 여러 개의 문장으로 분리**하여 `List[str]` 으로 저장
- `clean_sent=True`이면 **NFC Normalize**, **control char 제거**, **whitespace cleanup** 적용

```python
for doc in doc_lst:
    ar.add_data(
        data=doc,
        meta={
          "source": "kowiki",
          "meta_key_1": [othermetadata, otherrandomstuff],
          "meta_key_2": True
        },
        split_sent=False,
        clean_sent=False,
    )

# remember to commit at the end!
ar.commit()
```

### 2. Read Data

- `rdr.stream_data(get_meta=True)`로 할 시 `(doc, meta)` 의 튜플 형태로 반환

```python
import ko_lm_dataformat as kldf

rdr = kldf.Reader("output_dir")

for data in rdr.stream_data(get_meta=False):
  print(data)
  # "간단하게 설명하면, 언어를 통해 인간의 삶을 미적(美的)으로 형상화한 것이라고 볼...."


for data in rdr.stream_data(get_meta=True):
  print(data)
  # ("간단하게 설명하면, 언어를 통해 인간의 삶을 미적(美的)으로 형상화한 것이라고 볼....", {"source": "kowiki", ...})
```
