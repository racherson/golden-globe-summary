# Golden Globes Summary
Reads tweets about the Golden Globes and returns predicted results.

    Github: https://github.com/racherson/golden-globe-summary

## Install spaCy:

    $ pip install -U spacy

    $ python -m spacy download en
    
## API:
Contains pre-ceremony, main, and "get" functions. Pre-ceremony and main functions must be run using the data for any given year before any "get" functions for those year's results work. Only one year can be run at a time, and the year must be between 2000 and 2020. If there are multiple 'ggXXXX.json' files in the folder, it will run the earliest year.
    
    pre_ceremony(): This function processes golden globes data by looking for json files of tweets from the years 2000-2020. The json tweet files must be of the form 'ggXXXX.json'. After processing the data, new json files will be created for each year, titled 'processed_ggXXXX.json'.
    main(): Calls pre_ceremony to process data, then uses the processed json to find the hosts, awards, winner, nominees, and presenters for that year using Natural Language Processing techniques. The answers are then put in the file titled 'answerXXXX.json'. This answer file is used in the "get" functions to extract different parts.

The "get" functions for hosts, awards, winner, nominees, and presenters 

    get_hosts(year): Takes in award year and returns a list of one or more strings (host names).
    get_awards(year): Takes in award year and returns a list of strings (award names).
    get_winner(year): Takes in award year and returns dictionary of award strings to single winner string mappings.
    get_nominees(year): Takes in award year and returns dictionary of award strings to list of string (nominee name) mappings.
    get_presenters(year): Takes in award year and returns dictionary of award strings to list of string (presenter name) mappings.
    
