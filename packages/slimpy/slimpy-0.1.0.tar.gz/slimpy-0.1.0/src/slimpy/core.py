"""
-   Contain the core class and function to perform fragmentation.

-   Fragmentation done by slicing a string using the index as delimiter,
    for example a string "chorocter" that sliced at index 2 and 4
    (that is, two delimiter at index 2 and 4) will have fragments that has
    3 fragment which is ["ch", "r", "cter"].
"""
from time import sleep
from typing import Optional, Iterator
from warnings import warn


def fragmentation(string: str, delimiter_count: int,
                  string_length: Optional[int] = None) -> dict:
    """Return a dictionary of List of fragments of string.
    The returned dictionary "key: value" format is
    {
        int:
            [
                [str, ...],
                [str, ...],
                ...
            ], ...
    }
    to be more precise:
    {
        string_length - how many delimiter used:
            [
                [fragment, ...],
                [fragment, ...],
                ...
            ],
        ...
    }
    """
    string_length = len(string) if string_length is None else string_length
    frag_dict = {}
    for i in range(1, delimiter_count + 1):
        frag_dict[string_length - i] = slicer(string, i + 1, i + 1,
                                              string_length - (i - 1))
    return frag_dict


def slicer(word, ori_factor, indicator_factor, length, start=0,
           new_list=None, template_list=None):
    """ Slicer engine for fragmentation """
    if new_list is None:
        new_list, template_list = [], []

    if indicator_factor == 1:
        word_fragment = word[start:length]
        new_end_list = new_list.copy()
        new_end_list.append(word_fragment)
        template_list.append(new_end_list)
    else:
        for i in range(start, length):
            word_fragment = word[start:i]
            new_end_list = new_list.copy()
            new_end_list.append(word_fragment)
            slicer(word, ori_factor, indicator_factor - 1, length + 1, i + 1,
                   new_end_list, template_list)

    if ori_factor == indicator_factor:
        return template_list


def count_delimiter(string_length: int, dp: float) -> int:
    """
    Translate how many delimiter in whole number (integer) from percentage

    :param string_length: The length of string
    :param dp: Delimiter percentage

    :return: How many delimiter will be used to slice a string
    """
    return int((string_length * dp) + 0.3)


def user_type_check(param_name, references, accepted_type):
    msg = False
    for i in range(len(param_name)):
        name = param_name[i]
        val = references[name]
        if not isinstance(val, accepted_type[i]):
            msg = f'Parameter {name} expect argument of type {accepted_type[i]} got {val} instead.'
            break
    return msg


class Fragment:
    """
    -   A class that perform fragmentation, permutation that compute
        any possible combination of fragment (slice of string).

    -   Fragmentation used the index as delimiter(s) then the delimiter
        incremented to create any possible combination of fragments.
    """

    def __init__(self, string: str, delimiter_percentage: float = 0.35,
                 delimiter_limit: Optional[int] = 5):
        """
        :param string: String in question that will be fragmented.

        :param delimiter_percentage: Percent delimiter, determine how many delimiter
            will be used, which is determined by multiply the value and the length of
            the string.

        :param delimiter_limit: The maximum number of how many delimiter allowed.

        :exception AssertionError: If any illegal argument passed.
        """
        # User Input Assertion
        all_var = ["string", "delimiter_percentage", "delimiter_limit"]
        accepted_type = [str, float, (type(None), int)]
        check_type = user_type_check(all_var, locals(), accepted_type)
        if check_type:
            raise AssertionError(check_type)
        #
        self.str_len = len(string)
        self.str = string
        self.tolerance = count_delimiter(self.str_len, delimiter_percentage)
        #
        if type(delimiter_limit) is int:
            assert delimiter_limit > 0, f'Parameter "{all_var[1]}" must be an integer ' \
                                        f'greater than 0, got {delimiter_limit} instead'
            if delimiter_limit > 8:
                warn('"delimiter_limit" bigger than 8 may exceed the memory capacity of your pc'
                     'and it might be slow as hell. Further development of this library will'
                     'address this issue. For now it is advised you lower the limit to 7 or 6.'
                     'Will continue the execution in 5 SECONDS')
                sleep(5)
            self.tolerance = delimiter_limit if self.tolerance > delimiter_limit else self.tolerance
        assert 0 < delimiter_percentage < 1, f'Parameter "{all_var[2]}" must be fractional number ' \
                                             f'between 0 and 1, got {delimiter_percentage} instead'

        self._fragments = fragmentation(string, self.tolerance, self.str_len)

    def iterate_fragment(self, re_Pattern: bool = False) -> Iterator:
        """
        A generator function to iterate the combination of fragments.

        :param re_Pattern: If True, yield regular expression pattern constructed from fragments, otherwise
            yield list of fragment.
        :return : generator object that either iterate list (fragments) or str (regular
            expression pattern).
        """
        if len(self._fragments) == 0:
            pass
        else:
            for key in key_of_fragment_dict(self._fragments):
                for fragments in self._fragments[key]:
                    yield pattern_constructor(fragments) if re_Pattern else fragments

    def __str__(self):
        return f'\nFragments object for : {self.str}' \
               f'\nDelimiter count      : {self.tolerance}'


def key_of_fragment_dict(dict_, iterate_backward=False):
    """This function ensure that iteration of fragments done in incrementally manner"""
    key = list(dict_.keys())
    key.sort()
    if not iterate_backward:
        key.reverse()
    return key


def pattern_constructor(list_):
    """Construct a pattern based on fragments provided"""
    # filter fragment that has length greater than 0
    non_0_fragment = [frag for frag in list_ if len(frag) > 0]

    # count how many trailing fragment that has 0 length
    count_0_start = count_leading_0(list_) if len(list_[0]) == 0 else None
    count_0_end = count_leading_0(list_, True) if len(list_[-1]) == 0 else None

    pattern = r''
    pattern = pattern + '.{0,%d}' % count_0_start if count_0_start is not None else pattern
    pattern = pattern + '.*?'.join(non_0_fragment)
    pattern = pattern + '.{0,%d}' % count_0_end if count_0_end is not None else pattern

    return pattern


def count_leading_0(list_, count_backward=False):
    length = len(list_)
    start = -1 if count_backward else 0
    it_jump = -1 if count_backward else 1
    count = 0
    for f in range(start, length * it_jump, it_jump):
        if len(list_[f]) == 0:
            count += 1
        else:
            break
    return count
