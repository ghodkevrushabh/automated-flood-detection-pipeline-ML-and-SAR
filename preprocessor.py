# preprocessor.py
import argparse
import os
import subprocess
import zipfile
import requests
from glob import glob
import sys

def preprocess_image(url, filename):
    print(f"--- Starting Preprocessing for {filename} ---")
    try:
        os.makedirs("raw_data", exist_ok=True)
        os.makedirs("clipped_data", exist_ok=True)
        zip_path = os.path.join("raw_data", filename)

        print("Downloading data...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("Download complete.")

        print("Unzipping file...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("raw_data")
        
        unzipped_folder = glob(f"raw_data/{os.path.splitext(filename)[0]}.SAFE")[0]
        input_tif = glob(f"{unzipped_folder}/measurement/*-vv-*.tiff")[0]
        print(f"Found TIF file: {input_tif}")
        
        # --- GOAL: Set correct clipping extent ---
        xmin, xmax, ymin, ymax = '523590.0000', '668010.0000', '2855310.0000', '2980680.0000'
        output_tif = os.path.join("clipped_data", "new_flood_image.tif")
        gdal_command = f"gdal_translate -projwin {xmin} {ymax} {xmax} {ymin} -of GTiff {input_tif} {output_tif}"
        
        print("Clipping raster...")
        subprocess.run(gdal_command, shell=True, check=True)
        print("Clipping complete.")
        
        subprocess.run(["python3", "predictor.py", "--image", output_tif], check=True)

    except Exception as e:
        print(f"FATAL: An error occurred during preprocessing: {e}")
        error_message = f"Error in preprocessor.py: {e}"
        subprocess.run(["python3", "reporter.py", "--status", "pipeline_failed", "--error-message", error_message])
        sys.exit(1) # Exit with an error code

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_glob_workaround_argument('--filename', required=True)
    args = parser.parse_args()
    preprocess_image(args.url, args.filename)
