from NLPDatasetIO.document import Document
from typing import  List
from NLPDatasetIO.data_io.utils import extract_entities


def iterate_over_plain(txt_file_path: str, ann_file_path: str, sep: str = ' '):
    with open(txt_file_path, encoding="utf-8") as txt_input_stream, \
      open(ann_file_path, encoding="utf-8") as ann_input_stream:
        for txt_line, ann_line in zip(txt_input_stream, ann_input_stream):
            yield txt_line.strip().split(), ann_line.strip().split()


def read_from_plain(path_to_plain_texts: str, path_to_plain_ann: str) -> List[Document]:
    #TODO: make common interface for all reading functions
    documents: List[Document] = []
    document_id = 0
    for tokens, labels in iterate_over_plain(path_to_plain_texts,  path_to_plain_ann):
        text = ' '.join(tokens)
        entities, _ = extract_entities(tokens, labels, text)
        document = Document(doc_id=document_id, text=text, entities=entities)
        document_id += 1
        documents.append(document)
    return documents


def save_plain(data, path_to_save_texts: str, path_to_save_ann: str):
    with open(path_to_save_texts, 'w', encoding='utf-8') as txt_output_stream, \
      open(path_to_save_ann, 'w',  encoding='utf-8') as ann_output_stream:
        for document in data.documents:
            tokens = document.tokens
            labels = document.token_labels
            for token in tokens:
                assert ' ' not in token
            txt_output_stream.write(' '.join(tokens) + '\n')
            ann_output_stream.write(' '.join(labels) + '\n')
