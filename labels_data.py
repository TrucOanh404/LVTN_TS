import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                           QComboBox, QScrollArea, QMessageBox, QSpinBox,
                           QGroupBox, QFormLayout, QProgressBar, QStatusBar,
                           QTabWidget, QTextEdit, QListWidget, QShortcut)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QImage, QFont, QKeySequence
from PyQt5.QtCore import Qt, QRect, QPoint, QThread, pyqtSignal, QSize
import cv2
import numpy as np
from pathlib import Path
import shutil
from ultralytics import YOLO
import random
import time
import json
from datetime import datetime

class DetectionWorker(QThread):
    """Worker thread for running detection"""
    progress = pyqtSignal(int)
    image_processed = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, model_path, input_dir, output_dir, conf_threshold):
        super().__init__()
        self.model_path = model_path
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.conf_threshold = conf_threshold
        self.stats = {
            'total_images': 0,
            'total_detections': 0,
            'class_counts': {0: 0, 1: 0},
            'processing_time': 0
        }
        
    def run(self):
        try:
            start_time = time.time()
            
            # Load model
            model = YOLO(self.model_path)
            image_files = list(Path(self.input_dir).glob('*.png'))
            total_files = len(image_files)
            self.stats['total_images'] = total_files
            
            for i, img_path in enumerate(image_files):
                # Read image
                img = cv2.imread(str(img_path))
                if img is None:
                    continue
                
                # Perform detection
                results = model.predict(source=img, conf=self.conf_threshold, save=False)
                result = results[0]
                
                # Draw boxes on image
                img_with_boxes = img.copy()
                detections_count = 0
                
                for box, cls, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf):
                    x1, y1, x2, y2 = map(int, box.cpu().numpy())
                    class_id = int(cls)
                    confidence = float(conf)
                    
                    # Update statistics
                    detections_count += 1
                    self.stats['class_counts'][class_id] = self.stats['class_counts'].get(class_id, 0) + 1
                    
                    # Draw box and label
                    color = (0, 0, 255) if class_id == 0 else (255, 0, 0)
                    cv2.rectangle(img_with_boxes, (x1, y1), (x2, y2), color, 2)
                    
                    # Add confidence score
                    class_names = {0: "Benign", 1: "Malignant", 2: "Normal"}
                    label = f'{class_names[class_id]}: {confidence:.2f}'
                    cv2.putText(img_with_boxes, label, (x1, y1-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                self.stats['total_detections'] += detections_count
                
                # Save annotated image
                output_img_path = os.path.join(self.output_dir, img_path.name)
                cv2.imwrite(output_img_path, img_with_boxes)
                
                # Save YOLO format annotations
                img_h, img_w = img.shape[:2]
                txt_path = os.path.join(self.output_dir, img_path.stem + '.txt')
                with open(txt_path, 'w') as f:
                    for box, cls in zip(result.boxes.xyxy, result.boxes.cls):
                        x1, y1, x2, y2 = box.cpu().numpy()
                        class_id = int(cls)
                        
                        # Convert to YOLO format
                        x_center = (x1 + x2) / (2 * img_w)
                        y_center = (y1 + y2) / (2 * img_h)
                        w = abs(x2 - x1) / img_w
                        h = abs(y2 - y1) / img_h
                        f.write(f"{class_id} {x_center} {y_center} {w} {h}\n")
                
                # Emit signals
                progress = int((i + 1) / total_files * 100)
                self.progress.emit(progress)
                self.image_processed.emit(output_img_path)
            
            # Calculate total processing time
            self.stats['processing_time'] = time.time() - start_time
            self.finished.emit(self.stats)
            
        except Exception as e:
            self.error.emit(str(e))

class DataSplitWorker(QThread):
    """Worker thread for splitting data"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, output_dir, train_ratio):
        super().__init__()
        self.output_dir = output_dir
        self.train_ratio = train_ratio
        
    def run(self):
        try:
            # Create train and valid directories
            train_dir = os.path.join(self.output_dir, 'train')
            valid_dir = os.path.join(self.output_dir, 'valid')
            os.makedirs(train_dir, exist_ok=True)
            os.makedirs(valid_dir, exist_ok=True)
            
            # Get all image files
            image_files = list(Path(self.output_dir).glob('*.png'))
            random.shuffle(image_files)
            
            # Calculate split
            train_size = int(len(image_files) * self.train_ratio / 100)
            train_files = image_files[:train_size]
            valid_files = image_files[train_size:]
            
            total_files = len(image_files)
            files_processed = 0
            
            # Move train files
            for img_path in train_files:
                txt_path = img_path.with_suffix('.txt')
                shutil.move(str(img_path), os.path.join(train_dir, img_path.name))
                if txt_path.exists():
                    shutil.move(str(txt_path), os.path.join(train_dir, txt_path.name))
                files_processed += 1
                self.progress.emit(int(files_processed / total_files * 100))
            
            # Move valid files
            for img_path in valid_files:
                txt_path = img_path.with_suffix('.txt')
                shutil.move(str(img_path), os.path.join(valid_dir, img_path.name))
                if txt_path.exists():
                    shutil.move(str(txt_path), os.path.join(valid_dir, txt_path.name))
                files_processed += 1
                self.progress.emit(int(files_processed / total_files * 100))
            
            stats = {
                'train_count': len(train_files),
                'valid_count': len(valid_files)
            }
            self.finished.emit(stats)
            
        except Exception as e:
            self.error.emit(str(e))

class LabelingImageView(QWidget):
    """Widget for displaying and editing image labels"""
    def __init__(self):
        super().__init__()
        self.image = None
        self.boxes = []  # [(x1,y1,x2,y2,class_id), ...]
        self.current_box = None
        self.selected_box_idx = None
        self.edit_mode = "Add Box"
        self.drawing = False
        self.moving = False
        self.resizing = False
        self.resize_handle = None
        self.current_class = 0
        self.resize_handle_size = 6
        
    def setImage(self, image_path):
        self.image = cv2.imread(image_path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.update()
        
    def setBoxes(self, boxes):
        self.boxes = boxes
        self.update()
        
    def mousePressEvent(self, event):
        if self.image is None:
            return
            
        pos = event.pos()
        if self.edit_mode == "Add Box":
            self.startDrawing(pos)
        elif self.edit_mode == "Edit Box":
            self.startEditing(pos)
        elif self.edit_mode == "Delete Box":
            self.deleteBoxAt(pos)
            
    def mouseMoveEvent(self, event):
        if self.image is None:
            return
            
        pos = event.pos()
        if self.edit_mode == "Add Box" and self.drawing:
            self.updateDrawing(pos)
        elif self.edit_mode == "Edit Box":
            if self.moving:
                self.moveBox(pos)
            elif self.resizing:
                self.resizeBox(pos)
                
    def mouseReleaseEvent(self, event):
        if self.drawing:
            self.finishDrawing()
        elif self.moving or self.resizing:
            self.finishEditing()
            
    def startDrawing(self, pos):
        self.drawing = True
        self.current_box = [pos.x(), pos.y(), pos.x(), pos.y()]
        
    def updateDrawing(self, pos):
        if self.current_box:
            self.current_box[2] = pos.x()
            self.current_box[3] = pos.y()
            self.update()
            
    def finishDrawing(self):
        if self.current_box:
            x1 = min(self.current_box[0], self.current_box[2])
            y1 = min(self.current_box[1], self.current_box[3])
            x2 = max(self.current_box[0], self.current_box[2])
            y2 = max(self.current_box[1], self.current_box[3])
            
            # Add box if it has minimum size
            if x2 - x1 > 5 and y2 - y1 > 5:
                self.boxes.append((x1, y1, x2, y2, self.current_class))
                
        self.drawing = False
        self.current_box = None
        self.update()
        
    def startEditing(self, pos):
        # Check if click is on resize handle of selected box
        if self.selected_box_idx is not None:
            box = self.boxes[self.selected_box_idx]
            x1, y1, x2, y2, _ = box
            
            # Check each corner
            corners = [
                (x1, y1, "top-left"),
                (x2, y1, "top-right"),
                (x1, y2, "bottom-left"),
                (x2, y2, "bottom-right")
            ]
            
            for corner_x, corner_y, handle in corners:
                if abs(pos.x() - corner_x) < self.resize_handle_size and \
                   abs(pos.y() - corner_y) < self.resize_handle_size:
                    self.resizing = True
                    self.resize_handle = handle
                    return
        
        # If not resizing, check if click is inside any box
        for i, (x1, y1, x2, y2, _) in enumerate(self.boxes):
            if (x1 < pos.x() < x2 and y1 < pos.y() < y2):
                self.selected_box_idx = i
                self.moving = True
                self.move_start = pos
                self.move_original = self.boxes[i]
                return
                
        self.selected_box_idx = None
        
    def moveBox(self, pos):
        if self.moving and self.selected_box_idx is not None:
            dx = pos.x() - self.move_start.x()
            dy = pos.y() - self.move_start.y()
            
            x1, y1, x2, y2, class_id = self.move_original
            new_x1 = max(0, min(self.image.shape[1], x1 + dx))
            new_y1 = max(0, min(self.image.shape[0], y1 + dy))
            new_x2 = max(0, min(self.image.shape[1], x2 + dx))
            new_y2 = max(0, min(self.image.shape[0], y2 + dy))
            
            self.boxes[self.selected_box_idx] = (new_x1, new_y1, new_x2, new_y2, class_id)
            self.update()
            
    def resizeBox(self, pos):
        if self.resizing and self.selected_box_idx is not None:
            x1, y1, x2, y2, class_id = self.boxes[self.selected_box_idx]
            
            if self.resize_handle == "top-left":
                x1 = pos.x()
                y1 = pos.y()
            elif self.resize_handle == "top-right":
                x2 = pos.x()
                y1 = pos.y()
            elif self.resize_handle == "bottom-left":
                x1 = pos.x()
                y2 = pos.y()
            elif self.resize_handle == "bottom-right":
                x2 = pos.x()
                y2 = pos.y()
                
            # Ensure x1 < x2 and y1 < y2
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
                
            self.boxes[self.selected_box_idx] = (x1, y1, x2, y2, class_id)
            self.update()
            
    def finishEditing(self):
        self.moving = False
        self.resizing = False
        self.resize_handle = None
        
    def deleteBoxAt(self, pos):
        """Delete box at clicked position"""
        for i, (x1, y1, x2, y2, _) in enumerate(self.boxes):
            if (x1 < pos.x() < x2 and y1 < pos.y() < y2):
                del self.boxes[i]
                # Xử lý selected_box_idx
                if self.selected_box_idx is not None:  # Thêm kiểm tra None
                    if self.selected_box_idx == i:
                        self.selected_box_idx = None
                    elif self.selected_box_idx > i:
                        self.selected_box_idx -= 1
                self.update()
                return True 
        return False 
     
    def paintEvent(self, event):
        if self.image is None:
            return
            
        painter = QPainter(self)
        
        # Draw image
        height, width = self.image.shape[:2]
        bytes_per_line = 3 * width
        qt_image = QImage(self.image.data, width, height, 
                         bytes_per_line, QImage.Format_RGB888)
        painter.drawImage(self.rect(), qt_image)
        
        # Draw boxes
        for i, (x1,y1,x2,y2,class_id) in enumerate(self.boxes):
            class_names = {0: "Benign", 1: "Malignant", 2: "Normal"}
            color = Qt.red if class_id == 0 else Qt.blue
            label = class_names[class_id]
            painter.drawText(int(x1), int(y1-5), label)
            if i == self.selected_box_idx:
                pen = QPen(color, 2, Qt.DashLine)
            else:
                pen = QPen(color, 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(int(x1), int(y1), int(x2-x1), int(y2-y1))
            
            # Draw resize handles for selected box
            if i == self.selected_box_idx and self.edit_mode == "Edit Box":
                painter.setPen(QPen(Qt.white, 1, Qt.SolidLine))
                painter.setBrush(Qt.black)
                s = self.resize_handle_size
                # Top-left
                painter.drawRect(int(x1-s/2), int(y1-s/2), s, s)
                # Top-right
                painter.drawRect(int(x2-s/2), int(y1-s/2), s, s)
                # Bottom-left
                painter.drawRect(int(x1-s/2), int(y2-s/2), s, s)
                # Bottom-right
                painter.drawRect(int(x2-s/2), int(y2-s/2), s, s)
            
        # Draw current box
        if self.current_box:
            painter.setPen(QPen(Qt.green, 2, Qt.DashLine))
            x1,y1,x2,y2 = self.current_box
            painter.drawRect(int(x1), int(y1), int(x2-x1), int(y2-y1))

class DataSplitWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    status = pyqtSignal(str)  # Thêm signal để báo trạng thái
    
    def __init__(self, input_dir, output_dir, save_dir, train_ratio):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir 
        self.save_dir = save_dir
        self.train_ratio = train_ratio
        
    def run(self):
        try:
            # Create directory structure 
            train_dir = os.path.join(self.save_dir, 'train')
            valid_dir = os.path.join(self.save_dir, 'valid')
            
            train_images_dir = os.path.join(train_dir, 'images')
            train_labels_dir = os.path.join(train_dir, 'labels')
            valid_images_dir = os.path.join(valid_dir, 'images')
            valid_labels_dir = os.path.join(valid_dir, 'labels')
            
            # Create directories
            os.makedirs(train_images_dir, exist_ok=True)
            os.makedirs(train_labels_dir, exist_ok=True) 
            os.makedirs(valid_images_dir, exist_ok=True)
            os.makedirs(valid_labels_dir, exist_ok=True)

            # Get input files
            input_images = list(Path(self.input_dir).glob('*.png'))
            if not input_images:
                raise Exception("No images found in input directory")
                
            # Split files
            random.shuffle(input_images)
            train_size = int(len(input_images) * self.train_ratio / 100)
            train_files = input_images[:train_size]
            valid_files = input_images[train_size:]
            
            total = len(input_images)
            processed = 0

            # Copy train files
            self.status.emit("Copying train files...")
            for img_path in train_files:
                try:
                    # Copy image
                    shutil.copy2(str(img_path), os.path.join(train_images_dir, img_path.name))
                    
                    # Copy annotation if exists
                    txt_path = os.path.join(self.output_dir, img_path.stem + '.txt')
                    if os.path.exists(txt_path):
                        shutil.copy2(txt_path, os.path.join(train_labels_dir, img_path.stem + '.txt'))
                        
                    processed += 1
                    self.progress.emit(int(processed * 100 / total))
                except Exception as e:
                    print(f"Error processing train file {img_path}: {e}")

            # Copy validation files  
            self.status.emit("Copying validation files...")
            for img_path in valid_files:
                try:
                    # Copy image
                    shutil.copy2(str(img_path), os.path.join(valid_images_dir, img_path.name))
                    
                    # Copy annotation if exists
                    txt_path = os.path.join(self.output_dir, img_path.stem + '.txt')
                    if os.path.exists(txt_path):
                        shutil.copy2(txt_path, os.path.join(valid_labels_dir, img_path.stem + '.txt'))
                        
                    processed += 1
                    self.progress.emit(int(processed * 100 / total))
                except Exception as e:
                    print(f"Error processing validation file {img_path}: {e}")

            # Create yaml file
            self.status.emit("Creating YAML file...")
            yaml_content = f"""
train: {train_images_dir}
val: {valid_images_dir}
nc: 2
names: ['Benign', 'Malignant', 'Normal']
"""
            with open(os.path.join(self.save_dir, 'data.yaml'), 'w') as f:
                f.write(yaml_content)

            stats = {
                'train_count': len(train_files),
                'valid_count': len(valid_files)
            }
            self.finished.emit(stats)
            
        except Exception as e:
            self.error.emit(str(e))

class YOLOTool(QMainWindow):
    """Main window class for YOLO Detection & Labeling Tool"""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle('YOLO Detection & Labeling Tool')
        self.setGeometry(100, 100, 1400, 900)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Detection tab
        detection_tab = self.initDetectionTab()
        tab_widget.addTab(detection_tab, "Detection & Split")
        
        # Labeling tab
        labeling_tab = self.initLabelingTab()
        tab_widget.addTab(labeling_tab, "Labeling")
        
        # Add tab widget to main layout
        main_layout.addWidget(tab_widget)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Initialize variables
        self.model_path = None
        self.input_dir = None
        self.output_dir = None
        self.detection_worker = None
        self.split_worker = None
        self.image_files = []
        self.current_image_idx = -1

    def initDetectionTab(self):
        """Initialize the detection tab"""
        detection_tab = QWidget()
        detection_layout = QHBoxLayout()
        detection_tab.setLayout(detection_layout)
        
        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(300)
        
        # Detection Group
        detect_group = QGroupBox("Detection Settings")
        detect_layout = QFormLayout()
        
        self.model_path_btn = QPushButton('Select Model')
        self.model_path_btn.clicked.connect(self.selectModel)
        self.input_dir_btn = QPushButton('Select Input Directory')
        self.input_dir_btn.clicked.connect(self.selectInputDir)
        self.output_dir_btn = QPushButton('Select Output Directory')
        self.output_dir_btn.clicked.connect(self.selectOutputDir)
        self.detect_btn = QPushButton('Run Detection')
        self.detect_btn.clicked.connect(self.runDetection)
        
        self.conf_threshold = QSpinBox()
        self.conf_threshold.setValue(25)
        self.conf_threshold.setRange(1, 100)
        
        detect_layout.addRow("Model:", self.model_path_btn)
        detect_layout.addRow("Input:", self.input_dir_btn)
        detect_layout.addRow("Output:", self.output_dir_btn)
        detect_layout.addRow("Confidence (%):", self.conf_threshold)
        detect_layout.addRow(self.detect_btn)
        detect_group.setLayout(detect_layout)
        
        # Data Split Group
        split_group = QGroupBox("Data Split")
        split_layout = QFormLayout()
        
        self.train_ratio = QSpinBox()
        self.train_ratio.setValue(80)
        self.train_ratio.setRange(1, 99)
        
        self.split_btn = QPushButton('Split Data')
        self.split_btn.clicked.connect(self.splitData)
        
        split_layout.addRow("Train Ratio (%):", self.train_ratio)
        split_layout.addRow(self.split_btn)
        split_group.setLayout(split_layout)
        
        # Progress Bars
        self.detection_progress = QProgressBar()
        self.detection_progress.setVisible(False)
        
        self.split_progress = QProgressBar()
        self.split_progress.setVisible(False)
        
        # Statistics Text Area
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFixedHeight(200)
        
        # Add components to left panel
        left_layout.addWidget(detect_group)
        left_layout.addWidget(split_group)
        left_layout.addWidget(self.detection_progress)
        left_layout.addWidget(self.split_progress)
        left_layout.addWidget(QLabel("Statistics:"))
        left_layout.addWidget(self.stats_text)
        
        # Image display area
        self.scroll_area = QScrollArea()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        
        # Add panels to layout
        detection_layout.addWidget(left_panel)
        detection_layout.addWidget(self.scroll_area)
        
        return detection_tab

    def initLabelingTab(self):
        """Initialize the labeling tab"""
        labeling_tab = QWidget()
        layout = QHBoxLayout()
        labeling_tab.setLayout(layout)
        
        # Left control panel
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(300)
        
        # Image navigation
        nav_group = QGroupBox("Image Navigation")
        nav_layout = QVBoxLayout()
        
        self.prev_image_btn = QPushButton("Previous Image")
        self.next_image_btn = QPushButton("Next Image")
        self.current_image_label = QLabel("Image: 0/0")
        
        nav_layout.addWidget(self.current_image_label)
        nav_layout.addWidget(self.prev_image_btn)
        nav_layout.addWidget(self.next_image_btn)
        nav_group.setLayout(nav_layout)
        
        # Box editing controls
        edit_group = QGroupBox("Box Editing")
        edit_layout = QVBoxLayout()
        
        self.edit_mode_combo = QComboBox()
        self.edit_mode_combo.addItems(["Add Box", "Edit Box", "Delete Box"])
        
        self.class_select = QComboBox()
        self.class_select.addItems(["Benign", "Malignant", "Normal"])
        
        edit_layout.addWidget(QLabel("Edit Mode:"))
        edit_layout.addWidget(self.edit_mode_combo)
        edit_layout.addWidget(QLabel("Class:"))
        edit_layout.addWidget(self.class_select)
        edit_group.setLayout(edit_layout)
        # shortcut Delete key
        delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        delete_shortcut.activated.connect(self.deleteSelectedBox)
        # Box list
        box_group = QGroupBox("Boxes")
        box_layout = QVBoxLayout()
        self.box_list = QListWidget()
        self.delete_box_btn = QPushButton("Delete Selected Box")
        box_layout.addWidget(self.box_list)
        box_layout.addWidget(self.delete_box_btn)
        box_group.setLayout(box_layout)
        
        # Save controls
        save_group = QGroupBox("Save")
        save_layout = QVBoxLayout()
        self.save_labels_btn = QPushButton("Save Labels")
        save_layout.addWidget(self.save_labels_btn)
        save_group.setLayout(save_layout)
        
        # Add all groups to left panel
        left_layout.addWidget(nav_group)
        left_layout.addWidget(edit_group)
        left_layout.addWidget(box_group)
        left_layout.addWidget(save_group)
        
        # Image display area
        self.label_image_view = LabelingImageView()
        
        # Connect signals
        self.prev_image_btn.clicked.connect(self.prevLabelImage)
        self.next_image_btn.clicked.connect(self.nextLabelImage)
        self.edit_mode_combo.currentTextChanged.connect(self.changeLabelingMode)
        self.class_select.currentIndexChanged.connect(self.updateCurrentClass)
        self.delete_box_btn.clicked.connect(self.deleteSelectedBox)
        self.save_labels_btn.clicked.connect(self.saveLabels)
        self.box_list.itemSelectionChanged.connect(self.boxSelectionChanged)
        
        # Add to layout
        layout.addWidget(left_panel)
        layout.addWidget(self.label_image_view)
        
        return labeling_tab

    def selectModel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select YOLO Model", "", "Model Files (*.pt)")
        if file_path:
            self.model_path = file_path
            self.model_path_btn.setText(os.path.basename(file_path))
            self.status_bar.showMessage(f"Selected model: {file_path}")
            
    def selectInputDir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if dir_path:
            self.input_dir = dir_path
            self.input_dir_btn.setText(os.path.basename(dir_path))
            self.status_bar.showMessage(f"Selected input directory: {dir_path}")
            
    def selectOutputDir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir = dir_path
            self.output_dir_btn.setText(os.path.basename(dir_path))
            self.status_bar.showMessage(f"Selected output directory: {dir_path}")
            
            # Update image files list for labeling
            self.image_files = [str(p) for p in Path(dir_path).glob('*.png')]
            if self.image_files:
                self.current_image_idx = 0
                self.loadLabelImage(0)
    
    def updateDetectionProgress(self, value):
        self.detection_progress.setValue(value)
        
    def updateSplitProgress(self, value):
        self.split_progress.setValue(value)
    
    def showProcessedImage(self, image_path):
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(self.image_label.size(), 
                                    Qt.KeepAspectRatio, 
                                    Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
    
    def updateStats(self, stats):
        report = f"Detection Report ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n"
        report += "-" * 50 + "\n"
        report += f"Total Images Processed: {stats['total_images']}\n"
        report += f"Total Detections: {stats['total_detections']}\n"
        report += f"Benign Count: {stats['class_counts'].get(0, 0)}\n"
        report += f"Malignant Count: {stats['class_counts'].get(1, 0)}\n"
        report += f"Normal Count: {stats['class_counts'].get(1, 0)}\n"
        report += f"Processing Time: {stats['processing_time']:.2f} seconds\n"
        report += f"Average Time per Image: {stats['processing_time']/stats['total_images']:.2f} seconds\n"
        
        self.stats_text.setText(report)
        
    def runDetection(self):
        if not all([self.model_path, self.input_dir, self.output_dir]):
            QMessageBox.warning(self, "Warning", "Please select model and directories first!")
            return
            
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Disable UI elements during detection
        self.detect_btn.setEnabled(False)
        self.split_btn.setEnabled(False)
        self.detection_progress.setVisible(True)
        self.detection_progress.setValue(0)
        self.status_bar.showMessage("Detection in progress...")
        
        # Create and start worker thread
        self.detection_worker = DetectionWorker(
            self.model_path,
            self.input_dir,
            self.output_dir,
            self.conf_threshold.value()/100
        )
        
        self.detection_worker.progress.connect(self.updateDetectionProgress)
        self.detection_worker.image_processed.connect(self.showProcessedImage)
        self.detection_worker.finished.connect(self.detectionFinished)
        self.detection_worker.error.connect(self.detectionError)
        
        self.detection_worker.start()
        
    def detectionFinished(self, stats):
        self.detect_btn.setEnabled(True)
        self.split_btn.setEnabled(True)
        self.detection_progress.setVisible(False)
        self.status_bar.showMessage("Detection completed successfully!")
        self.updateStats(stats)
        
        # Update image files list for labeling
        self.image_files = [str(p) for p in Path(self.output_dir).glob('*.png')]
        if self.image_files:
            self.current_image_idx = 0
            self.loadLabelImage(0)
            
        QMessageBox.information(self, "Success", 
                              f"Detection completed!\nProcessed {stats['total_images']} images.")
        
    def detectionError(self, error_msg):
        self.detect_btn.setEnabled(True)
        self.split_btn.setEnabled(True)
        self.detection_progress.setVisible(False)
        self.status_bar.showMessage("Detection failed!")
        QMessageBox.critical(self, "Error", f"Detection failed: {error_msg}")
    
    def splitData(self):
        if not self.input_dir or not os.path.exists(self.input_dir):
            QMessageBox.warning(self, "Warning", "Please select input directory first!")
            return
            
        if not self.output_dir or not os.path.exists(self.output_dir):
            QMessageBox.warning(self, "Warning", "Please run detection first!")
            return

        save_dir = QFileDialog.getExistingDirectory(self, "Select Directory to Save Dataset")
        if not save_dir:
            return

        # Disable UI
        self.split_btn.setEnabled(False)
        self.detect_btn.setEnabled(False)
        self.split_progress.setVisible(True)
        self.split_progress.setValue(0)

        # Create and start worker
        self.split_worker = DataSplitWorker(
            self.input_dir,
            self.output_dir, 
            save_dir,
            self.train_ratio.value()
        )
        
        self.split_worker.progress.connect(self.split_progress.setValue)
        self.split_worker.status.connect(self.status_bar.showMessage)
        self.split_worker.finished.connect(self.splitFinished)
        self.split_worker.error.connect(self.splitError)
        
        self.split_worker.start()
        
    def splitFinished(self, stats):
        self.split_btn.setEnabled(True)
        self.detect_btn.setEnabled(True)
        self.split_progress.setVisible(False)
        self.status_bar.showMessage("Data split completed successfully!")
        
        # Update statistics
        current_stats = self.stats_text.toPlainText()
        split_report = f"\nData Split Results:\n"
        split_report += f"Train Images: {stats['train_count']}\n"
        split_report += f"Validation Images: {stats['valid_count']}\n"
        
        self.stats_text.setText(current_stats + split_report)
        
        QMessageBox.information(self, "Success", 
                              f"Data split completed!\n"
                              f"Train: {stats['train_count']} images\n"
                              f"Validation: {stats['valid_count']} images")
        
    def splitError(self, error_msg):
        self.split_btn.setEnabled(True)
        self.detect_btn.setEnabled(True)
        self.split_progress.setVisible(False)
        self.status_bar.showMessage("Data split failed!")
        QMessageBox.critical(self, "Error", f"Data split failed: {error_msg}")
    def loadLabelImage(self, idx):
        """Load image and its annotations for labeling"""
        if 0 <= idx < len(self.image_files):
            self.current_image_idx = idx
            image_path = self.image_files[idx]
            self.label_image_view.setImage(image_path)
            self.loadBoxes(image_path)
            self.current_image_label.setText(f"Image: {idx+1}/{len(self.image_files)}")
            self.status_bar.showMessage(f"Loaded image: {image_path}")
            
    def loadBoxes(self, image_path):
        """Load existing box annotations with option to clear"""
        reply = QMessageBox.question(self, 'Load Boxes', 
                                'Do you want to keep existing detections?',
                                QMessageBox.Yes | QMessageBox.No)
                                
        if reply == QMessageBox.No:
            # Clear existing boxes
            self.label_image_view.boxes = []
            self.label_image_view.selected_box_idx = None
            
        txt_path = image_path.rsplit('.', 1)[0] + '.txt'
        if os.path.exists(txt_path):
            with open(txt_path, 'r') as f:
                for line in f:
                    class_id, x_center, y_center, w, h = map(float, line.strip().split())
                    # Convert to pixel coordinates
                    img_h, img_w = self.label_image_view.image.shape[:2]
                    x1 = int((x_center - w/2) * img_w)
                    y1 = int((y_center - h/2) * img_h)
                    x2 = int((x_center + w/2) * img_w)
                    y2 = int((y_center + h/2) * img_h)
                    self.label_image_view.boxes.append((x1,y1,x2,y2,int(class_id)))
        
        self.updateBoxList()
        self.label_image_view.update()
        
    def saveLabels(self):
        """Save box annotations in YOLO format"""
        if not self.label_image_view.image:
            return
            
        image_path = self.image_files[self.current_image_idx]
        txt_path = image_path.rsplit('.', 1)[0] + '.txt'
        
        img_h, img_w = self.label_image_view.image.shape[:2]
        with open(txt_path, 'w') as f:
            for x1,y1,x2,y2,class_id in self.label_image_view.boxes:
                # Convert to YOLO format
                x_center = (x1 + x2) / (2 * img_w)
                y_center = (y1 + y2) / (2 * img_h)
                w = abs(x2 - x1) / img_w
                h = abs(y2 - y1) / img_h
                f.write(f"{class_id} {x_center} {y_center} {w} {h}\n")
                
        self.status_bar.showMessage(f"Saved annotations to: {txt_path}")
                
    def updateBoxList(self):
        """Update the list of boxes in the UI"""
        self.box_list.clear()
        for i, (x1,y1,x2,y2,class_id) in enumerate(self.label_image_view.boxes):
            class_names = {0: "Benign", 1: "Malignant", 2: "Normal"}
            self.box_list.addItem(f"Box {i+1}: {class_names[class_id]}")
            
    def prevLabelImage(self):
        """Load previous image"""
        if self.current_image_idx > 0:
            self.loadLabelImage(self.current_image_idx - 1)
            
    def nextLabelImage(self):
        """Load next image"""
        if self.current_image_idx < len(self.image_files) - 1:
            self.loadLabelImage(self.current_image_idx + 1)
            
    def changeLabelingMode(self, mode):
        """Change the current editing mode"""
        self.label_image_view.edit_mode = mode
        self.status_bar.showMessage(f"Changed to {mode} mode")
        
    def updateCurrentClass(self, idx):
        """Update the current class for new boxes"""
        self.label_image_view.current_class = idx
        
    def deleteSelectedBox(self):
        """Delete the currently selected box"""
        if self.box_list.currentRow() >= 0:
            idx = self.box_list.currentRow()
            del self.label_image_view.boxes[idx]
            if self.label_image_view.selected_box_idx == idx:
                self.label_image_view.selected_box_idx = None
            self.updateBoxList()
            self.label_image_view.update()
            self.status_bar.showMessage(f"Deleted box {idx+1}")
            
    def boxSelectionChanged(self):
        """Handle box selection change in the list"""
        idx = self.box_list.currentRow()
        self.label_image_view.selected_box_idx = idx
        self.label_image_view.update()

    def closeEvent(self, event):
        """Handle application closing"""
        # Clean up and save any necessary data before closing
        if self.detection_worker and self.detection_worker.isRunning():
            self.detection_worker.terminate()
        if self.split_worker and self.split_worker.isRunning():
            self.split_worker.terminate()
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Apply some styling
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #cccccc;
            border-radius: 6px;
            margin-top: 6px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 7px;
            padding: 0px 5px 0px 5px;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:disabled {
            background-color: #BDBDBD;
        }
        QProgressBar {
            border: 2px solid grey;
            border-radius: 5px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #2196F3;
            width: 10px;
        }
        QLabel {
            color: #333333;
        }
        QComboBox {
            padding: 5px;
            border: 1px solid #cccccc;
            border-radius: 3px;
        }
        QTextEdit {
            border: 1px solid #cccccc;
            border-radius: 3px;
        }
        QListWidget {
            border: 1px solid #cccccc;
            border-radius: 3px;
        }
    """)
    
    # Create and show the tool
    tool = YOLOTool()
    tool.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()