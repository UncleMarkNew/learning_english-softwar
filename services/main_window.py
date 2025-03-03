import tkinter as tk
from tkinter import ttk, messagebox
import os

from ui.upload_tab import UploadTab
from ui.query_tab import QueryTab
from ui.edit_tab import EditTab

class MainWindow:
    """Main application window."""
    
    def __init__(self, root, db_manager, llm_processor=None):
        """Initialize the main window."""
        self.root = root
        self.db_manager = db_manager
        self.llm_processor = llm_processor
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the main window UI."""
        self.root.title("智能文件管理系统")
        self.root.geometry("900x700")
        
        # API Key setup if LLM processor is not initialized
        if not self.llm_processor:
            self.show_api_key_dialog()
        
        # Create main notebook (tabbed interface)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.upload_tab = UploadTab(notebook, self)
        self.query_tab = QueryTab(notebook, self)
        self.edit_tab = EditTab(notebook, self)
        
        # Add tabs to notebook
        notebook.add(self.upload_tab, text="上传文件")
        notebook.add(self.query_tab, text="查询文件")
        notebook.add(self.edit_tab, text="编辑文件")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # LLM Status indicator
        self.llm_status_frame = ttk.Frame(self.root)
        self.llm_status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        self.llm_status_var = tk.StringVar()
        self.llm_status_var.set("LLM: " + ("已连接" if self.llm_processor else "未连接"))
        
        llm_status = ttk.Label(self.llm_status_frame, textvariable=self.llm_status_var)
        llm_status.pack(side=tk.LEFT)
        
        if self.llm_processor:
            ttk.Button(self.llm_status_frame, text="更改 API Key", 
                      command=self.show_api_key_dialog).pack(side=tk.LEFT, padx=5)
    
    def show_api_key_dialog(self):
        """Show dialog to enter DeepSeek API key."""
        dialog = tk.Toplevel(self.root)
        dialog.title("设置 DeepSeek API Key")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Get existing API key from environment or previous setup
        existing_key = os.environ.get("DEEPSEEK_API_KEY", "")
        if self.llm_processor and self.llm_processor.api_key:
            existing_key = self.llm_processor.api_key
        
        # API key entry
        ttk.Label(dialog, text="请输入您的 DeepSeek API Key:").pack(padx=20, pady=(20, 5), anchor=tk.W)
        
        api_key_var = tk.StringVar(value=existing_key)
        api_key_entry = ttk.Entry(dialog, textvariable=api_key_var, width=50, show="*")
        api_key_entry.pack(padx=20, pady=5, fill=tk.X)
        
        # Show/hide key checkbox
        show_key_var = tk.BooleanVar(value=False)
        
        def toggle_show_key():
            if show_key_var.get():
                api_key_entry.config(show="")
            else:
                api_key_entry.config(show="*")
        
        ttk.Checkbutton(dialog, text="显示 API Key", variable=show_key_var, 
                       command=toggle_show_key).pack(padx=20, pady=5, anchor=tk.W)
        
        # API key save
        def save_api_key():
            api_key = api_key_var.get().strip()
            if not api_key:
                messagebox.showerror("错误", "请输入有效的 API Key")
                return
            
            try:
                # Initialize or update LLM processor
                from services.llm_processor import LLMProcessor
                self.llm_processor = LLMProcessor(api_key=api_key)
                
                # Update status
                self.llm_status_var.set("LLM: 已连接")
                
                # Show success message
                messagebox.showinfo("成功", "API Key 设置成功")
                dialog.destroy()
                
                # Add button to status bar if not already there
                for widget in self.llm_status_frame.winfo_children():
                    if isinstance(widget, ttk.Button) and widget["text"] == "更改 API Key":
                        break
                else:
                    ttk.Button(self.llm_status_frame, text="更改 API Key", 
                              command=self.show_api_key_dialog).pack(side=tk.LEFT, padx=5)
                
            except Exception as e:
                messagebox.showerror("错误", f"设置 API Key 时出错: {str(e)}")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(button_frame, text="保存", command=save_api_key).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def set_status(self, message):
        """Set status bar message."""
        self.status_var.set(message)
