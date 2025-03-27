import os
from ultralytics import YOLO
import torch
import yaml
from datetime import datetime  # 新增 datetime 模組

if __name__ == '__main__':
    # 設置你要使用的GPU，選擇第0個GPU
    torch.cuda.set_device(0)
    
    # 檢查是否正確選擇了GPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print("Using device:", torch.cuda.get_device_name(0))

    # 讀取 data.yaml 文件，指定編碼為 'utf-8'
    data_yaml_path = "C:/Users/洪婉玲/Desktop/113上/project2/model/data.yaml"
    with open(data_yaml_path, 'r', encoding='utf-8') as f:
        data_yaml = yaml.safe_load(f)

    # 設定訓練結果保存路徑
    project_dir = "C:/Users/洪婉玲/Desktop/113上/project2/results"

    # 自動生成唯一的實驗名稱，使用日期時間
    experiment_name = "fall_detection_" + datetime.now().strftime("%Y%m%d_%H%M%S")

    # 檢查是否存在結果目錄，不存在則創建
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    # 設置日誌文件路徑
    log_file_path = os.path.join(project_dir, f"{experiment_name}.log")

    # 加載並設置模型
    model = YOLO("yolov10n.pt").to(device)

    # 開始訓練，並指定訓練結果和日誌的保存路徑
    model.train(
        data=data_yaml_path,
        epochs=150,
        batch=8,
        imgsz=640,
        project=project_dir,  # 指定結果保存路徑
        name=experiment_name,  # 自動生成的實驗名稱
        device=device,
        exist_ok=True,  # 如果存在相同名稱的實驗結果文件夾，覆蓋它
        close_mosaic=30, 
        patience=10
    )

    # 將訓練日誌保存到文件
    with open(log_file_path, 'w') as log_file:
        log_file.write("Training and validation logs:\n")

    # 測試模型
    results_test = model.val(
        data=data_yaml_path,
        project=project_dir,
        name=experiment_name + "_test",
        device=device,
        split='test'
    )
    

    # 在 TensorBoard 中可視化結果（可選）
    print(f"訓練和驗證結果已保存到 {project_dir}/{experiment_name}")
    print("你可以使用以下命令來啟動 TensorBoard 來檢視訓練過程：")
    print(f"tensorboard --logdir {project_dir}")