# aurora-roll20-converter
Converts aurora .dnd5e files to json files that can be importet to roll20 using the VTTEhancement suite

### Installation
To install clone the repo to the folder aurora is installed to. the repo should be at the same level as the custom folder which contains aurora's XML files.
Once the repo is set up set up the environment, if running in pycharm simply run `pip install -r requirements.txt` in its virtual environment, otherwise create
a virtual environment, activate it, and again run `pip install -r requirements.txt`

### Running
To run, put the files to be converted in the `input` folder and run `converter.py` this must be run from the virtual environment or pycharm. Once complete the files will be
in the `output` folder.
