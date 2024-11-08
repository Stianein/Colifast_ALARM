### Program to get baseline readings of earlier runs    ###
### added to the fluorescent_baseline parameter of the  ###
### SampleInfo entry of the databse. This is now        ###
### automatically added in new runs.                    ###

import sqlite3

# Define the path to the database
db_path = "C:/Colifast/APPDATA/uttesting.db"

def update_fluorescent_baselines():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Step 1: Fetch the first intensity reading at 430 nm for each sample_id
    select_query = """
    SELECT sd.sample_id, sd.intensity
    FROM SpectralData AS sd
    WHERE sd.wavelength_id = 430 
    AND sd.time_measured = (
        SELECT MIN(time_measured)
        FROM SpectralData
        WHERE sample_id = sd.sample_id AND wavelength_id = 430
    );
    """
    cursor.execute(select_query)
    baseline_data = cursor.fetchall()

    # Step 2: Update each sample's fluorescent_baseline in SampleInfo with the fetched intensity
    update_query = "UPDATE SampleInfo SET fluorescent_baseline = ? WHERE id = ?;"
    for sample_id, intensity in baseline_data:
        cursor.execute(update_query, (intensity, sample_id))

    # Commit the updates and close the connection
    conn.commit()
    conn.close()
    print("Updated fluorescent_baseline for each sample based on first 430 nm reading.")

# Run the update function
update_fluorescent_baselines()
