from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon, QPixmap, QFont
import sys
from database import check_login, create_database
from signup import SignupWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Breast Cancer Diagnosis System')
        self.setFixedSize(900, 600)
        self.setWindowIcon(QIcon('./Code_app/assets/logo.jpg'))
        self.settings = QSettings('BCDS', 'Login')
        self.initUI()
        self.load_saved_credentials()

    def initUI(self):
        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Left panel
        left_panel = QWidget()
        left_panel.setStyleSheet('background-color:rgb(145, 184, 235);')
        left_panel.setFixedWidth(450)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # Logo and title
        logo_label = QLabel()
        logo_pixmap = QPixmap('./Code_app/assets/logo.png')
        logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        
        title = QLabel('Breast Cancer\nDiagnosis System')
        title.setStyleSheet('color: white; font-size: 42px; font-weight: bold;')
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel('Powered by Artificial Intelligence')
        subtitle.setStyleSheet('color: white; font-size: 24px; margin-top: 20px;')
        subtitle.setAlignment(Qt.AlignCenter)
        
        left_layout.addWidget(logo_label)
        left_layout.addWidget(title)
        left_layout.addWidget(subtitle)
        
        # Right panel
        right_panel = QWidget()
        right_panel.setStyleSheet('background-color: #f0f2f5;')
        
        form_layout = QVBoxLayout(right_panel)
        form_layout.setAlignment(Qt.AlignCenter)
        
        # Login form
        form = QWidget()
        form.setFixedWidth(396)
        form.setStyleSheet("""
            QWidget { 
                background-color: white;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(form)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Username
        username_container = QWidget()
        username_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            QWidget:focus-within {
                border: 2px solidrgb(5, 11, 19);
            }
        """)
        username_layout = QHBoxLayout(username_container)
        username_layout.setContentsMargins(12, 0, 12, 0)
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        self.username.setFixedHeight(40)
        self.username.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 0;
                font-size: 15px;
                background: transparent;
            }
        """)
        
        username_layout.addWidget(self.username)
        
        # Password with eye icon
        password_container = QWidget()
        password_container.setStyleSheet(username_container.styleSheet())
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(12, 0, 6, 0)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(40)
        self.password.setStyleSheet(self.username.styleSheet())
        
        # Lưu show_pw button như một thuộc tính của class
        self.show_pw_btn = QPushButton()
        self.show_pw_btn.setIcon(QIcon('./Code_app/assets/eye.png'))
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
        
        # Options
        options = QWidget()
        options.setStyleSheet('background: transparent;')
        opt_layout = QHBoxLayout(options)
        opt_layout.setContentsMargins(0,0,0,0)
        
        self.remember = QCheckBox('Remember me')
        self.remember.setStyleSheet("""
            QCheckBox {
                color: #65676b;
                background: transparent;
            }
        """)
        
        forgot = QPushButton('Forgot password?')
        forgot.setCursor(Qt.PointingHandCursor)
        forgot.setStyleSheet("""
            QPushButton {
                color: #1877f2;
                border: none;
                padding: 0;
                background: transparent;
                text-align: right;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        forgot.clicked.connect(self.forgot_password)
        
        opt_layout.addWidget(self.remember)
        opt_layout.addWidget(forgot)
        
        # Login button
        login_btn = QPushButton('Login')
        login_btn.setFixedHeight(40)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1877f2;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #166fe5;
            }
        """)
        login_btn.clicked.connect(self.login)
        
        # Divider
        divider = QWidget()
        divider.setStyleSheet('background: transparent;')
        div_layout = QHBoxLayout(divider)
        
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setStyleSheet('background: #ccd0d5;')
        
        or_label = QLabel('OR')
        or_label.setStyleSheet('color: #96999e;')
        or_label.setAlignment(Qt.AlignCenter)
        
        line2 = QFrame() 
        line2.setFrameShape(QFrame.HLine)
        line2.setStyleSheet('background: #ccd0d5;')
        
        div_layout.addWidget(line1)
        div_layout.addWidget(or_label)
        div_layout.addWidget(line2)
        
        # Social buttons
        social = QWidget()
        social.setStyleSheet('background: transparent;')
        social_layout = QHBoxLayout(social)
        social_layout.setSpacing(8)
        
        google = QPushButton(QIcon('./Code_app/assets/google.png'), 'Google')
        facebook = QPushButton(QIcon('./Code_app/assets/facebook.png'), 'Facebook')
        
        for btn in [google, facebook]:
            btn.setFixedHeight(36)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 0 16px;
                    color: #4b4f56;
                    background: white;
                }
                QPushButton:hover {
                    background: #f5f6f7;
                }
            """)
            
        social_layout.addWidget(google)
        social_layout.addWidget(facebook)
        
        # Sign up section
        signup_text = QLabel("Don't have an account?")
        signup_text.setAlignment(Qt.AlignCenter)
        signup_text.setStyleSheet('color: #65676b;')
        
        signup_btn = QPushButton('Create new account')
        signup_btn.setFixedHeight(40)
        signup_btn.setCursor(Qt.PointingHandCursor)
        signup_btn.setStyleSheet("""
            QPushButton {
                background-color: #42b72a;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #36a420;
            }
        """)
        signup_btn.clicked.connect(self.signup)
        
        # Add widgets to form
        layout.addWidget(username_container)
        layout.addWidget(password_container)
        layout.addWidget(options)
        layout.addWidget(login_btn)
        layout.addWidget(divider)
        layout.addWidget(social)
        layout.addWidget(signup_text)
        layout.addWidget(signup_btn)
        
        form_layout.addWidget(form)
        
        # Add panels to main layout
        self.layout.addWidget(left_panel)
        self.layout.addWidget(right_panel)

    def toggle_password(self):
        if self.password.echoMode() == QLineEdit.Password:
            self.password.setEchoMode(QLineEdit.Normal)
            self.show_pw_btn.setIcon(QIcon('./Code_app/assets/eye-off.png'))
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.show_pw_btn.setIcon(QIcon('./Code_app/assets/eye.png'))

    def login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        
        if not username or not password:
            self.show_error('Please enter all fields')
            return
            
        role = check_login(username, password)
        if role:
            if self.remember.isChecked():
                self.save_credentials(username, password)
            from main_window import MainWindow
            self.window = MainWindow(role)
            self.window.show()
            self.close()
        else:
            self.show_error('Invalid username or password')
            
    def signup(self):
        self.signup_window = SignupWindow()
        self.signup_window.show()

    def forgot_password(self):
        email, ok = QInputDialog.getText(
            self, 'Forgot Password', 
            'Enter your email to reset password:'
        )
        if ok and email:
            QMessageBox.information(
                self, 'Notice',
                'Password reset instructions have been sent to your email!'
            )

    def show_error(self, message):
        QMessageBox.warning(self, 'Error', message)

    def save_credentials(self, username, password):
        self.settings.setValue('username', username)
        self.settings.setValue('password', password)

    def load_saved_credentials(self):
        if username := self.settings.value('username'):
            self.username.setText(username)
            self.password.setText(self.settings.value('password', ''))
            self.remember.setChecked(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())