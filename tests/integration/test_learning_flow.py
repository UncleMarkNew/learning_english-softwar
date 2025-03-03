import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目根目录到 Python 路径，以便导入模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.learning_service import LearningService
from models.user import User
from models.word import Word

class TestLearningFlow(unittest.TestCase):
    def setUp(self):
        # 模拟用户和学习服务
        self.user = User(id=1, username="testuser", email="test@example.com", level=2)
        self.learning_service = LearningService()
    
    @patch('database.db_manager.DatabaseManager')
    def test_word_recommendation(self, mock_db_manager):
        """测试单词推荐流程"""
        # 创建模拟数据库管理器实例
        mock_db_instance = MagicMock()
        mock_db_manager.return_value = mock_db_instance
        
        # 设置模拟数据库返回值
        mock_db_instance.get_words_by_difficulty.return_value = [
            {"id": 1, "text": "apple", "translation": "苹果", "difficulty_level": 2, "examples": "I ate an apple."},
            {"id": 2, "text": "banana", "translation": "香蕉", "difficulty_level": 2, "examples": "I like bananas."}
        ]
        mock_db_instance.get_user_words.return_value = []  # 用户还没学过任何单词
        
        # 获取推荐单词
        recommended_words = self.learning_service.recommend_words_for_user(self.user)
        
        # 验证推荐结果
        self.assertEqual(len(recommended_words), 2)
        self.assertEqual(recommended_words[0]["text"], "apple")
        
        # 验证数据库查询参数
        mock_db_instance.get_words_by_difficulty.assert_called_with(2)
        mock_db_instance.get_user_words.assert_called_with(1)
    
    @patch('database.db_manager.DatabaseManager')
    def test_learning_progress_tracking(self, mock_db_manager):
        """测试学习进度跟踪"""
        # 创建模拟数据库管理器实例
        mock_db_instance = MagicMock()
        mock_db_manager.return_value = mock_db_instance
        
        # 设置模拟返回值
        mock_db_instance.get_user_progress.return_value = {
            "id": 1, "user_id": 1, "word_id": 1, 
            "status": "learning", "attempts": 1, "correct_attempts": 0
        }
        mock_db_instance.update_user_progress.return_value = 1
        
        # 模拟用户回答单词
        result = self.learning_service.process_word_answer(
            user_id=1, word_id=1, is_correct=True
        )
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证数据库操作
        mock_db_instance.get_user_progress.assert_called_with(1, 1)
        mock_db_instance.update_user_progress.assert_called_once()
        
        # 验证正确的更新参数
        call_args = mock_db_instance.update_user_progress.call_args[0]
        self.assertEqual(call_args[0], 1)  # user_id
        self.assertEqual(call_args[1], 1)  # word_id
        self.assertEqual(call_args[2], "learning")  # status
        self.assertEqual(call_args[3], 2)  # attempts (增加了1)
        self.assertEqual(call_args[4], 1)  # correct_attempts (增加了1)
    
    @patch('database.db_manager.DatabaseManager')
    def test_automatic_level_progression(self, mock_db_manager):
        """测试用户等级自动晋升"""
        # 创建模拟数据库管理器实例
        mock_db_instance = MagicMock()
        mock_db_manager.return_value = mock_db_instance
        
        # 设置模拟返回值，模拟用户已掌握足够的单词
        mock_db_instance.get_user.return_value = {
            "id": 1, "username": "testuser", "email": "test@example.com", 
            "level": 1, "created_at": "2025-03-01"
        }
        mock_db_instance.count_user_words_by_status.return_value = 50  # 用户已掌握50个单词
        mock_db_instance.update_user_level.return_value = True
        
        # 检查并更新用户等级
        result = self.learning_service.check_and_update_user_level(1)
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证数据库操作
        mock_db_instance.count_user_words_by_status.assert_called_with(1, "mastered")
        mock_db_instance.update_user_level.assert_called_with(1, 2)  # 提升到下一级
    
    @patch('database.db_manager.DatabaseManager')
    def test_learning_session_generation(self, mock_db_manager):
        """测试学习会话生成"""
        # 创建模拟数据库管理器实例
        mock_db_instance = MagicMock()
        mock_db_manager.return_value = mock_db_instance
        
        # 设置模拟返回值
        mock_db_instance.get_user_words.return_value = [
            {"id": 1, "text": "hello", "translation": "你好", "difficulty_level": 1, "status": "learning"},
            {"id": 2, "text": "goodbye", "translation": "再见", "difficulty_level": 1, "status": "learning"}
        ]
        mock_db_instance.get_words_by_difficulty.return_value = [
            {"id": 3, "text": "apple", "translation": "苹果", "difficulty_level": 1},
            {"id": 4, "text": "banana", "translation": "香蕉", "difficulty_level": 1}
        ]
        
        # 生成学习会话
        session_words = self.learning_service.generate_learning_session(
            user_id=1, 
            review_count=2,
            new_count=2
        )
        
        # 验证会话内容
        self.assertEqual(len(session_words), 4)
        
        # 验证数据库查询
        mock_db_instance.get_user_words.assert_called_with(1, "learning")
        mock_db_instance.get_words_by_difficulty.assert_called_once()


if __name__ == "__main__":
    unittest.main()
