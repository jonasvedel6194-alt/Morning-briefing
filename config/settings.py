import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent

def load_yaml(filename):
    with open(BASE_DIR / "config" / filename) as f:
        return yaml.safe_load(f)

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TOPICS = load_yaml("topics.yaml")["topics"]
SOURCES = load_yaml("sources.yaml")["sources"]
LOOKBACK_HOURS = 26
CLAUDE_MODEL = "claude-sonnet-4-20250514"
OUTPUT_FILE = BASE_DIR / "docs" / "index.html"
