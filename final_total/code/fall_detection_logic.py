import cv2
import os
from datetime import datetime
from ultralytics import YOLO
import requests
import math

class FallDetectionLogic:
    def __init__(self, model_path, line_token, window):
        self.model = YOLO(model_path)
        self.model_name = os.path.basename(model_path).split("best")[0]
        self.save_dir = "detected_falls"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        self.line_token = line_token
        self.last_sent_time = None  
        self.window = window

    def run(self, cap, fall_class_id=0, is_video=False):
        if not cap.isOpened():
            print("無法開啟攝影機或影片")
            return
            
        frame_count = 0
            
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1                
            if is_video or frame_count % 1 == 0:
                self.detect_fall(frame, fall_class_id)
            '''
            cv2.imshow("Fall Detection", frame)
            if cv2.waitKey(1) == 27 or cv2.getWindowProperty("Fall Detection", cv2.WND_PROP_VISIBLE) < 1:
                break
            '''     
            # 等比例放大顯示視窗
            scale_percent = 93 # 放大比例，這裡是130%
            width = int(frame.shape[1] * scale_percent / 100) 
            height = int(frame.shape[0] * scale_percent / 100) 
            dim = (width, height) 
            # 調整影像大小 
            resized_frame = cv2.resize(frame, dim, interpolation=cv2.INTER_LINEAR) 
            # 顯示等比放大的影像 
            cv2.imshow("Fall Detection", resized_frame) 
            if cv2.waitKey(1) == 27 or cv2.getWindowProperty("Fall Detection", cv2.WND_PROP_VISIBLE) < 1: break

        cap.release()
        cv2.destroyAllWindows()
        self.window.show()
    
    def detect_fall(self, frame, fall_class_id):
        if "pose" in self.model_name:
            self.detect_fall_with_pose(frame, fall_class_id)
        else:
            self.detect_fall_with_bounding_box(frame, fall_class_id)

    def detect_fall_with_bounding_box(self, frame, fall_class_id):
        results = self.model.predict(frame, conf=0.5)
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                if cls_id == fall_class_id:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, "Fall Detected", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    current_time = datetime.now()
                    timestamp = current_time.strftime("%Y%m%d_%H%M%S")  
                    filename = os.path.join(self.save_dir, f"fall_{timestamp}.jpg")
                    cv2.imwrite(filename, frame)
                    if self.last_sent_time is None or (current_time - self.last_sent_time).seconds >= 3:
                        self.send_to_line_notify(filename, current_time)
                        self.last_sent_time = current_time

    def detect_fall_with_pose(self, frame, fall_class_id):
        results = self.model.predict(frame, conf=0.5)
        for result in results:
            if result.keypoints:
                keypoints_tensor = result.keypoints.xy.cpu()
                keypoints = keypoints_tensor.numpy()
                if keypoints.shape[0] > 0:  # 有偵測測到人，keypoints.shape[0]取得人數
                    self.draw_predictions(frame, result)
                    for i, person_keypoints in enumerate(keypoints): # 遍歷每個人的關鍵點 , i表第i個人
                        # 確保 result.boxes 有足夠的元素 
                        if len(result.boxes) > i:
                            # 獲取對應的邊界框 
                            bbox = result.boxes[i].xyxy[0].cpu().numpy().astype(int) 
                            if self.is_fall_pose(person_keypoints, bbox):  # person_keypoints一個人共 17 個關鍵點座標
                                x, y = int(person_keypoints[0][0]), int(person_keypoints[0][1])
                                cv2.putText(frame, "Fall Detected (Pose)", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                                current_time = datetime.now()
                                timestamp = current_time.strftime("%Y%m%d_%H%M%S")
                                filename = os.path.join(self.save_dir, f"fall_{timestamp}.jpg")
                                cv2.imwrite(filename, frame)
                                if self.last_sent_time is None or (current_time - self.last_sent_time).seconds >= 3:
                                    self.send_to_line_notify(filename, current_time)
                                    self.last_sent_time = current_time

    def draw_predictions(self, frame, result):
        # 繪製預測框
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0]
            cls = int(box.cls[0])
            label = f"{cls} {conf:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        '''
        # 繪製關鍵點並標號，顯示所有人
        for person_keypoints in result.keypoints.xy:
            for i, keypoint in enumerate(person_keypoints):
                x, y = int(keypoint[0]), int(keypoint[1])
                if x == 0 and y == 0:
                    cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)
                    cv2.putText(frame, f"KP{i}", (x + 5, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                else:
                    cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
                    cv2.putText(frame, f"KP{i}", (x + 5, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        '''
        


    def is_fall_pose(self, keypoints, bbox):
        if len(keypoints) == 17:
            head_x, head_y = keypoints[0]
            left_shoulder_x, left_shoulder_y = keypoints[5] 
            right_shoulder_x, right_shoulder_y = keypoints[6] 
            left_hip_x, left_hip_y = keypoints[11]
            right_hip_x, right_hip_y = keypoints[12]
            left_knee_x, left_knee_y = keypoints[13]
            right_knee_x, right_knee_y = keypoints[14]

            valid_keypoints_mask = [0] * 17  # 初始化大小為 17 的陣列，全為 0

            # 確認所有 17 個關鍵點是否有效
            for i, (x, y) in enumerate(keypoints):
                if x == 0 and y == 0:
                    valid_keypoints_mask[i] = 0  # 將無效的關鍵點位置設為 0
                else:
                    valid_keypoints_mask[i] = 1

            # 身體角度
            if valid_keypoints_mask[5] and valid_keypoints_mask[6] and valid_keypoints_mask[11] and valid_keypoints_mask[12]:
                center_up_x = (left_shoulder_x + right_shoulder_x) / 2 
                center_up_y = (left_shoulder_y + right_shoulder_y) / 2 
                center_down_x = (left_hip_x + right_hip_x) / 2 
                center_down_y = (left_hip_y + right_hip_y) / 2 
                dx = center_down_x - center_up_x 
                dy = center_down_y - center_up_y 
                angle = abs(math.degrees(math.atan2(dy, dx))) 
                # 計算中心線與地平線的夾角 
                if angle < 50 or angle > 130: 
                    return True
            
            # 如果有效關鍵點數量不足 13，則返回 False
            if sum(valid_keypoints_mask) >= 13:
                # 預測框的寬高比條件
                x1, y1, x2, y2 = bbox  # 獲取邊界框的座標
                width = x2 - x1
                height = y2 - y1
                if width / height > 5 / 3:
                    return True

            # 頭和臀部同時低於膝蓋
            if valid_keypoints_mask[0] and valid_keypoints_mask[11] and valid_keypoints_mask[13]:
                if head_y >= left_knee_y and left_hip_y >= left_knee_y:
                    return True
            if valid_keypoints_mask[0] and valid_keypoints_mask[12] and valid_keypoints_mask[14]:
                if head_y >= right_knee_y and right_hip_y >= right_knee_y:
                    return True
                
        return False

    def send_to_line_notify(self, image_path, time):
        url = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': f'Bearer {self.line_token}'}
        data = {'message': f"{time.year}年{time.month}月{time.day}日 {time.hour:02}:{time.minute:02}:{time.second:02}"}
        files = {'imageFile': open(image_path, 'rb')}
        response = requests.post(url, headers=headers, data=data, files=files)
        if response.status_code == 200:
            print("圖片已成功傳送到 LINE Notify")
        else:
            print(f"圖片傳送失敗，狀態碼：{response.status_code}")
