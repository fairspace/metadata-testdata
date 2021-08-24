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

Configure the connection settings using environment variables (either specify using the shell or create a file `.env`). 
Make sure that the user specified in the config has an `Admin`, `Add shared metadata` and `Query metadata` roles.
Example for a local development environment:
```shell
FAIRSPACE_URL=http://localhost:8080
KEYCLOAK_URL=http://localhost:5100
KEYCLOAK_REALM=fairspace
KEYCLOAK_CLIENT_ID=workspace-client
KEYCLOAK_CLIENT_SECRET=**********
KEYCLOAK_USERNAME=organisation-admin
KEYCLOAK_PASSWORD=fairspace123
```

Run the script:
```shell
upload_test_data
```
This uploads 1,000 subjects, 1,500 tumor pathology events,
3,000 samples and creates 5 collection, each containing 50
directories with 500 files.

These numbers can be changed using environment variables:
```shell
SUBJECT_COUNT=1000
EVENT_COUNT=1500
SAMPLE_COUNT=3000
COLLECTION_COUNT=5
DIRS_PER_COLLECTION=50
FILES_PER_DIR=500
```

Or run with different parameters:
```python
from metadata_scripts.upload_test_data import TestData
def testrun():
    testdata = TestData()
    testdata.subject_count = 100
    testdata.event_count = 200
    testdata.sample_count = 500
    testdata.collection_count = 5
    testdata.dirs_per_collection = 5
    testdata.files_per_dir = 10
    testdata.run()

testrun()
```

At the end of the script a recreation of the Fairspace view database will be triggered, based on the updated RDF database.
This can take up to 2 minutes for the default count parameters configuration.

## Run queries

The `retrieve_view` command retrieves the first page of samples by default,
use `retrieve_view Subject` to retrieve a page of subjects, etc.

The API for retrieving pages can be used directly to specify the page and
filters:
```python
from fairspace_api.api import FairspaceApi
import json
import time

api = FairspaceApi()

filters = [{'field': 'gender', 'values': ['male']}]
start = time.time()
try:
    count = api.count('samples', filters=filters)
    print(f'Took {time.time() - start:.0f}s.')
    print(count)
    start = time.time()
    page = api.retrieve_view_page('samples', page=1, size=2, filters=filters)
    print(f'Took {time.time() - start:.0f}s.')
    print(page)
except Exception as e:
    print('Error', e)


# Retrieve first 2 female subjects for which blood samples with ChIP-on-Chip analysis are available
page = api.retrieve_view_page('Sample', page=1, size=2, include_counts=True, filters=[
  {'field': 'Subject.gender', 'values': ['Female']},
  {'field': 'Sample.nature', 'values': ['Blood']},
  {'field': 'Collection.analysisType', 'values': ['ChIP-on-Chip']}
])
print(json.dumps(page.__dict__, indent=2))
```

SPARQL queries:
```python
from fairspace_api.api import FairspaceApi
api = FairspaceApi()
query = """
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX curie: <https://institut-curie.org/ontology#>
PREFIX fs:    <https://fairspace.nl/ontology#>

SELECT ?sample ?sampleTopography ?sampleNature ?sampleOrigin ?tumorCellularity ?event ?tumorTopography ?morphology ?eventType
    ?laterality ?tumorGradeType ?tumorGradeValue ?tnmType ?tnmT ?tnmN ?tnmM ?ageAtDiagnosis ?subject ?gender
    ?species ?ageAtLastNews ?ageAtDeath
WHERE {
    OPTIONAL {?sample curie:topography ?sampleTopography }
    OPTIONAL {?sample curie:isOfNature ?sampleNature }
    OPTIONAL {?sample curie:hasOrigin ?sampleOrigin }
    OPTIONAL {?sample curie:tumorCellularity ?tumorCellularity }
    
    ?sample curie:subject ?subject .
    OPTIONAL {?subject curie:isOfSpecies ?species}
    OPTIONAL {?subject curie:gender ?gender}
    OPTIONAL {?subject curie:ageAtLastNews ?ageAtLastNews}
    OPTIONAL {?subject curie:ageAtDeath ?ageAtDeath}

    OPTIONAL {
        ?sample curie:diagnosis ?event .
        
        OPTIONAL { ?event curie:tumorMorphology ?morphology }
        OPTIONAL { ?event curie:eventType ?eventType }
        OPTIONAL { ?event curie:topography ?tumorTopography }
        OPTIONAL { ?event curie:tumorLaterality ?laterality }
        OPTIONAL { ?event curie:ageAtDiagnosis ?ageAtDiagnosis }
        OPTIONAL { ?event curie:tumorGradeType ?tumorGradeType }
        OPTIONAL { ?event curie:tumorGradeValue ?tumorGradeValue }
        OPTIONAL { ?event curie:tnmType ?tnmType }
        OPTIONAL { ?event curie:tnmT ?tnmT }
        OPTIONAL { ?event curie:tnmN ?tnmN }
        OPTIONAL { ?event curie:tnmM ?tnmM }
    }

    ?sample a curie:BiologicalSample .
    FILTER NOT EXISTS { ?sample fs:dateDeleted ?anyDateDeleted }
}
LIMIT 10
"""
results = api.query_sparql(query)
sample_ids = [sample['sample']['value'] for sample in results['results']['bindings']]
print(len(sample_ids), 'samples,', len(set(sample_ids)), 'unique:', set(sample_ids))
```

## License

Copyright (c) 2021 The Hyve B.V.

This program is free software: you can redistribute it and/or modify it under the terms of the Apache 2.0 
License published by the Apache Software Foundation, either version 2.0 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the Apache 2.0 License for more details.

You should have received a copy of the Apache 2.0 License along with this program (see [LICENSE](LICENSE)). If not, see https://www.apache.org/licenses/LICENSE-2.0.txt.
