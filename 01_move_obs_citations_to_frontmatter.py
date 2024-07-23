import yaml
import os
import re



def main():
    # Load the YAML config file
    with open('config.yaml', 'r') as f:
        config = yaml.full_load(f)

    # walk all md files in the obsidian path
    for root, dirs, files in os.walk(config['obsidian-path']):
        for file in files:
            citation = False
            if file.endswith(".md"):
                bibtex = []
                file_path = os.path.join(root, file)
                lines_of_file_clean = []

                with open(file_path, "r") as f:
                    # if you find the substring '## Citation', copy everything after to string
                    # loop lines
                    for line in f:
                        if citation:
                            bibtex.append(line)
                        if "## Citation" in line:
                            print(f'found citation in {file_path}')
                            citation = True
                        if not citation:
                            lines_of_file_clean.append(line)

                # make a yaml frontmatter object from the bibtex_string
                # also, delete citation from within file
                if citation:
                    with open(file_path, "w") as write_file:
                        nr_of_separators = 0
                        for i, line in enumerate(lines_of_file_clean):
                            if '---' in line:
                                print("found ---")
                                nr_of_separators += 1
                            if i < len(lines_of_file_clean) - 1:
                                if '---' in lines_of_file_clean[i+1] and nr_of_separators == 1:
                                    print("writing citation")
                                    # write line citation:
                                    write_file.write("citation:\n")
                                    for citation_line in bibtex:
                                        print(citation_line)
                                        # if empty line, skip
                                        if citation_line == "":
                                            continue
                                        # if line contains @, save type and key
                                        if '@' in citation_line and '{' in citation_line:
                                            # @article{barnett2014virtual,
                                            # becomes
                                            #  - type: article
                                            #  - key: barnett2014virtual
                                            entry_type = citation_line.split("{")[0].replace("@", "").strip().replace("},", "").replace("{", "").replace("}", "")
                                            print("split {:", citation_line.split("{"))
                                            key = citation_line.split("{")[1].split(",")[0].strip().replace("{", "").replace("},", "").replace("}", "")
                                            write_file.write(f"  - type: {entry_type}\n")
                                            write_file.write(f"    key: {key}\n")
                                        # else, split line into key and value
                                        elif '{' in citation_line and '=' in citation_line:
                                            # author={Barnett, Susan M},
                                            # becomes
                                            #   - author: 'Barnett, Susan M'
                                            key = citation_line.split("=")[0].strip()
                                            print("split = :", citation_line.split("="))
                                            value = citation_line.split("=")[1].strip().replace("},", "").replace("{", "").replace("}", "")
                                            write_file.write(f"    {key}: '{value}'\n")
                            write_file.write(line)
                    

if __name__ == '__main__':
    main()