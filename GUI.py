import tkinter as tk
from tkinter import filedialog
import subprocess
import re
import os
import shutil
from PIL import ImageTk, Image
from tkinter import Text, Scrollbar
import webbrowser

global file_path
global h1_range
global h2_range
global h3_range
global r1_range
global r2_range
global num
global ssr

def run_occam():
    # 执行OCCAM反演程序的逻辑
    print("执行OCCAM反演程序")
    root.withdraw()  # 隐藏旧界面
    occam_window()  # 打开OCCAM界面

def run_montecarlo():
    # 执行蒙特卡洛反演程序的逻辑
    print("执行蒙特卡洛反演程序")
    root.withdraw()  # 隐藏旧界面
    montecarlo_window()  # 打开Monte Carlo界面

def open_file():
    global file_path
    file_path = filedialog.askopenfilename(title="选择文件", filetypes=[("EDI Files", "*.edi")])

def occam_window():
    subprocess.Popen(['python', 'occam1d.py'])

def montecarlo_window():
    subprocess.Popen(['python', 'montecarlo.py'])

def open_readme():
    # Open README file in a web browser
    webbrowser.open('README.md')

def main():
    # Create main window
    global root
    root = tk.Tk()
    root.title("MT data inv GUI")

    # Set window size
    root.geometry("800x600")

    root.resizable(False, False)
    
    x = 550
    
    y = 150

    # Load background image and resize
    background_image = Image.open("background.jpg")
    background_image = background_image.resize((800, 600))
    background_photo = ImageTk.PhotoImage(background_image)

    # Create a Label to display the background image
    background_label = tk.Label(root, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Add custom font for the title
    title_font = ("Arial", 32, "bold")

    # Add the title label
    title_label = tk.Label(root, text="MT data inv GUI", font=title_font, bg="white", bd=1, relief="solid", borderwidth=1, fg="black")
    title_label.place(x=x-100, y=y)

    # Add buttons
    occam_btn = tk.Button(root, text="执行OCCAM反演", command=run_occam)
    occam_btn.place(x=x, y=y+100)

    montecarlo_btn = tk.Button(root, text="执行蒙特卡洛反演", command=run_montecarlo)
    montecarlo_btn.place(x=x, y=y+150)

    more_methods_btn = tk.Button(root, text="更多反演方法（待更新）")
    more_methods_btn.place(x=x, y=y+200)

    readme_btn = tk.Button(root, text="程序介绍", command=open_readme)
    readme_btn.place(x=x, y=y+250)

    # Add label at the bottom
    copyright_label = tk.Label(root, text="Copyright@Mengyuhang")
    copyright_label.pack(side=tk.BOTTOM)

    root.mainloop()

# 调用主函数
if __name__ == "__main__":
    main()