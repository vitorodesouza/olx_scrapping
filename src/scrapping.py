from bs4 import BeautifulSoup
from random import randint
from time import sleep
from src.config import load_config
import src.dbconnection as db
import logging, random, sys, os, json, requests

# Configure the logging settings
log_filename = 'scrapping.log'

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

## ------------------------------------------------------------------------------------------------------------------
# Function to filter the ads that are olx advertisement and not cars
def filter_advertising(json_list):
    """
    Function to filter the ads that are olx advertisement and not cars.

    Parameters
    ----------
    json_list : List
        DESCRIPTION: List of dictionaries with the scrapped data.

    Returns
    -------
    List
        DESCRIPTION: List of dictionaries with the scrapped data.

    """
    list_filtered = []
    for ad in json_list:
        if 'advertisingId' not in ad:
            list_filtered.append(ad)
    return list_filtered
## ------------------------------------------------------------------------------------------------------------------


## ------------------------------------------------------------------------------------------------------------------
# Function to insert scrapped data into a database
def insert_in_database(state, model, brand, json_list, database, features,list_type_features, list_type_features_map):
    '''
    Function to prepare scrapped data and insert it into the dabase.

    Parameters
    ----------
    json_list : List
        DESCRIPTION: List of dictionaries with the scrapped data.
    database : Dictionary
        DESCRIPTION: Database configuration.
    features : Dictionary
        DESCRIPTION: Dictionary with the features of the scrapped data.
    list_type_features : Dictionary
        DESCRIPTION: Dictionary with the list type features of the scrapped data.
    list_type_features_map : Dictionary
        DESCRIPTION: Dictionary with the list type features map of the scrapped data.

    Returns
    -------
    None.

    '''
    
    columns_list = []
    values_list = []
    # Iterate over the json_list and create a list of tuples with the values of the features
    for ad in json_list:
        # Initialize values and columns with the state information for all values inserted into the table
        columns = ['state','model','brand']
        values = [state,model,brand]
        for feature in features:
            if feature in list_type_features:
                for list_ad in ad[features[feature]]:
                    if list_ad[list_type_features_map[feature]['Column']] in list_type_features[feature]:
                        columns.append(features[feature]+'_'+list_ad[list_type_features_map[feature]['Column']])
                        values.append(list_ad[list_type_features_map[feature]['Value']])
            else:
                columns.append(features[feature])
                values.append(ad[features[feature]])
        values_list.append(values)
        columns_list.append(columns)

    # Insert data into the database
    db.insert_flex(
        database=database['database'],
        usr=database['username'],
        password=database['password'],
        table_name=database['tables']['scrap_table'],
        hostname=database['host'],
        port=database['port'],
        columns_list=columns_list,
        values_list=values_list,
        batch_commit=False,
        ignore_duplicates=True
    )
## ------------------------------------------------------------------------------------------------------------------


