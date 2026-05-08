#######################################################
## 1. Import libraries
#######################################################

import os
import pendulum
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

#######################################################
## 2. Set initial vars
#######################################################

postgres_db = os.getenv('POSTGRES_DB')
db_user = os.getenv('POSTGRES_USER')
db_pass = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')

pg_schema = 'raw'
pg_tables = ['account', 'category', 'subcategory', 'year', 'month', 'budget', 'transaction']

#######################################################
## 3. Reset raw notion dates
#######################################################

def lambda_handler(event, context):

    print("Starting Lambda Execution...")

    engine = create_engine(f'postgresql://{db_user}:{db_pass}@{db_host}:5432/{postgres_db}')

    try:
        with engine.begin() as conn:

            reset_date = pendulum.datetime(1990, 1, 1, tz='Europe/Sofia')

            for table_name in pg_tables:
                # UPDATE the created_time and last_edited time
                query = text(f"""
                    update {pg_schema}.{table_name} 
                    set 
                        created_time     = '{reset_date}', 
                        last_edited_time = '{reset_date}'
                """)
                conn.execute(query)

                print(f"Created_time and Last_edited_time were reset for {pg_schema}.{table_name}")

    except (SQLAlchemyError) as e:
        print(f'Error: The update of {pg_schema}.{table_name} failed. Details: {e}')
        raise

    return {
        'statusCode': 200,
        'body': 'Raw Notion dates reset completed successfully!'
    }


# So I can still test the script locally
if __name__ == "__main__":
    lambda_handler(None, None)
