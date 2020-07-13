from NLPDatasetIO.data_io import load_functions, save_functions
from NLPDatasetIO.document import Document
from typing import List


class Dataset:

    def __init__(self, location: str, format: str, split='train', **kwargs):
        self.location = location
        self.documents = self.read(location, format, **kwargs)
        self.split = split

    @staticmethod
    def read(path: str, fmt: str, **kwargs) -> List[Document]:
        # TODO: process wrong format passing cases
        load_f = load_functions[fmt]
        return load_f(path, **kwargs)

    def save(self, fmt, **kwargs) -> None:
        save_f = save_functions[fmt]
        save_f(self.documents, **kwargs)

    def iterate_token_level(self):
        for document in self.documents:
            yield document.tokens, document.token_labels

    def iterate_document_level(self):
        for document in self.documents:
            yield document.tokens, document.label

    def iterate_relations(self):
        raise NotImplementedError()

    def split_by_sentences(self):
        documents = []
        for document in self.documents:
            for sent_doc in document.sentences:
                documents.append(sent_doc)
        self.documents = documents

    def __getitem__(self, item):
        return self.documents[item]

    def __setitem__(self, key, value):
        self.documents[key] = value

    def __iter__(self):
        return self.documents
