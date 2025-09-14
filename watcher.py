# watcher.py
import requests
import datetime
import os
import subprocess
import schedule
import time

def check_for_new_imagery():
    print(f"[{datetime.datetime.now()}] Running watcher script...")

    # This is the search area for your Nagaon project
    area_of_interest = 'POLYGON((92.4958 26.2178,92.9387 26.2178,92.9387 26.466,92.4958 26.466,92.4958 26.2178))'
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

            # Trigger the preprocessor script
            subprocess.run(["python3", "preprocessor.py", "--url", download_url, "--filename", scene_name])
        else:
            print("No new scenes found.")
            # If no new imagery, trigger reporter to send a "no new data" email
            subprocess.run(["python3", "reporter.py", "--status", "no_data"])


    except requests.exceptions.RequestException as e:
        print(f"Error querying the ASF API: {e}")
    except IndexError:
        print("No new scenes found.")
        # If no new imagery, trigger reporter to send a "no new data" email
        subprocess.run(["python3", "reporter.py", "--status", "no_data"])
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Schedule the job to run every day at 7:00 AM IST
schedule.every().day.at("07:00").do(check_for_new_imagery)

print("Scheduler started. Waiting for the scheduled time...")
# Keep the script running to check the schedule
while True:
    schedule.run_pending()
    time.sleep(1)

if __name__ == '__main__':
    # Run the check immediately when the script is executed, then start the schedule
    check_for_new_imagery()