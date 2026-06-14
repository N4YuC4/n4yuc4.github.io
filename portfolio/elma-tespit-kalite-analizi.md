# Apple Detection and Quality Analysis System

This project is a professional industrial desktop application that detects apples on industrial conveyor belts using YOLOv8-based segmentation, measures their physical dimensions, and classifies their quality using CIEDE2000 color analysis.

It was developed collaboratively during my internship. My primary responsibilities involved designing the modern user interface and building the core system architecture, while my teammates focused on the AI model training and the mathematical color analysis. I successfully integrated their machine learning models and algorithms into a unified, asynchronous, and high-performance desktop executable using PyQt5.

## Overall System UI & Architecture

The application was designed specifically for factory environments. The hybrid architecture seamlessly blends Deep Learning algorithms with a responsive Dashboard. I implemented asynchronous Multithreading to ensure GPU acceleration tasks do not block the UI.

![AI Assisted Apple Quality Analysis Dashboard](/static/images/portfolio-images/elma-tespit-figures/genel_gorunum.png)

## Core Features & Interfaces

### 1. Hardware Integration and Configuration
The system features a two-tiered configuration mechanism. I integrated the HikRobot MVS SDK to provide direct sensor-level control over the industrial cameras.

![Hardware Level Control Panel](/static/images/portfolio-images/elma-tespit-figures/kamera_renk_ayarlari.png)
*Sensor-level hardware controls like Exposure, Gain, and White Balance.*

### 2. Real-Time Segmentation and ROI Layer
At the heart of the system is the interactive canvas. Segments predicted by YOLOv8-seg are rendered with pixel-perfect accuracy. Each segmented apple functions as an interactive ROI (Region of Interest). By clicking on them, the operator adds them to a "Reference Pool" which acts as the baseline for color comparisons.

![Real-time Segmentation and ROI Layers](/static/images/portfolio-images/elma-tespit-figures/merkezi_kanvas.png)

### 3. Industrial Data Center & Metrics
The right panel of the interface acts as the analytical heart of the software, reporting the key scientific metrics defining the apples' market value:
- **Color Deviation (Delta E00):** The perceptual difference against the reference pool.
- **Intra-Class Deviation (σ - Sigma):** Represents the stability and homogeneity of the packaging batch.
- **Homogeneity Index (%):** Visual uniformity score where 90%+ is targeted for high quality.

![Industrial Data Analysis Panel](/static/images/portfolio-images/elma-tespit-figures/sag_analiz_paneli.png)

### 4. Smart Color Calibration
To compensate for varying industrial lighting conditions, the system includes an "Auto Color Adjustment" module, enabling a shift from an inaccurate white balance to natural colors suitable for scientific analysis.

![Auto Calibration](/static/images/portfolio-images/elma-tespit-figures/renk_sonrasi.png)

### 5. Asynchronous Batch Processing
Processing streams from files or live cameras are handled in a queue structure. A dynamic bottom gallery tracks the processed frames.

![Batch Processing Thumbnail Gallery](/static/images/portfolio-images/elma-tespit-figures/alt_galeri.png)

## Technologies Used

- **UI Framework & Architecture:** PyQt5, Asynchronous Multithreading (My contribution)
- **Computer Vision & Processing:** OpenCV 4.x (My contribution)
- **Deep Learning:** YOLOv8-seg (Team contribution)
- **Mathematical Analysis:** CIEDE2000 Color Distance (Team contribution)
- **Hardware Integration:** HikRobot MVS SDK
- **Data Persistence:** YAML Configurations, CSV Logging
