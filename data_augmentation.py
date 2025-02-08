import os
import cv2
import albumentations as A
from tqdm import tqdm
import numpy as np

input_dir = 'Data_In'

output_dir = 'data_augmented'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
transform = A.Compose([
    A.RandomRotate90(p=0.5),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.5),
    A.OneOf([
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=1),
        A.ColorJitter(brightness=0.2, contrast=0.2, p=1),
    ], p=0.5),
    A.OneOf([
        A.GaussNoise(var_limit=(10.0, 50.0), p=1),
        A.GaussianBlur(blur_limit=(3, 7), p=1),
    ], p=0.3),
    A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.1, rotate_limit=45, p=0.5),
])

num_augmentations = 3

image_files = [f for f in os.listdir(input_dir) if f.endswith('.png')]

for image_file in tqdm(image_files, desc="Processing images"):
    image_path = os.path.join(input_dir, image_file)
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    for i in range(num_augmentations):
        augmented = transform(image=image)
        augmented_image = augmented['image']

        augmented_image = cv2.cvtColor(augmented_image, cv2.COLOR_RGB2BGR)
        
        filename, ext = os.path.splitext(image_file)
        new_filename = f"{filename}_aug_{i+1}{ext}"
        
        output_path = os.path.join(output_dir, new_filename)
        cv2.imwrite(output_path, augmented_image)

print(f"Data augmentation completed! Augmented images saved in {output_dir}")
