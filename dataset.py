from data_io import load_functions, save_functions
from document import Document
from typing import List


class Dataset:

    def __init__(self, location: str, format: str, split='train'):
        self.location
        self.documents = self.read(location, format)
        self.split = split

    @staticmethod
    def read(path: str, fmt: str) -> List[Document]:
        # TODO: process wrong format passing cases
        load_f = load_functions[fmt]
        return load_f(path)

    def save(self, path: str, fmt: str) -> None:
        save_f = save_functions[fmt]
        save_f(path, self.documents)

    def iterate_token_level(self):
        for document in self.documents:
            yield document.tokens, document.token_labels

    def iterate_document_level(self):
        for document in self.documents:
            yield document.tokens, document.label

    def iterate_relations(self):
        raise NotImplementedError()
