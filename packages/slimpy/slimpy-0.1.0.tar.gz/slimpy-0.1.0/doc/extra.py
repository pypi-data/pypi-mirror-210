"""This extra module contain class and function to extract field(s) from image.
It show the capability of this library
"""
from typing import Optional
from re import search, error as rer
from core import Fragment
from rematch import REM


class ExtractFieldWithRegex(REM):
    """
    - A class that show practical application of this package.
      It can extract field(s) from reference (text source).
    - An anchor is given as Fragment object that will be used as boundary rule.
    - A note to keep in mind: when defining boundary rule, extraction do not ignore
      "new line" (no re.DOTALL flag), so a line-break will be act as natural boundary
      if the end boundary is not specified.
    ====
    Methode:
    ====
    -   add_rule: Define rule to extract a field.
    -   extract: Perform an extraction.
    -   set_reference: add matching reference.
    ====
    """

    def __init__(self):
        """Instantiate an object to enable creation set of rule to use to extract field from text."""
        super().__init__()
        self._rule = {}
        self._boundary = {}

    def add_rule(self, field_name,
                 Fragment_start: Optional[Fragment] = None,
                 Fragment_end: Optional[Fragment] = None):
        """
        :param field_name: Used as key to store a rule to extract a field.
        :param Fragment_start: Fragment object of anchor that mark start of boundary.
        :param Fragment_end: Fragment object of anchor that mark end of boundary.
        """
        assert any([isinstance(Fragment_start, Fragment), isinstance(Fragment_end, Fragment)]), "You must pass \
            an argument at least one either to Fragment_start or Fragment_end as an anchor"
        self._rule[field_name] = Fragment_start, Fragment_end

    def perform_extraction(self, cs=True, default_not_found_val=''):
        """
        :return: a Dictionary with format: {field name: string extracted, ...}.
            If no matched pattern found when extracting
            the value of the dictionary will be an empty string.
        """
        extracted = {}
        for key in self._rule:
            frag_start = self._rule[key][0]
            frag_end = self._rule[key][1]
            start = self.perform_matching(frag_start, cs).match \
                if frag_start is not None \
                else None
            end = self.perform_matching(frag_end, cs).match \
                if frag_end is not None \
                else None
            pattern = construct_extract_pattern(start, end)
            if pattern is None:
                extracted[key] = default_not_found_val.__str__()
            else:
                try:
                    match = search(pattern, self._reference)
                    extracted[key] = match.group(0) if match else default_not_found_val.__str__()
                except rer:
                    extracted[key] = default_not_found_val.__str__()
        return extracted


def construct_extract_pattern(start, end):
    if all([start is None, end is None]):
        return None
    start = f"(?<={start})" if start is not None else ""
    end = f"(?={end})" if end is not None else ""
    return start + ".*" + end
