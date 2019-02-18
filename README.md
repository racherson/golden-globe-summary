# golden-globe-summary
Reads tweets about the Golden Globes and returns predicted results.

    Github: https://github.com/racherson/golden-globe-summary

Install spaCy:

    $ pip install -U spacy

    $ python -m spacy download en
    
Run gg_api.py file
    - Contains pre-ceremony, main, and get functions. Pre-ceremony and main functions must be run using the data for any given year before any get functions for those year's results work. Only one year can be run at a time, and the year must be between 2000 and 2020. If there are multiple 'ggXXXX.json' files in the folder, it will run the earliest year. 