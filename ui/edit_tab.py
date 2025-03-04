import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re
from file_utils import FileUtils
import os

class EditTab(ttk.Frame):
    """Tab for editing files in the system."""
    
    def __init__(self, parent, app):
        """Initialize the edit tab."""
        super().__init__(parent)
        self.app = app
        self.edit_file_id = None
        self.current_content = None  # 存储完整内容
        self.current_segments = []   # 存储分段后的内容
        self.current_segment_index = 0  # 当前显示的段落索引
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the edit tab UI."""
        # File selection area
        select_frame = ttk.LabelFrame(self, text="选择要修改的文件")
        select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 文件信息显示
        info_frame = ttk.Frame(select_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text="文件名：").pack(side=tk.LEFT)
        self.edit_file_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.edit_file_var, width=50, state='readonly').pack(side=tk.LEFT, padx=5)
        ttk.Button(info_frame, text="选择...", command=self.select_file_to_edit).pack(side=tk.LEFT, padx=5)
        
        # 文件类型和编码信息
        type_frame = ttk.Frame(select_frame)
        type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(type_frame, text="文件类型：").pack(side=tk.LEFT)
        self.filetype_var = tk.StringVar()
        ttk.Entry(type_frame, textvariable=self.filetype_var, width=20, state='readonly').pack(side=tk.LEFT, padx=5)
        
        ttk.Label(type_frame, text="编码：").pack(side=tk.LEFT)
        self.encoding_var = tk.StringVar()
        ttk.Entry(type_frame, textvariable=self.encoding_var, width=20, state='readonly').pack(side=tk.LEFT, padx=5)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(nav_frame, text="上一段", command=self.prev_segment).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="下一段", command=self.next_segment).pack(side=tk.LEFT, padx=5)
        
        self.segment_info = ttk.Label(nav_frame, text="")
        self.segment_info.pack(side=tk.LEFT, padx=5)
        
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
    
    def smart_split_content(self, content):
        """智能分段内容"""
        if not content:
            return []
            
        # 首先按空行分段
        segments = re.split(r'\n\s*\n', content)
        
        # 如果段落太长，进一步分割
        MAX_SEGMENT_LENGTH = 2000
        final_segments = []
        
        for segment in segments:
            if len(segment) > MAX_SEGMENT_LENGTH:
                # 按句子分割长段落
                sentences = re.split(r'([.!?。！？]\s*)', segment)
                current_segment = ""
                
                for i in range(0, len(sentences), 2):
                    sentence = sentences[i]
                    # 添加标点符号（如果有）
                    if i + 1 < len(sentences):
                        sentence += sentences[i + 1]
                        
                    if len(current_segment) + len(sentence) > MAX_SEGMENT_LENGTH:
                        if current_segment:
                            final_segments.append(current_segment)
                        current_segment = sentence
                    else:
                        current_segment += sentence
                
                if current_segment:
                    final_segments.append(current_segment)
            else:
                final_segments.append(segment)
        
        return final_segments
    
    def display_current_segment(self):
        """显示当前段落"""
        if not self.current_segments:
            return
            
        self.edit_content_text.delete(1.0, tk.END)
        self.edit_content_text.insert(tk.END, self.current_segments[self.current_segment_index])
        
        # 更新段落信息
        total_segments = len(self.current_segments)
        self.segment_info.config(text=f"第 {self.current_segment_index + 1} 段，共 {total_segments} 段")
    
    def prev_segment(self):
        """显示上一段"""
        if self.current_segment_index > 0:
            # 保存当前段落的修改
            self.current_segments[self.current_segment_index] = self.edit_content_text.get(1.0, tk.END).rstrip()
            self.current_segment_index -= 1
            self.display_current_segment()
    
    def next_segment(self):
        """显示下一段"""
        if self.current_segments and self.current_segment_index < len(self.current_segments) - 1:
            # 保存当前段落的修改
            self.current_segments[self.current_segment_index] = self.edit_content_text.get(1.0, tk.END).rstrip()
            self.current_segment_index += 1
            self.display_current_segment()
    
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
        
        def on_select():
            selection = file_tree.selection()
            if not selection:
                messagebox.showerror("错误", "请选择一个文件")
                return
                
            file_id = selection[0]
            result = self.app.db_manager.get_file_for_query(file_id)  # 使用 get_file_for_query 替代 get_file_for_edit
            if result:
                try:
                    # 更新文件信息
                    self.edit_file_var.set(result["original_name"])
                    file_type, file_size = os.path.splitext(result["original_name"])[1], os.path.getsize(result["stored_path"])
                    self.filetype_var.set(f"{file_type} ({file_size} 字节)")
                    
                    # 使用 FileUtils 预览文件内容
                    encoding = FileUtils.preview_file(result["stored_path"], self.edit_content_text)
                    self.encoding_var.set(encoding or "未知")
                    
                    # 获取文件内容并分段
                    self.current_content = self.edit_content_text.get(1.0, tk.END).strip()
                    self.current_segments = self.smart_split_content(self.current_content)
                    self.current_segment_index = 0
                    
                    # 显示第一段
                    if self.current_segments:
                        self.display_current_segment()
                    
                    # 显示元数据
                    self.edit_metadata_text.delete(1.0, tk.END)
                    if result["metadata"]:
                        self.edit_metadata_text.insert(tk.END, result["metadata"])
                    
                    # 保存文件ID
                    self.edit_file_id = file_id
                    select_dialog.destroy()
                    
                except Exception as e:
                    messagebox.showerror("错误", f"加载文件时出错：{str(e)}")
            else:
                messagebox.showerror("错误", "无法加载选中的文件")
        
        # Add select button
        ttk.Button(select_dialog, text="选择", command=on_select).pack(pady=5)
    
    def save_edit(self):
        """Save the edited content back to the file."""
        if not self.edit_file_id:
            messagebox.showerror("错误", "请先选择要编辑的文件")
            return
            
        try:
            # 保存当前段落的修改
            if self.current_segments:
                self.current_segments[self.current_segment_index] = self.edit_content_text.get(1.0, tk.END).rstrip()
                
                # 合并所有段落
                content = "\n\n".join(self.current_segments)
            else:
                content = self.edit_content_text.get(1.0, tk.END).strip()
                
            metadata = self.edit_metadata_text.get(1.0, tk.END).strip()
            
            # 更新数据库
            self.app.db_manager.update_file(self.edit_file_id, content, metadata)
            messagebox.showinfo("成功", "文件修改已保存")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存修改时出错：{str(e)}")
