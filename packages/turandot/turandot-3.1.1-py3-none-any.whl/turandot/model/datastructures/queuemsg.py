from typing import Optional
from dataclasses import dataclass
from turandot.model import MessageType


@dataclass
class QueueMessage:
    """Data class for messages to be passed from backend to frontend"""
    type: MessageType
    copy: Optional[tuple] = None
    exception: Optional[Exception] = None
    traceback: Optional[str] = None
    warning: Optional[str] = None
    n_step: Optional[int] = None
    total_steps: Optional[int] = None
    step_desc: Optional[str] = None

    @classmethod
    def startedmsg(cls, total_steps: int):
        """Create message indicating that the conversion process has started"""
        return cls(
            type=MessageType.STARTED,
            total_steps=total_steps
        )

    @classmethod
    def copymsg(cls, v: tuple):
        """Create message indicating that a file has been created (to delete on cleanup"""
        return cls(
            type=MessageType.COPY,
            copy=v
        )

    @classmethod
    def warningmsg(cls, v):
        """Create message indicating that the conversion process emitted a warning"""
        return cls(
            type=MessageType.WARNING,
            warning=v
        )

    @classmethod
    def stepmsg(cls, n_step, total_steps, step_desc):
        """Create message indicating that a mandatory processor has finished"""
        return cls(
            type=MessageType.NEXT_STEP,
            n_step=n_step,
            total_steps=total_steps,
            step_desc=step_desc
        )

    @classmethod
    def exceptionmsg(cls, e, tb):
        """Create message indicating that the conversion process threw an exception"""
        return cls(
            type=MessageType.EXCEPTION,
            exception=e,
            traceback=tb
        )

    @classmethod
    def successmsg(cls):
        """Create message indicating that the conversion process has succeeded"""
        return cls(
            type=MessageType.SUCCESS
        )

    @classmethod
    def deathmsg(cls):
        """Create message indicating that the conversion process has died"""
        return cls(
            type=MessageType.DIED
        )
