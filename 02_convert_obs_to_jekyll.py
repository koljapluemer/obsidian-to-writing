import os
import re

OBS_PATH = "/home/b/MEGA/Obsidian/Zettelkasten/"
FILE_PATH = "/home/b/MEGA/Obsidian/Zettelkasten/Intelligent Tutoring Systems﹕Entry Points (0).md"
OUTPUT = "output/test.md"
MISSING_CITATIONS = "output/missing_cite.md"
MISSING_DEFINITIONS = "output/missing_def.md"

def main():
    # convert every [[]] in a link to a <dfn> tag
    with open(FILE_PATH, "r") as f:
        lines = f.read()
        lines, citations, missing_citations = expand_citations(lines)

        with open(MISSING_CITATIONS, "w") as missing_cite_file:
            for missing_citation in missing_citations:
                missing_cite_file.write(f'- [ ] {missing_citation}\n')

        # definitions
        lines, definitions, missing_definitions = expand_terms(lines)

        # terms may include more terms, or citations, so continously expand
        # check if '[[' anywhere in the values of definitions dict: NOW:!!!
        while any('[[' in value for value in definitions.values()):
            print("continously expanding")
            for key, value in definitions.items():
                print("key", key)
                print("value", value)
                if '[[' in value:
                    print("found a link")
                    new_definition, new_definitions, new_missing_definitions = expand_terms(value)
                    definitions[key] = new_definition
                    for new_key, new_value in new_definitions.items():
                        # only if not in dict already, add
                        if new_key not in definitions:
                            definitions[new_key] = new_value
                    missing_definitions += new_missing_definitions



                

        with open(MISSING_DEFINITIONS, "w") as missing_def_file:
            for missing_definition in missing_definitions:
                missing_def_file.write(f'- [ ] {missing_definition}\n')
        
        with open(OUTPUT, "w") as write_file:
            write_file.write(lines)
            
            write_file.write("\n\n")
            write_file.write("## Terms")
            write_file.write("\n\n")

            for key, definition in definitions.items():
                write_file.write('- ' + definition)
                write_file.write("\n")

            write_file.write("\n\n")
            write_file.write("## Citations")
            write_file.write("\n\n")

            for key, citation in citations.items():
                write_file.write('- ' + citation)
                write_file.write("\n")


def expand_citations(text):
    citations = {}
    missing_citations = []
    citation_counter = 0
    # citations
    all_citations = re.findall(r'\@\[\[(.*?)\]\]', text)
    for citation in all_citations:
        print("doing citation", citation)
        cited_file = citation.split('|')[0]
        id_cleaned = re.sub(r'\W+', '', cited_file).lower()

        print_citation = hunt_citation(cited_file)

        if citation:
            definition = f'<dfn id="citation-{id_cleaned}">**[{citation_counter}]** {print_citation}</dfn>'
            citations[id_cleaned] = definition
        else:
            missing_citations.append(cited_file)

        replace_with = f'<a href="#citation-{id_cleaned}">[{citation_counter}]</a>'
        search_term = f'@[[{citation}]]'
        text = text.replace(search_term, replace_with)
        citation_counter += 1

    # print(text)
    return text, citations, missing_citations

def expand_terms(text):
    all_links = re.findall(r'\[\[(.*?)\]\]', text)
    definitions = {}
    missing_definitions = []

    for link in all_links:
        split = link.split('|')
        id = split[0]
        # replace all whitespaces and non alphanumeric with, also all lowercase
        id_cleaned = re.sub(r'\W+', '', id).lower()
        used_form = split[-1]

        definition = hunt_term(id)
        # only replace if we found a definition
        # otherwise replace only the markdown link
        if definition:
            replace_with = f'<a href="#definition-{id_cleaned}">{used_form}</a>'
            text = text.replace(f'[[{link}]]', replace_with)

            definition = f'<dfn id="definition-{id_cleaned}">{id}:{definition}</dfn>'
            definitions[id_cleaned] = definition
        else:
            replace_with = f'{used_form}'
            text = text.replace(f'[[{link}]]', replace_with)

            missing_definitions.append(id)

    return text, definitions, missing_definitions



def hunt_citation(cited_file):
    # TODO: make this recursive
    # open cited_file
    # if file does not exist, immediately return Null
    file_path = OBS_PATH + cited_file + ".md"
    if not os.path.isfile(file_path):
        return None
    with open(file_path, "r") as f:
        # go through lines until you find 'citation:'
        # after that, integrate properties into dict
        citation_found = False
        citation_data = {}
        for line in f:
            # print("line", line)
            if 'citation:' in line:
                citation_found = True
            if citation_found:
                if '---' in line:
                    break
                if ':' in line:
                    key, value = line.split(':')[0], ":".join(line.split(':')[1:])
                    citation_data[key.strip()] = value.strip()
        if citation_found:
            citation_string = f"*{citation_data['title']}*"
            if 'author' in citation_data:
                citation_string += f", {citation_data['author']}"
            if 'year' in citation_data:
                citation_string += f", {citation_data['year']}"
            if 'journal' in citation_data:
                citation_string += f", {citation_data['journal']}"
            if 'doi' in citation_data:
                citation_string += f", <https://doi.org/{citation_data['doi']}>"
            if 'url' in  citation_data:
                citation_string += f", <{citation_data['url']}>"
            if 'note' in citation_data:
                citation_string += f", {citation_data['note']}"

            return citation_string
        else:
            return None

def hunt_term(cited_file):
        # same as hunt_citation, but we're looking for a definition
        # which is marked by being the first line starting with "- *" and ending with "*"
        file_path = OBS_PATH + cited_file + ".md"
        if not os.path.isfile(file_path):
            return None
        with open(file_path, "r") as f:
            for line in f:
                # print("line", line)
                if '- *' in line:
                    return line[1:]
            return None







if __name__ == "__main__":
    main()