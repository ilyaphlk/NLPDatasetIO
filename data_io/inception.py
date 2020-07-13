from NLPDatasetIO.document import Document, Entity
import pandas as pd
from glob import glob
import os
import re


def read_texts(file_path):
    texts = []
    is_sent = False
    with open(file_path, encoding='utf-8') as input_stream:
        for line in input_stream:
            if line.startswith('#Text='):
                if is_sent:
                    texts[-1] += line[6:]
                else:
                    texts.append(line[6:])
            is_sent = line.startswith('#Text=')
    return texts


def read_annotations(file_path):
    annotation_data = pd.read_csv(file_path, sep='\t| {4,}', skip_blank_lines=True, comment='#', encoding='utf-8',
                                  names=['token_id', 'token_span', 'token', 'entity_id', 'type',
                                         'unknown_1', 'unknown_2'], engine='python')
    return annotation_data


def get_text_from_spans(entity, sentences):
    sentence = sentences[entity['sentence_id']]
    return sentence[entity['start']:entity['end']]


def get_entities_spans(annotation_data):
    annotation_data.fillna('_', inplace=True)
    annotation_data['sentence_id'] = annotation_data.token_id.apply(lambda tid: int(tid.split('-')[0]) - 1)
    annotation_data['type'] = annotation_data.type.apply(lambda eid: re.sub(r'\[\d+\]', '', eid))
    annotation_data['start'] = annotation_data.token_span.apply(lambda tid: int(tid.split('-')[0]))
    annotation_data['end'] = annotation_data.token_span.apply(lambda tid: int(tid.split('-')[1]))
    sentences_starts = annotation_data.groupby('sentence_id')['start'].min().reset_index(). \
        rename(columns={'start': 'sentence_start'})

    single_entities_count = annotation_data[annotation_data.entity_id == '*'].shape[0]
    annotation_data.loc[annotation_data.entity_id == '*', 'entity_id'] = ['*[{}]_se'.format(i) for i in
                                                                          range(single_entities_count)]
    annotation_data = annotation_data[annotation_data.entity_id != '_']
    entities_starts = annotation_data.groupby(['sentence_id', 'entity_id', 'type'])['start'].min().reset_index()
    entities_ends = annotation_data.groupby(['sentence_id', 'entity_id', 'type'])['end'].max().reset_index()

    entities = pd.merge(entities_starts, entities_ends, on=['sentence_id', 'entity_id', 'type'])
    entities = pd.merge(entities, sentences_starts, on=['sentence_id'])
    entities['start'] = entities['start'] - entities['sentence_start']
    entities['end'] = entities['end'] - entities['sentence_start']
    return entities


def parse_sentences(file_path):
    parent_directory = os.path.dirname(file_path)
    parent_directory = os.path.basename(parent_directory)
    resulting_data = []
    sentences = read_texts(file_path)
    annotation_data = read_annotations(file_path)
    entities_spans = get_entities_spans(annotation_data)
    entities_spans['text'] = None
    if entities_spans.shape[0] > 0:
        entities_spans['text'] = entities_spans.apply(get_text_from_spans, args=(sentences,), axis=1)
    for sentence_id, sentence in enumerate(sentences):
        sentence_annotations = entities_spans[entities_spans.sentence_id == sentence_id]
        sentence_annotations = sentence_annotations[['entity_id', 'type', 'start', 'end', 'text']].to_dict('records')
        sentence_annotations = [Entity(entity_id=annotation['entity_id'], text=annotation['text'],
                                       start=annotation['start'], end=annotation['end'],
                                       type=annotation['type']) for annotation in sentence_annotations]
        resulting_data.append({
            'text': sentence,
            'sentence_id': sentence_id,
            'file_name': parent_directory,
            'entities': sentence_annotations
        })
    return resulting_data


def read_from_inception(path_inception: str):
    document_id = 0
    documents = []
    file_pattern = os.path.join(path_inception, '*', '*.tsv')
    for file_path in glob(file_pattern):
        sentences = parse_sentences(file_path)
        for sentence in sentences:
            document = Document(doc_id=document_id, text=sentence['text'],
                                entities=sentence['entities'], relations=None)
            documents.append(document)
            document_id += 1
    return documents


def save_inception(path_to_save: str, data):
    pass
