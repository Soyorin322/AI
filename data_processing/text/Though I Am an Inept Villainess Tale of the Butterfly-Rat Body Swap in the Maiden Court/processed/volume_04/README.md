# Volume 04 Story Processing v0.1

Source: `惡女不才_第四卷_純文字版.md`

This directory contains the first story-level processing pass for Volume 4 under `data_processing/text/Readme.md`.

The original novel file is unchanged. Everything here is derived annotation / structured story analysis.

## Pipeline represented

```text
Raw text
→ source/scene spans
→ selected speaker attribution
→ source-grounded observations
→ story Events
→ participants / objective facts
→ chronology
→ fact-level perspective/accessibility
```

This package deliberately stops before Aiko character reconstruction. It does not contain Period Character State, Memory, Development, Character Skill Profile, or Compiled Character State.

## Files

- `manifest_v0.1.json` — source identity, scope, processing status and limitations.
- `speaker_annotations_v0.1.json` — event-relevant dialogue/inner-voice attribution with provenance class; this is not yet an exhaustive line-by-line speaker transcript.
- `observations_v0.1.json` — narrow source-grounded observations.
- `events_v0.1.json` — shared story Events, stored once.
- `timeline_v0.1.json` — narrative chronology independent of character Periods.
- `perspectives_v0.1.json` — fact-level accessibility for relevant characters.

## Important status

This is `v0.1`, an auditable first pass rather than a claim of final annotation accuracy.

Speaker labels inferred from context remain derived annotations. Private thoughts are never treated as automatically known by other characters. When accessibility cannot be established from Volume 4, it remains `UNKNOWN` or `STORY_ONLY` rather than being guessed.

Event boundaries are semantic and may occur multiple times within a chapter. Chapters are used as source locators only.

## Downstream handoff

Conceptually the output available to Aiko is:

```text
StoryEvent
+
PerspectiveReference(target_character)
+
Evidence / source lineage
```

Aiko is responsible for interpreting what these experiences mean to the target character; this directory is responsible only for what happened and who could know what.
