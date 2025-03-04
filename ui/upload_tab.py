import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import uuid
from file_utils import FileUtils

class UploadTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.selected_file_path = None
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the upload tab UI."""
        # 预览区域
        preview_frame = ttk.LabelFrame(self, text="文件信息")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 文件信息
        info_frame = ttk.Frame(preview_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text="文件名：").pack(side=tk.LEFT)
        self.filename_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.filename_var, width=50).pack(side=tk.LEFT, padx=5)
        
        # 文件类型和编码信息
        type_frame = ttk.Frame(preview_frame)
        type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(type_frame, text="文件类型：").pack(side=tk.LEFT)
        self.filetype_var = tk.StringVar()
        ttk.Entry(type_frame, textvariable=self.filetype_var, width=20, state='readonly').pack(side=tk.LEFT, padx=5)
        
        ttk.Label(type_frame, text="编码：").pack(side=tk.LEFT)
        self.encoding_var = tk.StringVar()
        ttk.Entry(type_frame, textvariable=self.encoding_var, width=20, state='readonly').pack(side=tk.LEFT, padx=5)
        
        # 文件内容预览
        content_frame = ttk.LabelFrame(preview_frame, text="文件内容预览")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.content_preview = scrolledtext.ScrolledText(content_frame, width=80, height=15)
        self.content_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 元数据编辑
        metadata_frame = ttk.LabelFrame(preview_frame, text="元数据")
        metadata_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.metadata_text = scrolledtext.ScrolledText(metadata_frame, width=80, height=5)
        self.metadata_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 提交按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            button_frame,
            text="确认上传",
            command=self.submit_upload
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="清除",
            command=self.clear_preview
        ).pack(side=tk.RIGHT, padx=5)
    
    def show_file_preview(self, file_path):
        """显示文件预览信息"""
        if not file_path:
            return
            
        try:
            # 设置文件名
            filename = os.path.basename(file_path)
            self.filename_var.set(filename)
            
            # 获取文件类型和大小
            file_type, file_size = FileUtils.get_file_info(file_path)
            self.filetype_var.set(f"{file_type} ({file_size} 字节)")
            
            # 预览文件内容
            encoding = FileUtils.preview_file(file_path, self.content_preview)
            self.encoding_var.set(encoding)
            
            # 清空元数据
            self.metadata_text.delete(1.0, tk.END)
            
            # 保存文件路径
            self.selected_file_path = file_path
            
        except Exception as e:
            messagebox.showerror("错误", f"预览文件时出错：{str(e)}")
    
    def submit_upload(self):
        """提交文件上传"""
        if not self.selected_file_path:
            messagebox.showerror("错误", "请先选择要上传的文件")
            return
            
        try:
            # 生成唯一文件ID
            file_id = str(uuid.uuid4())
            original_name = os.path.basename(self.selected_file_path)
            file_type = os.path.splitext(original_name)[1]
            file_size = os.path.getsize(self.selected_file_path)
            
            # 读取文件内容
            content, encoding = FileUtils.read_file_content(self.selected_file_path)
            if not content:
                messagebox.showerror("错误", "无法读取文件内容")
                return
            
            # 获取元数据
            metadata = self.metadata_text.get(1.0, tk.END).strip()
            
            # 保存到数据库
            stored_path = os.path.join(self.app.storage_dir, file_id + file_type)
            
            # 复制文件到存储目录
            import shutil
            shutil.copy2(self.selected_file_path, stored_path)
            
            # 插入数据库记录
            self.app.db_manager.insert_file(
                file_id, original_name, stored_path, file_type, file_size, content, metadata
            )
            
            messagebox.showinfo("成功", "文件上传成功")
            self.clear_preview()
            
            # 刷新文件列表
            if hasattr(self.app, 'refresh_file_list'):
                self.app.refresh_file_list()
            
        except Exception as e:
            messagebox.showerror("错误", f"上传文件时出错：{str(e)}")
    
    def clear_preview(self):
        """清除预览信息"""
        self.selected_file_path = None
        self.filename_var.set("")
        self.filetype_var.set("")
        self.encoding_var.set("")
        self.content_preview.delete(1.0, tk.END)
        self.metadata_text.delete(1.0, tk.END)
