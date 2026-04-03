from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[2]
STATE_FILENAME = "state.json"
STATE_FILE = PROJECT_DIR / STATE_FILENAME

APP_TITLE = "나만의 퀴즈 게임"

SEPARATOR_LENGTH = 40
PRIMARY_SEPARATOR = "=" * SEPARATOR_LENGTH
SECONDARY_SEPARATOR = "-" * SEPARATOR_LENGTH
DISPLAY_INDEX_START = 1

CHOICE_COUNT = 4
MIN_ANSWER = 1
MAX_ANSWER = 4
MINIMUM_SCORE = 0
INITIAL_CORRECT_COUNT = 0
INITIAL_HINT_USED_COUNT = 0
STATE_JSON_INDENT = 2
STATE_JSON_ENSURE_ASCII = False

MENU_PLAY = 1
MENU_ADD = 2
MENU_LIST = 3
MENU_DELETE = 4
MENU_SCORE = 5
MENU_EXIT = 6
MENU_MIN_CHOICE = MENU_PLAY
MENU_MAX_CHOICE_WITH_DELETE = MENU_EXIT
MENU_MAX_CHOICE_WITHOUT_DELETE = MENU_SCORE

ENABLE_DELETE_MENU = True

MENU_LINES_WITH_DELETE = (
    f"{MENU_PLAY}. 퀴즈 풀기",
    f"{MENU_ADD}. 퀴즈 추가",
    f"{MENU_LIST}. 퀴즈 목록",
    f"{MENU_DELETE}. 퀴즈 삭제",
    f"{MENU_SCORE}. 점수 확인",
    f"{MENU_EXIT}. 종료",
)

MENU_LINES_WITHOUT_DELETE = (
    f"{MENU_PLAY}. 퀴즈 풀기",
    f"{MENU_ADD}. 퀴즈 추가",
    f"{MENU_LIST}. 퀴즈 목록",
    f"{MENU_DELETE}. 점수 확인",
    f"{MENU_SCORE}. 종료",
)

SCORE_PER_CORRECT = 10
HINT_PENALTY = 2

STATE_ENCODING = "utf-8"
FILE_READ_MODE = "r"
FILE_WRITE_MODE = "w"
DATETIME_TIMESPEC = "seconds"
EMPTY_TEXT = ""

STATE_KEY_QUIZZES = "quizzes"
STATE_KEY_BEST_SCORE = "best_score"
STATE_KEY_HISTORY = "history"

QUIZ_FIELD_QUESTION = "question"
QUIZ_FIELD_CHOICES = "choices"
QUIZ_FIELD_ANSWER = "answer"
QUIZ_FIELD_HINT = "hint"

HISTORY_FIELD_PLAYED_AT = "played_at"
HISTORY_FIELD_TOTAL_QUESTIONS = "total_questions"
HISTORY_FIELD_CORRECT_COUNT = "correct_count"
HISTORY_FIELD_SCORE = "score"
HISTORY_FIELD_HINT_USED_COUNT = "hint_used_count"

YES_TOKENS = {"y", "yes"}
NO_TOKENS = {"n", "no"}
HINT_TOKENS = {"h", "hint"}
HINT_COMMAND_VALUE = "hint"

PROMPT_MENU_CHOICE = "선택: "
PROMPT_ENTER_QUESTION = "문제를 입력하세요: "
PROMPT_ENTER_CHOICE_TEMPLATE = "선택지 {index}번을 입력하세요: "
PROMPT_ENTER_ANSWER_TEMPLATE = "정답 번호를 입력하세요({min_answer}-{max_answer}): "
PROMPT_ENTER_HINT = "힌트를 입력하세요: "
PROMPT_ADD_HINT_CONFIRM = "힌트를 추가하시겠습니까? (y/n): "
PROMPT_ANSWER = "정답 번호를 입력하세요: "
PROMPT_QUESTION_COUNT_TEMPLATE = "몇 문제를 풀겠습니까? (1-{count}): "
PROMPT_DELETE_INDEX_TEMPLATE = "삭제할 퀴즈 번호를 입력하세요 (1-{count}): "
PROMPT_DELETE_CONFIRM = "정말 삭제하시겠습니까? (y/n): "

