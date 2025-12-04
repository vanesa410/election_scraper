# Czech Election Scraper 2017

## Project Description

This Python script downloads the results of the 2017 Czech Chamber of Deputies elections for individual municipalities in a given region and saves them into a CSV file. https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ 

## Installation ofrequired libraries

Install the required libraries from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Running the Project

Run the script by providing the URL of the region page and the name of the output CSV file:

```bash
python script.py <region_URL> <output.csv>
```
If the file was saved successfully, the program prints: "Saved <output.csv>"

### Example:

1. arg: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=13&xnumnuts=7204
2. arg: vysledky_Zlin.csv

```bash
python script.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=13&xnumnuts=7204" "vysledky_Zlin.csv"
```
# election_scraper
