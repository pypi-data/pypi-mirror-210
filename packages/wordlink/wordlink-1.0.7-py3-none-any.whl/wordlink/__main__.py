import os
import argparse
from fuzzysearch import find_near_matches
from prettytable import PrettyTable


class WordLinkGenerator:
    def __init__(self, search_term, search_directory, output_file):
        self.search_term = search_term
        self.search_directory = search_directory
        self.output_file = output_file

    def find_word_locations(self, file_path):
        word_locations = []
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line_num, line in enumerate(lines, start=1):
                matches = find_near_matches(self.search_term, line, max_l_dist=1)
                for match in matches:
                    word_locations.append((file_path, line_num, line.strip(), match.start))

        return word_locations

    def generate_links(self):
        all_word_locations = []
        for root, dirs, files in os.walk(self.search_directory):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.abspath(os.path.join(root, file))
                    word_locations = self.find_word_locations(file_path)
                    all_word_locations.extend(word_locations)

        if self.output_file:
            self.output_links_html(all_word_locations)
        else:
            self.output_links_console(all_word_locations)

    def output_links_html(self, word_locations):
        output_lines = []
        for location in word_locations:
            file_path, line_num, line_text, word_index = location
            link = f'<a href="{file_path}#L{line_num}">{line_text}</a>'
            output_lines.append(
                f'    <tr>\n'
                f'        <td>{file_path}</td>\n'
                f'        <td>{line_num}</td>\n'
                f'        <td>{link}</td>\n'
                f'    </tr>'
            )

        output_text = '''
        <html>
        <head>
            <style>
                table {{border-collapse: collapse;}}
                th, td {{border: 1px solid black; padding: 8px;}}
            </style>
        </head>
        <body>
            <table>
                <tr>
                    <th>File</th>
                    <th>Line</th>
                    <th>Text</th>
                </tr>
                {rows}
            </table>
        </body>
        </html>
        '''.format(rows='\n'.join(output_lines))

        with open(self.output_file, 'w') as file:
            file.write(output_text)

        print(f"Output written to {self.output_file}")

    def output_links_console(self, word_locations):
        output_table = PrettyTable(["File", "Line", "Text"])
        for location in word_locations:
            file_path, line_num, line_text, word_index = location
            output_table.add_row([file_path, line_num, line_text])

        output_table.format = True
        print(output_table)


def main():
    parser = argparse.ArgumentParser(description='Word Link Generator')
    parser.add_argument('search_term', help='Search term')
    parser.add_argument('search_directory', help='Search directory')
    parser.add_argument('-o', '--output_file', help='Output file')

    args = parser.parse_args()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    search_directory = os.path.join(current_dir, args.search_directory)
    output_file = os.path.join(current_dir, args.output_file) if args.output_file else None

    generator = WordLinkGenerator(args.search_term, search_directory, output_file)
    generator.generate_links()


if __name__ == '__main__':
    main()
