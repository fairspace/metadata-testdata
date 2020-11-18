# Testdata generator for metadata in Fairspace

## Dependencies

Requires Python 3.7 or newer.
Preferably run within a virtual environment:
```
python3 -m venv venv/
source venv/bin/activate
```
Install:
```
pip install .
```

## Testdata generation

Please check if the settings in [`upload_test_data.py`](metadata_scripts/upload_test_data.py) are adequate.
Do not forget to reinstall the package after any changes.

Run the script:
```
upload_test_data
```
This uploads 30,000 subjects, 60,000 tumor pathology events,
120,000 samples and creates 10, each containing 100
directories with 1,500 files.

Or run with different parameters:
```python
from metadata_scripts.upload_test_data import TestData
def testrun():
    testdata = TestData()
    testdata.subject_count = 10
    testdata.event_count = 20
    testdata.sample_count = 50
    testdata.collection_count = 2
    testdata.dirs_per_collection = 2
    testdata.files_per_dir = 10
    testdata.run()

testrun()
```

## Run queries

The `retrieve_view` command retrieves the first page of samples by default,
use `retrieve_view Subject` to retrieve a page of subjects, etc.

The API for retrieving pages can be used directly to specify the page and
filters:
```python
from fairspace_api.api import FairspaceApi
import json

api = FairspaceApi()

# Retrieve first 2 female subjects for which blood samples with ChIP-on-Chip analysis are available
page = api.retrieve_view_page('Sample', page=1, size=2, include_counts=True, filters=[
  {'field': 'Subject.gender', 'values': ['Female']},
  {'field': 'Sample.nature', 'values': ['Blood']},
  {'field': 'Collection.analysisType', 'values': ['ChIP-on-Chip']}
])
print(json.dumps(page.__dict__, indent=2))
```
