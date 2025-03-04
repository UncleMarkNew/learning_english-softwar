import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json

class LearnTab(ttk.Frame):
    """Learning assistant tab with various learning tools."""
    
    def __init__(self, parent, main_window):
        """Initialize the learning tab."""
        super().__init__(parent)
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the learning tab UI."""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)
        
        # Left panel - Tools
        tools_frame = ttk.LabelFrame(self, text="学习工具", padding="10")
        tools_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)
        
        # Tool buttons
        ttk.Button(
            tools_frame,
            text="分析难度级别",
            command=self.analyze_difficulty,
            style="Modern.TButton"
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            tools_frame,
            text="生成练习题",
            command=self.generate_quiz,
            style="Modern.TButton"
        ).pack(fill=tk.X, pady=5)
        
        ttk.Button(
            tools_frame,
            text="语法解析",
            command=self.explain_grammar,
            style="Modern.TButton"
        ).pack(fill=tk.X, pady=5)
        
        # Grammar point entry
        ttk.Label(tools_frame, text="特定语法点:").pack(fill=tk.X, pady=(10, 0))
        self.grammar_point = ttk.Entry(tools_frame)
        self.grammar_point.pack(fill=tk.X, pady=5)
        
        # Right panel - Content
        content_frame = ttk.Frame(self)
        content_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # Text input area
        input_frame = ttk.LabelFrame(content_frame, text="输入文本", padding="5")
        input_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame, 
            height=10,
            wrap=tk.WORD,
            font=('Segoe UI', 10)
        )
        self.input_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Results area
        results_frame = ttk.LabelFrame(content_frame, text="分析结果", padding="5")
        results_frame.grid(row=1, column=0, sticky="nsew")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 10)
        )
        self.results_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    
    def analyze_difficulty(self):
        """Analyze the difficulty level of the input text."""
        content = self.input_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "请先输入要分析的文本")
            return
            
        if not self.main_window.llm_processor:
            messagebox.showerror("错误", "LLM处理器未初始化")
            return
            
        try:
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", "分析中...\n")
            self.update()
            
            result = self.main_window.llm_processor.analyze_difficulty(content)
            
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"分析过程中出错: {str(e)}")
    
    def generate_quiz(self):
        """Generate quiz questions based on the input text."""
        content = self.input_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "请先输入要生成练习题的文本")
            return
            
        if not self.main_window.llm_processor:
            messagebox.showerror("错误", "LLM处理器未初始化")
            return
            
        try:
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", "生成练习题中...\n")
            self.update()
            
            result = self.main_window.llm_processor.generate_quiz(content)
            
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"生成练习题时出错: {str(e)}")
    
    def explain_grammar(self):
        """Explain grammar points in the input text."""
        content = self.input_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "请先输入要分析语法的文本")
            return
            
        if not self.main_window.llm_processor:
            messagebox.showerror("错误", "LLM处理器未初始化")
            return
            
        try:
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", "分析语法中...\n")
            self.update()
            
            specific_point = self.grammar_point.get().strip()
            result = self.main_window.llm_processor.explain_grammar(
                content,
                specific_point if specific_point else None
            )
            
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", result)
            
        except Exception as e:
            messagebox.showerror("错误", f"语法分析时出错: {str(e)}")
