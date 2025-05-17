import sqlite3
import pandas as pd

SQL_FILE_PATH = "mydata.sqlite3"  # Put in the same folder
EXCEL_FILE_PATH = "temp_output.csv"
TABLE_NAME = "jmdict_withjlpt_english_only"


# Open the file
f = open(EXCEL_FILE_PATH, "w")
# Create a connection and get a cursor
connection = sqlite3.connect(SQL_FILE_PATH)
cursor = connection.cursor()
# Execute the query
cursor.execute(f"select * from {TABLE_NAME}")
# Get data in batches
while True:
    # Read the data
    df = pd.DataFrame(cursor.fetchmany(1000))
    # We are done if there are no data
    if len(df) == 0:
        break
    # Let's write to the file
    else:
        df.to_csv(f, header=False)

# Clean up
f.close()
cursor.close()
connection.close()
