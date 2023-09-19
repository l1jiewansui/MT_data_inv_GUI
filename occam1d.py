import tkinter as tk
from tkinter import filedialog
import subprocess
import re
import os
import shutil
from PIL import ImageTk, Image
from tkinter import Text, Scrollbar

global file_path
global folder_path
global file_name

def return_to_old():
    # 返回到旧的界面
    new_root.destroy()  # 关闭新界面
    subprocess.Popen(['python', 'GUI.py'])

def move_png_files(folder_path):
    current_directory = os.getcwd()
    files = os.listdir(current_directory)
    
    for file in files:
        if file.endswith('.png'):
            file_path = os.path.join(current_directory, file)
            new_file_path = os.path.join(folder_path, file)
            shutil.move(file_path, new_file_path)



def clear_folder(folder_path):
    # Get the list of files in the folder
    file_list = os.listdir(folder_path)
    
    # Iterate over the files and delete them
    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
    # Provide feedback to the user
    print("Folder cleared successfully.")

def occam1d_window():
    global file_name
    global new_root
    new_root = tk.Tk()  # 创建一个新的Tkinter窗口
    new_root.title("Occam 1D")

    # 设置窗口大小
    new_root.geometry("800x600")  # 根据需要调整大小

    new_root.resizable(False, False)

    # 加载背景图像并调整大小
    background_image = Image.open("background.jpg")  # 替换为实际的图像文件路径
    background_image = background_image.resize((800, 600))  # 调整图像大小为800x600像素
    background_photo = ImageTk.PhotoImage(background_image)

    # 创建一个Label来显示背景图像
    background_label = tk.Label(new_root, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    def generate_parameters():
        global file_name
        # 从 file_path 获取文件名（去掉拓展名）
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        # 获取用户输入的参数值
        nlayer_value = nlayer_entry.get()
        maxit_value = maxit_entry.get()
        tol_value = tol_entry.get()
        mode_value = mode_entry.get()
        noise_value = noise_entry.get()

        parameters = {
            "site": file_name,
            "inv": f"{file_name}.RECV",
            "nlayer": nlayer_value,
            "mfile": f"{file_name}.mod",
            "dfile": f"{file_name}.dat",
            "maxit": maxit_value,
            "tol": tol_value,
            "mode": mode_value,
            "noise": noise_value,
            # 添加其他参数及其默认值
        }

        with open("mk.para", "w") as f:
            for key, value in parameters.items():
                f.write(f"{key}={value}\n")

        run_script()

    def open_file():
        global file_path
        file_path = filedialog.askopenfilename(title="选择文件", filetypes=[("EDI Files", "*.edi")])

            # Check if a file was selected
        if file_path:
            # Define the destination folder
            destination_folder = "./edi/"
            
            # Copy the file to the destination folder
            shutil.copy(file_path, destination_folder)
            
            # Provide feedback to the user
            status_text.insert("end", file_path + "导入成功\n")
    
    def select_folder():
        global folder_path
        folder_path = filedialog.askdirectory()  # 弹出文件夹选择对话框，获取用户选择的文件夹路径
        status_text.insert("end", folder_path + "设为图片保存文件夹\n")

    def run_script():
        global file_path
        global folder_path
        global file_name

        readedi(file_path)
        subprocess.run(['make'], shell=True)

        # Move the specified filename.png file
        current_directory = os.getcwd()
        source_filename = file_name + ".png"
        source_path = os.path.join(current_directory, source_filename)
        destination_path = os.path.join(folder_path, source_filename)
        
        # Load the image and resize it
        image = Image.open(source_path)
        resized_image = image.resize((300, 450))  

        # Display the resized image in image_label
        photo = ImageTk.PhotoImage(resized_image)
        image_label.configure(image=photo)
        image_label.image = photo

        os.rename(source_path, destination_path)

        # Clear the "./edi/" folder
        clear_folder("./edi/")

    def fill_default_values():
        nlayer_entry.delete(0, "end")  # 清空nlayer_entry文本框内容
        nlayer_entry.insert(0, "20")

        maxit_entry.delete(0, "end")  # 清空maxit_entry文本框内容
        maxit_entry.insert(0, "10")

        tol_entry.delete(0, "end")  # 清空tol_entry文本框内容
        tol_entry.insert(0, "1.2")

        mode_entry.delete(0, "end")  # 清空mode_entry文本框内容
        mode_entry.insert(0, "3")

        noise_entry.delete(0, "end")  # 清空noise_entry文本框内容
        noise_entry.insert(0, "6")

    # 计算偏移量以使控件居中
    offset_x = (800 - 640) / 2 - 40
    offset_y = 50

    label_font = ("楷体", 11, "bold")
    text_font = ("Times New Roman", 11)
    entry_font = ("Segoe UI", 10)

    # 属性栏的按钮
    return_btn = tk.Button(new_root, text="返回", command=return_to_old)
    return_btn.place(x=10 + offset_x, y=10)

    open_btn = tk.Button(new_root, text="打开文件", command=open_file)
    open_btn.place(x=60 + offset_x, y=10)

    select_btn = tk.Button(new_root, text="选择图像保存文件夹", command=select_folder)
    select_btn.place(x=135 + offset_x, y=10)

    # 第一列的标签和文本框
    nlayer_label = tk.Label(new_root, text="层数（nlayer）", font=label_font, bg="white", bd=1, relief="solid", borderwidth=1, fg="black")
    nlayer_label.place(x=10 + offset_x, y=60 + offset_y)
    nlayer_entry = tk.Entry(new_root, font=entry_font)
    nlayer_entry.place(x=140 + offset_x, y=60 + offset_y)

    maxit_label = tk.Label(new_root, text="最大迭代次数", font=label_font, bg="white", bd=1, relief="solid", borderwidth=1, fg="black")
    maxit_label.place(x=10 + offset_x, y=100 + offset_y)
    maxit_entry = tk.Entry(new_root, font=entry_font)
    maxit_entry.place(x=140 + offset_x, y=100 + offset_y)

    tol_label = tk.Label(new_root, text="容差（tol）", font=label_font, bg="white", bd=1, relief="solid", borderwidth=1, fg="black")
    tol_label.place(x=10 + offset_x, y=140 + offset_y)
    tol_entry = tk.Entry(new_root, font=entry_font)
    tol_entry.place(x=140 + offset_x, y=140 + offset_y)

    mode_label = tk.Label(new_root, text="模式（mode）", font=label_font, bg="white", bd=1, relief="solid", borderwidth=1, fg="black")
    mode_label.place(x=10 + offset_x, y=180 + offset_y)
    mode_entry = tk.Entry(new_root, font=entry_font)
    mode_entry.place(x=140 + offset_x, y=180 + offset_y)

    noise_label = tk.Label(new_root, text="噪声（noise）", font=label_font, bg="white", bd=1, relief="solid", borderwidth=1, fg="black")
    noise_label.place(x=10 + offset_x, y=220 + offset_y)
    noise_entry = tk.Entry(new_root, font=entry_font)
    noise_entry.place(x=140 + offset_x, y=220 + offset_y)

    generate_btn = tk.Button(new_root, text="执行脚本", command=generate_parameters)
    generate_btn.place(x=10 + offset_x, y=270 + offset_y)

    default_btn = tk.Button(new_root, text="一键生成参数", command=fill_default_values)
    default_btn.place(x=110 + offset_x, y=270 + offset_y)

    # 创建Text小部件
    status_text = Text(new_root, bg="light gray", bd=1, relief="solid", borderwidth=1, fg="black", font=entry_font)
    status_text.place(x=10 + offset_x, y=450, width=250, height=90)

    status_text_label = tk.Label(new_root, text="提示信息", font=text_font, bg="white")
    status_text_label.place(x=100 + offset_x, y=400)

    # 创建滚动条
    scrollbar = Scrollbar(new_root, command=status_text.yview)
    scrollbar.place(x=10 + offset_x + 250, y=470, height=90)

    # 将滚动条与Text小部件关联
    status_text.config(yscrollcommand=scrollbar.set)

    # 第二列的图像
    image_label = tk.Label(new_root, bg="white", bd=1, relief="solid", borderwidth=1, fg="black")
    image_label.place(x=320 + offset_x, y=60, width=400, height=500)

    image_text_label = tk.Label(new_root, text="Occam1D反演图像", font=text_font, bg="white")
    image_text_label.place(x=465 + offset_x, y=30)
    
    new_root.mainloop()

###readedi####

def convert_degrees(dms):
    # 解析度分秒格式的经纬度
    degrees, minutes, seconds = map(float, re.findall(r'(\d+):(\d+):([\d.]+)', dms)[0])
    # 转换为浮点数格式的经纬度，保留8位小数
    decimal_degrees = round(degrees + (minutes / 60) + (seconds / 3600), 8)
    return decimal_degrees

def readedi(file_path):
    # 清空或创建新的 edi.list 文件
    with open('edi.list', 'w'):
        pass

    with open('png.list', 'w'):
        pass

    # 读取指定文件路径的文件
    with open(file_path) as file:
        content = file.read()

    # 提取站点位置信息
    match = re.search(r'LONG=(.*?)\n', content)
    if match:
        longitude = match.group(1)
        longitude = convert_degrees(longitude)

    match = re.search(r'LAT=(.*?)\n', content)
    if match:
        latitude = match.group(1)
        latitude = convert_degrees(latitude)

    match = re.search(r'ELEV=(.*?)\n', content)
    if match:
        elevation = match.group(1)
        elevation = round(float(elevation), 8)

    # 获取文件名
    filename = os.path.basename(file_path)
    # 去除文件名的 .edi 后缀
    basename = os.path.splitext(filename)[0]

    # 将结果追加写入 edi.list 文件
    with open('edi.list', 'a') as outfile:
        outfile.write(f"{basename} {longitude:.8f} {latitude:.8f} {elevation:.8f}\n")

    print("站点位置信息提取完成，结果已保存到 edi.list 文件中。")

    # 将结果追加写入 png.list 文件
    with open('png.list', 'a') as outfile:
        outfile.write("png=\\\n")
        outfile.write(f"{basename}.png \\\n")

    print("站点位置信息提取完成，结果已保存到 png.list 文件中。")
    

if __name__ == "__main__":
    occam1d_window()

