# Obsidian To Writing

- `00`: demo for obs to tex. works via `config.yaml`, currently targeting my expose. feel free to run, non-destructive. pastes in `output`. doesn't have fancy quote hunting yet.
- `01`: semi destructive script looping my zk and moves bibtex that was pasted in into frontmatter. works, but is not perfectly formatted. also that i have to run this script manually is silly.
- `02`: obs to blog, currently hardcoded demo w/ the ITS blog post. has basic quote and acronym hunting.
- `03`: a redo of `00`, attempting to integrate the `02` stuff


- `pandoc --read=markdown --write=latex --output=output/expose.tex  output/expose.md` is pretty smart to use