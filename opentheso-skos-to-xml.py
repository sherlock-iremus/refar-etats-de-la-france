import json
from rdflib import RDF, SKOS
import sys
import xml.etree.ElementTree as ET

####################################################################################################
# SKOS DATA EXTRACTION
####################################################################################################

with open("skos.json", "r", encoding="utf-8") as f:
    data = json.load(f)

tree = {}

# DONE
# http://www.w3.org/1999/02/22-rdf-syntax-ns#type
# http://www.w3.org/2004/02/skos/core#broader
# http://www.w3.org/2004/02/skos/core#narrower
# http://www.w3.org/2004/02/skos/core#altLabel
# http://www.w3.org/2004/02/skos/core#historyNote
# http://www.w3.org/2004/02/skos/core#note
# http://www.w3.org/2004/02/skos/core#prefLabel
# http://www.w3.org/2004/02/skos/core#scopeNote

# NO
# http://purl.org/dc/terms/contributor
# http://purl.org/dc/terms/created
# http://purl.org/dc/terms/creator
# http://purl.org/dc/terms/identifier
# http://purl.org/dc/terms/language
# http://purl.org/dc/terms/modified
# http://purl.org/iso25964/skos-thes#narrowerGeneric
# http://purl.org/dc/terms/title
# http://purl.org/iso25964/skos-thes#broaderGeneric
# http://purl.org/iso25964/skos-thes#microThesaurusOf
# http://purl.org/umu/uneskos#memberOf
# http://www.w3.org/2004/02/skos/core#hasTopConcept
# http://www.w3.org/2004/02/skos/core#inScheme
# http://www.w3.org/2004/02/skos/core#member
# http://www.w3.org/2004/02/skos/core#topConceptOf

# TODO
# http://www.w3.org/2004/02/skos/core#exactMatch

THESAURUS_URI = 'https://opentheso.huma-num.fr/?idt=refar-institutions-corporations'
parents_to_children = {THESAURUS_URI: []}
children_to_parents = {}
metadata = {}

for uri, x in data.items():

    if x[str(RDF.type)][0]['value'] != str(SKOS.Concept):
        continue

    if uri not in metadata:
        metadata[uri] = {}

    # SKOS:NARROWER
    if str(SKOS.narrower) in x:
        if uri not in parents_to_children:
            parents_to_children[uri] = []
            for narrower in x[str(SKOS.narrower)]:
                parents_to_children[uri].append(narrower['value'])
                metadata[uri]['id'] = x['http://purl.org/dc/terms/identifier'][0]['value']

    # SKOS:BROADER
    if str(SKOS.broader) in x:
        if uri not in children_to_parents:
            children_to_parents[uri] = []
            for broader in x[str(SKOS.broader)]:
                children_to_parents[uri].append(broader['value'])
    else:
        parents_to_children[THESAURUS_URI].append(uri)

    # SKOS:
    for predicate in ['altLabel', 'historyNote', 'note', 'prefLabel', 'scopeNote',]:
        if str(SKOS[predicate]) in x:
            for o in x[str(SKOS[predicate])]:
                metadata[uri][predicate] = o['value'].strip()

####################################################################################################
# XML GENERATION
####################################################################################################


def crawl(parent_element, parent_uri):
    for child_uri in parents_to_children[uri]:
        child_element = ET.SubElement(parent_element, "section")
        child_element.set("id", 'REFAR-' + metadata[child_uri]['id'])


root = ET.Element("root")
crawl(root, THESAURUS_URI)

tree = ET.ElementTree(root)
tree.write("etats-de-la-france.xml", encoding="utf-8", xml_declaration=True)

xml_bytes = ET.tostring(root, encoding="utf-8")
xml_str = xml_bytes.decode("utf-8")
dtd = '<!DOCTYPE root SYSTEM "etats-de-la-france.dtd">\n'
xml_with_dtd = '<?xml version="1.0" encoding="utf-8"?>\n' + dtd + xml_str
with open("etats-de-la-france.xml", "w", encoding="utf-8") as f:
    f.write(xml_with_dtd)
