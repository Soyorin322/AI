from uuid import uuid4

from ai_friend.character.interfaces import CharacterProvider
from ai_friend.core.models import Message
from ai_friend.knowledge.interfaces import KnowledgeStore
from ai_friend.llm.interfaces import LLMProvider
from ai_friend.llm.models import LLMRequest, LLMResponse
from ai_friend.memory.interfaces import MemoryStore
from ai_friend.memory.models import MemoryRecord, MemoryType
from ai_friend.perception.models import PerceptionEvent
from ai_friend.runtime.context import RuntimeContext
from ai_friend.runtime.session import RuntimeSession
from ai_friend.skills.interfaces import SkillRegistry


class RuntimeOrchestrator:
    """Coordinates abstractions; it owns the application flow."""

    def __init__(
        self,
        character: CharacterProvider,
        knowledge: KnowledgeStore,
        memory: MemoryStore,
        skills: SkillRegistry,
        llm: LLMProvider,
    ) -> None:
        self.character = character
        self._knowledge = knowledge
        self._memory = memory
        self._skills = skills
        self._llm = llm
        self.session = RuntimeSession()

    def process_text(self, text: str) -> LLMResponse:
        return self._process(text, None)

    def process_event(self, event: PerceptionEvent) -> LLMResponse:
        text = str(event.payload)
        return self._process(text, event)

    def _process(self, text: str, event: PerceptionEvent | None) -> LLMResponse:
        self.session.append(Message(role="user", content=text))
        context = RuntimeContext(
            character=self.character.profile(),
            knowledge=tuple(self._knowledge.search(text)),
            memories=tuple(self._memory.search(text)),
            skills=tuple(self._skills.discover()),
            perception=event,
        )
        response = self._llm.generate(LLMRequest(input_text=text, context=context))
        self.session.append(Message(role="assistant", content=response.content))
        self._memory.add(
            MemoryRecord(id=str(uuid4()), content=text, metadata={"source": "interaction"}, kind=MemoryType.EPISODIC)
        )
        return response

