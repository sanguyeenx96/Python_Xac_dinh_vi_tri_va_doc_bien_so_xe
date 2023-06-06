import tkinter
import cv2
import PIL
from PIL import Image, ImageTk
from paddleocr import PaddleOCR,draw_ocr
import time
from lib_detection import load_model, detect_lp, im2single
from paddleocr import PaddleOCR,draw_ocr
import datetime as dt
import pyodbc

from hikvisionapi import Client
import re



class App:
    def __init__(self, window, window_title, video_source='rtsp://admin:Cev123456@192.168.1.64/h264_stream'):
        # Open the video source
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.vid = MyVideoCapture(self.video_source)

        #   #   #   ########### *** GIAO DIỆN HIỂN THỊ *** ############   #   #   #
        ################################################################################################
        # Frame tiêu đề
        self.fr0 = tkinter.Frame(window, relief=tkinter.RIDGE)
        self.fr0.pack(fill="x", pady=10, padx=10)
        self.fr0_1_1 = tkinter.Frame(self.fr0)
        self.fr0_1_1.grid(row=0, column=1, pady=3)
        self.lb0_1_1 = tkinter.Label(self.fr0_1_1)
        self.lb0_1_1.pack()
        self.fr0_1_2 = tkinter.Frame(self.fr0)
        self.fr0_1_2.grid(row=0, column=2, pady=3, padx=5)
        self.lb0_1_2 = tkinter.Label(self.fr0_1_2, text="CỔNG VÀO / GATE IN", font=("Tahoma", 25))
        self.lb0_1_2.pack()
        ################################################################################################
        self.border1 = tkinter.Frame(window, bg="gray", borderwidth=1, relief=tkinter.SOLID)
        self.border1.pack(fill="x", padx=5)
        # Hàng 1: (Luồng camera và ảnh chụp)
        # Frame chính:
        self.fr1 = tkinter.Frame(self.border1, bg="gray", borderwidth=1, relief=tkinter.SUNKEN)
        self.fr1.pack(fill="x", pady=5)
        # Frame luồng camera trục tiếp:
        self.fr1_1 = tkinter.Frame(self.fr1, bg="white", borderwidth=1, relief=tkinter.SOLID)
        self.fr1_1.pack(side="left", padx=3, pady=3)
        # self.fr1_1.grid(row=0, column=0, pady=3,padx=3)
        self.lb1_1 = tkinter.Label(self.fr1_1, bg="green", fg="white", text="Camera trực tiếp:", font=("Tahoma", 10))
        self.lb1_1.pack(side="top")
        self.canvas = tkinter.Canvas(self.fr1_1, bg='white', width=self.vid.width, height=self.vid.height)
        self.canvas.pack(side="left")


        # Frame ảnh camera chụp biển số:
        self.fr1_2 = tkinter.Frame(self.fr1, bg="white", borderwidth=1, relief=tkinter.SOLID)
        self.fr1_2.pack(side="left", padx=3, pady=3)
        # self.fr1_2.grid(row=0, column=1,pady=3)
        self.lb1_2 = tkinter.Label(self.fr1_2, text="Ảnh chụp từ Camera sau:", font=("Tahoma", 10))
        self.lb1_2.pack(side="top")
        self.picture1_2 = tkinter.Label(
            self.fr1_2)  # ,text="waiting...", bg='orange', borderwidth=1, relief=tkinter.RIDGE)
        self.picture1_2.pack(side="right", expand="True")
        # Frame ảnh camera chụp toàn cảnh
        self.fr1_3 = tkinter.Frame(self.fr1, bg="white", borderwidth=1, relief=tkinter.SOLID)
        self.fr1_3.pack(side="left", padx=3, pady=3)
        # self.fr1_3.grid(row=0, column=2,pady=3,padx=3)
        self.lb1_3 = tkinter.Label(self.fr1_3, text="Ảnh chụp từ Camera trước:", font=("Tahoma", 10))
        self.lb1_3.pack(side="top")
        self.picture1_3 = tkinter.Label(self.fr1_3)  # text="waiting...", bg='orange', borderwidth=1, relief=tkinter.RIDGE)
        self.picture1_3.pack(side="right", expand="True")
        # Frame kết quả
        self.fr1_4 = tkinter.Frame(self.fr1, bg="white", borderwidth=1, relief=tkinter.SOLID)
        self.fr1_4.pack(padx=3, pady=3, fill="both", expand="True")
        # self.fr1_4.grid(row=0, column=3, pady=3, padx=3)
        self.lbketqua = tkinter.Label(self.fr1_4)
        self.lbketqua.pack(fill="both", expand="True")
        ################################################################################################
        # Hàng 2: (Ảnh biển số crop và hiển thị biển số - KẾT QUẢ)
        # Frame chính:
        self.fr2 = tkinter.Frame(self.border1, bg="silver", borderwidth=1, relief=tkinter.RIDGE)
        self.fr2.pack(fill="x", pady=3, padx=3)
        # Frame chứa label và ảnh biển số crop
        self.fr2_1 = tkinter.Frame(self.fr2, bg="silver", relief=tkinter.RIDGE)
        self.fr2_1.pack(side="left", padx=3, pady=3)
        # Frame chứa ảnh biển số:
        self.fr2_1_1 = tkinter.Frame(self.fr2_1, bg="silver", borderwidth=1, relief=tkinter.RIDGE)
        self.fr2_1_1.pack(side="left", fill="y")
        # Label:
        self.lb2_1_1 = tkinter.Label(self.fr2_1_1, text="Biển số xe:", font=("Tahoma", 10))
        self.lb2_1_1.pack(side="top")
        # Ảnh biển số sau crop:
        self.picture2_1_1 = tkinter.Label(self.fr2_1_1)
        self.picture2_1_1.pack(expand="True")
        # Frame chứa kết quả biển số:
        self.fr2_2 = tkinter.Frame(self.fr2, bg="silver", borderwidth=1, relief=tkinter.RIDGE)
        self.fr2_2.pack(fill="both", expand="True")
        # Label kết quả biển sô
        self.lb2_2 = tkinter.Label(self.fr2_2, bg='orange', text="waiting...", font=("Tahoma", 10))
        self.lb2_2.pack(expand="True")

        # Hàng 4: (Mã thẻ)
        # Frame chính:
        self.fr3 = tkinter.Frame(window, bg="silver", borderwidth=1, relief=tkinter.SUNKEN)
        self.fr3.pack(side="bottom", fill="x", pady=5)
        # Frame chứa label và textbox mã thẻ:
        self.fr3_1 = tkinter.Frame(self.fr3, bg="silver")
        self.fr3_1.pack(pady=3, padx=3)
        self.lb3_1 = tkinter.Label(self.fr3_1, text="Mã thẻ:", font=("Tahoma", 30), relief=tkinter.RIDGE)
        self.lb3_1.pack(side="left", padx=3, pady=3)
        self.txtmathe = tkinter.Text(self.fr3_1, bg="white", fg="black", width=30, height=1, font=("Tahoma", 30))
        self.txtmathe.pack(side="right", padx=3, pady=3)
        self.txtmathe.focus()
        self.txtmathe.bind("<Return>", self.alertme)

        #Nút bấm check:
        self.btn_snapshot = tkinter.Button(window, text="Chụp ảnh", width=100,command=self.chup)
        self.btn_snapshot.pack(side="bottom")
        #self.btn_snapshot.grid(row=2, column=0)  # anchor=tkinter.CENTER


        self.show_frame1_empty()
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()
        count = 0
        self.window.geometry("1280x1000+250+10")
        self.window.mainloop()

    def alertme(self,*args):
        self.chup()

    def chup(self):
        self.show_frame1_empty()
        self.fr1.configure(background="gray")
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

        #cv2.imshow("show", img)
        #cv2.waitKey(0)

    def snapshot(self):
        self.show_frame1_empty()
        self.fr1.configure(background="gray")
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        if ret:
            self.tenanh = "Xevao_" + time.strftime("%d-%m-%Y-%H-%M-%S")
            #cv2.imwrite("Xevao_" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            cv2.imwrite(self.tenanh + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            try:
                self.nhandienbienso()
                self.show_frame()
                self.ocr()
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


    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
        self.window.after(self.delay, self.update)

    def nhandienbienso(self):
        img_path = self.tenanh + ".jpg"
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        # Load model LP detection
        wpod_net_path = "wpod-net_update1.json"
        wpod_net = load_model(wpod_net_path)
        # Đọc file ảnh đầu vào
        Ivehicle = cv2.imread(img_path)
        Dmax = 608
        Dmin = 288
        # Lấy tỷ lệ giữa W và H của ảnh và tìm ra chiều nhỏ nhất
        ratio = float(max(Ivehicle.shape[:2])) / min(Ivehicle.shape[:2])
        side = int(ratio * Dmin)
        bound_dim = min(side, Dmax)

        _, LpImg, lp_type = detect_lp(wpod_net, im2single(Ivehicle), bound_dim, lp_threshold=0.5)
        if (len(LpImg)):
            anhbienso = cv2.cvtColor(LpImg[0], cv2.COLOR_RGB2BGR)
            img = cv2.convertScaleAbs(anhbienso, alpha=(255.0))
            cv2.imwrite("anhbienso.jpg", img)

    def show_frame(self):
        # Frame ảnh camera chụp biển số:
        self.img0 = cv2.imread(self.tenanh + ".jpg", 1)
        #self.small1 = cv2.resize(self.img0, (0, 0), fx=0.5, fy=0.5)
        cv2img0 = cv2.cvtColor(self.img0, cv2.COLOR_BGR2RGB)
        img0 = PIL.Image.fromarray(cv2img0)
        imgtk0 = ImageTk.PhotoImage(image=img0)
        self.picture1_2.imgtk = imgtk0
        self.picture1_2.configure(image=imgtk0)

        # Frame ảnh biển số sau khi crop:
        self.img1 = cv2.imread("anhbienso.jpg", 1)
        #self.small2 = cv2.resize(self.img1, (0, 0), fx=0.5, fy=0.5)
        cv2img1 = cv2.cvtColor(self.img1, cv2.COLOR_BGR2RGB)
        img1 = PIL.Image.fromarray(cv2img1)
        imgtk1 = ImageTk.PhotoImage(image=img1)
        self.picture2_1_1.imgtk = imgtk1
        self.picture2_1_1.configure(image=imgtk1)

    def show_frame1_empty(self):
        # Kết quả:
        self.lbketqua.configure(text="READY", borderwidth=1, relief=tkinter.SOLID, foreground="orange",
                                background="gray", font=("ubuntu mono", 45))
        # Icon:
        self.i0 = cv2.imread("UI/wr.jpg", 1)
        cv2i0 = cv2.cvtColor(self.i0, cv2.COLOR_BGR2RGB)
        imgi0 = PIL.Image.fromarray(cv2i0)
        imgtki0 = ImageTk.PhotoImage(image=imgi0)
        self.lb0_1_1.imgtk = imgtki0
        self.lb0_1_1.configure(image=imgtki0)

        # Frame ảnh camera chụp biển số:
        self.i1 = cv2.imread("UI/loi1.jpg", 1)
        #self.s1 = cv2.resize(self.i1, (0, 0), fx=0.5, fy=0.5)
        cv2i1 = cv2.cvtColor(self.i1, cv2.COLOR_BGR2RGB)
        imgi1 = PIL.Image.fromarray(cv2i1)
        imgtki1 = ImageTk.PhotoImage(image=imgi1)
        self.picture1_2.imgtk = imgtki1
        self.picture1_2.configure(image=imgtki1)

        # Frame ảnh biển số sau khi crop:
        self.i2 = cv2.imread("UI/loi2.jpg", 1)
        #self.s2 = cv2.resize(self.i2, (0, 0), fx=0.5, fy=0.5)
        cv2i2 = cv2.cvtColor(self.i2, cv2.COLOR_BGR2RGB)
        imgi2 = PIL.Image.fromarray(cv2i2)
        imgtki2 = ImageTk.PhotoImage(image=imgi2)
        self.picture2_1_1.imgtk = imgtki2
        self.picture2_1_1.configure(image=imgtki2)

        # Frame ảnh camera chụp phía trước:
        self.i3 = cv2.imread("UI/loi1.jpg", 1)
        #self.s3 = cv2.resize(self.i3, (0, 0), fx=0.5, fy=0.5)
        cv2i3 = cv2.cvtColor(self.i3, cv2.COLOR_BGR2RGB)
        imgi3 = PIL.Image.fromarray(cv2i3)
        imgtki3 = ImageTk.PhotoImage(image=imgi3)
        self.picture1_3.imgtk = imgtki3
        self.picture1_3.configure(image=imgtki3)

    def ocr(self):
        ocr = PaddleOCR(use_angle_cls=True,lang='en')
        img_path = "anhbienso.jpg"
        result = ocr.ocr(img_path, cls=True)
        print(len(result))
        kq1 = str(result[0][1][0])
        kq1loc = kq1.replace(" ", "")
        kq2 = str(result[1][1][0])
        kq2loc = kq2.replace(" ", "")
        strbienso = kq1loc +" "+ kq2loc
        r2 = strbienso.replace("-", "")
        bienso = r2.replace(".", "")
        print(bienso)
        if len(bienso) > 7:
            #self.timdulieutrungSQL()
            self.lbketqua.configure(text="OK", borderwidth=1, relief=tkinter.SOLID, foreground="white",
                                    background="green", font=("ubuntu mono", 85))
            self.fr2_2.configure(background="green")
            self.lb2_2.configure(text=strbienso, foreground="white", background="green", font=("ubuntu mono", 85))
            self.fr1.configure(background="green")
            self.fr2.configure(background="green")

            mathe = self.txtmathe.get(1.0, "end-1c")
            #mathe2 = re.sub('[^0-9]', '', mathe1)
            #mathe = mathe2.replace("0", "")
            conx = pyodbc.connect("driver={ODBC Driver 17 for SQL Server}; server=CANON; database=Baidoxe2; uid=sa; pwd=123;")
            cursor = conx.cursor()
            date = dt.datetime.now()
            #thoigianvao = str(f'{date:%d/%m/%Y %H:%M:%S}')
            ngay = str(f'{date:%d/%m/%Y}')
            gio = str(f'{date:%H:%M:%S}')
            anhcamsau = str(self.tenanh+".jpg")
            anhcamtruoc = "none"
            cursor.execute("insert into dbo.Xetrongbai(mathe,bienso,ngay,gio,anhcamsau,anhcamtruoc) values (?,?,?,?,?,?)", mathe, bienso,ngay,gio,anhcamsau,anhcamtruoc)
            conx.commit()
            conx.close()
        else:
            raise Exception("Không đủ ký tự biển số")

    def timdulieutrungSQL(self):
        conx = pyodbc.connect(
            "driver={ODBC Driver 17 for SQL Server}; server=CANON; database=Baidoxe2; uid=sa; pwd=123;")
        cursor = conx.cursor()
        mathe1 = self.txtmathe.get(1.0, "end-1c")
        mathe2 = re.sub('[^0-9]', '', mathe1)
        mathe = mathe2.replace("0", "")
        cursor.execute("SELECT COUNT(*) from dbo.Xetrongbai where mathe LIKE '"+mathe+"'")
        result = cursor.fetchone()
        soluong = result[0]
        print(soluong)
        conx.close()
        if soluong >= 0:
            self.xoadulieutrungSQL()

    def xoadulieutrungSQL(self):
        conx = pyodbc.connect(
            "driver={ODBC Driver 17 for SQL Server}; server=CANON; database=Baidoxe2; uid=sa; pwd=123;")
        cursor = conx.cursor()
        mathe1 = self.txtmathe.get(1.0, "end-1c")
        mathe2 = re.sub('[^0-9]', '', mathe1)
        mathe = mathe2.replace("0", "")
        #cursor.execute("DELETE (*) from dbo.Xetrongbai where mathe LIKE '" + mathe + "'")
        cursor.execute("delete from dbo.Xetrongbai where mathe in (?)", mathe)
        conx.commit()
        conx.close()

class MyVideoCapture:
    def __init__(self, video_source='rtsp://admin:Cev123456@192.168.1.64/h264_stream'):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        # Get video source width and height
        self.width = 640 #self.vid.get(cv2.CAP_PROP_FRAME_WIDTH) // 3
        self.height = 480 #self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT) //3
    def get_frame(self, ret=None):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            resize = cv2.resize(frame, (640, 480))
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