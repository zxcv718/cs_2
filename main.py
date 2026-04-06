from app.config.constants import STATE_FILE
from app.application.quiz_game import QuizGame
from app.console.interface import ConsoleInterface
from app.repository.state_repository import StateRepository


# 프로그램에 필요한 객체를 만들고 실행을 시작하는 함수입니다.
def main() -> None:
    # 화면 입출력을 담당하는 객체입니다.
    console_interface = ConsoleInterface()
    # state.json 파일을 읽고 저장하는 객체입니다.
    state_repository = StateRepository(STATE_FILE)
    # 게임 전체 흐름을 조율하는 객체입니다.
    game = QuizGame(console_interface, state_repository)
    game.run()


# 이 파일을 직접 실행했을 때만 main()을 호출합니다.
if __name__ == "__main__":
    main()
