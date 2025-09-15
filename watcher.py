# watcher.py (Cleaned Version)
import requests
import datetime
import os
import subprocess

def check_for_new_imagery():
    """
    Checks the ASF API for new imagery and triggers the preprocessing pipeline if found,
    or a 'no_data' report if not.
    """
    print(f"[{datetime.datetime.now()}] Running watcher script...")

    # Define the search area for jorhat flood project
    area_of_interest = 'POLYGON((92.4958 26.2178,92.9387 26.2178,92.9387 26.466,92.4958 26.466,92.4958 26.2178))'
    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(hours=24) # Check for images in the last 24 hours

    api_url = f"https://api.daac.asf.alaska.edu/services/search/param?platform=SENTINEL-1&processingLevel=GRD_HD&intersectsWith={area_of_interest}&start={start_time.isoformat()}&output=json"

    try:
        print("Querying the ASF API for new satellite imagery...")
        response = requests.get(api_url)
        response.raise_for_status() # This will raise an error for bad responses like 404 or 500
        results = response.json()[0]

        if results:
            print(f"Found {len(results)} new scenes. Processing the first one.")
            scene = results[0]
            scene_name = scene['fileName']
            download_url = scene['downloadUrl']

            # Trigger the preprocessor script
            subprocess.run(["python3", "preprocessor.py", "--url", download_url, "--filename", scene_name], check=True)
        else:
            # This line will now correctly lead to the 'except' block below
            raise IndexError("No new scenes found in the last 24 hours.")

    except (requests.exceptions.RequestException, IndexError) as e:
        # This single block now handles both API errors and the case where no images are found
        print(f"No new scenes found or API error occurred: {e}")
        subprocess.run(["python3", "reporter.py", "--status", "no_data"], check=True)

    except Exception as e:
        print(f"An unexpected error occurred in the pipeline: {e}")


# This part runs the main function when the script is executed
if __name__ == "__main__":
    check_for_new_imagery()