## ------------------------------------------------------------------------------------------------------------------
# Function to scrap data from Olx Website
def ScrapCars_Olx(brand='jeep', model='compass',list_states=['sc'], save_in_database = True, config_file=''):
    
    '''
    Function to scrap cars ads data from Olx Website

    Parameters
    ----------
    brand : String
        DESCRIPTION: Manufacturer's name.
        The default is 'jeep'.
    
    model : String
        DESCRIPTION: Car model's name.
        The defaul is 'compass'.
    
    list_states : List[String]
        DESCRIPTION: List of states to scrap.
        The default is ['sc'].
    
    save_in_database : Boolean
        DESCRIPTION: Wheather or not to save the scrapped data into a database.
        The default is True.
    
    config_file : Dictionary
        DESCRIPTION: Json configuration file loaded from the project folder.

    Returns
    -------
    None.
    '''

    # Website link pattern to scrap
    # https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/jeep - Manufacturer Jeep
    # https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/jeep/compass - Model Compass
    # https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/jeep/compass/estado-ac - State AC
    # https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/jeep/compass/estado-al - State AL
    # https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/jeep/compass/estado-al?sf=1&o=2 - Second page (sf=1 orders the search by the publish date)
    # https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/jeep/compass/estado-al?sf=1&o=3 - Third page
    # https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/{manufac}/{model}/estado-{state}?sf=1&o={page} - Link pattern to scrap

    print(f'\nSTART: Scrapping {brand} {model} ads from Olx website')
    logging.info(f'START: Scrapping {brand} {model} ads from Olx website')

    # Loads the configuration file
    try:
        logging.info('Loading configuration file')
        if config_file != '':
            config = config_file
        else:
            config = load_config()
        # Load the database configuration
        database = config['database']
        # Define the features we want to scrap
        features = config['scraping_parameters']['features_to_scrap']
        list_type_features = config['scraping_parameters']['list_type_features']
        list_type_features_map = config['scraping_parameters']['list_type_features_map']
    except Exception as e:
        print('Error loading configuration file: ' + str(e))
        logging.error('Error loading configuration file: ' + str(e))
        return

    # We are specifying that we are sending a request with a real user agent, 
    # this is a common way to avoid being blocked by the server.
    hdr= {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
    }

    
    errors = {
        'total':0
    }

    # We are going to loop through all the states and pages
    for state in list_states:
        
        print('*******************************************')
        print('New state: ' + state)
        logging.info(f'Started scrapping new state {state}')

        # Initializing the scrapping errors counter
        errors[state] = 0

        # 100 is the maximum number of pages OLX allows in a search criteria but 
        # the great majority of the times the number of pages won't exceed this number
        # if we filter our search by manufacturer, model and state
        for page_number in range(1, 100):
            website = f'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios/{brand}/{model}/estado-{state}?sf=1&o={page_number}'
            print('Scrapping page: ' + str(page_number))
            print(website)

            try:
                # We are requesting the website with the specified headers
                response_page = requests.get(website, headers=hdr)

                # Checking if the request was redirected
                # If it was, it means that the search criteria was not valid and the server redirected the request to the root url (https://www.olx.com.br)
                if response_page.history:
                    print('*************************************************************')
                    print(f"Request was redirected")
                    print('Please check your inputs and try again')
                    for resp in response_page.history:
                        print(f"Redirected from: {resp.url}")
                    print(f"Final URL after redirection: {response_page.url}")
                    logging.error(f'Error: Tried to request {website} but got a redirection. Please check your inputs and try again')
                    sys.exit(1)
                
                # If the request was not redirected, we continue the scrapping process
                else:
                    soup = BeautifulSoup(response_page.text, 'html.parser')
                    script_data = soup.find('script', {'id': '__NEXT_DATA__'})
                    data = json.loads(script_data.contents[0])
                    ads = data['props']['pageProps']['ads']
            except Exception as e:
                print(f'\nError scrapping: ' + str(e))
                logging.error(f'Error scrapping page: {website}\n' + str(e))
                errors['total'] += 1
                errors[state] += 1
                continue

            if len(ads) == 0:
                print(f'No ads found, stopping scrapping {state} state')
                print(f'Total pages scrapped in {state}: {page_number-1}')
                break
            else:
                filtered_ads = filter_advertising(ads)
            
            # We are going to save the data in a file or in the database
            if save_in_database:
                try:
                    insert_in_database(state, model, brand, filtered_ads, database, features, list_type_features, list_type_features_map)
                except Exception as e:
                    print('Error inserting scrapped data into the database' + str(e))
                    logging.error('Error inserting scrapped data into the database' + str(e))
                    errors['total'] += 1
                    errors[state] += 1
                    continue 
            else:
                try: 
                    if not os.path.exists('./data'): 
                        os.makedirs('./data')
                    with open(f'./data/{model}_{brand}_{state}.txt', 'a') as f: 
                        for ads in filtered_ads:
                            json.dump(ads, f)
                            f.write('\n')
                except Exception as e:
                    print('Error saving scrapped data into a file' + str(e))
                    logging.error('Error saving scrapped data into a file' + str(e))
                    errors['total'] += 1
                    errors[state] += 1
                    continue 
        
        # Sleep because it's good manners to not flood the server with requests 
        # We avoid being blocked as well
        sleep(random.uniform(1,2))

    
    print('FINISH: Logging scrip has finished with the following errors: ' + str(errors))
    logging.info('FINISH: Logging scrip has finished with the following errors: ' + str(errors))
## ------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    print('Functions to scrap data from OLX')