ERROR_PREFIX = "[오류] "
ERROR_EMPTY_INPUT = "빈 입력은 허용되지 않습니다."
ERROR_ENTER_NUMBER = "숫자를 입력해주세요."
ERROR_RANGE_TEMPLATE = "{min_value}부터 {max_value} 사이의 숫자를 입력해주세요."
ERROR_YES_NO_INPUT = "y/yes 또는 n/no로 입력해주세요."
ERROR_ANSWER_OR_HINT_INPUT = "정답 번호 또는 h/hint를 입력해주세요."
ERROR_NO_HINT_FOR_QUESTION = "이 문제에는 힌트가 없습니다."
ERROR_HINT_ALREADY_USED = "이 문제의 힌트는 이미 사용했습니다."
ERROR_WRONG_ANSWER_TEMPLATE = "오답입니다. 정답은 {answer}번 ({correct_text})입니다."
ERROR_STATE_CORRUPTED = "저장 파일이 손상되어 기본 데이터로 복구합니다."
ERROR_STATE_READ = "저장 파일을 읽는 중 오류가 발생해 기본 데이터로 시작합니다."
ERROR_STATE_SAVE = "저장 중 오류가 발생했지만 프로그램은 안전하게 계속 진행합니다."

MESSAGE_NO_QUIZZES = "등록된 퀴즈가 없습니다."
MESSAGE_NO_BEST_SCORE = "아직 퀴즈를 시작하지 않았습니다."
MESSAGE_HINT_INSTRUCTION = "힌트를 보려면 h 또는 hint를 입력하세요."
MESSAGE_STATE_FILE_MISSING = "저장 파일이 없어 기본 데이터로 시작합니다."
MESSAGE_PROGRAM_EXIT = "프로그램을 종료합니다."
MESSAGE_INTERRUPTED_EXIT = "\n입력이 중단되어 저장 후 안전하게 종료합니다."
MESSAGE_HINT_TEMPLATE = "힌트: {hint}"
MESSAGE_CORRECT_ANSWER = "정답입니다."
MESSAGE_BEST_SCORE_UPDATED = "최고 점수가 갱신되었습니다."
MESSAGE_QUIZ_ADDED = "퀴즈가 추가되었습니다."
MESSAGE_NO_QUIZZES_TO_DELETE = "삭제할 퀴즈가 없습니다."
MESSAGE_DELETE_CANCELLED = "삭제를 취소했습니다."
MESSAGE_DELETE_SUCCESS_TEMPLATE = "'{question}' 퀴즈를 삭제했습니다."

TITLE_QUIZ_LIST = "퀴즈 목록"
TITLE_RESULT = "결과"
QUESTION_HEADER_TEMPLATE = "[문제 {index}/{total}] {question}"
QUIZ_LIST_ITEM_TEMPLATE = "{index}. {question}"
QUIZ_LIST_CHOICE_TEMPLATE = "   {choice_index}) {choice}"
QUESTION_CHOICE_TEMPLATE = "{choice_index}. {choice}"
BEST_SCORE_TEMPLATE = "최고 점수: {best_score}점"
RESULT_CORRECT_TEMPLATE = "맞힌 문제 수: {correct_count}/{total_questions}"
RESULT_SCORE_TEMPLATE = "점수: {score}"
RESULT_HINT_USED_TEMPLATE = "힌트 사용 수: {hint_used_count}"

ERROR_QUESTION_MUST_BE_STRING = "question must be a string"
ERROR_QUESTION_MUST_NOT_BE_EMPTY = "question must not be empty"
ERROR_CHOICES_LENGTH_TEMPLATE = "choices must be a list of {choice_count} items"
ERROR_CHOICE_MUST_BE_STRING = "choice must be a string"
ERROR_CHOICE_MUST_NOT_BE_EMPTY = "choice must not be empty"
ERROR_ANSWER_MUST_BE_INTEGER = "answer must be an integer"
ERROR_ANSWER_RANGE_TEMPLATE = "answer must be between {min_answer} and {max_answer}"
ERROR_HINT_MUST_BE_STRING_OR_NONE = "hint must be a string or None"

