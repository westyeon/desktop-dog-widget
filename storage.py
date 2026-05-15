import json, os

DATA_DIR      = os.path.join(os.path.dirname(__file__), "data")
TODOS_FILE    = os.path.join(DATA_DIR, "todos.json")
CONFIG_FILE   = os.path.join(DATA_DIR, "config.json")
SCHEDULE_FILE = os.path.join(DATA_DIR, "schedules.json")

DEFAULT_CONFIG = {"moving": True}
os.makedirs(DATA_DIR, exist_ok=True)

def load_todos():
    if not os.path.exists(TODOS_FILE): return []
    with open(TODOS_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_todos(todos):
    with open(TODOS_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)

def load_config():
    if not os.path.exists(CONFIG_FILE): return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_schedules():
    if not os.path.exists(SCHEDULE_FILE): return []
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f: return json.load(f)

def save_schedules(schedules):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)