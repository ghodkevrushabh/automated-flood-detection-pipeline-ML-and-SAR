# preprocessor.py
import argparse
import os
import subprocess
import zipfile
import requests
from glob import glob

def preprocess_image(url, filename):
    print(f"--- Starting Preprocessing for {filename} ---")
    try:
        # Create directories to store data
        os.makedirs("raw_data", exist_ok=True)
        os.makedirs("clipped_data", exist_ok=True)

        zip_path = os.path.join("raw_data", filename)

        # 1. Download the file
        print("Downloading data...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("Download complete.")

        # 2. Unzip the file
        print("Unzipping file...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("raw_data")

        # Find the VV polarization tif file
        unzipped_folder = glob(f"raw_data/{filename.replace('.zip', '')}*")[0]
        input_tif = glob(f"{unzipped_folder}/*_VV.tif")[0]
        print(f"Found TIF file: {input_tif}")

        # 3. Clip the file
        xmin, xmax, ymin, ymax = '523590.0000', '668010.0000', '2855310.0000', '2980680.0000' # Your project coordinates [EPSG:32646]
        output_tif = os.path.join("clipped_data", "new_flood_image.tif")
        gdal_command = f"gdal_translate -projwin {xmin} {ymax} {xmax} {ymin} {input_tif} {output_tif}"

        print("Clipping raster...")
        subprocess.run(gdal_command, shell=True, check=True)
        print("Clipping complete.")

        # Trigger the predictor script
        subprocess.run(["python3", "predictor.py", "--image", output_tif])

    except Exception as e:
        print(f"An error occurred during preprocessing: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--filename', required=True)
    args = parser.parse_args()
    preprocess_image(args.url, args.filename)