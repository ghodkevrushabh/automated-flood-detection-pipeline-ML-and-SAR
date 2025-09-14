# predictor.py
import argparse
import joblib
import rasterio
import numpy as np
import pandas as pd
from tqdm import tqdm
import subprocess

def make_prediction(new_image_path):
    print(f"--- Starting Prediction for {new_image_path} ---")
    try:
        # Load the trained model
        model = joblib.load("random_forest_flood_model.joblib")

        # Load the reference pre-flood image and the new during-flood image
        with rasterio.open("pre_flood_nagaon.tif") as src:
            pre_flood_img = src.read(1).astype(np.float32)
        with rasterio.open(new_image_path) as src:
            during_flood_img = src.read(1).astype(np.float32)

        # Make prediction in chunks to save memory
        height, width = pre_flood_img.shape
        chunk_size = 1000
        prediction_map = np.zeros((height, width), dtype=np.uint8)

        for i in tqdm(range(0, height, chunk_size), desc="Predicting"):
            start_row = i
            end_row = min(i + chunk_size, height)
            pre_chunk = pre_flood_img[start_row:end_row, :]
            during_chunk = during_flood_img[start_row:end_row, :]
            chunk_df = pd.DataFrame({'pre_flood': pre_chunk.flatten(), 'during_flood': during_chunk.flatten()})
            chunk_prediction = model.predict(chunk_df)
            prediction_map[start_row:end_row, :] = chunk_prediction.reshape(pre_chunk.shape)

        # Save the raw prediction map
        prediction_path = "clipped_data/prediction.tif"
        with rasterio.open(new_image_path) as src: meta = src.meta
        meta.update(count=1, dtype='uint8')
        with rasterio.open(prediction_path, 'w', **meta) as dst:
            dst.write(prediction_map, 1)

        print("Prediction map saved.")

        # Check for floods
        # (1 is flood, 0 is no flood in your model)
        flood_pixels = np.count_nonzero(prediction_map)
        total_pixels = prediction_map.size
        flood_percentage = (flood_pixels / total_pixels) * 100
        print(f"Flood percentage: {flood_percentage:.2f}%")

        # Set a threshold for flood detection (e.g., 1%)
        flood_threshold = 1.0
        if flood_percentage > flood_threshold:
            status = "flood"
        else:
            status = "no_flood"

        # Trigger the reporter script with the status
        subprocess.run(["python3", "reporter.py", "--status", status, "--map", prediction_path])


    except Exception as e:
        print(f"An error occurred during prediction: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', required=True)
    args = parser.parse_args()
    make_prediction(args.image)