import yaml
import os

def main():
    # Load the YAML config file
    with open('config.yaml', 'r') as f:
        config = yaml.full_load(f)

    # load the file to convert
    with open(os.path.join(config['obsidian-path'], config['obsidian-file']), 'r') as f:
        obs = f.read()
        print(obs)


if __name__ == '__main__':
    main()