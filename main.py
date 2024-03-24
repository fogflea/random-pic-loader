import wx
import requests
import io
import random
import threading

# 图片URL列表
image_urls = []

class ImageFrame(wx.Frame):
    def __init__(self, parent, bitmap):
        super(ImageFrame, self).__init__(parent, title="图片")
        self.panel = wx.Panel(self)
        self.image = wx.StaticBitmap(self.panel, bitmap=bitmap)

        # 计算窗口边框和标题栏的大小
        self.Layout()  # 更新窗口布局以获取正确的窗口大小
        frame_size = self.GetSize()
        client_size = self.GetClientSize()
        border_width = frame_size.width - client_size.width
        border_height = frame_size.height - client_size.height

        # 计算新的窗口大小
        new_width = bitmap.GetWidth() + border_width
        new_height = bitmap.GetHeight() + border_height

        # 调整窗口大小
        self.SetSize(new_width, new_height)

        self.Centre()
        self.Show(True)

import pickle
import os

class Mywin(wx.Frame):
    def __init__(self, parent, title): 
        super(Mywin, self).__init__(parent, title = title, size = (500,150)) 

        self.panel = wx.Panel(self) 
        vbox = wx.BoxSizer(wx.VERTICAL) 

        self.btn = wx.Button(self.panel, -1, "更换图片") 
        self.btn.Bind(wx.EVT_BUTTON, self.load_image) 
        vbox.Add(self.btn, 0, flag = wx.ALIGN_CENTER) 

        self.load_btn = wx.Button(self.panel, -1, "从txt中加载图片网址") 
        self.load_btn.Bind(wx.EVT_BUTTON, self.load_urls) 
        vbox.Add(self.load_btn, 0, flag = wx.ALIGN_CENTER) 

        self.file_label = wx.StaticText(self.panel, label="No file selected")
        vbox.Add(self.file_label, 0, flag = wx.ALIGN_CENTER)

        self.gauge = wx.Gauge(self.panel, range = 100, size = (250, 25), style = wx.GA_HORIZONTAL)  # 将gauge属性创建在self对象上
        vbox.Add(self.gauge, 0, flag = wx.ALIGN_CENTER) 

        self.last_file_path = self.load_last_file_path()  # 从磁盘上加载上次选择的文件路径

        self.panel.SetSizer(vbox) 

        self.Centre() 
        self.Show(True)

        if self.last_file_path:
            self.load_urls(None, self.last_file_path)  # 在运行时自动选择上次关闭的txt文件

    def load_urls(self, event, default_path=None):
        if default_path is None:
            dialog_args = {"message": "Open TXT file", "wildcard": "TXT files (*.txt)|*.txt"}
            if self.last_file_path:
                dialog_args["defaultFile"] = self.last_file_path
            with wx.FileDialog(self, **dialog_args) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                pathname = fileDialog.GetPath()
        else:
            pathname = default_path
        try:
            with open(pathname, 'r') as file:
                global image_urls
                image_urls = [line.strip() for line in file]
            self.file_label.SetLabel("Selected file: " + pathname)
            self.last_file_path = pathname  # 更新上次选择的文件路径
            self.save_last_file_path()  # 保存上次选择的文件路径到磁盘上
        except IOError:
            wx.LogError("Cannot open file '%s'." % pathname)

    def save_last_file_path(self):
        with open('last_file_path.pkl', 'wb') as f:
            pickle.dump(self.last_file_path, f)

    def load_last_file_path(self):
        if os.path.exists('last_file_path.pkl'):
            with open('last_file_path.pkl', 'rb') as f:
                return pickle.load(f)
        else:
            return ""

    def download_image(self):
        # 从列表中随机选择一个URL
        selected_url = random.choice(image_urls)

        # 从URL中获取图片
        response = requests.get(selected_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        bytes_read = 0
        img_data = b''
        for chunk in response.iter_content(1024):
            bytes_read += len(chunk)
            img_data += chunk
            wx.CallAfter(self.gauge.SetValue, int(round(100 * bytes_read / total_size)))

        stream = io.BytesIO(img_data)
        image = wx.Image(stream)

        # 获取图片的原始大小
        original_width = image.GetWidth()
        original_height = image.GetHeight()

        # 获取窗口的大小
        window_width = self.GetSize().width
        window_height = self.GetSize().height

        # 计算缩放比例
        scale_factor = min(500 / original_width, 600 / original_height)

        # 计算新的大小
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        # 将图片缩放到新的大小
        image = image.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)

        # 显示图片
        wx.CallAfter(ImageFrame, self, wx.Bitmap(image))

    def load_image(self, event):
        threading.Thread(target=self.download_image).start()

app = wx.App() 
Mywin(None, '随机图片加载器') 
app.MainLoop()