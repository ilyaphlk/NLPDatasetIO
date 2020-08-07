from nltk.tokenize import word_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer
from typing import List, Tuple, Optional, Callable, Any
from dataclasses import dataclass
from NLPDatasetIO.data_io.utils import extract_entities

sent_tokenize = PunktSentenceTokenizer().span_tokenize


@dataclass
class Entity:
    entity_id: Any
    text: str
    start: int
    end: int
    type: str
    label: Optional[str] = None


@dataclass
class Relation:
    def __init__(self):
        raise NotImplementedError()


@dataclass
class Token:
    token: str
    token_start: int
    token_end: int
    label: str


class Document:

    def __init__(self, doc_id: int, text: str, label: Optional[str] = None, entities: Optional[List[Entity]] = [],
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
        self._tokens: List[Token] = self.token_level_labeling()
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
            tokens.append(Token(token=token, token_start=token_start, token_end=token_end, label=label))
            search_start_pos_idx = token_end
        return tokens

    def token_level_labeling(self) -> List[Token]:
        sorted_entities = sorted(self.entities, key=lambda t: t.start)
        prev_entity_end = 0
        processed_tokens: List[Token] = []
        for entity in sorted_entities:
            no_entity_part = self.text[prev_entity_end:entity.start]
            entity_part = self.text[entity.start:entity.end]
            processed_tokens += self.tokenize_with_spans(no_entity_part, 'O')
            processed_tokens += self.tokenize_with_spans(entity_part, entity.type)
            prev_entity_end = entity.end
        no_entity_part = self.text[prev_entity_end:]
        processed_tokens += self.tokenize_with_spans(no_entity_part, 'O')
        return processed_tokens

    def filter_entities(self, start_idx: int, end_idx: int) -> List[Entity]:
        filtered_entities: List[Entity] = []
        for entity in self.entities:
            if entity.start >= start_idx and entity.end <= end_idx:
                entity.start = entity.start - start_idx
                entity.end = entity.end - start_idx
                filtered_entities.append(entity)
        return filtered_entities

    def filter_relations(self, start_idx: int, end_idx: int):
        return self.relations

    @property
    def tokens(self) -> List[str]:
        return [t.token for t in self._tokens]

    @property
    def token_labels(self) -> List[str]:
        return [t.label for t in self._tokens]

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

    def from_token_level_labeling(self, tokens: List[str], labels: List[str]) -> None:
        self.entities, _ = extract_entities(tokens, labels, self.text)
        self._tokens: List[Token] = self.token_level_labeling()

