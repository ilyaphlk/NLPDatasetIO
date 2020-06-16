from NLPDatasetIO.dataset import Dataset


def test_load_dataset():
    dataset = Dataset('data/data_conll.txt', 'conll', sep='\t')
    gold_tokens = [
        ['22', '-', 'oxacalcitriol', 'suppresses', 'secondary', 'hyperparathyroidism', 'without', 'inducing', 'low',
         'bone', 'turnover', 'in', 'dogs', 'with', 'renal', 'failure', '.'],
        ['BACKGROUND', ':', 'Calcitriol', 'therapy', 'suppresses', 'serum', 'levels', 'of', 'parathyroid', 'hormone',
         '(', 'PTH', ')', 'in', 'patients', 'with', 'renal', 'failure', 'but', 'has', 'several', 'drawbacks', ',',
         'including', 'hypercalcemia', 'and', '/', 'or', 'marked', 'suppression', 'of', 'bone', 'turnover', ',',
         'which', 'may', 'lead', 'to', 'adynamic', 'bone', 'disease', '.']
    ]
    gold_labels = [
        ['O', 'O', 'O', 'O', 'B-DISO', 'I-DISO',
         'O', 'O', 'B-DISO', 'I-DISO', 'I-DISO', 'O', 'O', 'O', 'B-DISO', 'I-DISO', 'O'],
        ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-DISO', 'I-DISO', 'O', 'O',
         'O', 'O', 'O', 'O', 'B-DISO', 'O', 'O', 'O', 'O', 'B-DISO', 'I-DISO', 'I-DISO', 'I-DISO', 'O', 'O', 'O', 'O',
         'O', 'B-DISO', 'I-DISO', 'I-DISO', 'O']
    ]
    example_id = 0
    for tokens, labels in dataset.iterate_token_level():
        tokens_length = len(tokens)
        labels_length = len(labels)
        assert tokens_length == labels_length, 'Length of tokens and labels mismatch at example ' + str(example_id)
        assert tokens_length == len(gold_tokens[example_id]), 'Readed and Gold tokens length mismatch ' + str(example_id)
        assert labels_length == len(gold_labels[example_id]), 'Readed and Gold labels length mismatch ' + str(example_id)
        for token_idx in range(tokens_length):
            assert tokens[token_idx] == gold_tokens[example_id][token_idx], 'Token mismatch ' + str(example_id)
            assert labels[token_idx] == gold_labels[example_id][token_idx], 'Label mismatch ' + str(example_id)
        example_id += 1
        if example_id == 2: break


if __name__ == '__main__':
    test_load_dataset()
