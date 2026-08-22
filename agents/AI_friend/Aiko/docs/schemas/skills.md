# Skill contracts

Skill ownership is deliberately split:

- `ai_friend.character.CharacterSkillProfile` is persistent character state;
- `ai_friend.character.SkillEvidence` links demonstrated ability to Event/Evidence;
- `ai_friend.skills.CapabilitySkill` is a replaceable technical execution protocol;
- `ai_friend.skills.RuntimeCapability` records current executable availability;
- root `Aiko/skills/` contains reusable human-readable capability resources.

The following are never interchangeable:

```text
canon-supported proficiency
post-canon learned proficiency
runtime technical capability
underlying LLM knowledge
```

Canonical proficiency requires evidence and must remain bounded by what was
demonstrated. Installing a capability pack or using a knowledgeable LLM cannot
rewrite it. Post-canon learning uses a distinct acquisition origin. Task 005 does
not implement real capability packs or a proficiency formula.
