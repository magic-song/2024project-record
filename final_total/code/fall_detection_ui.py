# fall_detection_ui.py

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QFileDialog, QLineEdit, QLabel, QComboBox
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt

class FallDetectionUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setup_window()
        self.setup_widgets()
        self.setup_layout()

    def setup_window(self):
        self.setWindowTitle("Fall Detection System")
        self.setFixedSize(600, 360)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(220, 220, 220))
        self.setPalette(palette)

    def setup_widgets(self):  # 修改此方法名稱和內容
        self.cam_button = QPushButton("使用攝影機", self)
        self.video_button = QPushButton("選擇影片", self)
        
        # 加入Line Token的輸入框
        self.line_token_label = QLabel("輸入LINE Token:", self)
        self.line_token_input = QLineEdit(self)
        self.line_token_input.setPlaceholderText("請輸入您的LINE Notify Token")

        # 新增下拉式表單（QComboBox） 
        self.model_selector = QComboBox(self) 
        self.model_selector.addItem("YOLOv10") 
        self.model_selector.addItem("YOLOv11") 
        self.model_selector.addItem("YOLO11N-POSE")
        self.model_selector.setPlaceholderText("選擇辨識模型")

        self.cam_button.setMinimumSize(130, 60)
        self.video_button.setMinimumSize(130, 60)
        self.line_token_input.setMinimumSize(230, 60)
        self.model_selector.setMinimumSize(230, 60)


        # 設定按鈕和字體樣式
        font = QFont()
        font.setPointSize(12)
        self.cam_button.setFont(font)
        self.video_button.setFont(font)
        button_style = """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #388E3C;
        }
        """
        self.cam_button.setStyleSheet(button_style)
        self.video_button.setStyleSheet(button_style)

    def setup_layout(self):
        layout = QGridLayout() 
        layout.addWidget(self.line_token_label, 0, 0) 
        layout.addWidget(self.line_token_input, 0, 1, 1, 2) 
        layout.addWidget(self.model_selector, 1, 0, 1, 2)
        layout.addWidget(self.cam_button, 2, 0) 
        layout.addWidget(self.video_button, 2, 1) 
        self.setLayout(layout)


    def get_video_file(self):
        # 彈出選擇影片的對話框
        video_path, _ = QFileDialog.getOpenFileName(self, "選擇影片", "", "Video Files (*.mp4 *.avi)")
        if video_path:
            return video_path
        else:
            return None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FallDetectionUI()
    window.show()
    sys.exit(app.exec_())
