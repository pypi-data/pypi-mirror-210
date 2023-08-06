"""Provide a set of tools to perform string matching using regular expression technique
"""
from re import findall, error as rer, IGNORECASE as IC
from collections.abc import Iterable as Iter_type
from typing import Iterable, Union
from warnings import warn

from core import Fragment


class REM:
    """A class that can perform string matching against reference using regex."""

    def __init__(self):
        self._reference = None

    def set_reference(self, reference: Union[str, Iterable]):
        assert isinstance(reference, (str, Iter_type)), "Only a string or an iterable of string accepted"
        self._reference = reference
        if not isinstance(reference, str):
            self._reference = []
            for i in reference:
                warn(f"Found an object that is not {str} from string_reference"
                     ) if not isinstance(i, str) \
                    else self._reference.append(i)

            self._reference = set(self._reference)
            assert len(self._reference) > 0, f'No valid string found in iterable object'
            self._reference = '\n'.join(self._reference)

    def perform_matching(self, Frag_obj: Fragment, case_sensitivity: bool = True):
        """
        :param case_sensitivity: A flag to indicate if the matching
            that will be performed is case-sensitive or not.
        :param Frag_obj: A Fragment object of string that will be matched.
        :return: A ReMatchingStatus object. ReMatchingStatus object make matching result  easier to
            access and manipulate. It also can be used in if else statement.
            Read the API documentation to know more.
        """
        if self._reference is None:
            raise Exception('Reference not yet set. Use set_reference() methode to set one')
        return ReMatchingStatus(Frag_obj.str, matching_by_regex(Frag_obj, self._reference, case_sensitivity))


class ReMatchingStatus:
    """Class that define matching result and status. Read the API documentation to know more"""

    def __init__(self, string: str, obj):
        """
        :param string: string
        :param obj: matching result, the format must be tuple with 3 value:
            a list, a bool and a pattern ([...], bool, str)
        """
        self._string = string
        self._result, self._status, self._pattern = obj

    def __bool__(self):
        return self._status

    def __len__(self):
        return 0 if self._result[0] is None else len(self._result)

    @property
    def status(self):
        """Matching status, True if it found candidate(s) that match and False otherwise"""
        return self._status

    @property
    def match(self):
        """return one match value"""
        return self._result[0]

    @property
    def match_list(self):
        """list of matching candidate"""
        return self._result if self._status else None

    @property
    def pattern(self):
        """The regular expression pattern that match in reference"""
        return self._pattern

    def __str__(self):
        list_ = None if not self._status else self.match_list
        return f'\nFragmented string: {self._string}' \
               f'\nPattern match    : {self._pattern}' \
               f'\nList of match    : {list_}'


def matching_by_regex(Fragment_obj: Fragment, reference: str, cs: bool):
    for pattern in Fragment_obj.iterate_fragment(True):
        try:
            list_match = findall(pattern, reference) if cs else findall(pattern, reference, IC)
            if len(list_match) > 0:
                return list_match, True, pattern
        except rer:
            pass
    return [None], False, None
