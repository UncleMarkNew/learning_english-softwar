import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class EditTab(ttk.Frame):
    """Tab for editing files in the system."""
    
    def __init__(self, parent, app):
        """Initialize the edit tab."""
        super().__init__(parent)
        self.app = app
        self.edit_file_id = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the edit tab UI."""
        # File selection area
        select_frame = ttk.LabelFrame(self, text="选择要修改的文件")
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.edit_file_var = tk.StringVar()
        ttk.Entry(select_frame, textvariable=self.edit_file_var, width=70, state='readonly').pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(select_frame, text="选择...", command=self.select_file_to_edit).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Edit area
        edit_content_frame = ttk.LabelFrame(self, text="编辑文件内容")
        edit_content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.edit_content_text = scrolledtext.ScrolledText(edit_content_frame, width=80, height=20)
        self.edit_content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Metadata edit area
        metadata_frame = ttk.LabelFrame(self, text="编辑元数据")
        metadata_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.edit_metadata_text = scrolledtext.ScrolledText(metadata_frame, width=80, height=5)
        self.edit_metadata_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Save button
        save_button = ttk.Button(self, text="保存修改", command=self.save_edit)
        save_button.pack(pady=10)
    
    def select_file_to_edit(self):
        """Open dialog to select a file for editing."""
        # Create file selection dialog
        select_dialog = tk.Toplevel(self.app.root)
        select_dialog.title("选择文件")
        select_dialog.geometry("600x400")
        select_dialog.transient(self.app.root)
        select_dialog.grab_set()
        
        # Create file list
        columns = ('文件名', '类型', '上传日期')
        file_tree = ttk.Treeview(select_dialog, columns=columns, show='headings')
        
        for col in columns:
            file_tree.heading(col, text=col)
            file_tree.column(col, width=100)
        
        yscroll = ttk.Scrollbar(select_dialog, orient=tk.VERTICAL, command=file_tree.yview)
        file_tree.configure(yscrollcommand=yscroll.set)
        
        file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load file list
        files = self.app.db_manager.get_files_for_selection()
        for file in files:
            file_id, name, file_type, upload_date = file
            file_tree.insert('', tk.END, iid=file_id, values=(name, file_type, upload_date))
        
        # Confirm button callback
        def on_select():
            selection = file_tree.selection()
            if not selection:
                messagebox.showerror("错误", "请选择一个文件")
                return
                
            file_id = selection[0]
            
            result = self.app.db_manager.get_file_for_edit(file_id)
            if result:
                name, content, metadata = result
                
                self.edit_file_id = file_id
                self.edit_file_var.set(name)
                
                self.edit_content_text.delete(1.0, tk.END)
                self.edit_content_text.insert(tk.END, content or "")
                
                self.edit_metadata_text.delete(1.0, tk.END)
                self.edit_metadata_text.insert(tk.END, metadata or "")
                
                select_dialog.destroy()
        
        # Add confirm and cancel buttons
        button_frame = ttk.Frame(select_dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="确定", command=on_select).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=select_dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def save_edit(self):
        """Save edited file content and metadata."""
        if not self.edit_file_id:
            messagebox.showerror("错误", "请先选择一个文件")
            return
            
        try:
            # Get edited content and metadata
            content = self.edit_content_text.get(1.0, tk.END)
            metadata = self.edit_metadata_text.get(1.0, tk.END)
            
            # Update database
            self.app.db_manager.update_file(self.edit_file_id, content, metadata)
            
            # Update status bar
            self.app.set_status(f"文件 '{self.edit_file_var.get()}' 修改成功")
            
            # Clear edit area
            self.edit_file_id = None
            self.edit_file_var.set("")
            self.edit_content_text.delete(1.0, tk.END)
            self.edit_metadata_text.delete(1.0, tk.END)
            
            messagebox.showinfo("成功", "文件修改保存成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存文件时出错: {e}")
    
    def clear(self):
        """Clear all fields in the edit tab."""
        self.edit_file_id = None
        self.edit_file_var.set("")
        self.edit_content_text.delete(1.0, tk.END)
        self.edit_metadata_text.delete(1.0, tk.END)
