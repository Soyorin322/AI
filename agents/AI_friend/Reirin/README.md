# Reirin character instance

This directory contains character-specific persistent data produced with the
adjacent Aiko framework. It does not define or modify Aiko's generic contracts.

Reconstruction `v0.1` is deliberately limited to the approved source file
`character_data/Reirin/sources/raw/novel/惡女不才_第一卷_前三章.md`. It is the
first Aiko-compliant reconstruction from that source window, not a complete or
final account of 黃玲琳.

Canonical flow:

```text
approved source -> exact SourceUnit -> Observation -> Event -> Evidence
-> Period Assignment -> Period Character State -> Development -> Compiled State
```

Memory and canonical skill profiles reference the same single-copy Events.
Future source expansion must create a new reconstruction version and must not
silently overwrite this historical version.

Run persisted-data validation from this directory with the Aiko `src` directory
on `PYTHONPATH`:

```powershell
python validation/validate_instance.py
```
