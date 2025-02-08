import os
import shutil
import random
from sklearn.model_selection import train_test_split

def split_dataset(input_dir, output_dir, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
   if not os.path.exists(output_dir):
       os.makedirs(output_dir)
       
   # Create train/val/test directories
   for split in ['train', 'val', 'test']:
       for class_name in ['Benign', 'Malignant', 'Normal']:
           os.makedirs(os.path.join(output_dir, split, class_name), exist_ok=True)

   # Split and copy files for each class
   for class_name in ['Benign', 'Malignant', 'Normal']:
       files = os.listdir(os.path.join(input_dir, class_name))
       
       # First split: train and temp (val + test)
       train_files, temp_files = train_test_split(files, train_size=train_ratio, random_state=42)
       
       # Second split: val and test from temp
       val_ratio_adjusted = val_ratio / (val_ratio + test_ratio)
       val_files, test_files = train_test_split(temp_files, train_size=val_ratio_adjusted, random_state=42)

       # Copy files to respective directories
       for file in train_files:
           shutil.copy2(
               os.path.join(input_dir, class_name, file),
               os.path.join(output_dir, 'train', class_name, file)
           )
       
       for file in val_files:
           shutil.copy2(
               os.path.join(input_dir, class_name, file),
               os.path.join(output_dir, 'val', class_name, file)
           )
           
       for file in test_files:
           shutil.copy2(
               os.path.join(input_dir, class_name, file),
               os.path.join(output_dir, 'test', class_name, file)
           )

# Usage
input_directory = "Augmented_Data_Transfer"  
output_directory = "Split_Dataset"
split_dataset(input_directory, output_directory)