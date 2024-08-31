import cv2  # 影片讀取和顯示
import tkinter as tk  # 創建GUI
from tkinterdnd2 import DND_FILES, TkinterDnD   # 支持拖放功能的 Tkinter 擴展庫
from tkinter import filedialog  # tkinter文件對話框，打開文件
from PIL import Image, ImageTk  # 處理影像，將 OpenCV 的影像轉換為 Tkinter 可以顯示的格式
from datetime import timedelta  # 處理影片時間的計算

# 創建VideoPlayer類別
class VideoPlayer:
    # Videoplayer類別的初始化方式_init_，開啟視窗，初始畫面
    def __init__(self, window, window_title):
        self.window = window  # 建立視窗，並儲存實例self的window屬性中，以便在類別的其他部分使用
        self.window.title(window_title)  #設視窗名稱為參數window_title值

        # 綁定關閉事件以關閉所有視窗
        # protocol() 方法是 tkinter 視窗對象的一個方法，用來設定視窗管理器對特定事件的回應方式
        # "WM_DELETE_WINDOW" 是一個特殊的協定（protocol）名稱，它對應於使用者試圖關閉視窗的行為
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # 創建拖放區域
        # 創建一個標籤（Label），作為拖放區域，並設置其顯示的文字、背景顏色及尺寸
        self.drop_frame = tk.Label(window, text="拖放影片檔案到這裡，或點擊以選擇檔案", bg="lightgray", width=60, height=10)
        # 將標籤添加到視窗中並設置其佈局
        self.drop_frame.pack(pady=20, expand=True, fill=tk.BOTH)
        # self.drop_frame 可以接受拖放進來的文件
        # DND_FILES 是一個常量，表示這個拖放目標接受文件類型的拖放操作（通常需要 tkinterdnd2 模組來支持拖放功能）
        self.drop_frame.drop_target_register(DND_FILES)
        # 將 <<Drop>> 事件（即文件被拖放到標籤上的事件）綁定到 self.on_file_drop 方法
        self.drop_frame.dnd_bind('<<Drop>>', self.on_file_drop)
        # 將 <Button-1> 事件（即左鍵單擊事件）綁定到 self.on_file_click 方法
        self.drop_frame.bind("<Button-1>", self.on_file_click)

        # 創建主畫布來顯示影片
        # 創建了一個新的 tk.Canvas 物件，這個畫布要添加到的父視窗window，並將其賦值給 self.canvas 屬性
        self.canvas = tk.Canvas(window, width=640, height=480)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        # 圈選的起始點和結束點
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.tracking = False

        # 創建控制面板
        self.control_frame = tk.Frame(window)
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # 按鈕
        # tk.Button 用來創建一個按鈕物件，將按鈕添加到容器self.control_frame中，設置按鈕上顯示的文字為 "Play"，當按鈕被點擊時會呼叫 self.play_video 方法
        self.play_button = tk.Button(self.control_frame, text="Play", command=self.play_video)
        self.play_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(self.control_frame, text="Pause", command=self.pause_video)
        self.pause_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(self.control_frame, text="Stop", command=self.stop_video)
        self.stop_button.pack(side=tk.LEFT)

        # 進度條
        # tk.Scale 用來創建一個滑動條（進度條），方向水平，範圍從 0 到 100，並設置其長度為 400 像素，並且不顯示進度值。
        self.progress = tk.Scale(self.control_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=400, showvalue=0)
        # 設置進度條在父容器 self.control_frame 的佈局，放置在框架的底部，度條會在水平方向上填滿其父容器的可用空間 (進度條的寬度會擴展以匹配框架的寬度)
        self.progress.pack(side=tk.BOTTOM, fill=tk.X)
        # 當滑鼠在進度條上移動時，會被呼叫 self.on_progress_move 這個方法來處理相關事件
        self.progress.bind("<Motion>", self.on_progress_move)

        # 顯示時間的標籤
        '''
        self.time_label = tk.Label(self.control_frame, text="00:00 / 00:00")
        self.time_label.pack(side=tk.BOTTOM)
        '''
        self.time_label = tk.Label(self.window, text="00:00 / 00:00")
        self.time_label.pack(side=tk.BOTTOM, fill=tk.X)

        # 創建放大視窗
        # 創建一個新的頂層視窗（子視窗或彈出視窗），為self.window 的子視窗
        self.zoom_window = tk.Toplevel(self.window)
        # 視窗名稱設為 "Zoomed View"
        self.zoom_window.title("Zoomed View")
        # "WM_DELETE_WINDOW" 是一個特殊的協定（protocol）名稱，它對應於使用者試圖關閉視窗的行為
        self.zoom_window.protocol("WM_DELETE_WINDOW", self.on_close)
        # 創建畫布到 "Zoom View" 視窗
        self.zoom_canvas = tk.Canvas(self.zoom_window, width=640, height=480)
        self.zoom_canvas.pack(expand=True, fill=tk.BOTH)

        # 綁定鼠標事件
        self.canvas.bind("<Button-1>", self.on_mouse_click)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

        self.vid = None  # cv2.VideoCapture對象
        self.video_source = None  # 影片資料路徑
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 0
        self.delay = 0
        self.total_duration = timedelta(0)
        self.tracker = None
        self.roi = None

        self.window.mainloop()  # 啟動 Tkinter 的主循環，讓窗口保持顯示並等待事件觸發
    
    # 處理當文件被拖放到特定區域時的事件
    def on_file_drop(self, event):
        file_path = self.get_file_path_from_event(event)
        # 檢查 file_path 是否有效
        if file_path:
            # 將文件路徑傳入函式以加載並播放這個視頻文件
            self.load_video(file_path)
    
    # 移除路徑字符串開頭和結尾的 {}，所有的斜杠 / 替換為反斜杠 \
    def get_file_path_from_event(self, event):
        file_path = event.data.strip('{}').replace('/', '\\')
        return file_path
    
    # 顯示一個文件選擇對話框，讓用戶選擇視頻文件，選擇後加載並播放該視頻
    def on_file_click(self, event):
        # 顯示一個文件選擇對話框，讓用戶選擇一個文件
        file_path = filedialog.askopenfilename(
            # 用參數 filetypes 指定文件選擇對話框內用戶可以選擇的文件類型，顯示文字為 Video files
            #filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"), ("All files", "*.*")]
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv")]
        )
        if file_path:
            self.load_video(file_path)

    # 一開始播放影片
    def load_video(self, video_source):
        # 如果之前已經有一個視頻文件被打開，self.vid.release() 會釋放該視頻文件佔用的資源
        if self.vid:
            self.vid.release()
        self.video_source = video_source  # 將傳入的視頻來源保存到實例屬性中
        self.vid = cv2.VideoCapture(self.video_source)  # 打開指定的視頻文件
        self.current_frame = 0  # 將當前幀設置為 0，表示視頻從頭開始播放
        self.total_frames = int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT))  # 獲取視頻的總幀數
        self.fps = self.vid.get(cv2.CAP_PROP_FPS)  # 獲取視頻的幀率（每秒幀數，frames per second）
        self.delay = int(1000 / self.fps)  # 計算每一幀之間的延遲，以毫秒為單位，用來控制幀播放速度
        self.total_duration = timedelta(seconds=int(self.total_frames / self.fps))  # 計算視頻的總時長，並使用 timedelta 對象表示
        self.tracker = None  # 初始化物件跟蹤器屬性
        self.roi = None  # 初始化感興趣區域（ROI）的屬性
        self.drop_frame.pack_forget()  # 隱藏或移除用來拖放文件的框架（drop_frame）
        self.canvas.pack(expand=True, fill=tk.BOTH)  # 將顯示視頻的畫布（canvas）重新顯示，並設置其在窗口中擴展填充
        #self.control_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.play_video()  # 調用 self.play_video() 方法來開始播放視頻

    # 對影片的每一幀做處理，物件追蹤，放大後畫面處理，影片適應視窗大小
    def update(self):
        # 確認通過 OpenCV (cv2.VideoCapture) 打開的視頻文件或流存在且被成功打開
        if self.vid and self.vid.isOpened():
            ret, frame = self.vid.read()  # 讀取當前幀，ret 表示讀取是否成功，frame 是讀取到的圖像幀
            # 當前幀讀取成功
            if ret:
                # 跟踪器 (self.tracker) 和跟踪狀態 (self.tracking) 都被啟用
                if self.tracker and self.tracking:
                    # 更新追蹤器，success 紀錄追蹤是否成功，bbox 是返回的邊界框（bounding box）坐標(左上角x, 左上角y, width, height)
                    success, bbox = self.tracker.update(frame)
                    if success:
                        # 繪製追蹤框
                        p1 = (int(bbox[0]), int(bbox[1]))  # p1 表示矩形框的左上角坐標
                        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))  # p2 = (x + w, y + h)表示矩形框的右下角坐標
                        # cv2.rectangle 在圖像上繪製矩形框
                        # frame 是要繪製矩形的圖像幀，(255, 0, 0) 定義了矩形的顏色，2 表示矩形邊框的厚度，1 是線型
                        cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
                        '''
                        # 在 Tkinter 畫布上繪製追蹤框
                        self.canvas.delete("tracker")  # 刪除畫布上標記為 "tracker" 的所有圖形元素 (刪除舊的框)
                        # 在 Tkinter 畫布上繪製一個矩形框
                        self.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1], outline="blue", width=2, tags="tracker")
                        '''
                        # 顯示放大畫面
                        # 切片操作 [p1[1]:p2[1], p1[0]:p2[0]]，表示從 frame 中提取出這個矩形區域的像素
                        zoomed_frame = frame[p1[1]:p2[1], p1[0]:p2[0]]
                        # cv2.resize 函式將提取的影像區域調整為 640x480 的大小，cv2.INTER_LINEAR 是一種插值方法，用來在縮放影像時計算新的像素值
                        zoomed_frame = cv2.resize(zoomed_frame, (640, 480), interpolation=cv2.INTER_LINEAR)
                        # cv2.cvtColor 函式將 BGR 格式(OpenCV 使用)的影像轉換為 RGB 格式(Tkinter 和大多數圖像處理庫（如 PIL）使用)
                        zoomed_frame = cv2.cvtColor(zoomed_frame, cv2.COLOR_BGR2RGB)
                        # Image.fromarray(zoomed_frame) 是使用 PIL（Python Imaging Library）將 NumPy 陣列 zoomed_frame 轉換為 PIL 影像對象
                        # ImageTk.PhotoImage 則將 PIL 影像對象轉換為 Tkinter 可用的 PhotoImage 對象，這樣它可以在 Tkinter 的 Canvas 上顯示
                        self.zoom_photo = ImageTk.PhotoImage(image=Image.fromarray(zoomed_frame))
                        # 在 Tkinter 的畫布 self.zoom_canvas 上繪製影像
                        # (0, 0) 指定了影像的起始位置 (畫布左上角)，anchor=tk.NW 表示影像的錨點是左上角（Northwest），因此影像的 (0, 0) 點會對應到畫布的 (0, 0) 點
                        self.zoom_canvas.create_image(0, 0, image=self.zoom_photo, anchor=tk.NW)

                # 獲取畫布的寬度和高度
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()

                # 從影像幀 frame 中提取出影像的高度和寬度，並分別存儲在變量 frame_height 和 frame_width 中
                frame_height, frame_width = frame.shape[:2]

                # 計算了一個縮放比例，以確保影像在 Tkinter 的畫布上顯示時能夠適應畫布的尺寸而不失真
                scale = min(canvas_width / frame_width, canvas_height / frame_height)

                # 調整影像的大小
                new_width = int(frame_width * scale)
                new_height = int(frame_height * scale)
                resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

                # 影像在畫布上居中顯示，計算座標偏移量
                x_offset = (canvas_width - new_width) // 2  # 使用 // 2 計算畫布寬度和影像寬度之間的差距的一半，這樣可以將影像居中顯示在畫布上
                y_offset = (canvas_height - new_height) // 2  #高度

                # 將 BGR 影像轉換為 RGB
                resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                # 換為 Tkinter 可用的 PhotoImage 對象，這樣它可以在 Tkinter 的 Canvas 上顯示
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(resized_frame))
                # self.canvas.create_image 是 Tkinter 的 Canvas 小部件中的方法，用來在畫布上創建一個圖像項
                # x_offset 和 y_offset 是之前計算的偏移量，image=self.photo 指定要顯示的圖像，anchor=tk.NW 指定圖像的錨點，即左上角（North-West），確保圖像按照指定的偏移量從左上角開始顯示
                self.canvas.create_image(x_offset, y_offset, image=self.photo, anchor=tk.NW)

                # self.vid 是一個 OpenCV 的 VideoCapture 物件，用來讀取視頻文件
                # cv2.CAP_PROP_POS_FRAMES 是一個屬性，用來獲取當前視頻流的位置（即當前幀的索引）
                self.current_frame = int(self.vid.get(cv2.CAP_PROP_POS_FRAMES))
                # 計算進度條的值
                progress_value = (self.current_frame / self.total_frames) * 100
                # 進度條會顯示當前播放進度，使用 set 方法更新進度條的值，progress_value 是計算出的百分比值
                self.progress.set(progress_value)

                # 計算從開始播放到當前幀所經過的時間（以秒為單位），用 timedelta 來創建一個表示時間間隔的對象
                current_time = timedelta(seconds=int(self.current_frame / self.fps))
                # 使用格式化字符串生成最終的顯示字符串，顯示當前播放時間和總時長，以 "/" 分隔
                time_str = f"{str(current_time)[:7]} / {str(self.total_duration)[:7]}"
                self.time_label.config(text=time_str)  # 更新一個 Tkinter 的 Label 小部件，用於顯示時間

            # after 方法是 Tkinter 窗口對象的一部分，用於安排定時任務， 將 self.update 方法安排為在 self.delay 毫秒後被調用
            self.window.after(self.delay, self.update)
    
    # 開始播放視頻並啟動物體追蹤
    def play_video(self):
        # 檢查和打開影片
        if self.vid and not self.vid.isOpened():
            # 如果視頻沒有打開（即 self.vid.isOpened() 返回 False），則重新打開視頻文件
            self.vid = cv2.VideoCapture(self.video_source)
            # 設置視頻的起始幀位置為 self.current_frame，這樣可以從視頻的當前位置繼續播放
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        # 初始化追蹤器（如果有選擇的 ROI）
        # self.roi[2] 寬和 self.roi[3] 高
        if self.roi and self.roi[2] and self.roi[3]:
            # 創建 CSRT 追蹤器實例
            self.tracker = cv2.TrackerCSRT_create()
            # 從視頻流中讀取一幀影像
            ret, frame = self.vid.read()
            if ret:
                # 用讀取的影像和指定的 ROI 初始化追蹤器
                self.tracker.init(frame, self.roi)
        self.tracking = True  # 開始追蹤
        self.update()  # 調用 update 方法，開始進行定時更新。update 方法會定期刷新視頻畫面，並在必要時進行追蹤處理

    # 暫停視頻播放並停止追蹤
    def pause_video(self):
        if self.vid:
            self.vid.release()
        self.tracking = False  # 停止追蹤
        # 進入圈選模式
        self.start_x = None  # 記錄用戶在畫布上開始拖動的起始坐標
        self.start_y = None  # 記錄用戶在畫布上開始拖動的起始坐標
        self.rect_id = None  # 在畫布上繪製的矩形的 ID

    # 停止視頻播放、重置界面以及清除所有相關狀態
    def stop_video(self):
        if self.vid:
            self.vid.release()
        self.canvas.delete("all")  # 刪除畫布上的所有圖形元素，"all" 是一個標誌，用於刪除畫布上的所有物件
        self.current_frame = 0  # 當前播放的幀數設置為 0，表示重置為視頻的起始位置
        self.progress.set(0)  # 將進度條的值設置為 0，表示進度條回到起始位置
        self.time_label.config(text="00:00 / 00:00")  # 重置時間顯示
        self.tracker = None  # 表示追蹤器已經停止
        self.roi = None  # 表示不再有有效的 ROI 區域
        self.tracking = False  # 表示追蹤功能已經停止

    def on_progress_move(self, event):
        if self.vid:
            progress_value = self.progress.get()# 獲取進度條的當前值
            self.current_frame = int((progress_value / 100) * self.total_frames)  # 根據進度條的百分比計算當前幀的位置，並將其轉換為整數
            # 使用 OpenCV 的 set 方法將視頻的播放位置設置到計算出的幀數，cv2.CAP_PROP_POS_FRAMES 是一個屬性，用於設置視頻的幀位置
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

    '''
    def set_frame_position(self, frame_pos):
        if self.vid:
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
    '''

    # 處理用戶在畫布上點擊的事件，並用於初始化選擇區域的起始坐標
    def on_mouse_click(self, event):
        # 只有在非追蹤模式下，才允許用戶進行圈選操作
        if not self.tracking:
            # event.x 和 event.y 是 Tkinter 事件對象中的屬性，鼠標點擊位置的 x 和 y 坐標
            self.start_x, self.start_y = event.x, event.y

    
    # 處理用戶在畫布上拖動鼠標的事件，並用於在畫布上繪製選擇框
    def on_mouse_drag(self, event):
        # 只有在非追蹤模式下，才允許進行選擇框的繪製
        if not self.tracking and self.start_x and self.start_y:
            # 刪除先前繪製的矩形，這樣在每次拖動時，只顯示當前的選擇框
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            # 用於在畫布上創建一個矩形
            # 起始坐標是 self.start_x 和 self.start_y，結束坐標是當前鼠標位置的 event.x 和 event.y，框的顏色為紅色，self.rect_id 保存新創建的矩形的 ID
            self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red")

    # 處理用戶在畫布上釋放鼠標按鈕的事件，並用於確定並記錄選擇的區域
    def on_mouse_release(self, event):
        # 保當前不在追蹤模式下，這樣才能進行選擇區域的設定，確保起始坐標已經記錄
        if not self.tracking and self.start_x and self.start_y:
            end_x, end_y = event.x, event.y
            # 計算選擇區域的左上角坐標，計算選擇區域的寬度和高度並用abs保證為正數，self.roi 儲存選擇區域的坐標和大小(左上角x, 左上角y, width, height)
            self.roi = (min(self.start_x, end_x), min(self.start_y, end_y), abs(self.start_x - end_x), abs(self.start_y - end_y))
            # 打印選擇的區域信息，以便於調試和確認
            print(f"Selected ROI: {self.roi}")

    
    # 處理應用程式關閉時的清理工作，確保資源得到妥善釋放
    def on_close(self):
        # 檢查並釋放與 self.vid 相關的視頻資源，確保程序結束時不會留下未釋放的硬體資源或打開的視頻流
        if self.vid:
            self.vid.release()
        # 銷毀主視窗和 zoom_window，確保應用程式完全退出並釋放所有資源。
        self.window.destroy()  # 銷毀主視窗，這會終止 Tkinter 應用程序的主循環，並關閉主視窗。這樣可以確保應用程式完全退出
        self.zoom_window.destroy()

# 創建了一個 TkinterDnD 的主要視窗（root），這是 Tkinter 應用程序的主窗口
root = TkinterDnD.Tk()
# root 是前面創建的 TkinterDnD 主視窗，它被傳遞給 VideoPlayer 類的構造函數，以便在這個視窗上創建和顯示視頻播放器界面。
VideoPlayer(root, "Tkinter OpenCV Video Player")
