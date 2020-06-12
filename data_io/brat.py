from ..document import Document, Entity
from ..dataset import Dataset
from typing import List
from .utils import find_offset, read_file
from glob import glob
import os
import re

BRAT_FORMAT = r'(?P<entity_id>^T[0-9]+)\t(?P<type>[a-zA-Z\_]+) (?P<positions>[0-9; ]+)\t(?P<text>.*)'


class AnnFilesIterator(object):

    def __init__(self, directory):
        self.directory = directory
        txt_files_pattern = os.path.join(directory, '*.txt')
        ann_files_pattern = os.path.join(directory, '*.ann')
        txt_files = [txt_file for txt_file in glob(txt_files_pattern)]
        ann_files = [ann_file for ann_file in glob(ann_files_pattern)]
        self.txt_files = sorted(txt_files)
        self.ann_files = sorted(ann_files)

    def __iter__(self):
        return iter(zip(self.txt_files, self.ann_files))


def parse_annotation(annotation_raw):
    annotation = re.search(BRAT_FORMAT, annotation_raw).groupdict()
    positions = re.findall(r'\d+', annotation['positions'])
    positions = [int(pos) for pos in positions]
    annotation['start'] = min(positions)
    annotation['end'] = max(positions)
    return annotation


def extract_entities_from_brat(annotations_raw: str, text: str) -> List[Entity]:
    entities = []
    for annotation_raw in annotations_raw.split('\n'):
        if not annotation_raw.startswith('T'): continue
        annotation = parse_annotation(annotation_raw)
        start = annotation['start']
        end = annotation['end']
        entity_text = annotation['text']
        if text[start:end] != annotation['text']:
            start, end = find_offset(text, entity_text, start, end)
        entities.append(Entity(text=entity_text,
                               start=start,
                               end=end,
                               type=annotation['type']))
    return entities


def extract_relations_from_brat(annotations_raw: str):
    return []


def read_from_brat(path_to_brat_folder):
    document_id = 0
    documents = []
    for text_file, ann_file in AnnFilesIterator(path_to_brat_folder):
        text = read_file(text_file)
        annotations_raw = read_file(ann_file)
        entities = extract_entities_from_brat(annotations_raw, text)
        relations = extract_relations_from_brat(annotations_raw)
        document = Document(doc_id=document_id, text=text,
                            entities=entities, relations=relations)
        documents.append(document)
        document_id += 1
    return document


def save_brat(path_to_save: str, data: Dataset):
    pass