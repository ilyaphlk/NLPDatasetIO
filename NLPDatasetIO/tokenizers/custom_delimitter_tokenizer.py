import re
from nltk.tokenize.punkt import PunktSentenceTokenizer
from typing import Generator, Tuple


class CustomDelimiterSpanTokenizer:
    punkt_span_tokenize = PunktSentenceTokenizer().span_tokenize
    delimitters = ['\n+']
    pattern = re.compile('|'.join(delimitters))

    @classmethod
    def span_tokenize(cls, text: str) -> Generator[Tuple[int], None, None]:
        custom_delim_part_start = 0
        delim_end_positions = [custom_delim_part_end_g.end() for custom_delim_part_end_g in cls.pattern.finditer(text)]
        if len(delim_end_positions) == 0 or delim_end_positions[-1] != len(text):
            delim_end_positions.append(len(text))
        for custom_delim_part_end in delim_end_positions:
            custom_delim_part = text[custom_delim_part_start:custom_delim_part_end]
            for sentence_start_idx, sentence_end_idx in cls.punkt_span_tokenize(custom_delim_part):
                yield sentence_start_idx + custom_delim_part_start, sentence_end_idx + custom_delim_part_start
            custom_delim_part_start = custom_delim_part_end
