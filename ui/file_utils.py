import os
import chardet
import tkinter as tk

class FileUtils:
    """工具类，用于处理文件读取和预览"""

    @staticmethod
    def detect_encoding(file_path):
        """检测文件编码"""
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            return result['encoding'], raw_data

    @staticmethod
    def read_file_content(file_path, max_chars=None):
        """读取文件内容，支持自动检测编码"""
        encoding, raw_data = FileUtils.detect_encoding(file_path)
        if not encoding:
            return "无法检测文件编码", None
        
        try:
            content = raw_data.decode(encoding, errors='replace')
            if max_chars:
                content = content[:max_chars]
            return content, encoding
        except:
            return "无法解码文件内容", None

    @staticmethod
    def get_file_info(file_path):
        """获取文件基本信息"""
        file_type = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        return file_type, file_size

    @staticmethod
    def preview_file(file_path, preview_widget, max_chars=5000):
        """预览文件内容并写入到指定的 tk.Text 控件"""
        file_type, file_size = FileUtils.get_file_info(file_path)
        preview_widget.delete(1.0, tk.END)

        # 支持的文件类型
        text_extensions = ['.txt', '.py', '.md', '.csv', '.json', '.xml', '.html', '.css', '.js', '.java', '.c', '.cpp']
        office_extensions = ['.doc', '.docx', '.wps', '.rtf']
        pdf_extensions = ['.pdf']

        if file_type in text_extensions:
            content, encoding = FileUtils.read_file_content(file_path, max_chars)
            preview_widget.insert(tk.END, content)
            return encoding or "未知"

        elif file_type in office_extensions:
            preview_widget.insert(tk.END, f"文件类型: {file_type}\n文件大小: {file_size} 字节\n路径: {file_path}\n\n")
            preview_widget.insert(tk.END, "Word/WPS文档需要安装python-docx或textract库来预览文本内容。\n")
            preview_widget.insert(tk.END, "安装方法: pip install python-docx textract\n\n")
            preview_widget.insert(tk.END, "'''\n# Word文档预览\ntry:\n    import docx\n    doc = docx.Document(file_path)\n    content = '\\n'.join([para.text for para in doc.paragraphs])\n    preview_widget.insert(tk.END, content[:{max_chars}])\nexcept:\n    preview_widget.insert(tk.END, \"无法预览此Word文档\")\n'''")
            return "不适用"

        elif file_type in pdf_extensions:
            preview_widget.insert(tk.END, f"文件类型: {file_type}\n文件大小: {file_size} 字节\n路径: {file_path}\n\n")
            preview_widget.insert(tk.END, "PDF文档需要安装PyPDF2或pdfminer库来预览文本内容。\n")
            preview_widget.insert(tk.END, "安装方法: pip install PyPDF2\n\n")
            preview_widget.insert(tk.END, "'''\n# PDF预览\ntry:\n    import PyPDF2\n    with open(file_path, 'rb') as file:\n        reader = PyPDF2.PdfReader(file)\n        content = ''\n        for i in range(min(5, len(reader.pages))):\n            content += reader.pages[i].extract_text() + '\\n'\n        preview_widget.insert(tk.END, content[:{max_chars}])\nexcept:\n    preview_widget.insert(tk.END, \"无法预览此PDF文档\")\n'''")
            return "不适用"

        else:
            preview_widget.insert(tk.END, f"文件类型: {file_type}\n文件大小: {file_size} 字节\n路径: {file_path}\n\n")
            preview_widget.insert(tk.END, "该文件类型暂不支持预览。")
            return "不适用"
