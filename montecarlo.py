import tkinter as tk
from tkinter import filedialog
import subprocess
import re
import os
import shutil
from PIL import ImageTk, Image
from tkinter import Text, Scrollbar
import webbrowser
import numpy as np
import cmath as cm
import matplotlib.pyplot as plt

global file_path
global h1_range
global h2_range
global h3_range
global r1_range
global r2_range
global num
global ssr
global status_text

def return_to_old():
    # 返回到旧的界面
    new_root.destroy()  # 关闭新界面
    subprocess.Popen(['python', 'GUI.py'])
    
    
def montecarlo1d_window():
    global new_root
    new_root = tk.Tk()  # Create a new Tkinter window
    new_root.title("Monte Carlo")

    # 设置窗口大小
    new_root.geometry("800x600")  # 根据需要设置合适的大小

    new_root.resizable(False, False)

    # Load background image and resize
    background_image = Image.open("background.jpg")
    background_image = background_image.resize((800, 600))
    background_photo = ImageTk.PhotoImage(background_image)

    # Create a Label to display the background image
    background_label = tk.Label(new_root, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

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
        
    def execute_main_wrapper():
        # 添加一个包装函数，在其中调用execute_main并传递file_path
        
        # 获取输入的范围参数值
        h1_min = float(h1_min_entry.get())
        h1_max = float(h1_max_entry.get())
        h2_min = float(h2_min_entry.get())
        h2_max = float(h2_max_entry.get())
        r1_min = float(r1_min_entry.get())
        r1_max = float(r1_max_entry.get())
        r2_min = float(r2_min_entry.get())
        r2_max = float(r2_max_entry.get())
        r3_min = float(r3_min_entry.get())
        r3_max = float(r3_max_entry.get())
        
        # 获取输入的迭代次数和拟合差限制
        num = int(num_entry.get())
        ssr = float(ssr_entry.get())
        
        # 构建范围参数数组
        h1_range = [h1_min, h1_max]
        h2_range = [h2_min, h2_max]
        r1_range = [r1_min, r1_max]
        r2_range = [r2_min, r2_max]
        r3_range = [r3_min, r3_max]
        
        montecarlo_main(file_path, h1_range, h2_range, r1_range, r2_range, r3_range, num, ssr)


    def montecarlo_main(file_path, h1_range, h2_range, r1_range, r2_range, r3_range, num, ssr):
        def mt1dan(freq, dz, sig):
            # 用于计算一维MT正演模型的视电阻率响应
            # 返回视电阻率、相位、阻抗
            mu = 4.0E-7 * np.pi
            II = cm.sqrt(-1)
            nf = len(freq)
            nz = len(sig)
            rho = np.zeros(nf)
            phs = np.zeros(nf)
            zxy = np.zeros(nf, dtype=complex)
            for kf in range(nf):
                omega = 2.0 * np.pi * freq[kf]
                Z = cm.sqrt(II * omega * mu / sig[nz-1])
                for m in range(nz-2, -1, -1):
                    km = cm.sqrt(II * omega * mu * sig[m])
                    Z0 = II * omega * mu / km
                    Z = cm.exp(-2 * km * dz[m]) * (Z - Z0) / (Z + Z0)
                    Z = Z0 * (1 + Z) / (1 - Z)
                zxy[kf] = Z
                rho[kf] = np.abs(zxy[kf] * zxy[kf]) / (2 * np.pi * freq[kf] * mu)
                phs[kf] = cm.phase(zxy[kf]) * 180.0 / np.pi
            return rho, phs, zxy

        def monte_carlo_inversion(data, freq, h1_range, h2_range, r1_range, r2_range, r3_range, num, ssr):
            best_models = []  # 存储拟合程度最佳的模型
            misfits = []  # 存储拟合差
            
            h1_values = np.linspace(*h1_range, num) 
            h2_values = np.linspace(*h2_range, num)  
            r1_values = np.linspace(*r1_range, num)  
            r2_values = np.linspace(*r2_range, num) 
            r3_values = np.linspace(*r3_range, num)  
            
            for h1 in h1_values:
                for h2 in h2_values:
                    for r1 in r1_values:
                        for r2 in r2_values:
                            for r3 in r3_values:
                                # 构建模型参数数组
                                h = np.array([h1, h2])
                                sig = np.array([1/r1, 1/r2, 1/r3])
                                
                                # 进行正演计算
                                synthetic_data, _, _ = mt1dan(freq, h, sig)
                                
                                # 计算残差平方和
                                residuals = synthetic_data - data
                                nssr = np.sum(residuals**2)
                                
                                # 拟合差小于某个数的模型被视为较好的模型
                                if nssr < ssr:
                                    best_models.append([h1, h2, r1, r2, r3])
                                    misfits.append(nssr)
                


            def plot_best_model():
                
                h_values1 = np.linspace(0, best_model[0], 100)
                h_values2 = np.linspace(best_model[0], best_model[1]+best_model[0], 100)
                h_values3 = np.linspace(best_model[1]+best_model[0], best_model[1]+best_model[0]+(best_model[1]+best_model[0])/2, 100)

                r1_values = np.full_like(h_values1, best_model[2])
                r2_values = np.full_like(h_values2, best_model[3])
                r3_values = np.full_like(h_values3, best_model[4])
                
                plt.figure(figsize=(8, 6))
                plt.plot(h_values1, r1_values, 'b')
                plt.plot(h_values2, r2_values, 'b')
                plt.plot(h_values3, r3_values, 'b')
                
                # 垂直连接线段
                plt.step([best_model[0], best_model[0]], [best_model[2], best_model[3]], 'b')
                plt.step([best_model[1]+best_model[0], best_model[1]+best_model[0]], [best_model[3], best_model[4]], 'b')
                
                plt.xlabel('Depth')
                plt.ylabel('Resistivity')
                plt.title('Best Model')
                plt.grid(True)
                plt.legend()
                plt.tight_layout()
                plt.savefig('best_model.png')  # 保存为图片文件
                plt.close()

                # 在image_label中显示图片
                image = Image.open('best_model.png')
                image = image.resize((400, 300), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                image_label.configure(image=photo)
                image_label.image = photo

            # 在monte_carlo_inversion函数中调用plot_best_model函数
            if best_models:
                best_models = np.array(best_models)
                misfits = np.array(misfits)
                # 计算均值和拟合差作为最佳模型和不确定度
                best_model = np.mean(best_models, axis=0)
                uncertainty = np.std(misfits)
                best_model_str = f"best model:\nh1:{best_model[0]}\nh2:{best_model[1]}\nr1:{best_model[2]}\nr2:{best_model[3]}\nr3:{best_model[4]}\nmisfit: {uncertainty}"
                status_text.insert("end", best_model_str + "\n")
                
                # 调用绘图函数
                plot_best_model()

                # Move the specified filename.png file
                current_directory = os.getcwd()
                source_filename = 'best_model.png'
                source_path = os.path.join(current_directory, source_filename)
                destination_path = os.path.join(folder_path, source_filename)

                os.rename(source_path, destination_path)

            else:
                status_text.insert("end", "best_model " + "not found\n")
                
        # 读取文件内容
        with open(file_path, "r") as file:
            content = file.read()

        # 提取频率数组
        freq_match = re.search(r">FREQ //(\d+)(.*?)>", content, re.DOTALL)
        if freq_match:
            freq_count = int(freq_match.group(1))
            freq_values = re.findall(r"\b\d+\.\d+E[+-]\d+\b", freq_match.group(2))
            freq = [float(value) for value in freq_values[:freq_count]]

        # 提取zxyr数组
        zxyr_match = re.search(r">ZXYI ROT=ZROT\s*//(\d+)(.*?)>", content, re.DOTALL)
        zxyr_values = []
        if zxyr_match:
            zxyr_count = int(zxyr_match.group(1))
            zxyr_values = re.findall(r"\b[-+]?\d+\.\d+E[+-]\d+\b", zxyr_match.group(2))
            zxyr_values = [float(value) for value in zxyr_values[:zxyr_count]]

        # 提取zyxr数组
        zyxr_match = re.search(r">ZYXR ROT=ZROT\s*//(\d+)(.*?)>", content, re.DOTALL)
        zyxr_values = []
        if zyxr_match:
            zyxr_count = int(zyxr_match.group(1))
            zyxr_values = re.findall(r"\b[-+]?\d+\.\d+E[+-]\d+\b", zyxr_match.group(2))
            zyxr_values = [float(value) for value in zyxr_values[:zyxr_count]]

        # 提取zxyi数组
        zxyi_match = re.search(r">ZXYI ROT=ZROT\s*//(\d+)(.*?)>", content, re.DOTALL)
        zxyi_values = []
        if zxyi_match:
            zxyi_count = int(zxyi_match.group(1))
            zxyi_values = re.findall(r"\b[-+]?\d+\.\d+E[+-]\d+\b", zxyi_match.group(2))
            zxyi_values = [float(value) for value in zxyi_values[:zxyi_count]]

        # 提取zyxi数组
        zyxi_match = re.search(r">ZYXI ROT=ZROT\s*//(\d+)(.*?)>", content, re.DOTALL)
        zyxi_values = []
        if zyxi_match:
            zyxi_count = int(zyxi_match.group(1))
            zyxi_values = re.findall(r"\b[-+]?\d+\.\d+E[+-]\d+\b", zyxi_match.group(2))
            zyxi_values = [float(value) for value in zyxi_values[:zyxi_count]]

        mu = 4 * 3.14159 * 1.e-7

        # 计算ZXY和ZYX
        II = complex(0, 1)
        zxy = [(r + i * II) * mu * 1e3 for r, i in zip(zxyr_values, zxyi_values)]
        zyx = [(r + i * II) * mu * 1e3 for r, i in zip(zyxr_values, zyxi_values)]

        # 计算omega和mu
        omega = [2.0 * 3.14159 * freq_val for freq_val in freq]

        # 计算rhoxy和rhoyx
        rhoxy = [1e3 * abs(zxy_val)**2 / (omega_val * mu * 1e3) for zxy_val, omega_val in zip(zxy, omega)]
        rhoyx = [1e3 * abs(zyx_val)**2 / (omega_val * mu * 1e3) for zyx_val, omega_val in zip(zyx, omega)]

        monte_carlo_inversion(rhoxy, freq, h1_range, h2_range, r1_range, r2_range, r3_range, num, ssr)

    def select_folder():
        global folder_path
        folder_path = filedialog.askdirectory()  # 弹出文件夹选择对话框，获取用户选择的文件夹路径
        status_text.insert("end", folder_path + "设为图片保存文件夹\n")

    return_btn = tk.Button(new_root, text="返回", command=return_to_old)
    return_btn.place(x=10, y=10)
    
    open_btn = tk.Button(new_root, text="打开文件", command=open_file)
    open_btn.place(x=60, y=10)

    select_btn = tk.Button(new_root, text="选择图像保存文件夹", command=select_folder)
    select_btn.place(x=135, y=10)

    execute_btn = tk.Button(new_root, text="执行脚本", command=execute_main_wrapper)
    execute_btn.place(x=270, y=10)

    y = 70

    h1_label = tk.Label(new_root, text="h1范围：")
    h1_label.place(x=10, y=10+y)
    h1_min_entry = tk.Entry(new_root)
    h1_min_entry.place(x=80, y=10+y)
    h1_max_entry = tk.Entry(new_root)
    h1_max_entry.place(x=230, y=10+y)

    h2_label = tk.Label(new_root, text="h2范围：")
    h2_label.place(x=10, y=60+y)
    h2_min_entry = tk.Entry(new_root)
    h2_min_entry.place(x=80, y=60+y)
    h2_max_entry = tk.Entry(new_root)
    h2_max_entry.place(x=230, y=60+y)

    r1_label = tk.Label(new_root, text="r1范围：")
    r1_label.place(x=10, y=110+y)
    r1_min_entry = tk.Entry(new_root)
    r1_min_entry.place(x=80, y=110+y)
    r1_max_entry = tk.Entry(new_root)
    r1_max_entry.place(x=230, y=110+y)

    r2_label = tk.Label(new_root, text="r2范围：")
    r2_label.place(x=10, y=160+y)
    r2_min_entry = tk.Entry(new_root)
    r2_min_entry.place(x=80, y=160+y)
    r2_max_entry = tk.Entry(new_root)
    r2_max_entry.place(x=230, y=160+y)

    r3_label = tk.Label(new_root, text="r3范围：")
    r3_label.place(x=10, y=210+y)
    r3_min_entry = tk.Entry(new_root)
    r3_min_entry.place(x=80, y=210+y)
    r3_max_entry = tk.Entry(new_root)
    r3_max_entry.place(x=230, y=210+y)

    num_label = tk.Label(new_root, text="迭代次数：")
    num_label.place(x=10, y=260+y)
    num_entry = tk.Entry(new_root)
    num_entry.place(x=120, y=260+y)

    ssr_label = tk.Label(new_root, text="拟合差限制：")
    ssr_label.place(x=10, y=310+y)
    ssr_entry = tk.Entry(new_root)
    ssr_entry.place(x=120, y=310+y)

    def set_default_parameters():
        # 设置默认参数
        h1_min_entry.delete(0, tk.END)
        h1_min_entry.insert(0, "1")
        h1_max_entry.delete(0, tk.END)
        h1_max_entry.insert(0, "1000")
        
        h2_min_entry.delete(0, tk.END)
        h2_min_entry.insert(0, "1")
        h2_max_entry.delete(0, tk.END)
        h2_max_entry.insert(0, "1000")
        
        r1_min_entry.delete(0, tk.END)
        r1_min_entry.insert(0, "1")
        r1_max_entry.delete(0, tk.END)
        r1_max_entry.insert(0, "1000")
        
        r2_min_entry.delete(0, tk.END)
        r2_min_entry.insert(0, "1")
        r2_max_entry.delete(0, tk.END)
        r2_max_entry.insert(0, "1000")
        
        r3_min_entry.delete(0, tk.END)
        r3_min_entry.insert(0, "1")
        r3_max_entry.delete(0, tk.END)
        r3_max_entry.insert(0, "1000")
        
        num_entry.delete(0, tk.END)
        num_entry.insert(0, "5")
        
        ssr_entry.delete(0, tk.END)
        ssr_entry.insert(0, "1000")
    

    # 添加一键设置参数的按钮
    set_params_btn = tk.Button(new_root, text="一键设置参数", command=set_default_parameters)
    set_params_btn.place(x=290, y=350)

    # 创建Text小部件
    status_text = Text(new_root, bg="light gray", bd=1, relief="solid", borderwidth=1, fg="black")
    status_text.place(x=60, y=480, width=250, height=90)

    status_text_label = tk.Label(new_root, text="提示信息")
    status_text_label.place(x=150, y=430)

    # 创建滚动条
    scrollbar = Scrollbar(new_root, command=status_text.yview)
    scrollbar.place(x=60 + 250, y=500, height=90)

    # 将滚动条与Text小部件关联
    status_text.config(yscrollcommand=scrollbar.set)

    # 第二列的图像
    image_label = tk.Label(new_root, bg="white", bd=1, relief="solid", borderwidth=1, fg="black")
    image_label.place(x=390, y=60, width=400, height=500)

    image_text_label = tk.Label(new_root, text="Monte Carlo反演图像")
    image_text_label.place(x=535, y=30)
    
    new_root.mainloop()

if __name__ == "__main__":
    montecarlo1d_window()