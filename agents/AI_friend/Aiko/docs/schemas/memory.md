# Memory contracts

`ai_friend.memory` owns retained, subjective experience records—not Events.

`MemoryFormationDecision` records a replaceable decision to persist or not persist
an Event. No retention or salience algorithm is mandated. A `persist` decision
must identify a corresponding `MemoryRecord`; `do_not_persist` must not.

`MemoryRecord` references one or more Event IDs and may carry remembered content,
subjective meaning, affective trace, uncertainty, period, accessible fact IDs,
and retrieval metadata. It must never embed the complete objective Event or act
as a second Event store.

`MemoryIndexMetadata` contains retrieval hints such as entities, topics, period,
importance, and relationship relevance. It requires no vector database. Preferred
retrieval depth is `index -> MemoryRecord -> Event -> Observation -> SourceUnit`.
Character-inaccessible or later-only facts must not be inserted into an earlier
memory.
