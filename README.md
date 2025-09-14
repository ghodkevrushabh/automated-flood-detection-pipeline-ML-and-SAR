# Automated Flood Detection Pipeline with SAR Imagery & ML

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ghodkevrushabh/automated-flood-detection-pipeline-sar-ml/main.yml?branch=main&style=for-the-badge)

An end-to-end, fully automated pipeline that leverages Sentinel-1 SAR satellite imagery and a Random Forest machine learning model to detect and map flood inundation. The entire workflow is orchestrated with GitHub Actions for daily, hands-off execution and reporting.

---

## Key Features

- **Automated Daily Execution**: The pipeline automatically runs every morning at 7:00 AM IST, checking for new satellite imagery over a predefined Area of Interest (AOI).
- **End-to-End Processing**: From data acquisition to final prediction, the entire workflow is automated—no manual intervention required.
- **SAR Imagery**: Utilizes Sentinel-1's C-band Synthetic Aperture Radar (SAR) data, which has the powerful ability to see through clouds, making it ideal for monitoring floods during monsoon seasons.
- **Machine Learning Core**: Employs a pixel-based Random Forest classifier to accurately distinguish between water and non-water areas.
- **Comprehensive Email Alerts**: Automatically sends detailed email notifications for every possible outcome:
  - **`FLOOD ALERT`**: If significant flooding is detected.
  - **`NO FLOOD`**: If an image is processed and no flooding is found.
  - **`NO NEW DATA`**: If no new satellite imagery is available for the day.
  - **`PIPELINE FAILURE`**: If any part of the pipeline encounters a critical error.

---

## How It Works: The Automated Pipeline

The project is architected as a modular pipeline where each script is responsible for a specific task and triggers the next one in the sequence.

```
┌──────────────────────────┐      ┌──────────────────────────┐      ┌──────────────────────────┐      ┌──────────────────────────┐
│                          │      │                          │      │                          │      │                          │
│      1. Watcher          ├─────►│      2. Preprocessor     ├─────►│      3. Predictor        ├─────►│      4. Reporter         │
│     (watcher.py)         │      │    (preprocessor.py)     │      │     (predictor.py)       │      │     (reporter.py)        │
│                          │      │                          │      │                          │      │                          │
└──────────────────────────┘      └──────────────────────────┘      └──────────────────────────┘      └──────────────────────────┘
          │                                │                                │                                │
          ▼                                ▼                                ▼                                ▼
  - Checks ASF for new             - Downloads & unzips raw         - Loads ML model & new           - Composes & sends email
    Sentinel-1 imagery               satellite data                   image                            alert based on status
  - Triggers Preprocessor          - Clips image to Area of         - Performs pixel-wise            - Notifies on success,
    if new image found               Interest (AOI)                   flood prediction                 failure, or no data
  - Triggers Reporter if           - Triggers Predictor             - Calculates flood %
    no new image                                                    - Triggers Reporter
```

---

## Project Methodology

Before the pipeline could be automated, the core assets and machine learning model were developed.

### Data Preparation in QGIS

The foundational data for the project, including the static pre-flood image and the ground truth data for model training, was prepared using **QGIS**. The key files produced during this stage were:
- **`pre_flood_2022.tif`**: A cloud-free, pre-flood Sentinel-1 image serving as a permanent baseline for "dry" conditions.
- **`during_flood_2022.tif`**: A Sentinel-1 image captured during a known flood event, used for creating the ground truth.
- **`ground_truth_2022.tif`**: A manually created raster where each pixel was labeled as either **Water (1)** or **Land (0)**. This file is the cornerstone of the model's training data.

### Machine Learning Procedure

The flood detection model is a **Random Forest Classifier** from `scikit-learn`, chosen for its high accuracy and robustness. The procedure to train and use the model is as follows:

1.  **Training Data Generation**:
    - The script loads the `pre_flood_2022.tif`, `during_flood_2022.tif`, and the `ground_truth_2022.tif` images.
    - It then samples thousands of pixels from these images, creating a structured dataset.
    - For each pixel, the training features (`X`) are the radar backscatter values from the pre-flood and during-flood images. The target label (`y`) is the corresponding value (1 for Water, 0 for Land) from the ground truth file.

2.  **Model Training**:
    - The Random Forest Classifier is trained on this dataset (`X`, `y`).
    - The model learns the complex patterns and thresholds in SAR backscatter that differentiate flooded areas from permanently dry land or permanent water bodies.

3.  **Prediction**:
    - In the automated pipeline, the trained model is loaded.
    - This pair of values for each pixel is fed to the trained model, which predicts if the new pixel is "Water" or "Land".
    - The final output is a complete, geo-referenced flood map (`.tif`) showing the extent of the inundation.

---

## Technology Stack

- **Cloud Automation**: GitHub Actions (CI/CD)
- **Manual GIS Prep**: QGIS
- **Data Source**: Alaska Satellite Facility (ASF) API for Sentinel-1 GRD Imagery
- **Machine Learning**: Scikit-learn (Random Forest Classifier)
- **Geospatial Processing**: GDAL, Rasterio, NumPy
- **Core Language**: Python 3.10
- **Data Handling**: Pandas
- **Large File Management**: Git LFS (Large File Storage)

---

## Setup and Configuration

To run this project, you need to configure the following:

### 1. Clone the Repository

```bash
# Clone the repository
git clone [https://github.com/ghodkevrushabh/automated-flood-detection-pipeline-sar-ml.git](https://github.com/ghodkevrushabh/automated-flood-detection-pipeline-sar-ml.git)

# Navigate into the project directory
cd automated-flood-detection-pipeline-sar-ml

# Install LFS and pull the large files
git lfs install
git lfs pull
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure GitHub Secrets

1.  Generate a 16-character **App Password** for your Google Account.
2.  In your GitHub repository, go to **Settings > Secrets and variables > Actions**.
3.  Create a new repository secret named `GMAIL_APP_PASSWORD` and paste the App Password as the value.

### 4. Update Email Addresses
In `reporter.py`, change the placeholder email addresses to your own.

```python
# reporter.py
...
sender_email = "your_email@gmail.com"  # CHANGE THIS
receiver_email = "your_email@gmail.com" # CHANGE THIS
...
```

---

## Deployment

The pipeline is automatically deployed upon pushing to the `main` branch. The GitHub Actions workflow (`.github/workflows/main.yml`) is configured with two triggers:

- **`schedule`**: Runs the pipeline automatically every day at 7:00 AM IST.
- **`workflow_dispatch`**: Allows for manual test runs directly from the GitHub Actions tab.
