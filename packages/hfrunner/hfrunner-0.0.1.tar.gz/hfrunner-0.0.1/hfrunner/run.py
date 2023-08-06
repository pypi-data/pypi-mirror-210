from train_script import run
from ruamel.yaml import load, Loader
config_path = '/'.join(__file__.split('/')[:-1])+'/config.yaml'
with open(config_path, 'rb') as f:
    config = load(f, Loader=Loader)
run(config)