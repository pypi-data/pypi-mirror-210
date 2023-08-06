import plotly.graph_objects as go
import random
import teradataml as tdml


import random  # Importing the random module for random number generation

def colors(n, alpha=0.8, random_seed=124):
    """
    Generates a list of n colors in the form of RGBA strings.

    Parameters:
    - n (integer): The number of colors to generate.
    - alpha (float, optional): The alpha value (opacity) for each color. Defaults to 0.8.
    - random_seed (integer, optional): The seed value used for random number generation. Defaults to 124.

    Returns:
    - ret (list): A list of RGBA strings representing the generated colors.
    """

    random.seed(random_seed)  # Seed the random number generator for consistent colors

    ret = []  # Initialize an empty list to store the generated colors

    # Generate random values for the initial color components (r, g, b)
    r = int(random.random() * 256)
    g = int(random.random() * 256)
    b = int(random.random() * 256)

    step = 256 / n  # Calculate the step interval between each color component

    # Generate n colors
    for i in range(n):
        r += step  # Increment the red component by the step interval
        g += step  # Increment the green component by the step interval
        b += step  # Increment the blue component by the step interval

        r = int(r) % 256  # Wrap around the red component to the range 0-255
        g = int(g) % 256  # Wrap around the green component to the range 0-255
        b = int(b) % 256  # Wrap around the blue component to the range 0-255

        # Construct the RGBA string and append it to the ret list
        ret.append("rgba(" + str(r) + "," + str(g) + "," + str(b) + "," + str(alpha) + ")")

    return ret  # Return the list of generated colors



def plot_first_main_paths(myPathAnalysis, path_column='mypath', id_column='travelid', nb_paths=15, print_query=False):
    """
        Plots the first main paths based on a given output of the teradataml NPATH function or the teradataml dataframe of its result field.

        Parameters:
        - myPathAnalysis (DataFrame or tdml.dataframe.dataframe.DataFrame): The input DataFrame containing path analysis data.
        - path_column (str, optional): The column name representing the path. Defaults to 'mypath'.
        - id_column (str or list, optional): The column name(s) representing the unique identifier(s). Defaults to 'travelid'.
        - nb_paths (int, optional): The number of main paths to plot. Defaults to 15.
        - print_query (bool, optional): Whether to print the generated query. Defaults to False.

        Returns:
        - None (it display an interactive Sankey plot)
    """
    if type(id_column) != list:
        id_column = [id_column]

    if type(myPathAnalysis) != tdml.dataframe.dataframe.DataFrame:
        df_agg = myPathAnalysis.result.select(id_column+[path_column]).groupby(path_column).count()
    else:
        df_agg = myPathAnalysis.select(id_column+[path_column]).groupby(path_column).count()

    df_agg._DataFrame__execute_node_and_set_table_name(df_agg._nodeid, df_agg._metaexpr)

    query = f"""SEL
        row_number() OVER (PARTITION BY 1 ORDER BY count_{id_column[0]} DESC) as id
    ,	REGEXP_REPLACE(lower(A.{path_column}),'\\[|\\]', '') as str
    ,	count_{id_column[0]} as weight
    FROM {df_agg._table_name} A
    QUALIFY id < {nb_paths}+1"""

    df_selection = tdml.DataFrame.from_query(query)

    query2 = f"""
    sel
        CC.id
    ,	CC.node_source
    ,	CC.node_target
    ,	CC.beg
    ,	CC."end"
    ,	sum(CC.weight) as weight
    FROM 
    (
    sel
        B.*
    ,	LAG(id_end,1,0) OVER (PARTITION BY B."path" ORDER BY B."path",B."index") as id_beg
    ,	B."beg" || '_' || TRIM(CAST(id_beg AS VARCHAR(200))) as node_source
    ,	B."end" || '_' || TRIM(CAST(id_end AS VARCHAR(200))) as node_target
    FROM 
    (
        sel 
            A.*
        ,	row_number() OVER (PARTITION BY A."path" ORDER BY A."path",A."index") as id_end
        from (
        SELECT

            lag(AA.token,1) IGNORE NULLS OVER (PARTITION BY AA.outkey ORDER BY AA.tokennum) as "beg"
        ,	AA.token as "end"
        ,	AA.outkey as "path"
        ,	B.weight
        ,	AA.tokennum as "index"
        ,   B.id
        FROM (

        SELECT 
            d.*
        FROM TABLE (strtok_split_to_table({df_selection._table_name}.id, {df_selection._table_name}.str, ',')
        RETURNS (outkey integer, tokennum integer, token varchar(200)character set unicode) ) as d 

        ) AA
        ,{df_selection._table_name} B
        WHERE AA.outkey = B.id
        QUALIFY beg IS NOT NULL
    ) A
    ) B
    --ORDER BY "path","index"
    ) CC
    GROUP BY 1,2,3,4,5
    """

    if print_query:
        print(query2)

    df_ready = tdml.DataFrame.from_query(query2)

    df_ready_local = df_ready.to_pandas()

    df_ready_local = df_ready_local.sort_values(by='id')

    labs = dict()
    labels = list(set(df_ready_local.node_source.tolist() + df_ready_local.node_target.tolist()))

    for i, label in enumerate(labels):
        labs[label] = i

    labels = ['_'.join(x.split('_')[0:(len(x.split('_')) - 1)]) for x in labels]

    df_ready_local['color'] = df_ready_local.id.map(
        {id: col for id, col in zip(list(set(df_ready_local.id)), colors(len(set(df_ready_local.id)), random_seed=45))})

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=colors(len(labels), random_seed=123)
        ),
        link=dict(
            source=df_ready_local.node_source.map(labs),  # indices correspond to labels, eg A1, A2, A2, B1, ...
            target=df_ready_local.node_target.map(labs),
            value=df_ready_local.weight,
            color=df_ready_local.color
        ))])

    fig.update_layout(font_size=10, width=1200,
                      height=800)
    fig.show()

    return

