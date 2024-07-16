# Interactive Image Labeling Tool

## Overview
This Python script provides a tool for interactively labeling raw images. The labeled images generated are suitable for training machine learning models. Each pixel in the labeled image is assigned a numerical value corresponding to a specific class label.

## Setup Instructions

1. **Create Virtual Environment**:
    ```bash
    conda create -p venv python==3.9 -y && conda activate venv\
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```


3. **Run the Application**:
    ```bash
    python app.py
    ```



## Functionalities
1. **Load Raw Image**: The script can load raw images using OpenCV.
2. **Pre-processing (Optional)**: The script can toggle grayscale view of the image.
3. **Label Integration**:
   - User-Provided Labeled Image: Load a pre-made labeled image.
   - Interactive Labeling: Create labeled images by interactively drawing polygons on the raw image.

## Requirements
- Python 3.9
- opencv-python (`cv2`)
- Numpy
- Pillow (`PIL`)
- Tkinter (usually included with Python)

## How to Run
1. Ensure you have all required libraries installed:
2. Run the script:
3. Use the interface to load images, toggle grayscale, select labels, and draw polygons to label the image.
4. Save the labeled image for use in machine learning tasks.

## Assumptions
- Raw images can be in formats supported by OpenCV (jpg, jpeg, png, bmp).
- Labeled images are grayscale images in PNG format.

## Error Handling
- The script includes error handling for loading invalid images, saving issues, and other operations.

## Bonus Points
- Implemented interactive labeling.
- Error handling for invalid file formats or missing labeled images.

## Notes
- This script uses OpenCV for image processing and Tkinter for the GUI.
