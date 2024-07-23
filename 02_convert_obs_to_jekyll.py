import os
import re

FILE_PATH = "/home/b/MEGA/Obsidian/Zettelkasten/Intelligent Tutoring Systems﹕Entry Points (0).md"
OUTPUT = "output/test.md"

def main():
    # convert every [[]] in a link to a <dfn> tag
    with open(FILE_PATH, "r") as f:
        lines = f.read()
        all_links = re.findall(r'\[\[(.*?)\]\]', lines)
        definitions = []

        for link in all_links:
            split = link.split('|')
            id = split[0]
            # replace all whitespaces and non alphanumeric with, also all lowercase
            id_cleaned = re.sub(r'\W+', '', id).lower()
            used_form = split[-1]

            replace_with = f'<a href="#definition-{id_cleaned}">{used_form}</a>'
            lines = lines.replace(f'[[{link}]]', replace_with)

            definition = f'<dfn id="definition-{id_cleaned}">{id}</dfn>'
            definitions.append(definition)
        
        with open(OUTPUT, "w") as write_file:
            write_file.write(lines)
            write_file.write("\n\n")
            for definition in definitions:
                write_file.write('- ' + definition)
                write_file.write("\n")

if __name__ == "__main__":
    main()