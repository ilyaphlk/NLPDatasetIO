from NLPDatasetIO.document import Entity
from typing import List, Optional


def extract_entities(tokens: List[str], labels: List[str], text: str,
                     search_start_idx: int = 0, entity_label_sep: str ='_'):
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
    entity_label: Optional[str] = None
    entity_id = 0
    for token, label in zip(tokens, labels):
        token_start = text.find(token, search_start_idx)
        token_end = token_start + len(token)
        search_start_idx = token_end
        if (label == 'O' or label.startswith('B-')) and len(entity) > 0:
            entities.append(Entity(entity_id=entity_id, text=' '.join(entity), start=entity_start,
                                   end=entity_end, type=entity_type))
            entity = []
            entity_id += 1
            entity_start = None
            entity_end = None
        if label.startswith('B-'):
            entity.append(token)
            entity_start = token_start
            entity_end = token_end
            entity_type = label[2:].split(entity_label_sep)[0]
            entity_label = label[2:].split(entity_label_sep)[1]
        if label.startswith('I-'):
            entity.append(token)
            if entity_start is None: entity_start = token_start
            entity_end = token_end
            entity_type = label[2:].split(entity_label_sep)[0]
            entity_label = label[2:].split(entity_label_sep)[1]
    if len(entity):
        entities.append(Entity(entity_id=entity_id, text=' '.join(entity), start=entity_start,
                               end=entity_end, type=entity_type, label=entity_label))
    return entities, search_start_idx


def find_offset(text, entity_text, start, end, max_offset=50):
    for i in range(-10, max_offset):
        for j in range(-10, max_offset):
            if text[start + i:end + j] == entity_text:
                return start + i, end + i
            if text[start - i: end - j] == entity_text:
                return start - i, end - i
    return start, end


def read_file(fpath):
    with open(fpath, encoding='utf-8') as input_stream:
        data = input_stream.read()
    return data
