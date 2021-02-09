from NLPDatasetIO.document import Document, Entity, Relation
from typing import List
import json


def read_from_json(path_to_json: str) -> List[Document]:
    documents: List[Document] = []
    with open(path_to_json, encoding='utf-8') as input_stream:
        for document_id, line in enumerate(input_stream):
            document_dict = json.loads(line)
            document_id = document_dict.get('document_id', document_id)
            text = document_dict['text']
            label = document_dict.get('label', None)
            entities = {entity_id: Entity(**entity_dict) for entity_id, entity_dict in document_dict['entities'].items()}
            relations = document_dict.get('relations', [])
            relations = [Relation(**relation) for relation in relations]
            shift = document_dict.get('shift', 0)
            document = Document(doc_id=document_id, text=text, label=label,
                                entities=entities, relations=relations, shift=shift)
            documents.append(document)
    return documents


def save_json(data, path_to_save: str) -> None:
    with open(path_to_save, 'w', encoding='utf-8') as output_stream:
        for document in data.documents:
            output_json = document.to_dict()
            serialized_output_str = json.dumps(output_json, ensure_ascii=False)
            output_stream.write(serialized_output_str + '\n')
