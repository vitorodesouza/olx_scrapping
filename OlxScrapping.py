from src.scrapping import ScrapCars_Olx
from src.config import load_config
import src.dbconnection as db
import argparse, sys


## ------------------------------------------------------------------------------------------------------------------
# Function to create the table to store the data
def create_project_table(database,features, list_type_features):

    # Create columns list to prepare the query to create table
    # Starts with id as primary key and the standard columns for the table
    columns = ['id SERIAL PRIMARY KEY', 'state VARCHAR(2)', 'model VARCHAR(25)', 'brand VARCHAR(50)']

    # We add the columns constraints to the columns list
    for feature in features:
        if feature in list_type_features:
            for subfeature in list_type_features[feature]:
                if subfeature == 'mileage':
                    columns.append(f"{features[feature]}_{subfeature} NUMERIC")
                else:
                    columns.append(f"{features[feature]}_{subfeature} VARCHAR(255)")
        else:
            if feature == 'Link':
                columns.append(f'{features[feature]} VARCHAR(500) UNIQUE')
            # elif feature == 'Price':
            #     columns.append(f'{features[feature]} NUMERIC')
            # elif feature == 'Date':
            #     columns.append(f'{features[feature]} TIMESTAMPTZ')
            else:
                columns.append(f'{features[feature]} VARCHAR(255)')

    print(f"Creating table: {database['tables']['scrap_table']}")
    # Try to create the table, if the table already existis it'll just skip this part
    db.create_table(
        database=database['database'],
        usr=database['username'],
        password=database['password'],
        hostname=database['host'],
        port=database['port'],
        table_name=database['tables']['scrap_table'],
        columns=columns
    )
## ------------------------------------------------------------------------------------------------------------------

## ------------------------------------------------------------------------------------------------------------------
## Function to create the database
def create_project_database(database):
    # Try to create the database, if the database already exists it'll return a message but won't affect the init process
    db.create_database(
        database_name=database['database'],
        usr=database['username'],
        password=database['password'],
        hostname=database['host'],
        port=database['port']
    )
## ------------------------------------------------------------------------------------------------------------------

## ------------------------------------------------------------------------------------------------------------------
## Function to initialize the project
def init_project(config):
    database = config['database']
    columns = config['scraping_parameters']['features_to_scrap']
    list_type_features = config['scraping_parameters']['list_type_features']
    create_project_database(database)
    create_project_table(database,columns, list_type_features)
## ------------------------------------------------------------------------------------------------------------------

## ------------------------------------------------------------------------------------------------------------------
## Function to start scrapping data
def scrap(config, args):
    # If the user don't specify the state list
    if args.state is None: list_states = list(config['scraping_parameters']['states'].values())
    # If the user specify the state list
    else: list_states = args.state
    
    ScrapCars_Olx(
        brand=args.brand,
        model=args.model,
        list_states=list_states,
        save_in_database=args.save_in_database,
        config_file=config
    )
## ------------------------------------------------------------------------------------------------------------------

## ------------------------------------------------------------------------------------------------------------------
## Function to parsing scrapping function arguments
def parse_args():
    # Add the arguments for this script
    parser = argparse.ArgumentParser(description='Scrap car ads data from OLX')
    # parser.add_argument('-i', '--init', action='store_true', help='Function to initialize the project')
    parser.add_argument('--scrap', action='store_true', help='Function to scrap data')
    parser.add_argument('--init', action='store_true', help='Function initialize the project')
    parser.add_argument('-b', '--brand', default='jeep', type=str,required=False, help="Car's brand")
    parser.add_argument('-m', '--model', default='compass', type=str,required=False, help="Car's model")
    parser.add_argument('-db', '--save_in_database', action='store_true', default=True, required=False, help='Option to save the data in the database')
    parser.add_argument('--state', nargs='*', default=None, required=False, help='List of states to scrap the data (Separate the states by space). Ex: "sp rj mg"')
    
    return parser.parse_args()
## ------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # Get the arguments
    args = parse_args()

    # Load the config file
    config = load_config()

    # If the user wants to initialize the project
    if args.init: 
        print('Initializing project...')
        init_project(config)
    # If the user wants to scrap data
    if args.scrap:
        print('Function scrap selected')
        scrap(config, args)
    
    # If the user doesn't specify any function
    if not(args.scrap or args.init):
        print('Invalid function name')