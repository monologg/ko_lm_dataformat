# ko_lm_dataformat

- Utilities for storing data for Korean PLM.
- Code is based on [lm_dataformat](https://github.com/leogao2/lm_dataformat).

## What have been changed

### 기능 추가

- Sentence splitter
  - `kss v1.3.1`

### 로직 변경

- 기존과 달리 `json`의 `"text"` 는 무조건 하나의 document만 받음.
  - `str` 이 아닌 `List[str]` 로 들어오게 되면 기존에는 각 str이 document였으나, 여기서는 sentence로 취급.
  - 기존에는 여러 document를 `\n\n`으로 join 하였지만, `ko_lm_dataformat` 에서는 해당 로직을 없앰.

## Basic Usage

To write:

```python
import ko_lm_dataformat as kldf

ar = kldf.Archive('output_dir')

for x in something():
  # do other stuff
  ar.add_data(somedocument, meta={
    'example': stuff,
    'someothermetadata': [othermetadata, otherrandomstuff],
    'otherotherstuff': True
  })

# remember to commit at the end!
ar.commit()
```

To read:

```python
import ko_lm_dataformat as kldf

rdr = kldf.Reader('input_dir_or_file')

for doc in rdr.stream_data(get_meta=False):
  # do something with the document
```
