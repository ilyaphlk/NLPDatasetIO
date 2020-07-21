"""
attribute_format = r'(?P<attribute_id>^A[0-9]+)\t(?P<attribute_type>[a-zA-Z\_]+) (?P<entity_id>T[0-9]+) (?P<attribute_value>[a-zA-Z\_]+)'

def parse_attribute(line):
    return re.search(attribute_format, line).groupdict()

def convert_brt_ann(ann_file, txt_file):
    entities = {}
    with open(ann_file, encoding='utf-8') as input_stream:
        for line in input_stream:
            line = line.strip()
            try:
                if line.startswith('T'):
                    annotation = parse_entity(line)
                    entity_id = annotation['entity_id']
                    entities[entity_id] = annotation
                elif line.startswith('A'):
                    annotation = parse_attribute(line)
                    entity_id = annotation['entity_id']
                    attribute_type = annotation['attribute_type']
                    attribute_value = annotation['attribute_value']
                    if entity_id in entities: entities[entity_id][attribute_type] = attribute_value
            except Exception as e:
                print('Bad Line', line, e)

    entities = [entity for entity in entities.values() if entity is not None]

    entities = sorted(entities, key=lambda e: int(e['start']))

    with open(txt_file, encoding='utf-8') as input_stream:
        text = input_stream.read().replace('\n', ' ')

    processed_data = {
        'document_id': txt_file,
        'text': text,
        'entities': {}
    }

    for entity in entities:
        if False and text[entity['start']:entity['end']] != entity['text']:
            if entity['text'].replace(' ', '') in text[entity['start']:entity['end']].replace(' ', ''):
                entity['text'] = text[entity['start']:entity['end']]
            else:
                entity['start'], entity['end'] = find_offset(text, entity['text'], entity['start'], entity['end'])
        if False and entity['start'] is None:
            logging.warning(' Not found "{}" in text file {}'.
                            format(entity['text'], txt_file))
            continue
        processed_data['entities'][entity['entity_id']] = entity

    return processed_data
    
"""