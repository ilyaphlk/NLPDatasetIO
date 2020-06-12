from ..document import Document
from ..dataset import Dataset
from typing import  List
from .utils import extract_entities


def iterate_over_conll(file_path: str, sep: str = ' '):
    with open(file_path, encoding="utf-8") as f:
        words = []
        labels = []
        gazetteers = []
        for line in f:
            if line.startswith("-DOCSTART-") or line == "" or line == "\n":
                if words:
                    yield words, labels, gazetteers
                    words = []
                    labels = []
                    gazetteers = []
            else:
                splits = line.split(sep)
                #replacing spaces with underscore in words
                words.append(splits[0].replace(' ', '_'))
                if len(splits) > 1:
                    labels.append(splits[1].replace("\n", ""))
                else:
                    # Examples could have no label for mode = "test"
                    labels.append("O")
                if len(splits) > 2:
                    gazetteers.append(splits[2].replace("\n", ""))
                else:
                    gazetteers.append("O")
        if words:
            yield words, labels, gazetteers


def read_from_conll(path_to_conll: str, sep: str = ' ') -> List[Document]:
    documents: List[Document] = []
    document_id = 0
    for tokens, labels, gazetteers in iterate_over_conll(path_to_conll, sep):
        text = ' '.join(tokens)
        entities, _ = extract_entities(tokens, labels, text)
        document = Document(doc_id=document_id, text=text, entities=entities)
        document_id += 1
        documents.append(document)
    return documents


def save_conll(path_to_save: str, data: Dataset):
    pass