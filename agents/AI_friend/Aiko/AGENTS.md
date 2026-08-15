# Aiko development rules

## Project intent

Aiko (`ai-friend`) is a modular framework for persistent AI characters. The
framework must remain character-agnostic.

## Architectural rules

- Maintain strict subsystem boundaries and prefer dependency inversion.
- Do not couple domain logic to vendor APIs or introduce global mutable state.
- Do not bypass interfaces for convenience.
- Keep Knowledge (available information) separate from Memory (experiences).
- Runtime coordinates modules; modules do not orchestrate each other.
- Prefer simple implementations until real requirements justify complexity.

## Coding rules

- Use Python with type hints and focused modules.
- Document public interfaces.
- Avoid unnecessary dependencies and premature optimization.
- Prefer the standard library when practical.

## Validation

From this directory, run:

```powershell
python -m pytest
"Hello`nexit" | python -m ai_friend
```

