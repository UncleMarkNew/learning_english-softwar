import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sqlite3
import os
import shutil
from datetime import datetime
import uuid
from file_utils import FileUtils  # 导入新模块

class FileManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("文件管理系统")
        self.root.geometry("1000x700")
        
        # 创建数据库连接
        self.conn = sqlite3.connect('file_system.db')
        self.create_tables()
        
        # 设置存储上传文件的目录
        self.storage_dir = "storage"
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        
        # 初始化状态变量
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
            
        # 创建主界面
        self.create_ui()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # 创建文件表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            original_name TEXT NOT NULL,
            stored_path TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            upload_date TEXT,
            last_modified TEXT,
            content TEXT,
            metadata TEXT
        )
        ''')
        
        self.conn.commit()
        
    def create_ui(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建标签页控件
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 上传文件标签页
        self.upload_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.upload_frame, text="上传文件")
        self.setup_upload_tab()
        
        # 查询文件标签页
        self.query_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.query_frame, text="查询文件")
        self.setup_query_tab()
        
        # 修改文件标签页
        self.edit_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.edit_frame, text="修改文件")
        self.setup_edit_tab()
        
        # 状态栏
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_upload_tab(self):
        # 文件选择区域
        select_frame = ttk.LabelFrame(self.upload_frame, text="选择文件")
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.selected_file_var = tk.StringVar()
        ttk.Entry(select_frame, textvariable=self.selected_file_var, width=70, state='readonly').pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(select_frame, text="浏览...", command=self.browse_file).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 文件信息区域
        info_frame = ttk.LabelFrame(self.upload_frame, text="文件信息")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(info_frame, text="文件类型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_type_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.file_type_var, state='readonly').grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(info_frame, text="文件大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_size_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.file_size_var, state='readonly').grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(info_frame, text="元数据:").grid(row=2, column=0, sticky=tk.NW, padx=5, pady=5)
        self.metadata_text = scrolledtext.ScrolledText(info_frame, width=50, height=5)
        self.metadata_text.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 文件内容预览区域
        preview_frame = ttk.LabelFrame(self.upload_frame, text="文件内容预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, width=80, height=15)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 上传按钮
        upload_button = ttk.Button(self.upload_frame, text="上传文件", command=self.upload_file)
        upload_button.pack(pady=10)
        
    def setup_query_tab(self):
        # 搜索区域
        search_frame = ttk.LabelFrame(self.query_frame, text="搜索文件")
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="文件名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.search_name_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(search_frame, text="文件类型:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.search_type_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_type_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(search_frame, text="搜索", command=self.search_files).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(search_frame, text="显示全部", command=self.load_all_files).grid(row=0, column=5, padx=5, pady=5)
        
        # 文件列表区域
        list_frame = ttk.LabelFrame(self.query_frame, text="文件列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('文件名', '类型', '大小', '上传日期', '最后修改')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=100)
        
        yscroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=yscroll.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        preview_frame = ttk.LabelFrame(self.query_frame, text="文件内容预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.query_preview_text = scrolledtext.ScrolledText(preview_frame, width=80, height=10)
        self.query_preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.file_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        
        self.load_all_files()
        
    def setup_edit_tab(self):
        select_frame = ttk.LabelFrame(self.edit_frame, text="选择要修改的文件")
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.edit_file_id = None
        self.edit_file_var = tk.StringVar()
        ttk.Entry(select_frame, textvariable=self.edit_file_var, width=70, state='readonly').pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(select_frame, text="选择...", command=self.select_file_to_edit).pack(side=tk.LEFT, padx=5, pady=5)
        
        edit_content_frame = ttk.LabelFrame(self.edit_frame, text="编辑文件内容")
        edit_content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.edit_content_text = scrolledtext.ScrolledText(edit_content_frame, width=80, height=20)
        self.edit_content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        metadata_frame = ttk.LabelFrame(self.edit_frame, text="编辑元数据")
        metadata_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.edit_metadata_text = scrolledtext.ScrolledText(metadata_frame, width=80, height=5)
        self.edit_metadata_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        save_button = ttk.Button(self.edit_frame, text="保存修改", command=self.save_edit)
        save_button.pack(pady=10)
        
    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.selected_file_var.set(file_path)
            self.load_file_info(file_path)
    
    def load_file_info(self, file_path):
        # 获取文件信息并更新 UI
        file_type, file_size = FileUtils.get_file_info(file_path)
        self.file_type_var.set(file_type)
        self.file_size_var.set(f"{file_size} 字节")
        
        # 预览文件内容
        FileUtils.preview_file(file_path, self.preview_text)
    
    def upload_file(self):
        file_path = self.selected_file_var.get()
        if not file_path:
            messagebox.showerror("错误", "请先选择文件")
            return
        
        try:
            # 生成唯一文件ID
            file_id = str(uuid.uuid4())
            original_name = os.path.basename(file_path)
            file_type = os.path.splitext(original_name)[1]
            file_size = os.path.getsize(file_path)
            upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 创建目标存储路径
            stored_path = os.path.join(self.storage_dir, file_id + file_type)
            
            # 复制文件到存储目录
            shutil.copy2(file_path, stored_path)
            
            # 使用 FileUtils 读取文件内容
            content, _ = FileUtils.read_file_content(file_path)
            
            # 获取元数据
            metadata = self.metadata_text.get(1.0, tk.END).strip()
            
            # 将文件信息存入数据库
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO files (id, original_name, stored_path, file_type, file_size, upload_date, last_modified, content, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (file_id, original_name, stored_path, file_type, file_size, upload_date, upload_date, content, metadata))
            
            self.conn.commit()
            
            # 更新状态栏和重置表单
            self.status_var.set(f"文件 '{original_name}' 上传成功")
            self.selected_file_var.set("")
            self.file_type_var.set("")
            self.file_size_var.set("")
            self.metadata_text.delete(1.0, tk.END)
            self.preview_text.delete(1.0, tk.END)
            
            self.load_all_files()
            messagebox.showinfo("成功", f"文件 '{original_name}' 上传成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"上传文件时出错: {str(e)}")
    
    def search_files(self):
        name_search = f"%{self.search_name_var.get()}%"
        type_search = f"%{self.search_type_var.get()}%"
        
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, original_name, file_type, file_size, upload_date, last_modified
        FROM files
        WHERE original_name LIKE ? AND file_type LIKE ?
        ''', (name_search, type_search))
        
        files = cursor.fetchall()
        self.update_file_tree(files)
    
    def load_all_files(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, original_name, file_type, file_size, upload_date, last_modified
        FROM files
        ''')
        
        files = cursor.fetchall()
        self.update_file_tree(files)
    
    def update_file_tree(self, files):
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        for file in files:
            file_id, name, file_type, size, upload_date, last_modified = file
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size/1024:.2f} KB"
            else:
                size_str = f"{size/(1024*1024):.2f} MB"
                
            self.file_tree.insert('', tk.END, iid=file_id, values=(name, file_type, size_str, upload_date, last_modified))
            
        self.status_var.set(f"共找到 {len(files)} 个文件")
    
    def on_file_select(self, event):
        selection = self.file_tree.selection()
        if not selection:
            return
            
        file_id = selection[0]
        
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT content
        FROM files
        WHERE id = ?
        ''', (file_id,))
        
        result = cursor.fetchone()
        if result:
            content = result[0]
            self.query_preview_text.delete(1.0, tk.END)
            self.query_preview_text.insert(tk.END, content)
    
    def select_file_to_edit(self):
        select_dialog = tk.Toplevel(self.root)
        select_dialog.title("选择文件")
        select_dialog.geometry("600x400")
        select_dialog.transient(self.root)
        select_dialog.grab_set()
        
        columns = ('文件名', '类型', '上传日期')
        file_tree = ttk.Treeview(select_dialog, columns=columns, show='headings')
        
        for col in columns:
            file_tree.heading(col, text=col)
            file_tree.column(col, width=100)
        
        yscroll = ttk.Scrollbar(select_dialog, orient=tk.VERTICAL, command=file_tree.yview)
        file_tree.configure(yscrollcommand=yscroll.set)
        
        file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, original_name, file_type, upload_date
        FROM files
        ''')
        
        files = cursor.fetchall()
        for file in files:
            file_id, name, file_type, upload_date = file
            file_tree.insert('', tk.END, iid=file_id, values=(name, file_type, upload_date))
        
        def on_select():
            selection = file_tree.selection()
            if not selection:
                messagebox.showerror("错误", "请选择一个文件")
                return
                
            file_id = selection[0]
            
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT original_name, content, metadata
            FROM files
            WHERE id = ?
            ''', (file_id,))
            
            result = cursor.fetchone()
            if result:
                name, content, metadata = result
                
                self.edit_file_id = file_id
                self.edit_file_var.set(name)
                
                self.edit_content_text.delete(1.0, tk.END)
                self.edit_content_text.insert(tk.END, content or "")
                
                self.edit_metadata_text.delete(1.0, tk.END)
                self.edit_metadata_text.insert(tk.END, metadata or "")
                
                select_dialog.destroy()
        
        button_frame = ttk.Frame(select_dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="确定", command=on_select).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=select_dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def save_edit(self):
        if not self.edit_file_id:
            messagebox.showerror("错误", "请先选择一个文件")
            return
            
        try:
            content = self.edit_content_text.get(1.0, tk.END)
            metadata = self.edit_metadata_text.get(1.0, tk.END)
            last_modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor = self.conn.cursor()
            cursor.execute('''
            UPDATE files
            SET content = ?, metadata = ?, last_modified = ?
            WHERE id = ?
            ''', (content, metadata, last_modified, self.edit_file_id))
            
            self.conn.commit()
            
            self.status_var.set(f"文件 '{self.edit_file_var.get()}' 修改成功")
            
            self.edit_file_id = None
            self.edit_file_var.set("")
            self.edit_content_text.delete(1.0, tk.END)
            self.edit_metadata_text.delete(1.0, tk.END)
            
            self.load_all_files()
            
            messagebox.showinfo("成功", f"文件 '{self.edit_file_var.get()}' 修改成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存修改时出错: {str(e)}")
    
    def on_closing(self):
        if self.conn:
            self.conn.close()
        self.root.destroy()

class LLMProcessor:
    def __init__(self):
        pass
    
    def process_text(self, text):
        return text
    
    def extract_metadata(self, text):
        return {}

if __name__ == "__main__":
    root = tk.Tk()
    app = FileManagementSystem(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
