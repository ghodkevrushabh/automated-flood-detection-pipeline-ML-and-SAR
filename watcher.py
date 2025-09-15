# watcher.py (Corrected Version)
import requests
import datetime
import os
import subprocess

def run_pipeline():
    """
    This is the main function that runs the entire pipeline once from start to finish.
    """
    print(f"[{datetime.datetime.now()}] Starting the flood detection pipeline...")

<<<<<<< HEAD
=======
    # Define the search area for your Nagaon project
>>>>>>> 3676517252cd846a1a8d7011df9b892957423902
    area_of_interest = 'POLYGON((92.4958 26.2178,92.9387 26.2178,92.9387 26.466,92.4958 26.466,92.4958 26.2178))'
    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(hours=24) 

    api_url = f"https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&processingLevel=GRD_HD&intersectsWith={area_of_interest}&start={start_time.isoformat()}&output=json"

    try:
        print("Querying the ASF API for new satellite imagery...")
        response = requests.get(api_url)
        response.raise_for_status()
        results = response.json()[0]

        if results:
            print(f"Found {len(results)} new scenes. Processing the first one.")
            scene = results[0]
            scene_name = scene['fileName']
            download_url = scene['downloadUrl']

<<<<<<< HEAD
            subprocess.run(["python3", "preprocessor.py", "--url", download_url, "--filename", scene_name])
        else:
            print("No new scenes found.")
            subprocess.run(["python3", "reporter.py", "--status", "no_data"])

=======
            # Trigger the preprocessor script
            subprocess.run(["python3", "preprocessor.py", "--url", download_url, "--filename", scene_name], check=True)
        else:
            # This line will now correctly lead to the 'except' block
            raise IndexError("No new scenes found in the last 24 hours.")

    except (requests.exceptions.RequestException, IndexError) as e:
        # This block handles both API errors and the case where no images are found
        print(f"No new scenes found or API error occurred: {e}")
        subprocess.run(["python3", "reporter.py", "--status", "no_data"], check=True)
>>>>>>> 3676517252cd846a1a8d7011df9b892957423902
    except Exception as e:
        print(f"An unexpected error occurred in the pipeline: {e}")

<<<<<<< HEAD
# This part runs the function when the script is executed
if __name__ == "__main__":
    check_for_new_imagery()
=======

if __name__ == '__main__':
    # When the script is run, it just executes the main pipeline function once.
    run_pipeline()
    print(f"[{datetime.datetime.now()}] Pipeline run finished successfully.")
>>>>>>> 3676517252cd846a1a8d7011df9b892957423902
