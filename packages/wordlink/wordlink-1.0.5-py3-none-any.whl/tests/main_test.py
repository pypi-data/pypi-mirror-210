import unittest
import os
import sys
from io import StringIO
from contextlib import redirect_stdout

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from wordlink.__main__ import WordLinkGenerator


class WordLinkGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = WordLinkGenerator("test", "test_directory", "output.html")
        self.test_dir = 'test_directory'
        os.makedirs(self.test_dir, exist_ok=True)
        self.file_path = os.path.join(self.test_dir, 'test_file.txt')
        with open(self.file_path, 'w') as file:
            file.write('This is a test file.\nAnother line with test word.\n')

    def tearDown(self):
        os.remove(self.file_path)
        os.rmdir(self.test_dir)

    def capture_console_output(self, func, *args, **kwargs):
        # Capture the standard output
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            # Call the function with the provided arguments
            func(*args, **kwargs)
        finally:
            # Restore the standard output
            sys.stdout = sys.__stdout__

        # Get the captured output value
        return captured_output.getvalue()

    def test_find_word_locations(self):
        generator = WordLinkGenerator('test', self.test_dir, None)
        locations = generator.find_word_locations(self.file_path)
        expected_locations = [
            (self.file_path, 1, 'This is a test file.', 10),
            (self.file_path, 2, 'Another line with test word.', 18)
        ]
        self.assertEqual(locations, expected_locations)

    def test_generate_links_output_file(self):
        generator = WordLinkGenerator('test', self.test_dir, 'output.html')
        generator.generate_links()

        self.assertTrue(os.path.isfile('output.html'))

        with open('output.html', 'r') as file:
            output_text = file.read()
            self.assertIn('<html>', output_text)
            self.assertIn('<table>', output_text)
            self.assertIn('<th>File</th>', output_text)
            self.assertIn('<th>Line</th>', output_text)
            self.assertIn('<th>Text</th>', output_text)
            self.assertIn('</table>', output_text)
            self.assertIn('</html>', output_text)

    def test_generate_links_console(self):
        # Sample word_locations data
        word_locations = [
            ("/Users/bloom/wordlink/tests/test_directory/test_file.txt", 1, "This is a test file.", 0),
            ("/Users/bloom/wordlink/tests/test_directory/test_file.txt", 2, "Another line with test word.", 15)
        ]

        # Expected console output
        expected_output = (
            "+----------------------------------------------------------+------+------------------------------+\n"
            "|                           File                           | Line |             Text             |\n"
            "+----------------------------------------------------------+------+------------------------------+\n"
            "| /Users/bloom/wordlink/tests/test_directory/test_file.txt |  1   |     This is a test file.     |\n"
            "| /Users/bloom/wordlink/tests/test_directory/test_file.txt |  2   | Another line with test word. |\n"
            "+----------------------------------------------------------+------+------------------------------+"
        )

        # Generate the console output
        console_output = self.capture_console_output(self.generator.output_links_console, word_locations)

        # Compare the expected and actual output
        self.assertEqual(expected_output.strip(), console_output.strip())

if __name__ == '__main__':
    unittest.main()
