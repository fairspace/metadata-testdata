#!/usr/bin/env python3
import logging
import time

from fairspace_api.api import FairspaceApi

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger('sparql')


def sparql_query():
    api = FairspaceApi()

    # Query for samples
    queries = {

        'First 500 samples': {
            'query': """
    PREFIX curie: <https://institut-curie.org/ontology#>
    PREFIX fs:    <https://fairspace.nl/ontology#>

    SELECT DISTINCT ?sample
    WHERE {
      ?sample a curie:BiologicalSample .
      FILTER NOT EXISTS { ?sample fs:dateDeleted ?anyDateDeleted }
    }
    # ORDER BY ?sample
    LIMIT 500
    """,
            'aggregate': False
        },

        'Count all samples': {
            'query': """
    PREFIX curie: <https://institut-curie.org/ontology#>
    PREFIX fs:    <https://fairspace.nl/ontology#>

    SELECT COUNT(DISTINCT ?sample)
    WHERE {
      ?sample a curie:BiologicalSample .
      FILTER NOT EXISTS { ?sample fs:dateDeleted ?anyDateDeleted }
    }
    """,
            'aggregate': True
        },

        'Select samples by nature, gender and event type': {
            'query': """
    PREFIX curie:  <https://institut-curie.org/ontology#>
    PREFIX fs:     <https://fairspace.nl/ontology#>
    PREFIX ncit:   <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    PREFIX gender: <http://hl7.org/fhir/administrative-gender#>

    SELECT DISTINCT ?sample
    WHERE {
      ?sample a curie:BiologicalSample .
      ?sample curie:isOfNature ncit:C812 .
      ?sample curie:subject ?subject .
      ?subject curie:isOfGender gender:male .
      ?sample curie:diagnosis ?event .
      ?event curie:eventType ncit:C3262
      FILTER NOT EXISTS { ?sample fs:dateDeleted ?anyDateDeleted }
    }
    # ORDER BY ?sample
    LIMIT 500
    """,
            'aggregate': False
        },

        'Count samples by nature, gender and event type': {
            'query': """
    PREFIX curie:  <https://institut-curie.org/ontology#>
    PREFIX fs:     <https://fairspace.nl/ontology#>
    PREFIX ncit:   <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    PREFIX gender: <http://hl7.org/fhir/administrative-gender#>

    SELECT COUNT(DISTINCT ?sample)
    WHERE {
      ?sample a curie:BiologicalSample .
      ?sample curie:isOfNature ncit:C812 .
      ?sample curie:subject ?subject .
      ?subject curie:isOfGender gender:male .
      ?sample curie:diagnosis ?event .
      ?event curie:eventType ncit:C3262
      FILTER NOT EXISTS { ?sample fs:dateDeleted ?anyDateDeleted }
    }
    """,
            'aggregate': True
        },

        'First 500 samples by nature': {
            'query': """
    PREFIX curie: <https://institut-curie.org/ontology#>
    PREFIX fs:    <https://fairspace.nl/ontology#>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>

    SELECT DISTINCT ?sample
    WHERE {
      ?sample a curie:BiologicalSample .
      ?sample curie:isOfNature ncit:C812 .
      FILTER NOT EXISTS { ?sample fs:dateDeleted ?anyDateDeleted }
    }
    # ORDER BY ?sample
    LIMIT 500
    """,
            'aggregate': False
        },

        'Count samples by nature': {
            'query': """
    PREFIX curie: <https://institut-curie.org/ontology#>
    PREFIX fs:    <https://fairspace.nl/ontology#>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>

    SELECT COUNT(DISTINCT ?sample)
    WHERE {
      ?sample a curie:BiologicalSample .
      ?sample curie:isOfNature ncit:C812 .
      FILTER NOT EXISTS { ?sample fs:dateDeleted ?anyDateDeleted }
    }
    """,
            'aggregate': True
        },

        'First 500 samples by nature and cellularity': {
            'query': """
    PREFIX curie: <https://institut-curie.org/ontology#>
    PREFIX fs:    <https://fairspace.nl/ontology#>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>

    SELECT DISTINCT ?sample
    WHERE {
      ?sample a curie:BiologicalSample .
      ?sample curie:isOfNature ncit:C812 .
      ?sample curie:tumorCellularity ?cellularity .
      FILTER (?cellularity > 20 && ?cellularity < 90)
      FILTER NOT EXISTS { ?sample fs:dateDeleted ?anyDateDeleted }
    }
    # ORDER BY ?sample
    LIMIT 500
    """,
            'aggregate': False
        },

        'Count samples by nature and cellularity': {
            'query': """
    PREFIX curie: <https://institut-curie.org/ontology#>
    PREFIX fs:    <https://fairspace.nl/ontology#>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>

    SELECT COUNT(DISTINCT ?sample)
    WHERE {
      ?sample a curie:BiologicalSample .
      ?sample curie:isOfNature ncit:C812 .
      ?sample curie:tumorCellularity ?cellularity .
      FILTER (?cellularity > 20 && ?cellularity < 90)
      FILTER NOT EXISTS { ?sample fs:dateDeleted ?anyDateDeleted }
    }
    """,
            'aggregate': True
        },

        'First 500 samples by nature, event type and analysis type': {
            'query': """
    PREFIX curie: <https://institut-curie.org/ontology#>
    PREFIX fs:    <https://fairspace.nl/ontology#>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    PREFIX analysis: <https://institut-curie.org/analysis#>

    SELECT DISTINCT ?sample
    WHERE {
      ?sample a curie:BiologicalSample .
      ?sample curie:isOfNature ncit:C812 .
      ?sample curie:diagnosis ?event .
      ?event curie:eventType ncit:C3262 .
      ?location curie:sample ?sample .
      ?location curie:analysisType analysis:O6-12 .
      FILTER NOT EXISTS { ?sample fs:dateDeleted ?anyDateDeleted }
      FILTER NOT EXISTS { ?location fs:dateDeleted ?anyDateDeleted }
    }
    # ORDER BY ?sample
    LIMIT 500
    """,
            'aggregate': False
        },

        'Count samples by nature, event type and analysis type': {
            'query': """
    PREFIX curie: <https://institut-curie.org/ontology#>
    PREFIX fs:    <https://fairspace.nl/ontology#>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>
    PREFIX analysis: <https://institut-curie.org/analysis#>

    SELECT COUNT(DISTINCT ?sample)
    WHERE {
      ?sample a curie:BiologicalSample .
      ?sample curie:isOfNature ncit:C812 .
      ?sample curie:diagnosis ?event .
      ?event curie:eventType ncit:C3262 .
      ?location curie:sample ?sample .
      ?location curie:analysisType analysis:O6-12 .
      FILTER NOT EXISTS { ?sample fs:dateDeleted ?anyDateDeleted }
      FILTER NOT EXISTS { ?location fs:dateDeleted ?anyDateDeleted }
    }
    """,
            'aggregate': True
        },

        'First 500 files': {
            'query': """
    PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX fs:    <https://fairspace.nl/ontology#>

    SELECT DISTINCT ?location
    WHERE {
      ?location a fs:File .
      FILTER NOT EXISTS { ?location fs:dateDeleted ?anyDateDeleted }
    }
    # ORDER BY ?location
    LIMIT 500
    """,
            'aggregate': False,
            'skip': False
        },

        'Count files': {
            'query': """
    PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dcat:  <http://www.w3.org/ns/dcat#>
    PREFIX fs:    <https://fairspace.nl/ontology#>

    SELECT count(DISTINCT ?location)
    WHERE {
      ?location a fs:File .
      FILTER NOT EXISTS { ?location fs:dateDeleted ?anyDateDeleted }
    }
    """,
            'aggregate': True,
            'skip': False
        },

        'First 500 files with path prefix (STRSTARTS)': {
            'query': """
    PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX fs:    <https://fairspace.nl/ontology#>

    SELECT DISTINCT ?location
    WHERE {
      ?location a fs:File .
      FILTER ( STRSTARTS(STR(?location), 'http://localhost:8080/api/webdav/collection%202020-11-16-2') )
      FILTER NOT EXISTS { ?location fs:dateDeleted ?anyDateDeleted }
    }
    # ORDER BY ?location
    LIMIT 500
    """,
            'aggregate': False,
            'skip': False
        },

        'Count files with path prefix (STRSTARTS)': {
            'query': """
    PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX fs:    <https://fairspace.nl/ontology#>

    SELECT COUNT(DISTINCT ?location)
    WHERE {
      ?location a fs:File .
      FILTER ( STRSTARTS(STR(?location), 'http://localhost:8080/api/webdav/collection%202020-11-16-2') )
      FILTER NOT EXISTS { ?location fs:dateDeleted ?anyDateDeleted }
    }
    """,
            'aggregate': True,
            'skip': False
        },

        'First 500 files with path prefix (belongsTo)': {
            'query': """
    PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX fs:    <https://fairspace.nl/ontology#>

    SELECT DISTINCT ?location
    WHERE {
      ?location a fs:File .
      ?location fs:belongsTo* <http://localhost:8080/api/webdav/collection%202020-11-16-2> .
      FILTER NOT EXISTS { ?location fs:dateDeleted ?anyDateDeleted }
    }
    # ORDER BY ?location
    LIMIT 500
    """,
            'aggregate': False,
            'skip': False
        },

        'Count files with path prefix (belongsTo)': {
            'query': """
    PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dcat:  <http://www.w3.org/ns/dcat#>
    PREFIX fs:    <https://fairspace.nl/ontology#>

    SELECT count(DISTINCT ?location)
    WHERE {
      ?location a fs:File .
      ?location fs:belongsTo* <http://localhost:8080/api/webdav/collection%202020-11-16-2> .
      FILTER NOT EXISTS { ?location fs:dateDeleted ?anyDateDeleted }
    }
    """,
            'aggregate': True,
            'skip': False
        },

        'Files filtered by sample nature, analysis type': {
            'query': """
    PREFIX fs:    <https://fairspace.nl/ontology#>
    PREFIX curie: <https://institut-curie.org/ontology#>
    PREFIX analysis: <https://institut-curie.org/analysis#>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>

    SELECT DISTINCT ?location
    WHERE {
      ?location a fs:File .
      ?location curie:sample ?sample .
      ?sample curie:isOfNature ncit:C812 .
      ?location curie:analysisType analysis:O6-12 .
      FILTER NOT EXISTS { ?location fs:dateDeleted ?anyDateDeleted }
    }
    # ORDER BY ?location
    LIMIT 500
    """,
            'aggregate': False
        },

        'Count files filtered by sample nature, analysis type': {
            'query': """
    PREFIX fs:    <https://fairspace.nl/ontology#>
    PREFIX curie: <https://institut-curie.org/ontology#>
    PREFIX analysis: <https://institut-curie.org/analysis#>
    PREFIX ncit: <http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#>

    SELECT count(DISTINCT ?location)
    WHERE {
      ?location a fs:File .
      ?location curie:sample ?sample .
      ?sample curie:isOfNature ncit:C812 .
      ?location curie:analysisType analysis:O6-12 .
      FILTER NOT EXISTS { ?location fs:dateDeleted ?anyDateDeleted }
    }
    """,
            'aggregate': True
        },

        'Files filtered by keyword': {
            'query': """
    PREFIX fs:    <https://fairspace.nl/ontology#>
    PREFIX dcat:  <http://www.w3.org/ns/dcat#>

    SELECT DISTINCT ?location
    WHERE {
      ?location a fs:File .
      ?location dcat:keyword 'philosophy' .
      FILTER NOT EXISTS { ?location fs:dateDeleted ?anyDateDeleted }
    }
    # ORDER BY ?location
    LIMIT 500
    """,
            'aggregate': False
        },

        'Count files filtered by keyword': {
            'query': """
    PREFIX fs:    <https://fairspace.nl/ontology#>
    PREFIX dcat:  <http://www.w3.org/ns/dcat#>

    SELECT COUNT (DISTINCT ?location)
    WHERE {
      ?location a fs:File .
      ?location dcat:keyword 'philosophy' .
      FILTER NOT EXISTS { ?location fs:dateDeleted ?anyDateDeleted }
    }
    """,
            'aggregate': True
        },

        'Count files linked to samples': {
            'query': """
    PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dcat:  <http://www.w3.org/ns/dcat#>
    PREFIX fs:    <https://fairspace.nl/ontology#>
    PREFIX curie: <https://institut-curie.org/ontology#>

    SELECT count(DISTINCT ?location)
    WHERE {
      ?sample a curie:BiologicalSample .
      ?location curie:aboutMaterial ?sample .
      ?sample curie:tumorCellularity ?tumorCellularity .
      ?location a fs:File .
      FILTER (?tumorCellularity = 60)
      FILTER NOT EXISTS { ?location fs:dateDeleted ?anyDateDeleted }
    }
    """,
            'aggregate': True
        },

        'Sample topographies': {
            'query': """
    PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX curie: <https://institut-curie.org/ontology#>

    SELECT ?topography ?label
    WHERE {
      ?topography a curie:Topography .
      ?topography rdfs:label ?label
    }
    """,
            'aggregate': False
        }
    }

    for name, contents in queries.items():
        print(name)
        if 'skip' in contents and contents['skip']:
            print('(Skipped)\n')
            continue
        api.init_session()
        start = time.time()
        results = api.query_sparql(contents['query'])
        duration = time.time() - start
        print(f'{int(duration * 1000)}ms')
        if contents['aggregate']:
            print(results['results']['bindings'])
        else:
            print(len(results['results']['bindings']))
        print()


def main():
    sparql_query()


if __name__ == '__main__':
    main()
