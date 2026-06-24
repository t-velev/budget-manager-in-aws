#######################################################
## 1. Import libraries
#######################################################

import os
import pendulum
from src.ntn_utils import run_full_extraction_pipeline

#######################################################
## 2. Set initial vars
#######################################################

pg_table_name = 'budget'
budget_db_id = os.getenv('NOTION_DB_ID_BUDGET')

dag_name = os.getenv('dag_name', 'notion_to_dwh_main_pipeline')
task_name = os.getenv('task_name', 'extract_and_load_budget')

#######################################################
## 3. Execute lambda function
#######################################################

def map_all_data(item):
    """
    Parses a single raw JSON record from the Notion API into a flattened dictionary.

    Extracts specific properties (e.g., id, title, timestamps) and dynamically appends
    a current UTC 'load_date' evaluated at the exact moment of loop execution.

    Args:
        item (dict): A single record (row) payload returned by the Notion API.

    Returns:
        dict: A flattened dictionary perfectly mapped to the target raw database schema.
    """

    all_data_mapping = {
        'id':                item['id']                                                                                                                                   ,
        'title':             item['properties']['Name']['title'][0]['plain_text']                        if item['properties']['Name']['title']                 else None ,
        'period_end':        item['properties']['Край период']['date']['start']                          if item['properties']['Край период']['date']           else None ,
        'budget_amount':     item['properties']['Бюджет']['number']                                                                                                       ,
        'year_id':           item['properties']['Година']['relation'][0]['id']                           if item['properties']['Година']['relation']            else None ,
        'month_id':          item['properties']['Месец']['relation'][0]['id']                            if item['properties']['Месец']['relation']             else None ,
      # 'category_id':       item['properties']['Категория']['rollup']['array'][0]['relation'][0]['id']  if item['properties']['Категория']['rollup']['array']  else None ,  # Notion's Lazy API can't fetch all rollup values
        'subcategory_id':    item['properties']['Подкатегория']['relation'][0]['id']                     if item['properties']['Подкатегория']['relation']      else None ,
        'is_archived':       item['properties']['Скрита']['checkbox']                                                                                                     ,
        'created_time':      item['created_time']                                                                                                                         ,
        'last_edited_time':  item['last_edited_time']                                                                                                                     ,
        'load_date':         pendulum.now('UTC')
        }

    return all_data_mapping


def map_filtered_data(item):
    """
    Parses a 'skinny' JSON record from the Notion API for the hard-delete audit process.

    Extracts only the essential fields (id, title) required to verify which
    records currently exist in the source system without pulling heavy payloads.

    Args:
        item (dict): A single record (row) payload returned by the Notion API.

    Returns:
        dict: A flattened dictionary mapped for the notion_ids_audit table.
    """

    filtered_data_mapping = {
        'id':          item['id']                                                                                            ,
        'title':       item['properties']['Name']['title'][0]['plain_text'] if item['properties']['Name']['title'] else None ,
        'source_name': pg_table_name
        }

    return filtered_data_mapping


def lambda_handler(event, context):

    print("Starting Lambda Execution...")

    # A list of notion db columns to be filtered. Empty list filters nothing.
    new_data_filter = ['Name', 'Край период', 'Бюджет', 'Година', 'Месец', 'Подкатегория', 'Скрита']

    # A list of notion db column names to be filtered. Empty list filters nothing.
    id_cols_filter = ['Name']

    # Call the main extract function in ntn_utils.py
    status = run_full_extraction_pipeline(event, pg_table_name, budget_db_id, dag_name, task_name, map_all_data, map_filtered_data, new_data_filter, id_cols_filter)

    return status


# So I can still test the script locally
if __name__ == "__main__":
    lambda_handler(None, None)