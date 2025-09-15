# watcher.py (Corrected Version)
import requests
import datetime
import os
import subprocess

def check_for_new_imagery():
    print(f"[{datetime.datetime.now()}] Running watcher script...")

    area_of_interest = 'POLYGON((92.4958 26.2178,92.9387 26.2178,92.9387 26.466,92.4958 26.466,92.4958 26.2178))'
    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(hours=24) 

    api_url = f"https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&processingLevel=GRD_HD&intersectsWith={area_of_interest}&start={start_time.isoformat()}&output=json"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        results = response.json()[0]

        if results:
            print(f"Found {len(results)} new scenes. Processing the first one.")
            scene = results[0]
            scene_name = scene['fileName']
            download_url = scene['downloadUrl']

            subprocess.run(["python3", "preprocessor.py", "--url", download_url, "--filename", scene_name])
        else:
            print("No new scenes found.")
            subprocess.run(["python3", "reporter.py", "--status", "no_data"])

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# This part runs the function when the script is executed
if __name__ == "__main__":
    check_for_new_imagery()