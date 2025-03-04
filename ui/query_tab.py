import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from file_utils import FileUtils
import os

class QueryTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the query tab UI."""
        # File selection area
        select_frame = ttk.LabelFrame(self, text="选择要查询的文件")
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 文件信息显示
        info_frame = ttk.Frame(select_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text="文件名：").pack(side=tk.LEFT)
        self.file_name_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.file_name_var, width=50, state='readonly').pack(side=tk.LEFT, padx=5)
        
        # 文件类型和编码信息
        type_frame = ttk.Frame(select_frame)
        type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(type_frame, text="文件类型：").pack(side=tk.LEFT)
        self.filetype_var = tk.StringVar()
        ttk.Entry(type_frame, textvariable=self.filetype_var, width=20, state='readonly').pack(side=tk.LEFT, padx=5)
        
        ttk.Label(type_frame, text="编码：").pack(side=tk.LEFT)
        self.encoding_var = tk.StringVar()
        ttk.Entry(type_frame, textvariable=self.encoding_var, width=20, state='readonly').pack(side=tk.LEFT, padx=5)
        
        # File list (Treeview)
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.file_tree = ttk.Treeview(tree_frame, columns=("文件名", "类型", "上传日期"), show="headings")
        self.file_tree.heading("文件名", text="文件名")
        self.file_tree.heading("类型", text="类型")
        self.file_tree.heading("上传日期", text="上传日期")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.file_tree.bind('<Double-1>', lambda e: self.on_select())
        
        # 添加文件内容显示区域
        content_frame = ttk.LabelFrame(self, text="文件内容")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.content_text = scrolledtext.ScrolledText(content_frame, width=80, height=10)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加元数据显示区域
        metadata_frame = ttk.LabelFrame(self, text="元数据")
        metadata_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.metadata_text = scrolledtext.ScrolledText(metadata_frame, width=80, height=5)
        self.metadata_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Load file list
        self.load_file_list()
    
    def load_file_list(self):
        """Load files into the Treeview."""
        # 清空现有内容
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        # 加载文件列表
        files = self.app.db_manager.get_files_for_selection()
        for file in files:
            file_id, name, file_type, upload_date = file
            self.file_tree.insert("", tk.END, iid=file_id, values=(name, file_type, upload_date))
    
    def get_selected_file_id(self):
        """Get the selected file ID from the Treeview."""
        selection = self.file_tree.selection()
        if selection:
            return selection[0]  # 返回选中的文件 ID
        else:
            return None  # 如果没有选中文件，返回 None
    
    def on_select(self):
        """Handle file selection for querying."""
        file_id = self.get_selected_file_id()
        if not file_id:
            messagebox.showerror("错误", "请选择一个文件")
            return
        
        # 获取文件的完整信息
        file_info = self.app.db_manager.get_file_for_query(file_id)
        if file_info:
            try:
                # 更新文件名和类型信息
                self.file_name_var.set(file_info["original_name"])
                file_type, file_size = os.path.splitext(file_info["original_name"])[1], os.path.getsize(file_info["stored_path"])
                self.filetype_var.set(f"{file_type} ({file_size} 字节)")
                
                # 使用 FileUtils 预览文件内容
                encoding = FileUtils.preview_file(file_info["stored_path"], self.content_text)
                self.encoding_var.set(encoding or "未知")
                
                # 显示元数据
                metadata = file_info["metadata"] or ""
                if isinstance(metadata, bytes):
                    metadata = metadata.decode('utf-8')
                elif not isinstance(metadata, str):
                    metadata = str(metadata)
                
                self.metadata_text.delete(1.0, tk.END)
                self.metadata_text.insert(tk.END, metadata)
                
            except Exception as e:
                messagebox.showerror("错误", f"预览文件时出错：{str(e)}")
        else:
            messagebox.showerror("错误", "未找到文件")
