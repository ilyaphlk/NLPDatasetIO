from NLPDatasetIO.document import Document, Entity


def parse_line(line):
    line_parts = line.strip().split('\t')
    if len(line_parts) == 3:
        doc_id = line_parts[0]
        parsed_line = {'text': line_parts[1], 'label': line_parts[2]}
    else:
        doc_id = 0
        parsed_line = {'text': line_parts[0], 'label': line_parts[1]}
    parsed_line['start'] = 0
    parsed_line['end'] = 0
    return doc_id, parsed_line


def read_normalization_tab(path_to_tab_file):
    documents = {}
    with open(path_to_tab_file, encoding='utf-8') as input_stream:
        for line in input_stream:
            doc_id, entity = parse_line(line)
            if doc_id not in documents: documents[doc_id] = []
            documents[doc_id].append(entity)

    dataset = []
    for doc_id, entities in documents.items():
        entities = [Entity(**entity) for entity in entities]
        document = Document(doc_id, '', entities=entities)
        dataset.append(document)
    return dataset