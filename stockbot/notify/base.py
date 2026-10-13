"""알림 채널 공통 인터페이스."""
from abc import ABC, abstractmethod


class Notifier(ABC):
    name: str = "base"

    @abstractmethod
    def send(self, message: str) -> bool:
        """메시지를 보내고 성공 여부를 반환한다. 예외를 던지지 않고 False로 처리한다."""
        raise NotImplementedError
