import tkinter
import cv2
import PIL
from PIL import Image, ImageTk
from paddleocr import PaddleOCR,draw_ocr
import time
#from lib_detection import load_model, detect_lp, im2single
#rom paddleocr import PaddleOCR,draw_ocr
import datetime as dt
#import pyodbc

#from hikvisionapi import Client
import re


class App:
    def __init__(self, window, window_title, video_source=0):
        # Open the video source
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.vid = MyVideoCapture(self.video_source)

        #Phần trên(logo - tiêu đề)
        self.frame_tieude = tkinter.Frame(window, relief=tkinter.RIDGE)
        self.frame_tieude.pack(fill='x',pady=10,padx=10)
        #self.frame_tieude.configure(background="red")
        self.frame_tieude_1 = tkinter.Frame(self.frame_tieude)
        self.frame_tieude_1.grid(row=0, column=1, pady=3)
        self.tieude_logo = tkinter.Label(self.frame_tieude_1)
        self.tieude_logo.pack()
        self.frame_tieude_2 = tkinter.Frame(self.frame_tieude)
        self.frame_tieude_2.grid(row=0, column=2, pady=3, padx=5)
        self.tieude_label = tkinter.Label(self.frame_tieude_2, text="CỔNG XE VÀO / GATE IN", font=("Tahoma", 25))
        self.tieude_label.pack()

        #Phần dưới
        self.frame_camera = tkinter.Frame(window, bg="gray", borderwidth=1, relief=tkinter.SUNKEN)
        self.frame_camera.pack(fill="x", pady=5)
        self.frame_camera.configure(background="gray")
#Camera trực tiếp
        self.frame_camera_1 = tkinter.Frame(self.frame_camera, bg="white", borderwidth=1, relief=tkinter.SOLID)
        self.frame_camera_1.pack(side="left",padx=3, pady=3)

        self.frame_camera_1_tieude = tkinter.Label(self.frame_camera_1, bg="green", fg="white", text="Camera trực tiếp:", font=("Tahoma", 10))
        self.frame_camera_1_tieude.pack(side="top")

        self.canvas = tkinter.Canvas(self.frame_camera_1, bg='white', width=self.vid.width, height=self.vid.height)
        self.canvas.pack()
#Ảnh chụp phía trước
        self.frame_camera_2 = tkinter.Frame(self.frame_camera, bg="white", borderwidth=1, relief=tkinter.SOLID)
        self.frame_camera_2.pack(side="right",padx=3, pady=3)
        self.frame_camera_2_tieude = tkinter.Label(self.frame_camera_2, text="Ảnh chụp từ Camera trước:", font=("Tahoma", 10))
        self.frame_camera_2_tieude.pack(side="top")
        self.frame_camera_2_picture = tkinter.Label(self.frame_camera_2)  # text="waiting...", bg='orange', borderwidth=1, relief=tkinter.RIDGE)
        self.frame_camera_2_picture.pack(expand="True")
# Ảnh chụp phía sau
        self.frame_camera_3 = tkinter.Frame(self.frame_camera, bg="white", borderwidth=1, relief=tkinter.SOLID)
        self.frame_camera_3.pack(side="right",padx=3, pady=3)
        self.frame_camera_3_tieude = tkinter.Label(self.frame_camera_3, text="Ảnh chụp từ Camera sau:",
                                                   font=("Tahoma", 10))
        self.frame_camera_3_tieude.pack(side="top")
        self.frame_camera_3_picture = tkinter.Label(
            self.frame_camera_3)  # text="waiting...", bg='orange', borderwidth=1, relief=tkinter.RIDGE)
        self.frame_camera_3_picture.pack(expand="True")

        #Ảnh biển số crop và kết quả biển số (Kết quả)
# Frame chính:
        self.frame_ketqua = tkinter.Frame(self.window, bg="silver", borderwidth=1, relief=tkinter.RIDGE)
        self.frame_ketqua.pack(fill="x", pady=3, padx=3)
# Frame chứa label và ảnh biển số crop
        self.frame_ketqua_1= tkinter.Frame(self.frame_ketqua, bg="silver", relief=tkinter.RIDGE)
        self.frame_ketqua_1.pack(side="left", padx=3, pady=3)
# Label:
        self.frame_ketqua_1_tieude = tkinter.Label(self.frame_ketqua_1, text="Biển số xe:", font=("Tahoma", 10))
        self.frame_ketqua_1_tieude.pack(side="top",fill="x")

#Frame chứa ảnh biển số:
        self.frame_ketqua_1_1 = tkinter.Frame(self.frame_ketqua_1, bg="silver", borderwidth=1, relief=tkinter.RIDGE)
        self.frame_ketqua_1_1.pack(side="bottom", fill="y")
# Ảnh biển số sau crop:
        self.anhbienso_crop = tkinter.Label(self.frame_ketqua_1_1)
        self.anhbienso_crop.pack(expand="True")

# Frame chứa kết quả biển số:
        self.frame_ketqua_2 = tkinter.Frame(self.frame_ketqua, bg="silver", borderwidth=1, relief=tkinter.RIDGE)
        self.frame_ketqua_2.pack(fill="both", expand="True")
        # Label kết quả biển sô
        self.frame_ketqua_2_ketqua = tkinter.Label(self.frame_ketqua_2, bg='orange', text="waiting...", font=("Tahoma", 10))
        self.frame_ketqua_2_ketqua.pack(fill="both", expand="True")



