from NLPDatasetIO.dataset import Dataset


def test_load_dataset():
    dataset = Dataset('data/brat_format_data', 'brat')
    for document in dataset.documents:
        for entity in document.entities:
            print(entity.start, entity.end, entity.text, entity.type, entity.label)


if __name__ == '__main__':
    test_load_dataset()
