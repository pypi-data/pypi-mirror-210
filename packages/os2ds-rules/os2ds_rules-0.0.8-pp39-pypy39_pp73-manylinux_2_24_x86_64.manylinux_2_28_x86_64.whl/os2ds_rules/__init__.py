from .cpr_detector import find_matches as cpr_find_matches
from .name_rule import find_matches as name_find_matches
from .address_rule import find_matches as address_find_matches


class CPRDetector:
    '''Drop-in replacement for CPRRule.'''

    def __init__(self, check_mod11: bool = False, examine_context: bool = False):
        self._check_mod11 = check_mod11
        self._examine_context = examine_context

    def find_matches(self, content: str):
        yield from cpr_find_matches(content, self._check_mod11, self._examine_context)


class NameRule:
    '''Drop-in replacement for NameRule.'''

    def __init__(self, expansive: bool = False):
            self._expansive = expansive

    def find_matches(self, content: str):
        yield from name_find_matches(content, self._expansive)


class AddressRule:
    '''Drop-in replacement for AddressRule.'''

    def find_matches(self, content: str):
        yield from address_find_matches(content)
