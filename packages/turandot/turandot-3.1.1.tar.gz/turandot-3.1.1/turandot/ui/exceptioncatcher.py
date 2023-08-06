from abc import ABC, abstractmethod
from typing import Optional
import traceback
from functools import wraps

from turandot import Singleton


class CatcherStrategy(ABC):

    @abstractmethod
    def handle_exception(self, e: Exception, tb: str):
        """Forward caught exception to GUI implementation"""
        pass


class ExceptionCatcher(metaclass=Singleton):
    """Catch exception and forward to strategy, needs to be instanced by GUI first!"""

    def __init__(self):
        self.strat: Optional[CatcherStrategy] = None

    def set_strategy(self, strat: CatcherStrategy):
        """Define GUI-specific strategy to output exceptions"""
        self.strat = strat

    def catch(self, e: Exception, tb: str):
        """Pass exception to specific GUI implementation"""
        if self.strat is None:
            raise ValueError("Set exception catcher strategy first!")
        self.strat.handle_exception(e, tb)


def catch_exception(f):
    """Decorator: Catch exception, show on frontend"""
    @wraps(f)
    def catch(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            catcher = ExceptionCatcher()
            catcher.catch(e, tb)
    return catch
