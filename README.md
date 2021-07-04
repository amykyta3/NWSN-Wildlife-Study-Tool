# NWSN Wildlife Study helper tool

Scan through your folder of images and pre-load some values into your excel sheet

Automatically groups series of images together and generates "Wildlife event" rows
with some columns pre-loaded.


## Setup Instructions

* Install Python 3.6 or newer: https://www.python.org/
* Download or clone this repository
* Install requirements:
    ```bash
    python3 -m pip install -r requirements.txt
    ```

## Usage

```
./analyzer.py PATH/TO/IMAGES
```

Output is printed to your console where you can copy/paste into your excel sheet.

Disclaimer: Entries will need to be adjusted based on actual wildlife observations!
