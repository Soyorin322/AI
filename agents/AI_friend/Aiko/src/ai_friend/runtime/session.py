from dataclasses import dataclass, field

from ai_friend.core.models import Message


@dataclass(slots=True)
class RuntimeSession:
    messages: list[Message] = field(default_factory=list)

    def append(self, message: Message) -> None:
        self.messages.append(message)

