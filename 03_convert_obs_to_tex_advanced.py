import yaml
import os
import re

OBS_PATH =  '/home/b/MEGA/Obsidian/Zettelkasten'
OBS_FILE =  'thesis expose 3rd draft.md'
OUT_DIR = 'output'
OUT_TEX =  'expose.tex'
OUT_BIB = 'bibliography.tex'
OUT_GLOSSARY = 'glossary.tex'


def main():

    # load the file to convert
    with open(os.path.join(OBS_PATH, OBS_FILE), 'r') as f:
        obs = f.read()

    # Convert the markdown to tex
    tex = convert_md_to_tex(obs)

    # Write the tex file
    with open(os.path.join(OUT_DIR, OUT_TEX), 'w') as f:
        f.write(tex)

def convert_md_to_tex(obs):
    obs = obs.split('---')[-1]
    # replace headers with wrapping tags like subparagraph{}:
    obs = re.sub(r'^##### (.*)$', r'\\subparagraph{\1}', obs, flags=re.MULTILINE)
    obs = re.sub(r'^#### (.*)$', r'\\paragraph{\1}', obs, flags=re.MULTILINE)
    obs = re.sub(r'^### (.*)$', r'\\subsubsection{\1}', obs, flags=re.MULTILINE)
    obs = re.sub(r'^## (.*)$', r'\\subsection{\1}', obs, flags=re.MULTILINE)
    obs = re.sub(r'^# (.*)$', r'\\section{\1}', obs, flags=re.MULTILINE)

    # replace bold and italic, and `` with texttt
    obs = re.sub(r'\*\*(.*)\*\*', r'\\textbf{\1}', obs)
    obs = re.sub(r'\*(.*)\*', r'\\textit{\1}', obs)
    obs = re.sub(r'``(.*)``', r'\\texttt{\1}', obs)

    return obs




if __name__ == '__main__':
    main()