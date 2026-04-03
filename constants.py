from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
STATE_FILE = PROJECT_DIR / "state.json"

APP_TITLE = "나만의 퀴즈 게임"

CHOICE_COUNT = 4
MIN_ANSWER = 1
MAX_ANSWER = 4

MENU_PLAY = 1
MENU_ADD = 2
MENU_LIST = 3
MENU_DELETE = 4
MENU_SCORE = 5
MENU_EXIT = 6

ENABLE_DELETE_MENU = True

SCORE_PER_CORRECT = 10
HINT_PENALTY = 2

STATE_ENCODING = "utf-8"

YES_TOKENS = {"y", "yes"}
NO_TOKENS = {"n", "no"}
HINT_TOKENS = {"h", "hint"}

