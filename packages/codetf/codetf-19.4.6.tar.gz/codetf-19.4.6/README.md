

# Installation


To install requirements: `python -m pip install requirements.txt`

To save requirements: `python -m pip list --format=freeze --exclude-editable -f https://download.pytorch.org/whl/torch_stable.html > requirements.txt`

* Note we use Python 3.9.4 for our experiments

The code in augerino_lib is an extension (with our modification) from the original Augerino code https://github.com/g-benton/learning-invariances. The code in data_augmentation/my_training.py is a modification of the pytorch example in https://github.com/pytorch/examples/tree/master/imagenet.

# Running the code 

For remaining experiments: 

Navigate to the corresponding directory, then execute: `python run.py -m` with the corresponding `config.yaml` file (which stores experiment configs).

# License

Consult License.md