ERROR_INVALID_JSON_STATE = "Invalid JSON state file"
ERROR_INVALID_STATE_SCHEMA = "Invalid state schema"
ERROR_BEST_SCORE_MUST_BE_INTEGER_OR_NONE = "best_score must be an integer or None"
ERROR_QUIZ_MUST_BE_INSTANCE = "quiz must be a Quiz instance"
ERROR_STATE_MUST_BE_DICTIONARY = "state must be a dictionary"
ERROR_STATE_MUST_INCLUDE_QUIZZES = "state must include quizzes list"
ERROR_STATE_MUST_INCLUDE_BEST_SCORE = "state must include best_score"
ERROR_HISTORY_MUST_BE_LIST = "history must be a list"
ERROR_QUIZ_ITEM_MUST_BE_DICTIONARY = "quiz item must be a dictionary"
ERROR_QUESTION_MUST_BE_NON_EMPTY_STRING = "question must be a non-empty string"
ERROR_CHOICE_MUST_BE_NON_EMPTY_STRING = "choice must be a non-empty string"
ERROR_HINT_MUST_BE_NON_EMPTY_STRING = "hint must be a non-empty string if provided"
ERROR_HISTORY_ITEM_MUST_BE_DICTIONARY = "history item must be a dictionary"
ERROR_PLAYED_AT_MUST_BE_NON_EMPTY_STRING = "played_at must be a non-empty string"
ERROR_NON_NEGATIVE_INTEGER_TEMPLATE = "{key} must be a non-negative integer"
ERROR_CORRECT_COUNT_EXCEEDS_TOTAL = "correct_count must not exceed total_questions"
ERROR_HINT_USED_COUNT_EXCEEDS_TOTAL = "hint_used_count must not exceed total_questions"

DEFAULT_QUIZ_DATA = (
    {
        QUIZ_FIELD_QUESTION: "Python의 창시자는?",
        QUIZ_FIELD_CHOICES: [
            "Guido van Rossum",
            "Linus Torvalds",
            "Bjarne Stroustrup",
            "James Gosling",
        ],
        QUIZ_FIELD_ANSWER: 1,
        QUIZ_FIELD_HINT: "이름이 Guido로 시작합니다.",
    },
    {
        QUIZ_FIELD_QUESTION: "리스트를 만드는 기호는?",
        QUIZ_FIELD_CHOICES: ["()", "[]", "{}", "<>"],
        QUIZ_FIELD_ANSWER: 2,
        QUIZ_FIELD_HINT: "대괄호를 사용합니다.",
    },
    {
        QUIZ_FIELD_QUESTION: "함수를 정의할 때 사용하는 키워드는?",
        QUIZ_FIELD_CHOICES: ["for", "def", "class", "return"],
        QUIZ_FIELD_ANSWER: 2,
        QUIZ_FIELD_HINT: "d로 시작하는 키워드입니다.",
    },
    {
        QUIZ_FIELD_QUESTION: "조건 분기에서 사용할 수 있는 키워드는?",
        QUIZ_FIELD_CHOICES: ["elif", "import", "break", "pass"],
        QUIZ_FIELD_ANSWER: 1,
        QUIZ_FIELD_HINT: "if와 else 사이에서 자주 씁니다.",
    },
    {
        QUIZ_FIELD_QUESTION: "반복문에서 즉시 탈출할 때 주로 사용하는 키워드는?",
        QUIZ_FIELD_CHOICES: ["continue", "return", "break", "yield"],
        QUIZ_FIELD_ANSWER: 3,
        QUIZ_FIELD_HINT: "반복을 끊는 의미의 키워드입니다.",
    },
)

