import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from ui.upload_tab import UploadTab
from ui.query_tab import QueryTab
from ui.edit_tab import EditTab
from ui.learn_tab import LearnTab

class MainWindow:
    """Main application window with modern UI."""
    
    def __init__(self, root, db_manager, llm_processor=None):
        """Initialize the main window."""
        self.root = root
        self.db_manager = db_manager
        self.llm_processor = llm_processor
        
        # Set up storage directory
        self.storage_dir = "storage"
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the modern main window UI."""
        self.root.title("英语学习助手")
        self.root.state('zoomed')
        
        # Configure style
        style = ttk.Style()
        style.configure(".", font=('Segoe UI', 10))
        style.configure("Header.TLabel", font=('Segoe UI', 12, 'bold'))
        style.configure("Modern.TButton", padding=10)
        style.theme_use('clam')  # Use 'clam' theme
        
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top buttons frame
        buttons_frame = ttk.Frame(main_container)
        buttons_frame.pack(fill=tk.X)
        
        # Add action buttons
        ttk.Button(
            buttons_frame,
            text="上传文件",
            command=self.show_upload_dialog,
            style="Modern.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="查询文件",
            command=lambda: self.notebook.select(1),
            style="Modern.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="编辑文件",
            command=lambda: self.notebook.select(2),
            style="Modern.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        # API Key setup if LLM processor is not initialized
        if not self.llm_processor:
            self.show_api_key_dialog()
        
        # Create main notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.upload_tab = UploadTab(self.notebook, self)
        self.query_tab = QueryTab(self.notebook, self)
        self.edit_tab = EditTab(self.notebook, self)
        self.learn_tab = LearnTab(self.notebook, self)
        
        # Add tabs to notebook without any text
        self.notebook.add(self.upload_tab, text="")
        self.notebook.add(self.query_tab, text="")
        self.notebook.add(self.edit_tab, text="")
        self.notebook.add(self.learn_tab, text="")
        
        # Hide the tab bar completely
        style.configure('TNotebook.Tab', padding=0)
        style.layout('TNotebook.Tab', [])
        
        # Status bar with modern style
        status_frame = ttk.Frame(main_container, relief=tk.GROOVE, padding=(5, 2))
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X)
        
    def show_api_key_dialog(self):
        """Show dialog for API key input with improved UI."""
        dialog = tk.Toplevel(self.root)
        dialog.title("设置 API 密钥")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Content frame with padding
        content_frame = ttk.Frame(dialog, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(
            content_frame,
            text="请输入您的 DeepSeek API 密钥:",
            style="Header.TLabel"
        ).pack(pady=(0, 10))
        
        # Entry field
        api_key = tk.StringVar()
        entry = ttk.Entry(content_frame, textvariable=api_key, width=40)
        entry.pack(pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="确定",
            style="Modern.TButton",
            command=lambda: self.save_api_key(api_key.get(), dialog)
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="取消",
            style="Modern.TButton",
            command=dialog.destroy
        ).pack(side=tk.RIGHT)
        
        entry.focus()
        dialog.bind("<Return>", lambda e: self.save_api_key(api_key.get(), dialog))
        dialog.bind("<Escape>", lambda e: dialog.destroy())
    
    def save_api_key(self, api_key, dialog):
        """Save the API key and initialize LLM processor."""
        if api_key.strip():
            os.environ["DEEPSEEK_API_KEY"] = api_key.strip()
            from services.llm_processor import LLMProcessor
            try:
                self.llm_processor = LLMProcessor(api_key=api_key.strip())
                dialog.destroy()
                self.status_var.set("API 密钥已设置")
            except Exception as e:
                messagebox.showerror("错误", f"API 密钥验证失败: {str(e)}")
        else:
            messagebox.showwarning("警告", "请输入有效的 API 密钥")
            
    def set_status(self, message):
        """Set status bar message."""
        self.status_var.set(message)
        
    def refresh_file_list(self):
        """Refresh the file list in query tab."""
        if hasattr(self.query_tab, 'load_all_files'):
            self.query_tab.load_all_files()
            
    def on_closing(self):
        """Handle application closing."""
        self.root.destroy()
    
    def get_selected_file_id(self):
        """Get the selected file ID from the query tab."""
        if hasattr(self.query_tab, 'get_selected_file_id'):
            return self.query_tab.get_selected_file_id()
        return None

    def show_upload_dialog(self):
        """显示文件选择对话框"""
        file_path = filedialog.askopenfilename(
            title="选择要上传的文件",
            filetypes=[
                ("文本文件", "*.txt"),
                ("PDF文件", "*.pdf"),
                ("Word文件", "*.doc;*.docx"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.notebook.select(0)  # 切换到上传标签页
            self.upload_tab.show_file_preview(file_path)  # 显示文件预览
