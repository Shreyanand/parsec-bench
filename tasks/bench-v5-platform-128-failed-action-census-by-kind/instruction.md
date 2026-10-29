I'm putting together the weekly reliability note for the Babylon cluster `kite`, covering
lifecycle actions that finished between 2026-10-05 and 2026-10-11 inclusive (UTC).

I need:
- how many lifecycle actions failed that week, split by kind (provision, start, stop,
  destroy),
- how many distinct labs those failures hit, and
- which of those labs are still broken, meaning nothing of the same kind has succeeded
  for them since.

Only that week, and only `kite`.
