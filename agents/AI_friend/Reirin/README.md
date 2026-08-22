# Reirin Reconstruction v0.1

This directory is the reconstructed Reirin character instance. It depends on
Aiko's character-agnostic reconstruction contracts; Aiko does not depend on this
directory.

Reirin v0.1 is an evidence-grounded reconstruction made exclusively from the
approved speaker-rechecked Volume 1 and Volume 2 source files. It is not a
conversational runtime, a final Persona schema, or a prose character card.

The canonical v0.1 instance artifact is
`reconstruction/bundle_v0.1.json`, bounded by `reconstruction/manifest.json`.
Run the instance validation from this directory with:

```powershell
python -m pytest
python reconstruction/validate.py
```

