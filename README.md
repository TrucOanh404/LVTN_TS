# LVTN_TS

## Breast Cancer Diagnosis System using YOLO and CNN Models

This repository contains the implementation of a **Breast Cancer Diagnosis System** using deep learning models, specifically **YOLOv8, YOLOv9 for tumor detection** and **VGG16, DenseNet121, InceptionV3 for classification**. The system is designed to assist medical professionals in detecting and classifying breast cancer using mammographic images.

---

## 📌 Project Overview
Breast cancer is one of the leading causes of mortality among women worldwide. Early detection is crucial for effective treatment and improved survival rates. This project applies **state-of-the-art deep learning models** to detect and classify breast tumors from medical images.

The system consists of two main components:
- **Object Detection (YOLOv8, YOLOv9):** Identifying tumor locations in mammograms.
- **Classification (CNN - VGG16, DenseNet121, InceptionV3):** Determining the nature of the detected tumors (Benign, Malignant, Normal).

### 🔗 Key Resources:
- **Google Drive (YOLO Training Data & Weights):** [Link Here](https://drive.google.com/drive/folders/1aGNxpZmhLLq2BhBt8WVHhmSWmQO5NGuY?usp=sharing)
- **Kaggle (Training Code & Transfer Learning Results):** [Link Here](https://www.kaggle.com/code/oanhtrankaggle/utv-transfer)

---

## ⚙️ Installation
Before running the project, install the required dependencies:

```bash
pip install -r requirements.txt
```

### 📦 Required Dependencies
The project requires the following Python packages:

```txt
numpy 
pandas 
scipy 
scikit-learn 
torch 
torchvision 
torchaudio 
tensorflow 
keras 
onnx 
onnxruntime 
opencv-python 
opencv-contrib-python 
albumentations 
pillow 
matplotlib 
seaborn 
transformers 
fastapi 
uvicorn 
requests 
tqdm 
protobuf 
pyyaml 
jsonschema
```

Ensure you have **Python 3.8+** installed.

---

## 🚀 How to Run the Project

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/LVTN_TS.git
cd LVTN_TS
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Model for Breast Cancer Detection
```bash
python detect.py --model yolov9 --source test_images/
```

### 4️⃣ Run Classification Model
```bash
python classify.py --model DenseNet121 --image test_images/sample.jpg
```

---

## 📊 Model Performance
The models were evaluated on a dataset from **Kaggle** with extensive data preprocessing and augmentation techniques. Below are some key results:

| Model        | mAP@50-95 | Precision | Recall | Inference Time | Parameters |
|-------------|----------|-----------|--------|----------------|------------|
| YOLOv8s     | 0.599    | 0.811     | 0.799  | 6.7ms          | 11.1M      |
| YOLOv9s     | 0.616    | 0.873     | 0.722  | 9.0ms          | 7.1M       |
| VGG16       | 85.3%    | 0.89      | 0.85   | 12.3ms         | 138M       |
| DenseNet121 | 88.7%    | 0.91      | 0.89   | 8.5ms          | 8M         |
| InceptionV3 | 86.5%    | 0.90      | 0.88   | 10.1ms         | 23M        |

*More details on training and evaluation metrics are available in the Kaggle notebook.*

---

## 📌 Dataset
The dataset used in this project was collected from Kaggle:
- **Dataset Name:** [Breast Ultrasound Images Dataset](https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset)
- **Data Types:** Mammographic images categorized into **Benign, Malignant, and Normal**.
- **Preprocessing:** Data augmentation using **Contrast-Limited Adaptive Histogram Equalization (CLAHE)** and resizing to **224×224 pixels**.

---



## 📢 Acknowledgments
Special thanks to the authors of the Kaggle dataset and the deep learning community for their contributions.

If you find this project useful, feel free to ⭐ the repository and contribute!

---

## 📬 Contact
For questions or collaboration, feel free to reach out:
- **Email:** tranthitrucoanh404@gmail.com
- **GitHub:** (https://github.com/TrucOanh404)

---

🛠️ **This project is open-source and available for research purposes. Any commercial use requires permission.**
