from nltk.tokenize import word_tokenize
from NLPDatasetIO.tokenizers.custom_delimitter_tokenizer import CustomDelimiterSpanTokenizer
from typing import List, Optional, Callable, Any, Dict
from dataclasses import dataclass, asdict, replace

sent_tokenize = CustomDelimiterSpanTokenizer.span_tokenize


@dataclass
class Entity:
    entity_id: Any
    text: str
    start: int
    end: int
    type: str
    label: Optional[str] = None
    note: Optional[Any] = None


@dataclass
class Relation:
    relation_id: Any
    entity_id_1: Any
    entity_id_2: Any
    type: str
    note: Optional[Any] = None


@dataclass
class Token:
    token: str
    token_start: int
    token_end: int
    label: str
    entity_label: Optional[str]


class Document:

    def __init__(self, doc_id: int, text: str,
                 label: Optional[str] = None,
                 entities: Dict[Any, Entity] = {},
                 relations: Optional[List[Relation]] = None,
                 tokenize: Optional[Callable] = None,
                 subword_prefix: str = None, # TODO would be more convenient to get from callable
                 subword_suffix: str = None,
                 shift: int = None) -> None:

        self.doc_id: int = doc_id
        self.text: str = text
        self.label: Optional[str] = label
        self.entities: Optional[Dict[Any, Entity]] = entities
        self.relations: Optional[List[Relation]] = []
        if relations is not None:
            self.relations = relations
        if tokenize is None:
            self.tokenize: Callable = word_tokenize
        else:
            self.tokenize: Callable = tokenize

        self.subword_prefix = subword_prefix
        self.subword_suffix = subword_suffix

        # TODO add input to function, make static
        self._tokens: List[Token] = self.token_level_labeling()
        self.shift: int = shift

    @staticmethod
    def etype_to_bio_label(label: str, token_idx: int) -> str:
        if label == 'O':
            return label
        if token_idx == 0:
            return 'B-' + label
        return 'I-' + label

    def tokenize_with_spans(self, text: str, etype: str, entity_label: Optional[str] = None) -> List[Token]:
        search_start_pos_idx: int = 0
        tokens: List[Token] = []
        for token_idx, token in enumerate(self.tokenize(text)):
            if (self.subword_prefix is not None and
                token[:len(self.subword_prefix)] == self.subword_prefix):
                token = token[len(self.subword_prefix):]

            if (self.subword_suffix is not None and
                token[-len(self.subword_suffix):] == self.subword_suffix):
                token = token[:-len(self.subword_suffix)]

            label = self.etype_to_bio_label(etype, token_idx)
            token_start = text.find(token, search_start_pos_idx)
            token_end = token_start + len(token)
            tokens.append(Token(token=token, token_start=token_start,
                                token_end=token_end, label=label, entity_label=entity_label))
            search_start_pos_idx = token_end

        return tokens


    def token_level_labeling(self) -> List[Token]:
        sorted_entities = sorted(self.entities.values(), key=lambda t: t.start)
        prev_entity_end = 0
        processed_tokens: List[Token] = []
        for entity in sorted_entities:
            no_entity_part = self.text[prev_entity_end:entity.start]
            entity_part = self.text[entity.start:entity.end]
            processed_tokens += self.tokenize_with_spans(no_entity_part, 'O')
            processed_tokens += self.tokenize_with_spans(entity_part, entity.type, entity.label)
            prev_entity_end = entity.end
        no_entity_part = self.text[prev_entity_end:]
        processed_tokens += self.tokenize_with_spans(no_entity_part, 'O')
        return processed_tokens

    def filter_entities(self, start_idx: int, end_idx: int) -> List[Entity]:
        filtered_entities: Dict[Any, Entity] = {}
        for entity_id, entity in self.entities.items():
            if entity.start >= start_idx and entity.end <= end_idx:
                f_entity_start = entity.start - start_idx
                f_entity_end = entity.end - start_idx
                fentity = replace(entity)
                fentity.start = f_entity_start
                fentity.end = f_entity_end
                filtered_entities[entity_id] = fentity
        return filtered_entities

    def filter_relations(self, start_idx: int, end_idx: int):
        # stores only sentence relations
        filtered_relations = []
        for relation in self.relations:
            entity_1 = self.entities[relation.entity_id_1]
            entity_2 = self.entities[relation.entity_id_2]
            if start_idx < entity_1.start and entity_1.end < end_idx and \
                    start_idx < entity_2.start and entity_2.end < end_idx:
                filtered_relations.append(relation)
        return filtered_relations

    @property
    def tokens(self) -> List[str]:
        return [t.token for t in self._tokens]

    @property
    def token_labels(self) -> List[str]:
        return [t.label for t in self._tokens]

    @property
    def detailed_token_labels(self):
        return [f"{t.label}_{t.entity_label}" for t in self._tokens]

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

    def to_dict(self):
        output_json = {'document_id': self.doc_id, 'text': self.text, 'label': self.label,
                       'shift': self.shift}
        entities = {entity_id: asdict(entity) for entity_id, entity in self.entities.items()}
        output_json['entities'] = entities
        relations = [asdict(relation) for relation in self.relations]
        output_json['relations'] = relations
        return output_json

