# main.py

import sys
import cv2
from PyQt5.QtWidgets import QApplication
from fall_detection_ui import FallDetectionUI
from fall_detection_logic import FallDetectionLogic

def main():
    # 初始化 GUI 應用程式
    app = QApplication(sys.argv)
    window = FallDetectionUI()

    # 連接攝影機按鈕功能
    window.cam_button.clicked.connect(lambda: start_camera(window))

    # 連接選擇影片按鈕功能
    window.video_button.clicked.connect(lambda: open_video(window))

    # 顯示視窗
    window.show()
    sys.exit(app.exec_())

def start_camera(window):
    # 獲取使用者輸入的 Line Token
    line_token = window.line_token_input.text()
    # 檢查 Line Token 是否已輸入
    if not line_token:
        print("請輸入 LINE Token!")
        return
    # 獲取使用者選擇的模型
    selected_model = window.model_selector.currentText() 
    model_path = f"{selected_model.lower()}best.pt"
    print(model_path)
    # 初始化偵測邏輯
    fall_detector = FallDetectionLogic(model_path, line_token, window)
    # 啟動攝影機偵測
    window.hide()  # hide主視窗
    fall_detector.run(cv2.VideoCapture(0), is_video=False)
    # 當偵測結束後，重新開啟主視窗
    window.show()

def open_video(window):
    # 獲取使用者輸入的 Line Token
    line_token = window.line_token_input.text()
    # 檢查 Line Token 是否已輸入
    if not line_token:
        print("請輸入 LINE Token!")
        return
    
    # 獲取使用者選擇的模型
    selected_model = window.model_selector.currentText() 
    model_path = f"{selected_model.lower()}best.pt"
    print(model_path)
    # 初始化偵測邏輯
    fall_detector = FallDetectionLogic(model_path, line_token, window)
    # 啟動影片偵測
    video_path = window.get_video_file()
    if video_path:
        window.hide()  # hide主視窗
        fall_detector.run(cv2.VideoCapture(video_path), is_video=True)

if __name__ == '__main__':
    main()
