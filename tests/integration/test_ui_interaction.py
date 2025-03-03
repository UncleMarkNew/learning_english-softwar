import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目根目录到 Python 路径，以便导入模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ui.main_window import MainWindow
from services.learning_service import LearningService

class TestUIInteraction(unittest.TestCase):
    def setUp(self):
        # 创建模拟 UI 和服务
        self.learning_service_mock = MagicMock(spec=LearningService)
        
        # 注入模拟服务
        with patch('services.learning_service.LearningService', return_value=self.learning_service_mock):
            self.main_window = MainWindow()
    
    def test_word_display(self):
        """测试单词在UI中的显示"""
        # 设置模拟返回值
        test_word = {
            "id": 1, 
            "text": "hello", 
            "translation": "你好", 
            "difficulty_level": 1,
            "examples": ["Hello, world!", "Hello, how are you?"]
        }
        self.learning_service_mock.get_next_word.return_value = test_word
        
        # 模拟 UI 方法
        self.main_window.display_word = MagicMock()
        
        # 调用显示下一个单词的方法
        self.main_window.show_next_word()
        
        # 验证服务调用
        self.learning_service_mock.get_next_word.assert_called_once()
        
        # 验证 UI 显示
        self.main_window.display_word.assert_called_with(test_word)
    
    def test_answer_submission(self):
        """测试答案提交流程"""
        # 设置模拟返回值
        self.learning_service_mock.process_word_answer.return_value = True
        self.main_window.current_word = {"id": 1, "text": "hello"}
        self.main_window.user_id = 1
        
        # 模拟 UI 方法
        self.main_window.show_result = MagicMock()
        self.main_window.show_next_word = MagicMock()
        
        # 模拟用户提交正确答案
        self.main_window.submit_answer("hello")
        
        # 验证服务调用
        self.learning_service_mock.process_word_answer.assert_called_with(
            user_id=1, word_id=1, is_correct=True
        )
        
        # 验证正确答案的 UI 反馈
        self.main_window.show_result.assert_called_with(True)
        self.main_window.show_next_word.assert_called_once()
        
        # 重设模拟
        self.learning_service_mock.process_word_answer.reset_mock()
        self.main_window.show_result.reset_mock()
        self.main_window.show_next_word.reset_mock()
        
        # 模拟用户提交错误答案
        self.main_window.submit_answer("helo")  # 拼写错误
        
        # 验证服务调用
        self.learning_service_mock.process_word_answer.assert_called_with(
            user_id=1, word_id=1, is_correct=False
        )
        
        # 验证错误答案的 UI 反馈
        self.main_window.show_result.assert_called_with(False)
    
    def test_session_initialization(self):
        """测试学习会话初始化"""
        # 设置模拟返回值
        session_words = [
            {"id": 1, "text": "hello", "translation": "你好"},
            {"id": 2, "text": "goodbye", "translation": "再见"}
        ]
        self.learning_service_mock.generate_learning_session.return_value = session_words
        
        # 模拟 UI 方法
        self.main_window.display_session_info = MagicMock()
        self.main_window.show_next_word = MagicMock()
        
        # 初始化会话
        self.main_window.start_learning_session(user_id=1, review_count=5, new_count=5)
        
        # 验证服务调用
        self.learning_service_mock.generate_learning_session.assert_called_with(1, 5, 5)
        
        # 验证 UI 更新
        self.main_window.display_session_info.assert_called_with(2)  # 总共2个单词
        self.main_window.show_next_word.assert_called_once()
    
    def test_progress_display(self):
        """测试进度显示"""
        # 设置模拟数据
        progress_data = {
            "words_learned": 100,
            "words_mastered": 50,
            "current_streak": 7,
            "longest_streak": 14
        }
        self.learning_service_mock.get_user_statistics.return_value = progress_data
        
        # 模拟 UI 方法
        self.main_window.update_progress_display = MagicMock()
        
        # 显示进度
        self.main_window.show_user_progress(user_id=1)
        
        # 验证服务调用
        self.learning_service_mock.get_user_statistics.assert_called_with(1)
        
        # 验证 UI 更新
        self.main_window.update_progress_display.assert_called_with(progress_data)


if __name__ == "__main__":
    unittest.main()
