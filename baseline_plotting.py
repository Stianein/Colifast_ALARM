import sqlite3
import matplotlib.pyplot as plt
import os

# Define the path to the database (make sure this path is correct)
base_path = os.path.normpath("C:/Colifast/APPDATA/")
db_path = os.path.join(base_path, "Vækerød141.db")  # Update if your database file has a different name

def plot_baseline_readings(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch run_id, sample_number, and fluorescent_baseline from SampleInfo table
    query = "SELECT run_id, id, fluorescent_baseline FROM SampleInfo WHERE fluorescent_baseline IS NOT NULL"
    cursor.execute(query)
    baseline_data = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Check if any data was returned
    if not baseline_data:
        print("No baseline readings found in the database.")
        return

    # Organize data by run_id
    run_data = {}
    for run_id, sample_number, baseline in baseline_data:
        if run_id not in run_data:
            run_data[run_id] = {'sample_numbers': [], 'baseline_readings': []}
            i = 1
        run_data[run_id]['sample_numbers'].append(i)
        run_data[run_id]['baseline_readings'].append(baseline)
        i += 1

    # Plotting
    plt.figure(figsize=(10, 6))

    # Plot each run_id's data on the same graph
    for run_id, data in run_data.items():
        plt.plot(data['sample_numbers'], data['baseline_readings'], marker='o', linestyle='-', label=f"Run {run_id}")

    plt.title("Fluorescent Baseline Readings for All Sample Runs")
    plt.xlabel("Sample Number")
    plt.ylabel("Fluorescent Baseline")
    plt.grid(True)
    plt.legend()  # Show legend for each run_id
    plt.show()

# Run the function to plot baseline readings
plot_baseline_readings(db_path)
