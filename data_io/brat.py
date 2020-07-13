from NLPDatasetIO.document import Document, Entity
from typing import List
from NLPDatasetIO.data_io.utils import find_offset, read_file
from glob import glob
import os
import re

BRAT_FORMAT = r'(?P<entity_id>^T[0-9]+)\t(?P<type>[a-zA-Z\_]+) (?P<positions>[0-9; ]+)\t(?P<text>.*)'
#N1      Reference T1 GeneOntology:900   CCNG1
ANNOTATION = r'(?P<id>^N[0-9]+)\tReference (?P<entity_id>T[0-9]+) (?P<ontology_name>[a-zA-Z\_\:0-9]+)\t(?P<concept_id>.*)'


class AnnFilesIterator(object):

    def __init__(self, directory):
        self.directory = directory
        txt_files_pattern = os.path.join(directory, '*.txt')
        ann_files_pattern = os.path.join(directory, '*.ann')
        txt_files = [txt_file for txt_file in glob(txt_files_pattern)]
        ann_files = [ann_file for ann_file in glob(ann_files_pattern)]
        self.txt_files = list(sorted(txt_files))
        self.ann_files = list(sorted(ann_files))

    def __iter__(self):
        return iter(zip(self.txt_files, self.ann_files))


def parse_annotation(annotation_raw):
    #print(annotation_raw)
    annotation = re.search(BRAT_FORMAT, annotation_raw).groupdict()
    positions = re.findall(r'\d+', annotation['positions'])
    positions = [int(pos) for pos in positions]
    annotation['start'] = min(positions)
    annotation['end'] = max(positions)
    return annotation


def parse_label_annotation(annotation_raw):
    annotation = re.search(ANNOTATION, annotation_raw).groupdict()
    return annotation['entity_id'], annotation['concept_id']


def extract_entities_from_brat(annotations_raw: str, text: str) -> List[Entity]:
    entities = []
    for annotation_raw in annotations_raw.split('\n'):
        if not annotation_raw.startswith('T'): continue
        try:
            annotation = parse_annotation(annotation_raw)
        except:
            continue
        start = annotation['start']
        end = annotation['end']
        entity_text = annotation['text']
        if text[start:end] != annotation['text']:
            start, end = find_offset(text, entity_text, start, end)
            entity_text = text[start:end]
        entities.append(Entity(entity_id=annotation['entity_id'],
                               text=entity_text,
                               start=start,
                               end=end,
                               type=annotation['type']))
    return entities


def extract_entity_labels(annotations_raw: str):
    entity_labels = {}
    for annotation_raw in annotations_raw.split('\n'):
        if not annotation_raw.startswith('N'): continue
        entity_id, concept_id = parse_label_annotation(annotation_raw)
        entity_labels[entity_id] = concept_id
    return entity_labels


def set_labels(entities, entity_labels):
    for entity in entities:
        entity.label = entity_labels.get(entity.entity_id, None)


def extract_relations_from_brat(annotations_raw: str):
    return []


def read_from_brat(path_to_brat_folder):
    document_id = 0
    documents = []
    for text_file, ann_file in AnnFilesIterator(path_to_brat_folder):
        text = read_file(text_file)
        annotations_raw = read_file(ann_file)
        entities = extract_entities_from_brat(annotations_raw, text)
        entity_labels = extract_entity_labels(annotations_raw)
        set_labels(entities, entity_labels)
        relations = extract_relations_from_brat(annotations_raw)
        document = Document(doc_id=document_id, text=text,
                            entities=entities, relations=relations)
        documents.append(document)
        document_id += 1
    return documents


def save_text_file(path_to_save: str, document: Document):
    with open(path_to_save, 'w', encoding='utf-8') as output_stream:
        output_stream.write(document.text)


def save_ann_file(path_to_save: str, document: Document):
    with open(path_to_save, 'w', encoding='utf-8') as output_stream:
        for entity in document.entities:
            output_stream.write(f'{entity.entity_id}\t{entity.type} {entity.start} {entity.end}\t{entity.text}\n')


def save_brat(path_to_save: str, data):
    for document in data.document:
        ann_file = os.path.join(path_to_save, f'{document.document_id}.ann')
        txt_file = os.path.join(path_to_save, f'{document.document_id}.txt')
        save_text_file(txt_file, document)
        save_ann_file(ann_file, document)

