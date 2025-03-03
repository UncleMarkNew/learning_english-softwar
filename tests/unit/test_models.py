import unittest
import sys
import os

# 添加项目根目录到 Python 路径，以便导入模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.word import Word
from models.user import User
from models.progress import UserProgress

class TestWordModel(unittest.TestCase):
    def setUp(self):
        self.word = Word(
            id=1,
            text="hello",
            translation="你好",
            difficulty_level=1,
            examples=["Hello, world!", "Hello, how are you?"]
        )
    
    def test_word_creation(self):
        """测试单词对象是否正确创建"""
        self.assertEqual(self.word.id, 1)
        self.assertEqual(self.word.text, "hello")
        self.assertEqual(self.word.translation, "你好")
        self.assertEqual(self.word.difficulty_level, 1)
        self.assertEqual(len(self.word.examples), 2)
        
    def test_word_difficulty_range(self):
        """测试单词难度级别是否在有效范围内"""
        with self.assertRaises(ValueError):
            Word(id=2, text="test", translation="测试", difficulty_level=0)
        
        with self.assertRaises(ValueError):
            Word(id=3, text="test", translation="测试", difficulty_level=6)
    
    def test_word_representation(self):
        """测试单词的字符串表示"""
        self.assertEqual(str(self.word), "hello (你好)")


class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.user = User(
            id=1,
            username="learner123",
            email="learner@example.com",
            level=2
        )
    
    def test_user_creation(self):
        """测试用户对象是否正确创建"""
        self.assertEqual(self.user.id, 1)
        self.assertEqual(self.user.username, "learner123")
        self.assertEqual(self.user.email, "learner@example.com")
        self.assertEqual(self.user.level, 2)
    
    def test_user_level_range(self):
        """测试用户级别是否在有效范围内"""
        with self.assertRaises(ValueError):
            User(id=2, username="test", email="test@example.com", level=0)
        
        with self.assertRaises(ValueError):
            User(id=3, username="test", email="test@example.com", level=11)
    
    def test_email_validation(self):
        """测试电子邮件验证"""
        with self.assertRaises(ValueError):
            User(id=4, username="test", email="invalid-email", level=1)


class TestUserProgressModel(unittest.TestCase):
    def setUp(self):
        self.progress = UserProgress(
            id=1,
            user_id=1,
            word_id=1,
            status="learning",
            attempts=3,
            correct_attempts=2,
            last_reviewed="2025-03-03"
        )
    
    def test_progress_creation(self):
        """测试进度对象是否正确创建"""
        self.assertEqual(self.progress.id, 1)
        self.assertEqual(self.progress.user_id, 1)
        self.assertEqual(self.progress.word_id, 1)
        self.assertEqual(self.progress.status, "learning")
        self.assertEqual(self.progress.attempts, 3)
        self.assertEqual(self.progress.correct_attempts, 2)
        self.assertEqual(self.progress.last_reviewed, "2025-03-03")
    
    def test_correct_ratio(self):
        """测试正确率计算"""
        self.assertEqual(self.progress.correct_ratio(), 2/3)
    
    def test_status_validation(self):
        """测试状态值验证"""
        valid_statuses = ["new", "learning", "reviewing", "mastered"]
        
        # 测试有效状态
        for status in valid_statuses:
            progress = UserProgress(
                id=1, user_id=1, word_id=1, status=status,
                attempts=1, correct_attempts=1, last_reviewed="2025-03-03"
            )
            self.assertEqual(progress.status, status)
        
        # 测试无效状态
        with self.assertRaises(ValueError):
            UserProgress(
                id=1, user_id=1, word_id=1, status="invalid",
                attempts=1, correct_attempts=1, last_reviewed="2025-03-03"
            )


if __name__ == "__main__":
    unittest.main()
