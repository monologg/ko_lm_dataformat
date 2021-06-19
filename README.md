# ko_lm_dataformat

- Utilities for storing data for Korean LM training
- Most of the code are from [lm_dataformat](https://github.com/leogao2/lm_dataformat)

## Basic Usage

To write:

```python
ar = Archive('output_dir')

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
rdr = Reader('input_dir_or_file')

for doc in rdr.stream_data():
  # do something with the document
```
