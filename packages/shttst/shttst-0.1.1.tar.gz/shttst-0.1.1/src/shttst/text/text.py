from typing import List
from shttst.text import shmart_cleaner, symbols

class ShmartTextProcessor():
    def __init__(self, cleaner_fn=shmart_cleaner, symbols: List[str] = symbols) -> None:
        self.cleaner = cleaner_fn

        self.symbol_to_id_map = {s: i for i, s in enumerate(symbols)}
        self.id_to_symbol_map = {i: s for i, s in enumerate(symbols)}

    def encode_text(self, text: str) -> List[int]:
        space_id = self.symbol_to_id_map[' ']
        return [space_id, *self._symbols_to_sequence(self._clean_text(text)), space_id]

    def _clean_text(self, text: str):
        return self.cleaner(text)

    def _symbols_to_sequence(self, symbols: str):
        return [self.symbol_to_id_map[s] for s in symbols if s in self.symbol_to_id_map]