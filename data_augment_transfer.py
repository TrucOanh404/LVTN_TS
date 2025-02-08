import os
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import cv2
from tqdm import tqdm
import shutil

def create_augmented_dataset(input_dir, output_dir, target_count=1500):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    for subdir in ['Benign', 'Malignant', 'Normal']:
        input_path = os.path.join(input_dir, subdir)
        output_path = os.path.join(output_dir, subdir)
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        images = os.listdir(input_path)
        for img_name in images:
            shutil.copy2(os.path.join(input_path, img_name), 
                        os.path.join(output_path, img_name))
        
        current_count = len(images)
        if current_count >= target_count:
            continue
            
        augmentations_per_image = int(np.ceil((target_count - current_count) / current_count))
        
        for img_name in tqdm(images, desc=f'Augmenting {subdir}'):
            img_path = os.path.join(input_path, img_name)
            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = img.reshape((1,) + img.shape)
            
            i = 0
            for batch in datagen.flow(
                img,
                batch_size=1,
                save_to_dir=output_path,
                save_prefix=f'aug_{img_name[:-4]}',
                save_format='jpg'
            ):
                i += 1
                if i >= augmentations_per_image:
                    break
                if len(os.listdir(output_path)) >= target_count:
                    break

# Usage
input_directory = "Data_Transfer"  
output_directory = "Augmented_Data_Transfer"  
create_augmented_dataset(input_directory, output_directory)