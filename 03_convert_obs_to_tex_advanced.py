import yaml
import os
import re

OBS_PATH =  '/home/b/MEGA/Obsidian/Zettelkasten/'
OBS_FILE =  'thesis expose 3rd draft.md'
OUT_DIR = 'output'
OUT_TEX =  'expose.tex'
OUT_BIB = 'bibliography.tex'
OUT_GLOSSARY = 'glossary.tex'

MISSING_CITATIONS = "output/missing_cite.md"
MISSING_DEFINITIONS = "output/missing_def.md"

def main():

    # load the file to convert
    with open(os.path.join(OBS_PATH, OBS_FILE), 'r') as f:
        obs = f.read()
        obs, citations, missing_citations = expand_citations(obs)

        with open(MISSING_CITATIONS, "w") as missing_cite_file:
            for missing_citation in missing_citations:
                missing_cite_file.write(f'- [ ] {missing_citation}\n')

        # acronyms
        # (special type of definition)
        obs, definitions, missing_definitions = expand_acronyms(obs)

        # definitions
        obs, definitions, missing_definitions = expand_terms(obs)

        # terms may include more terms, or citations, so continously expand
        # check if '[[' anywhere in the values of definitions dict: NOW:!!!
        while any('[[' in value for value in definitions.values()):
            print("continously expanding")
            for key, value in definitions.items():
                if '@[[' in value:
                    print("found a citation")
                    new_definition, new_citations, new_missing_citations = expand_citations(value)
                    definitions[key] = new_definition
                    for new_key, new_value in new_citations.items():
                        # only if not in dict already, add
                        if new_key not in citations:
                            citations[new_key] = new_value
                            print("added new citation", new_key)
                    missing_citations += new_missing_citations
                    continue
                if '[[' in value:
                    print("found a term")
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

        # GLOSSARY
        with open(os.path.join(OUT_DIR, OUT_GLOSSARY), "w") as glossary_file:
            for key, definition in definitions.items():
                glossary_file.write(definition)
                glossary_file.write("\n")
        
        with open(os.path.join(OUT_DIR, OUT_TEX), "w") as write_file:
            write_file.write(obs)


    # Convert the markdown to tex
    tex = convert_md_to_tex(obs)

    # Write the tex file
    with open(os.path.join(OUT_DIR, OUT_TEX), 'w') as f:
        f.write(tex)

def convert_md_to_tex(obs):

    obs = replace_links_to_chapters(obs)

    obs = obs.split('---')[-1]
    # replace headers with wrapping tags like subparagraph{}:
    obs = re.sub(r'^##### (.*)$', r'\\subparagraph{\1}\n\\label{chap:\1}', obs, flags=re.MULTILINE)
    obs = re.sub(r'^#### (.*)$', r'\\paragraph{\1}\n\\label{chap:\1}', obs, flags=re.MULTILINE)
    obs = re.sub(r'^### (.*)$', r'\\subsubsection{\1}\n\\label{chap:\1}', obs, flags=re.MULTILINE)
    obs = re.sub(r'^## (.*)$', r'\\subsection{\1}\n\\label{chap:\1}', obs, flags=re.MULTILINE)
    obs = re.sub(r'^# (.*)$', r'\\section{\1}\n\\label{chap:\1}', obs, flags=re.MULTILINE)

    # replace bold and italic, and `` with texttt
    obs = re.sub(r'\*\*(.*)\*\*', r'\\textbf{\1}', obs)
    obs = re.sub(r'\*(.*)\*', r'\\textit{\1}', obs)
    obs = re.sub(r'``(.*)``', r'\\texttt{\1}', obs)

    return obs


def replace_links_to_chapters(obs):
    # replace links to chapters with \ref{chap:}
    obs = re.sub(r'\[\[#(.*)\]\]', r'\\autoref{chap:\1}', obs)
    return obs


def expand_citations(text):
    citations = {}
    missing_citations = []
    # citations
    all_citations = re.findall(r'\@\[\[(.*?)\]\]', text)
    for citation in all_citations:
        print("doing citation", citation)
        cited_file = citation.split('|')[0]

        print_citation = hunt_citation(cited_file)

        if not citation:
            missing_citations.append(cited_file)

        replace_with = '\cite{' + print_citation + '}'
        search_term = f'@[[{citation}]]'
        text = text.replace(search_term, replace_with)

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

def expand_acronyms(text):
    #     \newglossaryentry{CALL}
    # {
    #     name={call},
    #     description={An Application Programming Interface (API) is a particular set
    #             of rules and specifications that a software program can follow to access and make use of the services and resources provided by another particular software program that implements that API},
    #     first={Computer-Assisted Language Learning (CALL)},
    #     long={Computer-Assisted Language Learning}
    # }
    all_links = re.findall(r'#\[\[(.*?)\]\]', text)
    definitions = {}
    missing_definitions = []

    for link in all_links:
        split = link.split('|')
        id = split[-1]
        # replace all whitespaces and non alphanumeric with, also all lowercase
        id_cleaned = re.sub(r'\W+', '', id).lower()
        used_form = split[-1]

        definition = hunt_term(id)
        # Acronyms are always replaced, we are expecting to just always be #[[Artificial Intelligence|AI]]
        replace_with = '\Gls{' + id_cleaned + '}'
        text = text.replace(f'#[[{link}]]', replace_with)
        # If definition also exists, nice, add that (but only to the glossary, in-text nothing changes)
        glossary_entry = f'\\newglossaryentry{{{id_cleaned}}}\n'
        glossary_entry += '{\n'
        glossary_entry += f'    name={{{id}}},\n'
        glossary_entry += f'    description={{{definition}}},\n'
        # first: "$id ($used_form)"
        glossary_entry +=  '    first={' + id + ' (' + used_form + ')},\n'
        glossary_entry += f'    long={{{used_form}}}\n'
        glossary_entry += '}\n'
        definitions[id_cleaned] = glossary_entry

        if not definition:
            missing_definitions.append(id)

    return text, definitions, missing_definitions

def hunt_citation(cited_file):
    # TODO: make this recursive
    # open cited_file
    # if file does not exist, immediately return Null
    file_path = OBS_PATH + cited_file + ".md"
    if not os.path.isfile(file_path):
        print(f"file {file_path} not found")
        return ""
    with open(file_path, "r") as f:
        # go through obs until you find 'citation:'
        # after that, integrate properties into dict
        citation_found = False
        citation_data = {}
        for line in f:
            if 'citation:' in line:
                citation_found = True
            if citation_found:
                if '---' in line:
                    break
                if ':' in line:
                    key, value = line.split(':')[0], ":".join(line.split(':')[1:])
                    citation_data[key.strip()] = value.replace("'", "").strip()
        if citation_found:
            if 'key' in citation_data:
                return citation_data['key']
        return ""

def hunt_term(cited_file):
        # same as hunt_citation, but we're looking for a definition
        # which is marked by being the first line starting with "- *" and ending with "*"
        file_path = OBS_PATH + cited_file + ".md"
        if not os.path.isfile(file_path):
            return None
        with open(file_path, "r") as f:
            for line in f:
                if '- **' in line:
                    return line[1:].replace("**", "").strip()
            return ""


if __name__ == '__main__':
    main()