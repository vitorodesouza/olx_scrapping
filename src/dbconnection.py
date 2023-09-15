
import psycopg2 as pg2
import pandas as pd

## ------------------------------------------------------------------------------------------------------------------
# Function to create a database
def create_database(database_name, usr, password, hostname='localhost', port='5432'):

    """
    Parameters
    ----------
    database_name : String

    usr : String
        
    password: String

    Returns
    -------
    None.

    SQL Syntax
    -------

    CREATE DATABASE [IF NOT EXISTS] database_name;
    """

    # query = f"SELECT 'CREATE DATABASE {database_name}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{database_name}');"
    query = f'CREATE DATABASE {database_name}'
    conn = None

    # print(query)

    try:
        # Create a connection with PostgreSQL
        # print('Connecting to the PostgreSQL database...\n')
        conn=pg2.connect(user=usr,password=password, host=hostname, port=port)
        conn.autocommit = True
        with conn.cursor() as cur:
            # Pass in a PostgreSQL query as a string
            # print('Creating database: ' + database_name + '\n')
            cur.execute(query)
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
## ------------------------------------------------------------------------------------------------------------------

## ------------------------------------------------------------------------------------------------------------------
# Function to create a table in a database
def create_table(database, usr, password, table_name, columns, table_constraints = None, hostname='localhost', port='5432'):
    
    """
    Parameters
    ----------
    table_name : String
    
    columns : List of Strings
        DESCRIPTION: Column's name, data type and column constraint separeted by comma
        
    table_constraints: String
        DESCRIPTION: Table's constraints.

    Returns
    -------
    None.

    SQL Syntax
    -------
    
   CREATE TABLE [IF NOT EXISTS] table_name (
   column1 datatype(length) column_contraint,
   column2 datatype(length) column_contraint,
   column3 datatype(length) column_contraint,
   table_constraints
   );
   """
    query = 'CREATE TABLE IF NOT EXISTS ' + table_name + ' ( ' + (', '.join(columns)) + ((', ' + table_constraints) if table_constraints else "") + ' ) ;'
    conn = None
    
    # print(query)
    
    try:
        # Create a connection with PostgreSQL
        # print('Connecting to the PostgreSQL database...\n')
        conn=pg2.connect(database=database, user=usr,password=password, host=hostname, port=port)
        with conn.cursor() as cur:
            # Pass in a PostgreSQL query as a string
            # print('Creating table: ' + table_name + '\n')
            cur.execute(query)

        conn.commit()
    except(Exception, pg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
## ------------------------------------------------------------------------------------------------------------------

## ------------------------------------------------------------------------------------------------------------------
# Function to delete a table from a database
def delete_table(database, usr, password, table_name, Cas_Res = 'CASCADE', hostname='localhost', port='5432'):
    """
    Parameters
    ----------
    table_name : string
    
    Returns
    -------
    None.
    
    SQL Syntax
    -------  
    DROP TABLE [IF EXISTS] table_name 
    [CASCADE | RESTRICT];
    
    """
    query = 'DROP TABLE IF EXISTS ' + table_name + ' ' + Cas_Res + ';'
    
    
    try:
        # Create a connection with PostgreSQL
        # print('Connecting to the PostgreSQL database...\n')
        conn=pg2.connect(database=database, user=usr,password=password, host=hostname, port=port)
        with conn.cursor() as cur:                
            # Pass in a PostgreSQL query as a string
            # print('Dropping table: ' + table_name + '\n')
            cur.execute(query)
            
    except (Exception, pg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
## ------------------------------------------------------------------------------------------------------------------

## ------------------------------------------------------------------------------------------------------------------
# Function insert data into a table in a database
def insert(database, usr, password, table_name, columns_list, values_list, hostname='localhost', port='5432'):
    """
    Parameters
    ----------
    table_name : String
    
    columns_list : List
    
    values_list : Tuple
    
    Returns
    -------
    None.
    
    SQL Syntax
    -------  
    INSERT INTO table_name (column_list)
    VALUES
        (value_list_1),
        (value_list_2),
        ...
        (value_list_n);

    """
    
    query = 'INSERT INTO ' + table_name + ' ( ' + ', '.join(columns_list) + ' ) VALUES('
    
    for i in range(len(columns_list)):
        if i == len(columns_list)-1 :
            query = query + ' %s )'
        else:
            query = query + ' %s, '
    
    try:
        # Create a connection with PostgreSQL
        # print('Connecting to the PostgreSQL database...')
        conn = pg2.connect(database=database, user=usr, password=password, host=hostname, port=port)
        with conn.cursor() as cur:
            # Pass in a PostgreSQL query as a string
            # print(f'Inserting into table: {table_name}')
            cur.executemany(query,values_list)
        conn.commit()
    except (Exception, pg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
## ------------------------------------------------------------------------------------------------------------------

## ------------------------------------------------------------------------------------------------------------------
# Function insert data faster into a table in a database
def insert_faster(database: str, usr: str, password: str, table_name: str, columns_list: list[str], values_list: list[tuple], hostname='localhost', port='5432') -> None:
    """
    Parameters
    ----------
    database: String

    usr: String

    password: String

    table_name : String
    
    columns_list : List
    
    values_list : Tuple
    
    Returns
    -------
    None.
    
    SQL Syntax
    -------  
    INSERT INTO table_name (column_list)
    VALUES
        (value_list_1),
        (value_list_2),
        ...
        (value_list_n);

    """
    
    query = 'INSERT INTO ' + table_name + ' (' + ', '.join(columns_list) + ') VALUES '
    string_values = '('+ ','.join(['%s']*len(values_list[0]))  +')'
    
    try:
        # Create a connection with PostgreSQL
        # print('Connecting to the PostgreSQL database...')
        conn = pg2.connect(database=database, user=usr, password=password, host=hostname, port=port)
        with conn.cursor() as cur:
            # print('Inserting into table: ' + table_name)
            # cursor.mogrify() to insert multiple values faster than executemany()
            args = ','.join(cur.mogrify(string_values, i).decode('utf-8') for i in values_list)
            # print(query + args)
            cur.execute(query + args)
        conn.commit()    
    except (Exception, pg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
## ------------------------------------------------------------------------------------------------------------------

## ------------------------------------------------------------------------------------------------------------------
# Function to flexibly insert data into a table in a database
def insert_flex(database: str,usr: str, password: str, table_name: str, columns_list: list[list], values_list: list[tuple], hostname='localhost', port='5432', batch_commit=True) -> None:
    """
    This function will insert data in separated SQL statements and will allow different number and sequence of columns and values.

    Parameters
    ----------
    batch_commit : Boolean
        If the batch_commit is True, the data will be inserted in a batch.
        If the batch_commit is False, the data will be inserted one by one (open and close connection each time).

    database: String

    usr: String

    password: String

    table_name : String
    
    columns_list : List
    
    values_list : Tuple
    
    Returns
    -------
    None.
    
    SQL Syntax
    -------  
    INSERT INTO table_name (column_list_1)
    VALUES
        (value_list_1);

    INSERT INTO table_name (column_list_2)
    VALUES    
        (value_list_2);

    ...

    """
    # Check if columns_list and values_list have the same length
    if len(columns_list) != len(values_list):
        raise Exception('columns_list and values_list must have the same length')
    else:
        if batch_commit:
            try:
                # Create a connection with PostgreSQL
                # print('Connecting to the PostgreSQL database...\n')
                conn = pg2.connect(database=database, user=usr, password=password, host=hostname, port=port)
                for statement_number in range(len(columns_list)):
                    with conn.cursor() as cur:
                        query = 'INSERT INTO ' + table_name + ' ( ' + ', '.join(columns_list[statement_number]) + ' ) VALUES('
                        for i in range(len(columns_list[statement_number])):
                            if i == len(columns_list[statement_number])-1 :
                                query = query + '%s)'
                            else:
                                query = query + '%s, '
                        # print(query)
                        # Pass in a PostgreSQL query as a string
                        # print(F'Insertion number {statement_number+1} into table: {table_name}')
                        cur.execute(query,values_list[statement_number])
                conn.commit()
            except (Exception, pg2.DatabaseError) as error:
                conn.rollback()
                print(error)
            finally:
                if conn is not None:
                    conn.close()
        else:
            # Iterate over the columns_list and values_list and insert individually into the table
            for statement_number in range(len(columns_list)):
                insert(database, usr, password, table_name, columns_list[statement_number], [values_list[statement_number]], hostname=hostname, port=port)
## ------------------------------------------------------------------------------------------------------------------

## ------------------------------------------------------------------------------------------------------------------
# Function select data from a table in a database
def select(database, usr, password, table_name, column_list = None, filter_list = None, order_by = None, limit = None, hostname='localhost', port='5432'):
    """
    Parameters
    ----------
    table_name : String [Mandatory]
    column_list : List of Strings [Optional]
        If the column list is not passed returns all the columns '*'
    filter_list : List of Strings [Optional]
        If the filter list is not passed returns all the rows 
    order_by : List of Strings [Optional]
        If the order is not specified return the rows in whatever order the SQL return
    limit : String [Optional]
        If the limit is not specified returns all the rows in the result of the select statement

    Returns
    -------
    Array with selected elements if exists.
    If the query returns nothing, the array is empty
    
    SQL Syntax
    -------  
    SELECT
    	select_list
    FROM
    	table_name
    WHERE 
        condition
    ORDER BY
    	sort_expression1 [ASC | DESC],
            ...
    	sort_expressionN [ASC | DESC];
    LIMIT
        row_count
    """
    
    query = 'SELECT ' + (', '.join(column_list) if column_list else '* ') + ' FROM '+ table_name
    
    if filter_list:
        query = query + ' WHERE ' + ', '.join(filter_list)
    if order_by:
        query = query + ' ORDER BY ' + ', '.join(order_by)
    if limit:
        query = query + ' LIMIT ' + limit
    
    # print(query)
    
    data = pd.DataFrame()
    
    try:
        # Create a connection with PostgreSQL and perform the query
        # print('Connecting to the PostgreSQL database...\n')
        conn = pg2.connect(database=database, user=usr, password=password, host=hostname, port=port)
        with conn.cursor() as cur:
            # Pass in a PostgreSQL query as a string
            # print('Selecting from table: ' + table_name + '\n')
            cur.execute(query)
            
            # Getting column names
            colnames = [desc[0] for desc in cur.description]
            
            #Saving the data into a pandas DataFrame
            data = pd.DataFrame(cur.fetchall(),columns=colnames)
    except (Exception, pg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            
    return data
## ------------------------------------------------------------------------------------------------------------------

## ------------------------------------------------------------------------------------------------------------------
# Function update data in a table in a database
def update(database, usr, password, table_name, pk_column, pk_value , column, value, hostname='localhost', port='5432'):
    """
    Parameters
    ----------
    table_name : String
    pk_column : String
        PRIMARY KEY COLUMN
    pk_value : Integer
        PRIMARY KEY VALUE
    column : String
    value : String

    Returns
    -------
    None.
    
    SQL Syntax
    -------  
    
    UPDATE table_name
    SET column1 = value1,
        column2 = value2,
        ...
    WHERE condition;
    
    """
    query = 'UPDATE ' + table_name + ' SET ' + column + ' = %s WHERE ' + pk_column + ' = %s ;'
    
    # print('UPDATE ' + table_name + ' SET ' + column + ' = ' + value + ' WHERE ' + pk_column + ' = ' + pk_value)

    try:
        # Create a connection with PostgreSQL and perform the query
        # print('Connecting to the PostgreSQL database...\n')
        conn = pg2.connect(database=database, user=usr, password=password, host=hostname, port=port) 
        with conn.cursor() as cur:
            # Pass in a PostgreSQL query as a string
            # print('Updating table: ' + table_name + '\n')
            cur.execute(query, (value, pk_value))
            
    except (Exception, pg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
## ------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print('Some python functions to help implementing SQL call methods in Posgres')