
import secrets
import string
from typing import List


class PasswordMaker:
    @staticmethod
    def make_random_password(length: int = 10,
                             allowed_chars: str = None) -> str:
        """
        Generate a random password with the given length and allowed_chars.
        If allowed_chars is not specified, use a default set of characters.
        """
        # Use a default set of allowed characters if none is specified
        if not allowed_chars:
            allowed_chars = 'abcdefghjkmnpqrstuvwxyz' \
                            'ABCDEFGHJKLMNPQRSTUVWXYZ' \
                            '1234567890' \
                            '!@.#'
            
        token_length = (length * 3 + 1) // 4  # The token length must be multiple of 4

        return secrets.token_urlsafe(token_length).rstrip('=')[:length]


class PasswordStrength:
    """
    检查密码强度
    """
    def __init__(self, words_path):
        with open(words_path) as f:
            # 读取并存储弱密码库
            self.word_set = set(line.strip() for line in f)

    def is_weak_password(self, pw_str):
        """
        检测密码是否在弱密码库中
        """
        return pw_str in self.word_set or \
               pw_str.lower() in self.word_set or \
               pw_str.upper() in self.word_set or \
               pw_str.title() in self.word_set

    def password_strength(self, pw_str):
        """
        根据密码复杂度分类
        """
        if len(pw_str) < 8 or self.is_weak_password(pw_str):
            # 如果密码少于8个字符或者在弱密码库中出现，返回WEAK
            return 'WEAK'
        
        char_classes = [string.ascii_lowercase, string.ascii_uppercase, string.digits, string.punctuation]
        strength_score = sum(any(ch in char_class for ch in pw_str) for char_class in char_classes)
        # 计算密码中包含的不同字符类别数量
        
        if len(pw_str) >= 12 and strength_score == 4:
            # 如果密码长度大于等于12并且包含所有四种字符类别，返回STRONG
            return 'STRONG'
        else:
            # 其余情况视为MEDIUM
            return 'MEDIUM'