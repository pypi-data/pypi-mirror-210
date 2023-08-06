import unittest
from src.slimpy import REM
from core import fragmentation, pattern_constructor

test_fragment_with_2del = {
    3: [['', 'est'], ['t', 'st'], ['te', 't'], ['tes', '']],
    2: [['', '', 'st'], ['', 'e', 't'], ['', 'es', ''], ['t', '', 't'], ['t', 's', ''], ['te', '', '']]
}
fragments = ['', 'tr', 'ng', '']
fragments_expected_pattern = '.{0,1}tr.*?ng.{0,1}'
reference = ['This', 'is', 'a', 'reference,', 'it', 'contain', '8', 'string']
REM_ref = """This
is
a
reference,
it
contain
8
string"""


class TestCore(unittest.TestCase):
    def test_fragments(self):
        self.assertEqual(fragmentation('test', 2), test_fragment_with_2del, "fragmentation test fail")

    def test_constructor(self):
        self.assertEqual(pattern_constructor(fragments), fragments_expected_pattern,
                         "pattern construction test fail")

    def test_REM_ref(self):
        rem = REM()
        rem.set_reference(reference)
        self.assertTrue(all(ref in REM_ref for ref in reference), "reference constructor fail")


if __name__ == "__main__":
    unittest.main()
