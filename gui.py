import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os
import threading

# 全局变量
clip_module = None
clip_loaded = False
clip_lock = threading.Lock()

try:
    import compress
except ImportError as e:
    messagebox.showerror("错误", f"无法导入压缩模块: {str(e)}")

def select_dataset_path():
    path = filedialog.askdirectory()
    dataset_path_entry.delete(0, tk.END)
    dataset_path_entry.insert(0, path)

def select_output_path():
    path = filedialog.askdirectory()
    output_path_entry.delete(0, tk.END)
    output_path_entry.insert(0, path)

def load_clip_module():
    global clip_module, clip_loaded
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        import clip
        clip_module = clip
        with clip_lock:
            clip_loaded = True
        terminal_text.insert(tk.END, "CLIP模块加载完成！\n")
        classify_button.config(state=tk.NORMAL)
    except Exception as e:
        messagebox.showerror("错误", f"加载CLIP模块时出错: {str(e)}")

def start_compression():
    dataset_path = dataset_path_entry.get()
    output_path = output_path_entry.get()
    
    if not dataset_path or not output_path:
        messagebox.showerror("错误", "请先选择输入和输出路径")
        return
    
    thread = threading.Thread(target=perform_compression, args=(dataset_path, output_path))
    thread.start()

def perform_compression(input_path, output_path):
    try:
        class StdoutRedirector:
            def __init__(self, text_widget):
                self.text_space = text_widget
            def write(self, string):
                self.text_space.insert(tk.END, string)
                self.text_space.see(tk.END)
            def flush(self):
                pass
        sys.stdout = StdoutRedirector(terminal_text)
        compress.compress_images(input_path, output_path)
        messagebox.showinfo("完成", "图片压缩完成")
    except Exception as e:
        messagebox.showerror("错误", f"压缩出错: {str(e)}")
    finally:
        sys.stdout = sys.__stdout__

def start_classification():
    with clip_lock:
        if not clip_loaded:
            messagebox.showinfo("提示", "模型正在加载中，点击确定后继续等待...")
            classify_button.config(state=tk.DISABLED)
            root.after(1000, check_loading_status)
            return
        else:
            classify_button.config(state=tk.NORMAL)

    dataset_path = dataset_path_entry.get()
    output_path = output_path_entry.get()
    categories_input = categories_entry.get()
    categories = [category.strip() for category in categories_input.split(',')]

    if not dataset_path or not output_path or not categories:
        messagebox.showerror("错误", "请输入所有必要信息")
        return

    thread = threading.Thread(target=perform_classification, args=(dataset_path, output_path, categories))
    thread.start()

def check_loading_status():
    with clip_lock:
        if clip_loaded:
            classify_button.config(state=tk.NORMAL)
            start_classification()
        else:
            root.after(1000, check_loading_status)

def perform_classification(dataset_path, output_path, categories):
    try:
        text_features = clip_module.initialize_model(categories)
        class StdoutRedirector:
            def __init__(self, text_widget):
                self.text_space = text_widget
            def write(self, string):
                self.text_space.insert(tk.END, string)
                self.text_space.see(tk.END)
            def flush(self):
                pass
        sys.stdout = StdoutRedirector(terminal_text)
        clip_module.classify_images(dataset_path, output_path, text_features, categories)
        messagebox.showinfo("完成", "图片分类完成")
    except Exception as e:
        messagebox.showerror("错误", f"发生错误: {str(e)}")
    finally:
        sys.stdout = sys.__stdout__

# 创建主窗口
root = tk.Tk()
root.title("图片分类与压缩 GUI")

# UI组件布局
tk.Label(root, text="图片文件夹路径:").grid(row=0, column=0, padx=10, pady=5)
dataset_path_entry = tk.Entry(root, width=50)
dataset_path_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="选择路径", command=select_dataset_path).grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="输出文件夹路径:").grid(row=1, column=0, padx=10, pady=5)
output_path_entry = tk.Entry(root, width=50)
output_path_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="选择路径", command=select_output_path).grid(row=1, column=2, padx=10, pady=5)

tk.Label(root, text="分类类别 (用逗号分隔):").grid(row=2, column=0, padx=10, pady=5)
categories_entry = tk.Entry(root, width=50)
categories_entry.grid(row=2, column=1, padx=10, pady=5)

# 按钮行
compress_button = tk.Button(root, text="开始压缩", command=start_compression)
compress_button.grid(row=3, column=0, padx=10, pady=20)
classify_button = tk.Button(root, text="开始分类", command=start_classification, state=tk.NORMAL)
classify_button.grid(row=3, column=2, padx=10, pady=20)

# 终端输出
terminal_text = tk.Text(root, height=10, width=80)
terminal_text.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

# 启动后台加载线程
loading_thread = threading.Thread(target=load_clip_module, daemon=True)
loading_thread.start()

root.mainloop()