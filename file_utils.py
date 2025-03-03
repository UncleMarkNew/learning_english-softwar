import os
import chardet
import tkinter as tk

# 调试信息
print("FileUtils模块已加载 - 替代版本（不使用textract）", flush=True)

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
            # 尝试先使用python-docx（支持.docx格式）
            try:
                import docx
                doc = docx.Document(file_path)
                content = '\n'.join([para.text for para in doc.paragraphs])
                if max_chars and len(content) > max_chars:
                    content = content[:max_chars] + "...(内容已截断)"
                preview_widget.insert(tk.END, content)
                return "Word文档 (docx)"
            except Exception as docx_error:
                # 尝试使用win32com（适用于Windows系统，支持多种Office文档格式）
                try:
                    import win32com.client
                    import os
                    import re
                    
                    # 创建Word应用程序实例
                    word = win32com.client.Dispatch("Word.Application")
                    word.Visible = False
                    
                    # 打开文档
                    doc = word.Documents.Open(os.path.abspath(file_path))
                    
                    # 提取文本
                    content = doc.Content.Text
                    
                    # 关闭文档和Word应用
                    doc.Close(False)
                    word.Quit()
                    
                    # 清理文本（移除多余的换行符）
                    content = re.sub(r'\r+', '\r', content)
                    
                    if max_chars and len(content) > max_chars:
                        content = content[:max_chars] + "...(内容已截断)"
                    
                    preview_widget.insert(tk.END, content)
                    return "Word文档 (win32com)"
                except ImportError:
                    preview_widget.insert(tk.END, f"文件类型: {file_type}\n文件大小: {file_size} 字节\n路径: {file_path}\n\n")
                    preview_widget.insert(tk.END, "需要安装pywin32库来预览此类文档内容。\n")
                    preview_widget.insert(tk.END, "安装方法: pip install pywin32\n")
                    preview_widget.insert(tk.END, f"\n原始错误: {str(docx_error)}")
                    return "不适用"
                except Exception as win32_error:
                    preview_widget.insert(tk.END, f"文件类型: {file_type}\n文件大小: {file_size} 字节\n路径: {file_path}\n\n")
                    preview_widget.insert(tk.END, f"无法使用python-docx预览此文档: {str(docx_error)}\n\n")
                    preview_widget.insert(tk.END, f"同样无法使用win32com预览: {str(win32_error)}")
                    return "不适用"
        
        elif file_type in pdf_extensions:
            # 尝试使用PyPDF2
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    content = ''
                    for i in range(min(5, len(reader.pages))):
                        content += reader.pages[i].extract_text() + '\n'
                    if max_chars and len(content) > max_chars:
                        content = content[:max_chars] + "...(内容已截断)"
                    preview_widget.insert(tk.END, content)
                    return "PDF文档 (PyPDF2)"
            except Exception as pdf_error:
                # 尝试使用pdfminer
                try:
                    from pdfminer.high_level import extract_text
                    content = extract_text(file_path)
                    if max_chars and len(content) > max_chars:
                        content = content[:max_chars] + "...(内容已截断)"
                    preview_widget.insert(tk.END, content)
                    return "PDF文档 (pdfminer)"
                except ImportError:
                    preview_widget.insert(tk.END, f"文件类型: {file_type}\n文件大小: {file_size} 字节\n路径: {file_path}\n\n")
                    preview_widget.insert(tk.END, "需要安装pdfminer.six库来预览此PDF文档内容。\n")
                    preview_widget.insert(tk.END, "安装方法: pip install pdfminer.six\n")
                    preview_widget.insert(tk.END, f"\n原始错误: {str(pdf_error)}")
                    return "不适用"
                except Exception as pdfminer_error:
                    preview_widget.insert(tk.END, f"文件类型: {file_type}\n文件大小: {file_size} 字节\n路径: {file_path}\n\n")
                    preview_widget.insert(tk.END, f"无法使用PyPDF2预览此PDF: {str(pdf_error)}\n\n")
                    preview_widget.insert(tk.END, f"同样无法使用pdfminer预览: {str(pdfminer_error)}")
                    return "不适用"
        
        else:
            preview_widget.insert(tk.END, f"文件类型: {file_type}\n文件大小: {file_size} 字节\n路径: {file_path}\n\n")
            preview_widget.insert(tk.END, "该文件类型暂不支持预览。")
            return "不适用"
