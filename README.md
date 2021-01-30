# Compendium Reader
The Compendium Reader is a Google Doc reader that takes in a roughly standard format and converts it into usable YAML, 
because I'm a really big nerd. 

This was originally written entirely on May 16, 2020, but was left uncommitted for an unknown reason. 

## Why? 
For my Dungeons & Dragons games, I like taking notes and, in the case of one particularly epic game, transpiling those game notes into a comprehensive semi-Wiki of information organized into specific groups. However, copy-pasting from Docs is slow and cumbersome and can't be quickly automated. This script is meant to take the Google Doc and parse it down into a more machine-readable format (specifically, yaml).

While the original plan was to use the script to import into a local mediawiki instance, nothing is currently being done with the data. A future plan might be to upload the data to WorldAnvil using a Selenium script or something similar. 

## Some Misc Stuff from the original README
Follow directions for Google API setup here:
https://developers.google.com/drive/api/v3/quickstart/python

`pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`
