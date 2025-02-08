from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from database import create_connection
import sqlite3
import hashlib
import re
from datetime import datetime

class SignupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sign Up - Breast Cancer Diagnosis System')
        self.setFixedSize(900, 600)
        self.setWindowIcon(QIcon('./Code_app/assets/logo.jpg'))
        self.initUI()

    def initUI(self):
        # Main layout with left and right panels
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Panel
        left_panel = QWidget()
        left_panel.setStyleSheet('background-color:rgb(145, 184, 235);')
        left_panel.setFixedWidth(450)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel('Create Account\nDiagnosis System')
        title.setStyleSheet('color: white; font-size: 32px; font-weight: bold;')
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel('Fill in your information to create a new account')
        subtitle.setStyleSheet('color: white; font-size: 16px;')
        subtitle.setAlignment(Qt.AlignCenter)
        
        left_layout.addWidget(title)
        left_layout.addWidget(subtitle)

        # Right Panel - Form
        right_panel = QWidget()
        right_panel.setStyleSheet('background-color: #f0f2f5;')
        
        form_layout = QVBoxLayout(right_panel)
        form_layout.setAlignment(Qt.AlignCenter)

        # Form Container
        form = QWidget()
        form.setFixedWidth(380)
        form.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(form)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Username Field
        username_label = QLabel('Username')
        username_label.setStyleSheet('color: #333; font-weight: bold;')
        
        self.username = QLineEdit()
        self.username.setPlaceholderText('Enter username')
        self.username.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #1877f2;
            }
        """)

        # Password Field with Eye Icon
        password_label = QLabel('Password')
        password_label.setStyleSheet('color: #333; font-weight: bold;')
        
        self.password_container = QWidget()
        self.password_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            QWidget:focus-within {
                border: 2px solid #1877f2;
            }
        """)
        
        password_layout = QHBoxLayout(self.password_container)
        password_layout.setContentsMargins(12, 0, 6, 0)
        password_layout.setSpacing(6)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText('Enter password')
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 12px 0;
                font-size: 14px;
                background: transparent;
            }
        """)
        
        self.show_pw_btn = QPushButton()
        self.show_pw_btn.setIcon(QIcon('./Code_app/assets/eye.png'))
        self.show_pw_btn.setFixedSize(30, 30)
        self.show_pw_btn.setCursor(Qt.PointingHandCursor)
        self.show_pw_btn.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 5px;
                background: transparent;
            }
        """)
        self.show_pw_btn.clicked.connect(self.toggle_password)
        
        password_layout.addWidget(self.password)
        password_layout.addWidget(self.show_pw_btn)

        # Confirm Password Field with Eye Icon
        confirm_label = QLabel('Confirm Password')
        confirm_label.setStyleSheet('color: #333; font-weight: bold;')
        
        self.confirm_container = QWidget()
        self.confirm_container.setStyleSheet(self.password_container.styleSheet())
        
        confirm_layout = QHBoxLayout(self.confirm_container)
        confirm_layout.setContentsMargins(12, 0, 6, 0)
        confirm_layout.setSpacing(6)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText('Confirm your password')
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setStyleSheet(self.password.styleSheet())
        
        self.show_confirm_btn = QPushButton()
        self.show_confirm_btn.setIcon(QIcon('./Code_app/assets/eye.png'))
        self.show_confirm_btn.setFixedSize(30, 30)
        self.show_confirm_btn.setCursor(Qt.PointingHandCursor)
        self.show_confirm_btn.setStyleSheet(self.show_pw_btn.styleSheet())
        self.show_confirm_btn.clicked.connect(self.toggle_confirm_password)
        
        confirm_layout.addWidget(self.confirm_password)
        confirm_layout.addWidget(self.show_confirm_btn)

        # Role Selection
        role_label = QLabel('Role')
        role_label.setStyleSheet('color: #333; font-weight: bold;')
        
        self.role = QComboBox()
        self.role.addItems(['Doctor', 'Admin'])
        self.role.setStyleSheet("""
            QComboBox {
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QComboBox:focus {
                border: 2px solid #1877f2;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(./Code_app/assets/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)

        # Sign up button
        signup_btn = QPushButton('Sign Up')
        signup_btn.setCursor(Qt.PointingHandCursor)
        signup_btn.setStyleSheet("""
            QPushButton {
                background-color: #1877f2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #166fe5;
            }
        """)
        signup_btn.clicked.connect(self.handle_signup)
        
        # Back to login
        back_btn = QPushButton('Already have an account? Login')
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                color: #1877f2;
                border: none;
                background: transparent;
                font-size: 14px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        back_btn.clicked.connect(self.close)

        # Add all widgets to form layout
        layout.addWidget(username_label)
        layout.addWidget(self.username)
        layout.addWidget(password_label)
        layout.addWidget(self.password_container)
        layout.addWidget(confirm_label)
        layout.addWidget(self.confirm_container)
        layout.addWidget(role_label)
        layout.addWidget(self.role)
        layout.addWidget(signup_btn)
        layout.addWidget(back_btn)

        form_layout.addWidget(form)

        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

    def toggle_password(self):
        if self.password.echoMode() == QLineEdit.Password:
            self.password.setEchoMode(QLineEdit.Normal)
            self.show_pw_btn.setIcon(QIcon('./Code_app/assets/eye-off.png'))
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.show_pw_btn.setIcon(QIcon('./Code_app/assets/eye.png'))

    def toggle_confirm_password(self):
        if self.confirm_password.echoMode() == QLineEdit.Password:
            self.confirm_password.setEchoMode(QLineEdit.Normal)
            self.show_confirm_btn.setIcon(QIcon('./Code_app/assets/eye-off.png'))
        else:
            self.confirm_password.setEchoMode(QLineEdit.Password)
            self.show_confirm_btn.setIcon(QIcon('./Code_app/assets/eye.png'))

    def validate_input(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        confirm = self.confirm_password.text().strip()

        if not username or not password or not confirm:
            return False, "Please fill in all fields!"

        if len(username) < 4:
            return False, "Username must be at least 4 characters!"

        if not re.match("^[a-zA-Z0-9_]+$", username):
            return False, "Username can only contain letters, numbers and underscore!"

        if len(password) < 6:
            return False, "Password must be at least 6 characters!"

        if password != confirm:
            return False, "Passwords do not match!"

        return True, ""

    def hash_password(self, password):
        salt = hashlib.sha256(str(datetime.now()).encode()).hexdigest()
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{hashed}"

    def handle_signup(self):
        valid, message = self.validate_input()
        if not valid:
            QMessageBox.warning(self, 'Error', message)
            return

        username = self.username.text().strip()
        password = self.hash_password(self.password.text().strip())
        role = self.role.currentText().lower()

        conn = create_connection()
        if conn:
            try:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, password, role)
                )
                conn.commit()
                QMessageBox.information(
                    self, 'Success', 
                    'Account created successfully!\nPlease login to continue.'
                )
                self.close()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, 'Error', 'Username already exists!')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')
            finally:
                conn.close()

# if __name__ == '__main__':
#     app = QApplication([])
#     window = SignupWindow()
#     window.show()
#     app.exec_()