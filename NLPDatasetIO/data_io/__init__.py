from NLPDatasetIO.data_io.conll import read_from_conll, save_conll
from NLPDatasetIO.data_io.brat import read_from_brat, save_brat
from NLPDatasetIO.data_io.json import read_from_json, save_json
from NLPDatasetIO.data_io.plain import read_from_plain, save_plain
from NLPDatasetIO.data_io.inception import read_from_inception, save_inception
from NLPDatasetIO.data_io.normalization_tab import read_normalization_tab


load_functions = {
    'json': read_from_json,
    'brat': read_from_brat,
    'conll': read_from_conll,
    'inception': read_from_inception,
    'plain': read_from_plain,
    'normalization_tab': read_normalization_tab
}

save_functions = {
    'json': save_json,
    'brat': save_brat,
    'conll': save_conll,
    'inception': save_inception,
    'plain': save_plain
}
