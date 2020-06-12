from ..document import Entity
from typing import List, Tuple


def extract_entities(tokens: List[str], labels: List[str], text: str, search_start_idx: int = 0) -> Tuple[List[Entity], int]:
    """
    Function to convert predicted bio format to list of entities
    :param tokens: list of tokens
    :param labels: list of labels (for each token)
    :param text: full text
    :param search_start_idx: index of search start position
    :return: List of entities and last search start position
    """
    entities: List[Entity] = []
    entity: List[str] = []
    entity_start: int = 0
    entity_end: int = 0
    entity_type: str = 'NOTYPE'
    for token, label in zip(tokens, labels):
        token_start = text.find(token, search_start_idx)
        token_end = token_start + len(token)
        search_start_idx = token_end
        if (label == 'O' or label.startswith('B-')) and len(entity) > 0:
            entities.append(Entity(text=' '.join(entity), start=entity_start,
                                   end=entity_end, type=entity_type))
        entity = []
        if label.startswith('B-'):
            entity.append(token)
            entity_start = token_start
            entity_end = token_end
        if label.startswith('I-'):
            entity.append(token)
            entity_end = token_end
    if len(entity):
        entities.append(Entity(text=' '.join(entity), start=entity_start,
                                   end=entity_end, type=entity_type))
    return entities, search_start_idx


def find_offset(text, entity_text, start, end, max_offset=50):
    for i in range(-10, max_offset):
        for j in range(-10, max_offset):
            if text[start + i:end + j] == entity_text:
                return start + i, end + i
            if text[start - i: end - j] == entity_text:
                return start - i, end - i
    return None, None


def read_file(fpath):
    with open(fpath, encoding='utf-8') as input_stream:
        data = input_stream.read()
    return data