# OLX.com Car Ads Scraper
## Script that allows you to scrap car ads data from OLX.com

![GitHub](https://img.shields.io/github/license/vitorodesouza/olx_scrapping)
![GitHub last commit](https://img.shields.io/github/last-commit/vitorodesouza/olx_scrapping)

## Overview

This Python script allows you to scrape car ads data from OLX.com, a dynamically generated website that uses JavaScript to display data. You can use this script to collect car listings based on brand and model. It also provides an option to save the scraped data directly into a PostgreSQL database.

## Features

- Scrapes car ads data from OLX.com.
- Provides a command-line interface for easy usage.
- Supports scrapping by car brand and model.
- Supports scrapping by a list of states.
- Supports storing data directly into a PostgreSQL database.
- Can initialize a new PostgreSQL database and table for storing data.
- Follows the rules defined in `robots.txt` for web scraping.

## Requirements

Before using this script, ensure you have the following dependencies installed:

- Python 3.x
- Beautiful Soup
- Requests
- psycopg2
- pandas

You also need to have a PostgreSQL server installed as the script assumes its presence.

## Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/vitorodesouza/olx_scrapping
   ```

2. Create a virtual environment and install the required Python libraries inside the project's folder:

    ```bash
    python -m venv ~/.venv # Create a virtual environment
    source .venv/bin/activate # Activate your virtual environment (if you're running linux)
    .venv/Scripts/activate.bat # (if you're running cmd in windows)
    pip install -r requirements.txt # Install the project's requirements
    ```

3. Update the database configuration in config.json with your PostgreSQL credentials.

Use the config_example.json file as template and replace with your PostgreSQL credentials.

## Usage

1. Initialize the Project

    You can initialize the project by creating a new PostgreSQL database and table:
    ```bash
    python OlxScrapping.py --init
    ```

2. Scraping Data

    To scrape car ads data, use the following command:

    ```bash
    python OlxScrapping.py --scrap -b <brand> -m <model> -s <state1> <state2> ...
    ```

    Replace <brand> and <model> with the desired car brand and model, and <state1> <state2> ... with the list of states you want to scrape data from.

3. Save Data to Database Option

    ```bash
    python OlxScrapping.py --scrap -b <brand> -m <model> -s <state1> <state2> ... -db
    ```

    If you don't choose this option, the script will save the data into .txt files inside the data folder

## License

GNU General Public License (GPL) Version 3

The GNU General Public License (GPL) is a free, open-source software license that allows you to share and modify this software. It grants you the following rights:

- The freedom to run the program for any purpose.
- The freedom to study how the program works and adapt it to your needs.
- The freedom to redistribute copies so you can help others.
- The freedom to improve the program and release your improvements to the public.

For detailed terms and conditions, please refer to the [LICENSE](LICENSE) file in this repository.

## Acknowledgments

Thanks to OLX for providing car ads data.
This project follows web scraping best practices and respects the robots.txt file of OLX.com.