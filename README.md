# golden-globe-summary
Reads tweets about the Golden Globes and returns the results

    Github: https://github.com/racherson/golden-globe-summary

Install spacy: 

    $ pip install -U spacy

    $ python -m spacy download en
    
Run gg_api.py file
    - Contains preceremony, main, and get functions. Only one year can be run at a time. If there are multiple gg"year".json files in the folder it will run the earliest year. 