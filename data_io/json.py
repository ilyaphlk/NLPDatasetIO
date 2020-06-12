from ..document import Document, Entity
from ..dataset import Dataset
from typing import List
import json


def read_from_json(path_to_json: str) -> List[Document]:
    documents: List[Document] = []
    with open(path_to_json, encoding='utf-8') as input_stream:
        for document_id, line in enumerate(input_stream):
            document_dict = json.loads(line)
            document_id = document_dict.get('doc_id', document_id)
            text = document_dict['text']
            label = document_dict.get('label')
            entities = [Entity(**entity_dict) for entity_dict in document_dict['entities']]
            relations = document_dict.get('relations')
            shift = document_dict.get('shift', 0)
            document = Document(doc_id=document_id, text=text, label=label,
                                entities=entities, relations=relations, shift=shift)
            documents.append(document)
    return document


def save_json(path_to_save: str, data: Dataset) -> None:
    pass