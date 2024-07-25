import yaml
import os
import re

BIBTEX_FILE = "output/citations.bib"


def main():
    # Load the YAML config file
    with open('config.yaml', 'r') as f:
        config = yaml.full_load(f)

    bibtex_string = ""
    # walk all md files in the obsidian path
    for root, dirs, files in os.walk(config['obsidian-path']):
        for file in files:
            citation = False
            if file.endswith(".md"):
                bibtex = []
                file_path = os.path.join(root, file)
                lines_of_file_clean = []

                with open(file_path, "r") as f:
                    # loop lines
                    citation_found = False
                    for line in f:
                        # look for 'citation:'
                        # then get everything until first symbol is a letter or line contains '---'
                        if citation_found:
                            if '---' in line or line[0].isalpha():
                                break
                            bibtex.append(line)
                        if line.startswith('citation:'):
                            citation_found = True
                    if citation_found:
                        bibtex_dict = {}
                        for line in bibtex:
                            # ORIGINAL 

#                             citation:
                                #   - type: article
                                #     key: asher1993learning
                                #     title: 'Learning another language through actions'
                                #     author: 'Asher, James John'
                                #     journal: '(No Title)'
                                #     year: '1993'
                            # GOAL 

                            # @article{agnerPatientEmpowermentCritique2018,
                            #   title = {Patient Empowerment: {{A}} Critique of Individualism and Systematic Review of Patient Perspectives},
                            #   shorttitle = {Patient Empowerment},
                            #   author = {Agner, Joy and Braun, Kathryn L.},
                            #   year = {2018},
                            #   month = dec,
                            #   journal = {Patient Education and Counseling},
                            #   volume = {101},
                            #   number = {12},
                            #   pages = {2054--2064},
                            #   issn = {07383991},
                            #   doi = {10.1016/j.pec.2018.07.026},
                            #   urldate = {2023-07-13},
                            #   langid = {english}
                            # }
                            if '- type:' in line:
                                bibtex_dict['type'] = line.split(':')[1].strip()
                            else:
                                key, value = line.split(':')[0], ":".join(line.split(':')[1:])
                                bibtex_dict[key.strip()] = value.strip()
                        # if key not found, print error and skip
                        if 'key' not in bibtex_dict:
                            print(f"key not found in {file_path}")
                            continue
                        bibtex_string += f"@{bibtex_dict['type']}{{{bibtex_dict['key']},\n"
                        for key, value in bibtex_dict.items():
                            if key not in ['type', 'key']:
                                # if first or last char of value is a quote, remove it
                                if value[0] == "'":
                                    value = value[1:]
                                if value[-1] == "'":
                                    value = value[:-1]
                                bibtex_string += f"  {key} = {{{value}}},\n"
                        bibtex_string += "}\n\n"

    with open(BIBTEX_FILE, 'w') as f:
        f.write(bibtex_string)                   
                        

if __name__ == '__main__':
    main()