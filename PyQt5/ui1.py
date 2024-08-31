# ui.py
# 顯示文本或圖像的控件，按鈕控件，滑動條控件，垂直和水平佈局管理器，所有 GUI 控件的基類
from PyQt5.QtWidgets import QLabel, QPushButton, QSlider, QVBoxLayout, QHBoxLayout, QWidget
# 包含常量和枚舉，用於設置控件的屬性，例如對齊方式
from PyQt5.QtCore import Qt

# 定義了 VideoPlayerUI 類，這個類繼承自 QWidget，是視頻播放器界面的基礎類
class VideoPlayerUI(QWidget):
    def __init__(self):
        super().__init__()  # 調用父類的初始化方法
        
        # Layouts
        # 創建一個垂直佈局管理器 (QVBoxLayout) 並將其設置為主佈局。所有主要界面控件將按垂直方向排列。
        self.main_layout = QVBoxLayout(self)
        # 設置主佈局的邊距，以避免底部被系統工具列遮擋
        self.main_layout.setContentsMargins(0, 0, 0, 40)  # 上、左、右、下邊距
        # 創建一個水平佈局管理器 (QHBoxLayout)，用於排列控制按鈕和滑塊。
        self.controls_layout = QHBoxLayout()

        # 創建一個 QLabel 控件，用於顯示視頻
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)  # 將標籤中的內容（視頻）置中對齊
        self.main_layout.addWidget(self.video_label)  # 將 video_label 添加到主佈局中
        
        # 添加一個伸展項來推送控件到底部
        self.main_layout.addStretch()
        
        # 創建一個 QWidget，用作控件的容器
        self.controls_frame = QWidget()
        self.controls_frame.setLayout(self.controls_layout)  # 設置容器的佈局為水平佈局 (controls_layout)
        self.main_layout.addWidget(self.controls_frame)  # 將 controls_frame 添加到主佈局中

        # 創建一個標籤為 " " 的按鈕
        self.play_button = QPushButton("Play")  
        self.pause_button = QPushButton("Pause")
        self.reset_button = QPushButton("Reset")
        self.clear_button = QPushButton("Clear")
        self.open_file_button = QPushButton("Open File")

        # 將  按鈕添加到控制佈局中
        self.controls_layout.addWidget(self.open_file_button)
        self.controls_layout.addWidget(self.play_button)
        self.controls_layout.addWidget(self.pause_button)
        self.controls_layout.addWidget(self.reset_button)
        self.controls_layout.addWidget(self.clear_button)

        # 創建一個水平的滑動條控件 (QSlider)，用於顯示和控制視頻的播放進度。
        self.progress_slider = QSlider(Qt.Horizontal)
        self.controls_layout.addWidget(self.progress_slider)  # 將滑動條添加到控制佈局中

        # 創建一個顯示當前時間和總時長的標籤
        self.time_label = QLabel("00:00 / 00:00")
        self.controls_layout.addWidget(self.time_label)  # 將時間標籤添加到控制佈局中
