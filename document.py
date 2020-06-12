from nltk.tokenize import word_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass

sent_tokenize = PunktSentenceTokenizer().span_tokenize


@dataclass
class Entity:
    def __init__(self, text: str, start: int, end: int, type: str, label: Optional[str] = None) -> None:
        self.text: str = text
        self.start: int = start
        self.end: int = end
        self.type: str = type
        self.label: Optional[str] = label


@dataclass
class Relation:
    def __init__(self):
        raise NotImplementedError()


@dataclass
class Token:
    def __init__(self, token: str, token_start: int, token_end: int, label: str):
        self.token: str = token
        self.token_start: int = token_start
        self.token_end: int = token_end
        self.label: str = label


class Document:

    def __init__(self, doc_id: int, text: str, label: Optional[str] = None, entities: Optional[List[Entity]] = None,
                 relations: Optional[List[Relation]] = None, tokenize: Optional[Callable] = None, shift: int = None) -> None:

        self.doc_id: int = doc_id
        self.text: str = text
        self.label: Optional[str] = label
        self.entities: Optional[List[Entity]] = entities
        self.relations: Optional[List[Relation]] = relations
        if tokenize is None:
            self.tokenize: Callable = word_tokenize
        else:
            self.tokenize: Callable = tokenize
        self._tokens: List[Token] = self.token_level_labeling(text, entities, tokenize)
        self.shift: int = shift

    def etype_to_bio_label(self, label: str, token_idx: int) -> str:
        if label == 'O':
            return label
        if token_idx == 0:
            return 'B-' + label
        return 'I-' + label

    def tokenize_with_spans(self, text: str, etype: str) -> List[Token]:
        search_start_pos_idx: int = 0
        tokens: List[Token] = []
        for token_idx, token in enumerate(self.tokenize(text)):
            label = self.etype_to_bio_label(etype, token_idx)
            token_start = text.find(token, search_start_pos_idx)
            token_end = token_start + len(token)
            tokens.append(Token(token=token, start=token_start, end=token_end, label=label))
            search_start_pos_idx = token_end
        return tokens

    def token_level_labeling(self) -> List[Token]:
        sorted_entities = sorted(self.entities, key=lambda t: t.start)
        prev_entity_end = 0
        processed_tokens: List[Token] = []
        for entity in sorted_entities:
            no_entity_part = self.text[prev_entity_end:entity['start']]
            entity_part = self.text[entity['start']:entity['end']]
            processed_tokens += self.tokenize_with_spans(no_entity_part, 'O')
            processed_tokens += self.tokenize_with_spans(entity_part, entity['type'])
        no_entity_part = self.text[prev_entity_end:entity['start']]
        processed_tokens += self.tokenize_with_spans(no_entity_part, 'O')
        return processed_tokens

    def filter_entities(self, start_idx: int, end_idx: int) -> List[Entity]:
        filtered_entities: List[Entity] = []
        for entity in self.entities:
            if entity['start'] >= start_idx and entity['end'] <= end_idx:
                filtered_entities.append(entity)
        return filtered_entities

    def filter_relations(self, start_idx: int, end_idx: int):
        return self.relations

    @property
    def tokens(self) -> List[str]:
        return [t['token'] for t in self._tokens]

    @property
    def token_labels(self) -> List[str]:
        return [t['label'] for t in self._tokens]

    @property
    def sentences(self) -> 'List[Document]':
        sentence_documents: List[Document] = []
        for sentence_start_idx, sentence_end_idx in sent_tokenize(self.text):
            sentence_doc_id = self.doc_id
            sentence_text = self.text[sentence_start_idx:sentence_end_idx]
            sentence_entities = self.filter_entities(sentence_start_idx, sentence_end_idx)
            sentence_relations = self.filter_relations(sentence_start_idx, sentence_end_idx)
            sentence_label = self.label
            sentence_tokenize = self.tokenize
            sentence_shift = sentence_start_idx
            sentence = Document(doc_id=sentence_doc_id, text=sentence_text, label=sentence_label,
                                entities=sentence_entities, relations=sentence_relations,
                                tokenize=sentence_tokenize, shift=sentence_shift)
            sentence_documents.append(sentence)
        return sentence_documents

    @staticmethod
    def from_token_level_labeling(tokens: List[str], labels: List[str]) -> None:
        pass

