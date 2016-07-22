import au_pyutils.oututils as out
import unittest
import os

class OutputTestCase(unittest.TestCase):
    """
    Tests for the oututils module
    """
    def test_validator_double_underscores(self):
        self.assertFalse(out.valid_scriptname("p__123_this.py"))

    def test_function_return(self):
        func = out.au_output_path_factory(output_stem='.', output_extension='.p.gz') 
        self.assertEqual(func("do_something"), os.path.abspath("./out_01_do_something.p.gz"))

    def test_get_scriptname(self):
        self.assertEqual(out.get_scriptname(), 'p_01_oututils_tests.py')

    def test_get_prog_numbers_with_many_numbers(self):
        self.assertEqual(out.get_prog_numbers("p_123421_script.py"), "123421")


if __name__=="__main__":
    unittest.main()
