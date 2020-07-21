from .conll import read_from_conll, save_conll
from .brat import read_from_brat, save_brat
from .json import read_from_json, save_json
from .plain import read_from_plain, save_plain
from .inception import read_from_inception, save_inception


load_functions = {
    'json': read_from_json,
    'brat': read_from_brat,
    'conll': read_from_conll,
    'inception': read_from_inception,
    'plain': read_from_plain
}

save_functions = {
    'json': save_json,
    'brat': save_brat,
    'conll': save_conll,
    'inception': save_inception,
    'plain': save_plain
}
