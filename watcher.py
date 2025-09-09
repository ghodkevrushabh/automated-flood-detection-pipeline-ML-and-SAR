#watcher.py
import requests
import datetime
import os
import subprocess

def check_for_new_imagery():
    print(f"[{datetime.datetime.now()}] Running watcher script...")
    
    # This is the search area for your Nagaon project
    area_of_interest = 'POLYGON((91.80 26.08, 92.75 26.08, 92.75 26.63, 91.80 26.63, 91.80 26.08))'
    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(hours=24) # Check for images in the last 24 hours
    
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
            
            # Trigger the next script in the pipeline
            subprocess.run(["python3", "preprocessor.py", "--url", download_url, "--filename", scene_name])
        else:
            print("No new images found.")
    except Exception as e:
        print(f"An error occurred in watcher: {e}")

if __name__ == "__main__":
    check_for_new_imagery()