import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import shutil
import uuid
from services.llm_processor import LLMProcessor
import chardet  # 需要安装: pip install chardet
from file_utils import FileUtils  # 导入新模块

class UploadTab(ttk.Frame):
    """Tab for uploading files to the system."""
    
    def __init__(self, parent, app):
        """Initialize the upload tab."""
        super().__init__(parent)
        self.app = app
        self.llm_processor = LLMProcessor()
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the upload tab UI."""
        # File selection area
        select_frame = ttk.LabelFrame(self, text="选择文件")
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.selected_file_var = tk.StringVar()
        ttk.Entry(select_frame, textvariable=self.selected_file_var, width=70, state='readonly').pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(select_frame, text="浏览...", command=self.browse_file).pack(side=tk.LEFT, padx=5, pady=5)
        
        # File info area
        info_frame = ttk.LabelFrame(self, text="文件信息")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(info_frame, text="文件类型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_type_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.file_type_var, state='readonly').grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(info_frame, text="文件大小:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_size_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.file_size_var, state='readonly').grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(info_frame, text="文件编码:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.file_encoding_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.file_encoding_var, state='readonly').grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(info_frame, text="元数据:").grid(row=3, column=0, sticky=tk.NW, padx=5, pady=5)
        self.metadata_text = scrolledtext.ScrolledText(info_frame, width=50, height=5)
        self.metadata_text.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # File content preview area
        preview_frame = ttk.LabelFrame(self, text="文件内容预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, width=80, height=15)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Upload button area
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.convert_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(button_frame, text="自动转换为UTF-8", variable=self.convert_var).pack(side=tk.LEFT, padx=5)
        
        upload_button = ttk.Button(button_frame, text="上传文件", command=self.upload_file)
        upload_button.pack(side=tk.RIGHT, pady=10, padx=5)
    
    def detect_encoding(self, file_path):
        """Detect the encoding of a file."""
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            return result['encoding'], raw_data
    
    def read_file_with_encoding(self, file_path, max_chars=None):
        """Read file content with auto-detected encoding."""
        encoding, raw_data = self.detect_encoding(file_path)
        
        if not encoding:
            return "无法检测文件编码", None
        
        try:
            if max_chars:
                content = raw_data.decode(encoding, errors='replace')[:max_chars]
            else:
                content = raw_data.decode(encoding, errors='replace')
            return content, encoding
        except:
            return "无法解码文件内容", None
    
    def convert_to_utf8(self, file_path, target_path=None):
        """Convert file to UTF-8 encoding."""
        if target_path is None:
            target_path = file_path + ".utf8"
            
        content, original_encoding = self.read_file_with_encoding(file_path)
        
        if content and original_encoding:
            with open(target_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return target_path, original_encoding
        return None, None
    
    def browse_file(self):
        """Browse for a file to upload."""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.selected_file_var.set(file_path)
            self.load_file_info(file_path)
    
    def load_file_info(self, file_path):
        # 获取文件信息并更新 UI
        file_type, file_size = FileUtils.get_file_info(file_path)
        self.file_type_var.set(file_type)
        self.file_size_var.set(f"{file_size} 字节")
        
        # 预览文件内容并设置编码
        encoding = FileUtils.preview_file(file_path, self.preview_text)
        self.file_encoding_var.set(encoding)
    
    def upload_file(self):
        """Upload the selected file to the system."""
        file_path = self.selected_file_var.get()
        if not file_path:
            messagebox.showerror("错误", "请先选择文件")
            return
        
        try:
            file_id = str(uuid.uuid4())
            original_name = os.path.basename(file_path)
            file_type = os.path.splitext(original_name)[1]
            file_size = os.path.getsize(file_path)
            
            stored_path = os.path.join(self.app.storage_dir, file_id + file_type)
            
            # 检查是否需要转换为 UTF-8
            if self.convert_var.get() and file_type.lower() in ['.txt', '.md', '.py', '.java', '.c', '.cpp', '.html', '.css', '.js', '.json', '.xml']:
                utf8_path, original_encoding = self.convert_to_utf8(file_path)
                if utf8_path:
                    shutil.copy2(utf8_path, stored_path)
                    os.remove(utf8_path)
                    content, _ = FileUtils.read_file_content(stored_path)  # 读取转换后的文件
                    messagebox.showinfo("转换成功", f"文件已从 {original_encoding} 转换为 UTF-8")
                else:
                    shutil.copy2(file_path, stored_path)
                    content, _ = FileUtils.read_file_content(file_path)
            else:
                shutil.copy2(file_path, stored_path)
                content, _ = FileUtils.read_file_content(file_path)
            
            metadata = self.metadata_text.get(1.0, tk.END).strip()
            
            self.app.db_manager.insert_file(
                file_id, original_name, stored_path, file_type, file_size, content, metadata
            )
            
            self.app.set_status(f"文件 '{original_name}' 上传成功")
            self.selected_file_var.set("")
            self.file_type_var.set("")
            self.file_size_var.set("")
            self.file_encoding_var.set("")
            self.metadata_text.delete(1.0, tk.END)
            self.preview_text.delete(1.0, tk.END)
            
            self.app.refresh_file_list()
            messagebox.showinfo("成功", f"文件 '{original_name}' 上传成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"上传文件时出错: {str(e)}")
