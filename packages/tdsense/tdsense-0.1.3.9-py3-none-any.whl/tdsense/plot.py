import teradataml as tdml
import io
from IPython.display import Image
import imageio

# This function plots curves using TD_PLOT function from a DataFrame in Teradata.
# It generates an image of the plot and returns either the image data or displays the image.
def plotcurves(df, field='calculated_resistance', row_axis='time_no_unit', series_id='curve_id', select_id=None,
               width=1024, height=768, noplot=False, color=None, row_axis_type='SEQUENCE', plot_type='line'):
    """
    Plot curves using TD_PLOT function from a DataFrame in Teradata.

    Parameters:
    - df: DataFrame containing the data to plot.
    - field: Field name to plot (default: 'calculated_resistance').
    - row_axis: Field name representing the x-axis (default: 'time_no_unit').
    - series_id: Field name representing the series identifier (default: 'curve_id').
    - select_id: Optional, series identifier(s) to select (can be a single value or a list) (default: None).
    - width: Width of the plot image in pixels (default: 1024).
    - height: Height of the plot image in pixels (default: 768).
    - noplot: If True, returns the image data without displaying the image (default: False).
    - color: Optional, color specification for the plot (default: None).
    - row_axis_type: Type of the row axis, either 'SEQUENCE' or 'TIME' (default: 'SEQUENCE').
    - plot_type: Type of plot, either 'line' or 'scatter' (default: 'line').

    Returns:
    - If noplot is True, returns the image data as a NumPy array.
    - Otherwise, displays the image.

    Note:
    - The function assumes the existence of a TD_PLOT function in the Teradata environment.
    - The function requires the 'imageio' and 'Pillow' libraries to be installed.
    """

    # Execute the DataFrame node to obtain the table name
    df._DataFrame__execute_node_and_set_table_name(df._nodeid, df._metaexpr)

    # Construct the filter clause based on select_id
    if isinstance(select_id, list):
        if len(series_id) > 0:
            filter_ = f"WHERE {series_id} IN ({','.join([str(x) for x in select_id])}),"
        else:
            filter_ = ','
    else:
        if select_id is not None:
            filter_ = f"WHERE {series_id} = {select_id},"
        else:
            filter_ = ','

    # Calculate the number of series in the DataFrame
    nb_series = df[[series_id]+[row_axis]].groupby(series_id).count().shape[0]

    # Determine the number of plots based on series_id
    n = 1
    if type(series_id) == list:
        n = len(series_id)
        series_id = ','.join(series_id)

    # Handle the color parameter
    if color == None:
        color = ''
    else:
        color = f",FORMAT('{color}')"

    # Construct the query based on the number of series
    if nb_series < 1025:
        query = f"""
        EXECUTE FUNCTION
            TD_PLOT(
                SERIES_SPEC(
                TABLE_NAME({df._table_name}),
                ROW_AXIS({row_axis_type}({row_axis})),
                SERIES_ID({series_id}),
                PAYLOAD (
                    FIELDS({field}),
                    CONTENT(REAL)
                )
            )
            {filter_}
            FUNC_PARAMS(
            TITLE('{field}'),
            PLOTS[(
            TYPE('{plot_type}')
            {color}
            )],
            WIDTH({width}),
            HEIGHT({height})
            )
            );
        """
    else:
        # Create a modified DataFrame to handle a large number of series
        df_ = df.assign(**{series_id: 1})
        df_._DataFrame__execute_node_and_set_table_name(df_._nodeid, df_._metaexpr)
        query = f"""
        EXECUTE FUNCTION
            TD_PLOT(
                SERIES_SPEC(
                TABLE_NAME({df_._table_name}),
                ROW_AXIS({row_axis_type}({row_axis})),
                SERIES_ID({series_id}),
                PAYLOAD (
                    FIELDS({field}),
                    CONTENT(REAL)
                )
            )
            {filter_}
            FUNC_PARAMS(
            TITLE('{field}'),
            PLOTS[(
            TYPE('scatter')
            {color}
            )],
            WIDTH({width}),
            HEIGHT({height})
            )
            );
        """

    # Print the query if tdml.display.print_sqlmr_query is True
    if tdml.display.print_sqlmr_query:
        print(query)

    # Execute the query and fetch the result
    res = tdml.get_context().execute(query).fetchall()

    # Get the image data from the result
    stream_str = io.BytesIO(res[0][1 + n])

    # Return the image data or display the image
    if noplot:
        return imageio.imread(stream_str.getvalue())
    else:
        return Image(stream_str.getvalue())

# This function plots curves from a DataFrame that belongs to a specific cluster.
# It copies the cluster DataFrame to a temporary table in Teradata, performs a join with the original DataFrame,
# and then calls the plotcurves function to generate the plot.
def plotcurvescluster(df, cluster, no_cluster, schema, field='calculated_resistance', row_axis='time_no_unit', series_id='CURVE_ID', select_id=None):
    """
    Plot curves from a DataFrame that belongs to a specific cluster.

    Parameters:
    - df: Original DataFrame containing the data to plot.
    - cluster: DataFrame containing the cluster information.
    - no_cluster: Cluster number to select.
    - schema: Schema name in the Teradata environment for temporary table creation.
    - field: Field name to plot (default: 'calculated_resistance').
    - row_axis: Field name representing the x-axis (default: 'time_no_unit').
    - series_id: Field name representing the series identifier (default: 'CURVE_ID').
    - select_id: Optional, series identifier(s) to select (can be a single value or a list) (default: None).

    Returns:
    - The result of the plotcurves function called on the selected DataFrame.

    Note:
    - The function assumes the existence of the plotcurves function.
    - The function assumes the availability of the 'tdml' module for DataFrame operations.
    """

    # Copy the cluster DataFrame to a temporary table in Teradata
    tdml.copy_to_sql(df=cluster,table_name='cluster_temp',if_exists='replace',schema_name=schema)

    # Create a DataFrame for the cluster temporary table
    df_cluster = tdml.DataFrame(tdml.in_schema(schema,'cluster_temp'))

    # Join the original DataFrame with the cluster DataFrame based on the cluster number and series identifier
    df_select = df.join(df_cluster[df_cluster.cluster == no_cluster],
                        how='inner',
                        on=f'{series_id}=CURVE_ID', rsuffix='r',
                        lsuffix='l')
    try:
        # Assign the selected series identifier from the left DataFrame and drop unnecessary columns
        df_select = df_select.assign(**{series_id: df_select['l_' + series_id]}).drop(
            columns=[f'l_{series_id}', 'r_CURVE_ID'])
    except:
        1==1 # Placeholder statement to handle any exception silently
    df_select.shape

    # Call the plotcurves function with the selected DataFrame and other parameters
    return plotcurves(df_select,field=field, row_axis=row_axis, series_id=series_id,select_id=select_id)
