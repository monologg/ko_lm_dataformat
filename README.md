# ko_lm_dataformat

- Utilities for storing data for Korean PLM.
- Code is based on [lm_dataformat](https://github.com/leogao2/lm_dataformat).

## Additional Features for Korean Text

- Add sentence splitter

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
