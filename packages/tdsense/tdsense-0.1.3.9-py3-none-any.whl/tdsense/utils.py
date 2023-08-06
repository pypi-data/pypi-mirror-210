# This function creates a table based on a given query.
def create_table(query, table_name, schema_name):
    """
    Create a table based on a given query.

    Parameters:
    - query: SQL query for creating the table.
    - table_name: Name of the table to be created.
    - schema_name: Name of the schema where the table will be created.

    Returns:
    - query: SQL query for creating the table.

    Note:
    - The function assumes the availability of the specified schema.
    """

    # Generate the SQL query for creating the table
    query = f"""
    CREATE TABLE {schema_name}.{table_name} AS 
    (
        {query}
    ) WITH DATA
    --PRIMARY INDEX (CURVE_ID_1, CURVE_ID_2)
    NO PRIMARY INDEX
    """

    # Return the SQL query for creating the table
    return query

# This function generates an INSERT INTO query for inserting data into a table.
def insert_into(query, table_name, schema_name):
    """
    Generate an INSERT INTO query for inserting data into a table.

    Parameters:
    - query: SQL query for the data to be inserted.
    - table_name: Name of the table to insert the data into.
    - schema_name: Name of the schema where the table is located.

    Returns:
    - query: SQL query for inserting data into the table.

    Note:
    - The function assumes the availability of the specified schema and table.
    """

    # Generate the SQL query for inserting data into the table
    query = f"""
    INSERT INTO {schema_name}.{table_name}  
    {query}
    """

    # Return the SQL query for inserting data into the table
    return query