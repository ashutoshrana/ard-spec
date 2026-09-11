# Common Failure Patterns

| Symptom | Root cause | Fix |
|---|---|---|
| CLI reports PASS without schema validation | Missing dependency/schema was treated as successful validation | Strict unavailable validation exits 2 INCOMPLETE; explicit basic mode has a distinct label; subprocess regressions disable site-packages |
| Malformed manifest crashes semantic checks | JSON root/entry types were assumed after parsing | Check objects before field access and stop after schema rejection |