def create_all_pathes_views(myPathAnalysis, root_name = 'mytest',
                            schema = tdml.get_context().execute('SELECT DATABASE').fetchall()[0][0],
                            path_column='mypath', id_column='travelid'):
    """
        Creates multiple views related to the given myPathAnalysis DataFrame.

        Parameters:
        - myPathAnalysis (DataFrame or tdml.dataframe.dataframe.DataFrame): The input DataFrame containing path analysis data.
        - root_name (str, optional): The root name to be used for naming the created views. Defaults to 'mytest'.
        - schema (str, optional): The schema to create the views in. Defaults to the current database schema.
        - path_column (str, optional): The column name representing the path. Defaults to 'mypath'.
        - id_column (str or list, optional): The column name(s) representing the unique identifier(s). Defaults to 'travelid'.

        Returns:
        - None
    """

    if type(id_column) != list:
        id_column = [id_column]

    # Create the view of my npath
    npath_view = f"{schema}.{root_name}_NPATH_VIEW"

    try:
        query = f"""
        REPLACE VIEW  {npath_view} AS
        {myPathAnalysis.sqlmr_query}
        """
    except Exception as e:
        print(str(e).split('\n')[0])
        query = f"""
        REPLACE VIEW  {npath_view} AS
        {myPathAnalysis.show_query()}
        """
    tdml.get_context().execute(query)
    print(f'npath view created : {npath_view}')

    # Create the aggregated view of my npath
    aggregated_npath_view = f"{schema}.{root_name}_NPATH_VIEW_AGG"
    query = f"""
    REPLACE VIEW {aggregated_npath_view} AS
    SELECT 
        {path_column}
    ,   COUNT(*) as count_{id_column[0]}
    FROM {npath_view}
    GROUP BY 1
    """
    tdml.get_context().execute(query)
    print(f'aggregated npath view created : {aggregated_npath_view}')

    # Create the cleaned aggregated view of my npath
    clean_aggregated_npath_view = f"{schema}.{root_name}_CLEAN_NPATH_VIEW_AGG"
    query = f"""
    REPLACE VIEW {clean_aggregated_npath_view} AS
    SELECT 
        row_number() OVER (PARTITION BY 1 ORDER BY count_{id_column[0]} DESC) as id
    ,	REGEXP_REPLACE(lower(A.{path_column}),'\[|\]', '') as str
    ,	count_{id_column[0]} as weight
    FROM {aggregated_npath_view} A"""
    tdml.get_context().execute(query)
    print(f'clean aggregated npath view created : {clean_aggregated_npath_view}')

    # Create the graph view of the aggregated npath view
    graph_aggregated_npath_view =  f"{schema}.{root_name}_GRAPH_NPATH_VIEW_AGG"
    query = f"""
    REPLACE VIEW {graph_aggregated_npath_view} AS
    SELECT
        CC.id
    ,	CC.node_source
    ,	CC.node_target
    ,	CC.beg
    ,	CC."end"
    ,	sum(CC.weight) as weight
    FROM 
    (
    sel
        B.*
    ,	LAG(id_end,1,0) OVER (PARTITION BY B."path" ORDER BY B."path",B."index") as id_beg
    ,	B."beg" || '_' || TRIM(CAST(id_beg AS VARCHAR(10))) as node_source
    ,	B."end" || '_' || TRIM(CAST(id_end AS VARCHAR(10))) as node_target
    FROM 
        (
        sel 
            A.*
        ,	row_number() OVER (PARTITION BY A."path" ORDER BY A."path",A."index") as id_end
        from (
            SELECT
    
                lag(AA.token,1) IGNORE NULLS OVER (PARTITION BY AA.outkey ORDER BY AA.tokennum) as "beg"
            ,	AA.token as "end"
            ,	AA.outkey as "path"
            ,	B.weight
            ,	AA.tokennum as "index"
            ,   B.id
            FROM (
                SELECT 
                    d.*
                FROM TABLE (strtok_split_to_table({clean_aggregated_npath_view}.id, {clean_aggregated_npath_view}.str, ',')
                RETURNS (outkey integer, tokennum integer, token varchar(20)character set unicode) ) as d 
            ) AA
            ,   {clean_aggregated_npath_view} B
            WHERE AA.outkey = B.id
            QUALIFY beg IS NOT NULL
        ) A
       ) B
    --ORDER BY "path","index"
    ) CC
    GROUP BY 1,2,3,4,5
    """
    tdml.get_context().execute(query)
    print(f'npath view created : {graph_aggregated_npath_view}')

    return