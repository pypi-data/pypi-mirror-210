#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import plotly.express as px
import numpy as np
import os
import jellyfish
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.express as px
import plotly.io as pio


# In[3]:


def csv_to_df(file_path):
    """
    Read in a CSV file and return a pandas DataFrame.
    
    Args:
        file_path (str): The file path to the CSV file.
        
    Returns:
        pandas.DataFrame: A DataFrame containing the data from the CSV file.
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print("File not found: {}".format(file_path))
        return None
    except:
        print("Error reading file: {}".format(file_path))
        return None


# In[4]:


def get_column_names(df):
    """
    Returns a list of column names in the given dataframe.

    Parameters:
    -----------
    df : pandas.DataFrame
        The dataframe whose column names are to be returned.

    Returns:
    --------
    list
        A list of column names in the given dataframe.
    """
    print(list(df.columns))


# In[5]:


def read_shp(file_path):
    """
    Read in a shapefile and return a GeoDataFrame.
    
    Args:
        file_path (str): The file path to the shapefile.
        
    Returns:
        geopandas.GeoDataFrame: A GeoDataFrame containing the data from the shapefile.
    """
    try:
        shapefile = r"{}".format(file_path)
        return gpd.read_file(shapefile)
    except FileNotFoundError:
        print("File not found: {}".format(file_path))
        return None
    except:
        print("Error reading file: {}".format(file_path))
        return None


# In[6]:


def get_key_from_value(my_dict, value):
    """
    Return the key in a dictionary that corresponds to a given value.

    Args:
    my_dict (dict): The dictionary to search.
    value: The value to search for.

    Returns:
    The key in the dictionary that corresponds to the given value, or None if the value is not found.
    """
    for k, v in my_dict.items():
        if v == value:
            return k
        


# In[7]:


def get_state_map():
    
    
    """
    Retrieves a dictionary mapping state IDs to state names.
    
    Returns:
        state_map (dict): Dictionary mapping state IDs to state names.
    """
        
    id_name = 'shrid'
    state_variable ='state_name'
    latest_year='11-'
    import pkg_resources

    filepath = pkg_resources.resource_filename('shrug_viz', 'data/keys/shrug_names.csv')

    keys = pd.read_csv(filepath)
    keys=keys[[id_name,state_variable]]
    keys[id_name] = keys.shrid.str[0:5]
    keys=keys[keys[id_name].str.contains(latest_year)]
    keys[id_name] = keys.shrid.str[3:5]
    keys = keys.drop_duplicates()
    keys.dropna(inplace=True)
    keys[id_name]=keys[id_name].astype(str)
    state_map = keys.set_index(id_name)[state_variable].to_dict()
    return state_map


# In[8]:


def get_district_map():
    """
    Retrieves a dictionary mapping district IDs to district names.

    Returns:
        district_map (dict): Dictionary mapping district IDs to district names.
    """
    district_id = 'pc11_district_id'
    district_name = 'pc11_district_name'
    import pkg_resources

    filepath = pkg_resources.resource_filename('shrug_viz',"data/shrug-v1.5.samosa-keys-csv/shrug_pc11_district_key.csv")

    keys = pd.read_csv(filepath)
    keys=keys[[ district_id,district_name]]
    keys = keys.drop_duplicates()
    keys.dropna(inplace=True)
    keys[district_id]=keys[district_id].astype(int)
    keys[district_id]=keys[district_id].astype(str)
    district_map = keys.set_index(district_id)[district_name].to_dict()
    for k,v in district_map.items():
        k = str(k)
        district_map[k]=v
    return district_map



# In[9]:


def get_agg_map():
    """
    Retrieves a dictionary mapping variable names to aggregation functions.

    Returns:
        agg_map (dict): Dictionary mapping variable names to aggregation functions.
    """
    column_name_function = 'Aggregation'
    column_name_variable= 'SHRUG variable name'
    # URL of the published CSV file
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTfbwLwwi7z9jgVumExcIeERK0RStIQV9NK31mJtdw9PS41ySqRfqqrSJHXezeB_lOZlYUpitYvL8Hb/pub?gid=961461678&single=true&output=csv"
    # Use pandas to read the CSV file from the URL
    df = pd.read_csv(csv_url)
    df =df.iloc[20:,:]
    df = df.rename(columns=df.iloc[0]).iloc[1:]
    df = df[df[column_name_function].notna()]
    df=df[[column_name_variable,column_name_function]]
    agg_map = df.set_index(column_name_variable)[column_name_function].to_dict()
    for (k,v) in agg_map.items():
        agg_map[k] = agg_map[k].lower()
    return agg_map


# In[10]:


def get_state_names():
    """
    Gets a list of state names from the state_map dictionary.

    Returns:
    state_list (list): A list of state names
    """
    state_map=get_state_map()
    state_list=[]
    for k,v in state_map.items():
        state_list.append(v)
    return state_list


# In[11]:


def get_district_names(state_name='Maharashtra'):
    """
    Given a state name, returns a list of all district names within that state. 
    
    Args:
    state_name (str): Name of the state for which district names are to be returned.
    
    Returns:
    list: A list of strings, where each string represents a district name within the specified state.
    """
    state_variable ='state_name'
    district_variable = 'district_name'
    import pkg_resources

    filepath = pkg_resources.resource_filename('shrug_viz', 'data/keys/shrug_names.csv')

    keys = pd.read_csv(filepath)
    keys =keys[keys[state_variable]==state_name]
    keys = keys[[district_variable]]
    district_names = keys[district_variable].unique()
    print(district_names)

    
    


# In[12]:


def shp_corrections(shapefile, dataframe, granularity):
    """
    This function corrects the mismatch between the names of the locations in the shapefile and the data frame.
    
    Parameters:
        shapefile (GeoDataFrame): A GeoDataFrame containing the shapefile data of the locations.
        dataframe (DataFrame): A Pandas DataFrame containing the data of the locations.
        granularity (str): A string indicating the granularity of the locations. 
                           Possible values are 'state', 'district', and 'subdistrict'.
    
    Returns:
        GeoDataFrame: A new GeoDataFrame with corrected location names and containing only the 'geometry' and 'new_str' columns.
    """
    
    if(granularity=='state'):
        str_in_shp = 's_name'
        new_str = 'state_name'
    elif(granularity=='district'):
        str_in_shp = 'd_name'
        new_str = 'district_name'
    else:
        str_in_shp = 'sd_name'
        new_str = 'subdistrict_name'
    
    matches = []
    for location1 in shapefile[str_in_shp]:
        best_match = np.inf
        best_location = None
        if location1 is None:
            continue
        for location2 in dataframe[new_str]:
            distance = jellyfish.levenshtein_distance(location1, location2)
            if distance < best_match:
                best_match = distance
                best_location = location2
        matches.append(best_location)
        
    shapefile[new_str] = matches
    shapefile = shapefile[['geometry',new_str]]
    return shapefile


# In[13]:


def c_plot(merged_df, column_name, gb_str):
    """
    Plots a choropleth map based on a given column in a GeoDataFrame.

    Parameters:
    merged_df (GeoDataFrame): A GeoDataFrame containing geometry and column data.
    column_name (str): The name of the column to use for the color scale.
    gb_str (str): The name of the column to use as a hover data.

    Returns:
    None
    """

    pio.renderers.default = "browser"

    fig = px.choropleth(merged_df, geojson=merged_df.geometry, 
                    locations=merged_df.index, color=column_name,
                    height=800,
                   color_continuous_scale="tealrose",
                    hover_data=[gb_str,column_name]
    )
    #show only locations which are coloured
    fig.update_geos(fitbounds="locations", visible=True)
    #title of the plot
    fig.update_layout(
    title_text=column_name
    )
    #align the title in the centre
    fig.update(layout = dict(title=dict(x=0.5)))
    #title for scale
    fig.update_layout(
    coloraxis_colorbar={
        'title':column_name})

    fig.show()
    return


# In[14]:


def choropleth(df=None, column_name=None, granularity='state', state_name='Maharashtra', district_name='aurangabad',shapefile_path=None):
    """
    Creates a choropleth map using the provided dataframe, column name, and granularity.

    Args:
    - df (pandas.DataFrame): The dataframe containing the data to be plotted.
    - column_name (str): The name of the column containing the data to be plotted.
    - granularity (str): The level of granularity for the map. Valid values are 'state', 'district', or 'subdistrict'.
    - state_name (str): The name of the state for which the map will be plotted. Required for granularity of 'district' or 'subdistrict'.
    - district_name (str): The name of the district for which the map will be plotted. Required for granularity of 'subdistrict'.

    Returns:
    - None

    Raises:
    - ValueError: If an invalid granularity is specified.

    """
    #variables used
    id_name = 'shrid'
    state_variable = 'state_name'
    district_variable='district_name'
    subdistrict_variable = 'subdistrict_name'
    shapefile_col_name_state = 'pc11_s_id'
    shapefile_col_name_district = 'pc11_d_id'
    granularity = granularity
    
    #shapefile
    #shapefile_path = os.path.join('data/shapefiles', granularity+'.shp')
    shapefile = read_shp(shapefile_path)
    #keys dataframe
    import pkg_resources

    keys_path = pkg_resources.resource_filename('shrug_viz', 'data/keys/shrug_names.csv')


    keys = csv_to_df(keys_path)
    
    #aggregation_function
    aggregation_map =get_agg_map()
    agg_func = aggregation_map[column_name]
    
    gb_str = granularity+"_name"
    
    
    #filtering primary dataframe
    df = df[[column_name,id_name]]
    df = df.merge(keys, on=id_name)
    
    state_map = get_state_map()
    if granularity == 'state':
        
        #dataframe filtering
        df = df[[column_name,state_variable]]
        df = df.groupby(by=gb_str, as_index=False).agg(agg_func)
        df = df[[column_name,gb_str]]
        #shapefile operations
        shapefile = shapefile.dropna()
        
        shapefile = shp_corrections(shapefile,df,granularity)
        
      
        
    elif granularity == 'district':
        
        #dataframe filtering
        df = df[[column_name,state_variable,district_variable]]
        df = df[df[state_variable] == state_name]
        df = df.groupby([state_variable,district_variable], as_index=False).agg(agg_func)
        df = df[[column_name,gb_str]]
        #shapefile operations
        state_code= get_key_from_value(state_map, state_name)
        shapefile = shapefile[shapefile[shapefile_col_name_state]==state_code]
        shapefile = shapefile.dropna()
        shapefile = shp_corrections(shapefile,df,granularity)
        
        
    elif granularity == 'subdistrict':
        
        district_map = get_district_map()

        #dataframe filtering
        df = df[[column_name,state_variable,district_variable,subdistrict_variable]]
        df = df[(df[state_variable] == state_name) & (df[district_variable] == district_name)]
        # group by sub-district within district and state
        df = df.groupby([state_variable, district_variable, subdistrict_variable], as_index=False).agg(agg_func)
        df = df[[column_name,gb_str]]

        #shapefile operations
        state_code= get_key_from_value(state_map, state_name)
        district_code = get_key_from_value(district_map, district_name)
        
        if(len(district_code)==1):
            district_code="00"+district_code
        elif(len(district_code)==2):
            district_code="0"+district_code
            
        # Filter shapefile based on state_code and district_code
        shapefile = shapefile[shapefile[shapefile_col_name_state] == state_code]
        shapefile= shapefile[shapefile[shapefile_col_name_district] == district_code]
        shapefile = shapefile.dropna()
        
        shapefile = shp_corrections(shapefile,df,granularity)
      
    
    #merge
    merged_df  = shapefile.merge(df,on=gb_str)
    
    #plot
  
    c_plot(merged_df,column_name,gb_str)
        
        
    
    
    
    
    
    
    
    
    
    


# In[ ]:





# In[ ]:





# In[ ]:




