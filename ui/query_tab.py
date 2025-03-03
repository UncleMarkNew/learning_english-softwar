import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

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
        
        self.file_name_var = tk.StringVar()
        ttk.Entry(select_frame, textvariable=self.file_name_var, width=70, state='readonly').pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(select_frame, text="选择...", command=self.on_select).pack(side=tk.LEFT, padx=5, pady=5)
        
        # File list (Treeview)
        self.file_tree = ttk.Treeview(self, columns=("文件名", "类型", "上传日期"), show="headings")
        self.file_tree.heading("文件名", text="文件名")
        self.file_tree.heading("类型", text="类型")
        self.file_tree.heading("上传日期", text="上传日期")
        self.file_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
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
            # 更新界面显示
            self.display_file_info(file_info)
            
            # 准备与 LLM 交互
            self.prepare_for_llm_interaction(file_info)
        else:
            messagebox.showerror("错误", "未找到文件")
    
    def display_file_info(self, file_info):
        """Display file information in the UI."""
        self.file_name_var.set(file_info["original_name"])
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, file_info["content"])
        self.metadata_text.delete(1.0, tk.END)
        self.metadata_text.insert(tk.END, file_info["metadata"])
    
    def prepare_for_llm_interaction(self, file_info):
        """Prepare file information for future LLM interaction."""
        if self.app.llm_processor:
            # 调用 LLM 处理内容
            llm_response = self.call_llm(file_info["content"], file_info["metadata"])
            
            # 将 LLM 解析结果保存到 metadata 中
            if llm_response:
                file_info["metadata"] = llm_response
                self.app.db_manager.update_file(file_info["id"], file_info["content"], file_info["metadata"])
                messagebox.showinfo("成功", "LLM 解析结果已保存")
        else:
            messagebox.showwarning("警告", "未初始化 LLM 处理器")
    
    def call_llm(self, content, metadata):
        """Simulate calling an LLM for content analysis."""
        # 这里是模拟的 LLM 调用逻辑
        print("Sending content and metadata to LLM...")
        print(f"Content: {content}")
        print(f"Metadata: {metadata}")
        
        # 模拟 LLM 返回的解析结果
        llm_response = "LLM analysis result: This is a sample response."
        return llm_response
