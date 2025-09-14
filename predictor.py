# predictor.py
import argparse
import joblib
import rasterio
import numpy as np
import pandas as pd
from tqdm import tqdm
import subprocess
import sys

def make_prediction(new_image_path):
    print(f"--- Starting Prediction for {new_image_path} ---")
    try:
        model = joblib.load("random_forest_flood_model.joblib")
        with rasterio.open("pre_flood_nagaon.tif") as src:
            pre_flood_img = src.read(1).astype(np.float32)
        with rasterio.open(new_image_path) as src:
            during_flood_img = src.read(1).astype(np.float32)
            meta = src.meta

        height, width = pre_flood_img.shape
        prediction_map = np.zeros((height, width), dtype=np.uint8)

        # Process in chunks for memory efficiency
        for i in tqdm(range(0, height, 1000), desc="Predicting"):
            end_row = min(i + 1000, height)
            pre_chunk = pre_flood_img[i:end_row, :]
            during_chunk = during_flood_img[i:end_row, :]
            chunk_df = pd.DataFrame({'pre_flood': pre_chunk.flatten(), 'during_flood': during_chunk.flatten()})
            chunk_prediction = model.predict(chunk_df)
            prediction_map[i:end_row, :] = chunk_prediction.reshape(pre_chunk.shape)
        
        prediction_path = "clipped_data/prediction.tif"
        meta.update(count=1, dtype='uint8')
        with rasterio.open(prediction_path, 'w', **meta) as dst:
            dst.write(prediction_map, 1)
        print("Prediction map saved.")
        
        # --- CRITICAL FIX: Determine flood status ---
        flood_pixels = np.count_nonzero(prediction_map)
        flood_percentage = (flood_pixels / prediction_map.size) * 100
        print(f"Flood percentage: {flood_percentage:.2f}%")

        status = "flood" if flood_percentage > 1.0 else "no_flood"
        
        # --- CRITICAL FIX: Call reporter with correct arguments ---
        subprocess.run(["python3", "reporter.py", "--status", status, "--map", prediction_path], check=True)
        
    except Exception as e:
        print(f"FATAL: An error occurred during prediction: {e}")
        error_message = f"Error in predictor.py: {e}"
        subprocess.run(["python3", "reporter.py", "--status", "pipeline_failed", "--error-message", error_message])
        sys.exit(1) # Exit with an error code

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', required=True, help="Path to the new clipped satellite image.")
    args = parser.parse_args()
    make_prediction(args.image)
