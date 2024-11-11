from yaml import safe_load, safe_dump
with open("cfg.yaml", "r", encoding="utf-8") as f: CFG = safe_load(f)

EVENTS = CFG["events"]
TRIGGERS = CFG["triggers"]
SIMPLE_UTTERANCE = TRIGGERS["SimpleUtterance"]
DB = CFG["db"]
