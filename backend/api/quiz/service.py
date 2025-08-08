# Re-export quiz services from learning module for consistency
from api.learning.service import QuizService

__all__ = ['QuizService'] 