#Mã thẻ
        self.frame_mathe = tkinter.Frame(window, bg="silver", borderwidth=1, relief=tkinter.SUNKEN)
        self.frame_mathe.pack(fill="x", pady=5)
        # Frame chứa label và textbox mã thẻ:0
        self.frame_mathe_1 = tkinter.Frame(self.frame_mathe, bg="silver")
        self.frame_mathe_1.pack(pady=3, padx=3)
        self.frame_mathe_tieude = tkinter.Label(self.frame_mathe_1, text="Mã thẻ:", font=("Tahoma", 30), relief=tkinter.RIDGE)
        self.frame_mathe_tieude.pack(side="left", padx=3, pady=3)
        self.txtmathe = tkinter.Text(self.frame_mathe_1, bg="white", fg="black", width=30, height=1, font=("Tahoma", 30))
        self.txtmathe.pack(side="right", padx=3, pady=3)
        self.txtmathe.focus()
        self.txtmathe.bind("<Return>", self.alertme)


        self.show_picture_empty()

        self.delay = 15
        self.update()
        count = 0
        self.window.geometry("1280x1000+250+0")
        self.window.mainloop()

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        if ret:
            cv2.rectangle(frame, (100, 75), (300, 225), (0, 255, 0), 2)
            cv2.line(img=frame, pt1=(175, 150), pt2=(225, 150), color=(0, 255, 0), thickness=2, lineType=8, shift=0)
            cv2.line(img=frame, pt1=(200, 125), pt2=(200, 175), color=(0, 255, 0), thickness=2, lineType=8, shift=0)
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
        self.window.after(self.delay, self.update)

    def show_picture_empty(self):
        # Icon:
        self.i0 = cv2.imread("UI/wr.jpg", 1)
        cv2i0 = cv2.cvtColor(self.i0, cv2.COLOR_BGR2RGB)
        imgi0 = PIL.Image.fromarray(cv2i0)
        imgtki0 = ImageTk.PhotoImage(image=imgi0)
        self.tieude_logo.imgtk = imgtki0
        self.tieude_logo.configure(image=imgtki0)

        # Frame ảnh camera chụp phía trước:
        self.i1 = cv2.imread("UI/loi1.jpg", 1)
        # self.s1 = cv2.resize(self.i1, (0, 0), fx=0.5, fy=0.5)
        cv2i1 = cv2.cvtColor(self.i1, cv2.COLOR_BGR2RGB)
        imgi1 = PIL.Image.fromarray(cv2i1)
        imgtki1 = ImageTk.PhotoImage(image=imgi1)
        self.frame_camera_2_picture.imgtk = imgtki1
        self.frame_camera_2_picture.configure(image=imgtki1)

        # Frame ảnh camera chụp phía sau:
        self.i2 = cv2.imread("UI/loi1.jpg", 1)
        #self.s2 = cv2.resize(self.i2, (0, 0), fx=0.5, fy=0.5)
        cv2i2 = cv2.cvtColor(self.i2, cv2.COLOR_BGR2RGB)
        imgi2 = PIL.Image.fromarray(cv2i2)
        imgtki2 = ImageTk.PhotoImage(image=imgi2)
        self.frame_camera_3_picture.imgtk = imgtki2
        self.frame_camera_3_picture.configure(image=imgtki2)

        # Frame ảnh biển số sau khi crop:
        self.i3 = cv2.imread("UI/loi2.jpg", 1)
        # self.s3 = cv2.resize(self.i3, (0, 0), fx=0.5, fy=0.5)
        cv2i3 = cv2.cvtColor(self.i3, cv2.COLOR_BGR2RGB)
        imgi3 = PIL.Image.fromarray(cv2i3)
        imgtki3 = ImageTk.PhotoImage(image=imgi3)
        self.anhbienso_crop.imgtk = imgtki3
        self.anhbienso_crop.configure(image=imgtki3)


        #Label kết quả
        self.frame_ketqua_2_ketqua.configure(text="READY", borderwidth=1, relief=tkinter.SOLID, foreground="orange",
                                background="gray", font=("ubuntu mono", 45))

    def alertme(self,*args):
        self.chup()

    def chup(self):
        self.show_picture_empty()
        #self.fr1.configure(background="gray")
        cam = Client('http://192.168.1.64', 'admin', 'Cev123456', timeout=30)
        cam.count_events = 1  # The number of events we want to retrieve (default = 1)
        response = cam.Streaming.channels[102].picture(method='get', type='opaque_data')
        with open('screen.jpg', 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        time.sleep(0)
        img = cv2.imread('screen.jpg')
        self.tenanh = "Xevao_" + time.strftime("%d-%m-%Y-%H-%M-%S")
        cv2.imwrite(self.tenanh + ".jpg", img)
        try:
            self.nhandienbienso()
            self.show_frame()
            self.ocr()
            print("OK")
            self.txtmathe.delete(1.0, tkinter.END)
            self.txtmathe.focus()
        except:
            self.fr1.configure(background="red")
            self.fr2.configure(background="red")
            self.fr2_2.configure(background="red")
            self.lb2_2.configure(text="Lỗi - Hãy thử lại!", foreground="white", background="red",
                                 font=("ubuntu mono", 85))
            self.show_frame1_empty()
            self.lbketqua.configure(text="NG", borderwidth=1, relief=tkinter.SOLID, foreground="white",
                                    background="red", font=("ubuntu mono", 65))
            self.fr1.configure(background="red")
            self.fr2.configure(background="red")
            print("NG")
            self.txtmathe.delete(1.0, tkinter.END)
            self.txtmathe.focus()














class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        # Get video source width and height
        self.width = 400 #self.vid.get(cv2.CAP_PROP_FRAME_WIDTH) // 3
        self.height = 300 #self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT) //3
    def get_frame(self, ret=None):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            resize = cv2.resize(frame, (400, 300))
            if ret:
                # Return a boolean success flag and the current frame converted to BGR

                return (ret,resize) # cv2.cvtColor(resize, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

App(tkinter.Tk(), "Smart Parking Systems - ver1.0")