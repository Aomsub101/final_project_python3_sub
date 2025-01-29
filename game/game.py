
# ----- Libraries ----- #
import os
import dotenv
import json
import pygame
from enum import Enum
from mistralai import Mistral
import logging
from logging.handlers import RotatingFileHandler
# ----- --------- ----- #

# ----- load environment variables ----- #
dotenv.load_dotenv()
# ----- -------------------------- ----- #

# ----- setup logger ----- #
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
LOG_PATH = os.environ["LOG_PATH"] + "//game.log"
handler = RotatingFileHandler(
    LOG_PATH,
    maxBytes=1_000_000,
    backupCount=5
)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
# ----- ------------ ----- #

# ----- setup MistralAi ----- #
API_KEY = os.environ["MISTRAL_API_KEY"]
MODEL = "mistral-large-latest"
CLIENT = Mistral(api_key=API_KEY)
# ----- ------------------ ----- #

# ----- pygame_init ------ #
pygame.init()
# ----- ----------- ------ #

# ----- Constant ----- #
SURFACE_WIDHT = 1000
SURFACE_HEIGHT = 800
QUESTION_WIDTH = 1000
QUESTION_HEIGHT = 300
RECT_WIDTH = 500
RECT_HEIGHT = 200
# ----- -------- ----- #

# ----- Color ----- #
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0,139,139)
YELLOW = (253, 208, 23)
BLUE = (69,163,229)
LIGHT_PURPLE = (203, 195, 227)
# ------ ---- ----- #

# ----- path ----- #
DATA_PATH = os.environ["DATABASE_PATH"] + "//quizzes_data.json"
PROMPT_PATH = os.environ["DATABASE_PATH"] + "//prompt.txt"
# ----- --------- ----- #

class Player:
    def __init__(self):
        self.name = ""
        self.topic = ""
        self.score = 0

class Quizzes_data:
    def __init__(self) -> None:
        self.my_data = self.get_data()
        self.all_topics = self.my_data["all_topics"]
        self.all_quizzes = self.my_data["all_quizzes"]

    def record_data(self, is_new_quiz: bool, q_idx: int, topic: str, data: dict[str, any]) -> None:
        data["correct_percentage"] = 100 * (data["total_score"] / (5*data["use_count"]))
        if not is_new_quiz:
            if not self.all_quizzes[q_idx]["use_count"] >= 10:
                data["total_score"] += self.all_quizzes[q_idx]["total_score"]
                data["use_count"] = self.all_quizzes[q_idx]["use_count"] + 1
            self.my_data["all_quizzes"][q_idx] = data
            with open(DATA_PATH, "w") as file:
                json.dump(self.my_data, file, indent=4)
        else:
            self.my_data["all_quizzes"].append(data)
            self.my_data["all_topics"].append(topic)
            with open(DATA_PATH, "w") as file:
                json.dump(self.my_data, file, indent=4)

    def get_data(self) -> dict[str, any]:
        with open(DATA_PATH, "r") as file:
            return json.load(file)

class MistralAI:
    def __init__(self) -> None:
        self.model = MODEL
        self.client = CLIENT
        with open(PROMPT_PATH, "r") as file:
            self.prompt = file.read()

    def call(self, topic: str) -> str:
        full_prompt = self.prompt + "\nUSER PROMPT:" + topic
        try:
            response = self.client.chat.complete(
                model = self.model,
                messages = [
                    {
                        "role": "user",
                        "content": full_prompt,
                    },
                ]
            )
            return response.choices[0].message.content
        except Exception as error:
            print(f"Error calling Mistral API: {error}")
            return

class GameStage(Enum):
    NAME = "name"
    TOPIC = "topic"
    GENERATE_QUIZ = "generate_quiz"
    QUIZ = "quiz"
    CORRECT = "correct_answer"
    INCORRECT = "incorrect_answer"
    UPDATE = "update"
    END = "end"

class Gameplay:
    def __init__(self) -> None:
        self.quizzes_data = Quizzes_data()
        self.mistral_ai = MistralAI()
        self.player = Player()
        self.stage = GameStage.NAME
        self.questions = []
        self.choices = []
        self.correct_answers = []
        self.topic = ""
        self.q_number = 0
        self.is_new_quiz = True
        self.q_idx = 0
        self.setup_display()

    def setup_display(self) -> None:
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.medium_font = pygame.font.SysFont(None, 60)
        self.big_font = pygame.font.SysFont(None, 100)
        self.surface = pygame.display.set_mode((SURFACE_WIDHT,SURFACE_HEIGHT))

    def use_exist_quiz(self) -> None:
        self.questions = self.quizzes_data.all_quizzes[self.q_idx]["questions"]
        self.choices = self.quizzes_data.all_quizzes[self.q_idx]["choices"]
        self.correct_answers = self.quizzes_data.all_quizzes[self.q_idx]["correct_answers"]

    def extract_response(self, response: str) -> None:
        response = response.split('[]')
        self.topic = response[0]
        self.player.topic = self.topic
        if self.topic in self.quizzes_data.all_topics:
            self.is_new_quiz = False
            self.q_idx = self.quizzes_data.all_topics.index(self.topic)
        if not self.is_new_quiz and self.quizzes_data.all_quizzes[self.q_idx]["use_count"] < 10:
            self.use_exist_quiz()
        else:
            self.correct_answers = response[6].split('..')
            tmp_questions = response[1:6]

            for qt in tmp_questions:
                question, answer = qt.split('///')
                self.questions.append(question)
                self.choices.append(answer.split('..'))

    def handle_name_input(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_BACKSPACE:
            self.player.name = self.player.name[:-1]
        elif event.key == pygame.K_RETURN:
            print(f"User's name: {self.player.name}")
            self.stage = GameStage.TOPIC
        else:
            self.player.name += event.unicode

    def handle_topic_input(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_BACKSPACE:
            self.player.topic = self.player.topic[:-1]
        elif event.key == pygame.K_RETURN:
            print(f"Topic chosen: {self.player.topic}")
            self.stage = GameStage.GENERATE_QUIZ
        else:
            self.player.topic += event.unicode

    def handle_quiz_input(self, mouse_pos: tuple[int, int]) -> int:
        x, y = mouse_pos
        # print(mouse_pos)
        if 400 < y < 600 and x < 500:
            return 1
        if 400 < y < 600 and 500 < x:
            return 2
        if 600 < y < 800 and x < 500:
            return 3
        if 600 < y < 800 and 500 < x:
            return 4

    def check_answer(self, answer: int) -> None:
        if answer == int(self.correct_answers[self.q_number]):
            self.player.score += 1
            self.stage = GameStage.CORRECT
        else:
            self.stage = GameStage.INCORRECT

    def show_correct_interface(self) -> None:
        self.draw_text(self.big_font, "CORRECT!", BLACK, 320, 330)
        self.draw_text(self.font, "PRESS-ENTER TO CONTINUE", BLACK, 360, 470)

    def show_incorrect_interface(self) -> None:
        self.draw_text(self.big_font, "INCORRECT!", BLACK, 300, 330)
        correct_choice = int(self.correct_answers[self.q_number]) - 1
        text = f"Correct answer is: {self.choices[self.q_number][correct_choice]}"
        self.draw_text(self.font, text, RED, 300, 400, 740, 600)
        self.draw_text(self.font, "PRESS-ENTER TO CONTINUE", BLACK, 360, 500)

    def draw_rotated_square(self,
                            surface: pygame.Surface,
                            color: tuple[int, int, int],
                            center: int,
                            size: int,
                            angle: float) -> None:
        square_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(square_surface, color, (0, 0, size, size))  
        rotated_square = pygame.transform.rotate(square_surface, angle)
        rect = rotated_square.get_rect(center=center)
        surface.blit(rotated_square, rect.topleft)

    def draw_text(self, font: pygame.font.Font,
                  text: str,
                  color: tuple[int, int, int],
                  x1: int,
                  y1: int,
                  x2: int=0,
                  y2: int=0,
                  is_choice: bool=False) -> None:
        if x2 == 0 and y2 == 0:
            img = font.render(text, True, color)
            self.surface.blit(img, (x1, y1))
        else:
            words = text.split(' ')
            space_width = font.size(' ')[0]  # Width of a space character
            if is_choice:
                max_width = x2 - x1
                total_width = 0
                for word in words:
                    word_width, word_height = font.size(word)
                    total_width += word_width
                    total_width += space_width
                total_width -= space_width 

                lines = total_width / max_width
                if 2 > lines > 1:
                    y1 -= 10
                elif 3 > lines > 2:
                    y1 -= 20
                elif lines > 3:
                    y1 -= 30

            x, y = x1, y1

            for word in words:
                word_width, word_height = font.size(word)
                if x + word_width > x2:
                    x = x1
                    y += word_height
                if y + word_height > y2:
                    break
                img = font.render(word, True, color)
                self.surface.blit(img, (x, y))
                x += word_width + space_width

    def draw_decorative(self) -> None:
        triangle_points = [(50, 470), (20, 530), (80, 530)]
        pygame.draw.polygon(self.surface, WHITE, triangle_points)
        pygame.draw.circle(self.surface, WHITE, (50, 700), 30)
        pygame.draw.rect(self.surface, WHITE, pygame.Rect(520, 670, 60, 60))
        self.draw_rotated_square(self.surface, WHITE, (552, 500), 60, 45)

    def draw_interface(self) -> None:
        pygame.draw.rect(self.surface, LIGHT_PURPLE, pygame.Rect(0, 100, QUESTION_WIDTH, QUESTION_HEIGHT))
        pygame.draw.rect(self.surface, RED, pygame.Rect(0, 400, RECT_WIDTH, RECT_HEIGHT))
        pygame.draw.rect(self.surface, YELLOW, pygame.Rect(0, 600, RECT_WIDTH, RECT_HEIGHT))
        pygame.draw.rect(self.surface, BLUE, pygame.Rect(500, 400, RECT_WIDTH, RECT_HEIGHT))
        pygame.draw.rect(self.surface, GREEN, pygame.Rect(500, 600, RECT_WIDTH, RECT_HEIGHT))

        self.draw_decorative()

        self.draw_text(self.font, f"Name: {self.player.name}", RED, 50, 30)
        self.draw_text(self.font, f"Question No.{self.q_number+1}", RED, 400, 30)
        self.draw_text(self.font, f"Score: {self.player.score}/5", RED, 850, 30)

        # st_pos = self.dynamic_text_display_handler()
        self.draw_text(self.font, f"Question: {self.questions[self.q_number]}", WHITE, 50, 150, 950, 350)
        self.draw_text(self.font, self.choices[self.q_number][0], WHITE, 100, 490, 450, 550, is_choice=True)
        self.draw_text(self.font, self.choices[self.q_number][1], WHITE, 600, 490, 950, 550, is_choice=True)
        self.draw_text(self.font, self.choices[self.q_number][2], WHITE, 100, 690, 450, 750, is_choice=True)
        self.draw_text(self.font, self.choices[self.q_number][3], WHITE, 600, 690, 950, 750, is_choice=True)

    def make_json(self) -> dict[str, any]:
        data = {
            "questions": self.questions,
            "choices": self.choices,
            "correct_answers": self.correct_answers,
            "use_count": 1,
            "total_score": self.player.score,
            "correct_percentage": 0
        }
        return data

    def update(self) -> None:
        data = self.make_json()
        self.quizzes_data.record_data(self.is_new_quiz, self.q_idx, self.topic, data)
        self.choices = []
        self.questions = []
        self.q_number = 0
        self.correct_answers = []
        self.is_new_quiz = True
        self.stage = GameStage.END

    def end_game(self) -> None:
        self.draw_text(self.medium_font, f"Name: {self.player.name}", RED, 50, 50)
        self.draw_text(self.medium_font, f"Topic: {self.player.topic}", RED, 50, 120)
        self.draw_text(self.medium_font, f"Final Score: {self.player.score}/5", RED, 50, 190)
        self.draw_text(self.font, "RIGHT-CLICK TO CONTINUE PLAYING", BLACK, 320, 550)
        self.draw_text(self.font, "PRESS-ENTER TO END GAME", BLACK, 360, 600)

    def start_game(self) -> None:
        self.clock.tick(30)
        running = True
        while running:
            self.surface.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if event.type == pygame.KEYDOWN:
                    if self.stage == GameStage.NAME:
                        self.handle_name_input(event) 
                    elif self.stage == GameStage.TOPIC:
                        self.handle_topic_input(event)
                if event.type == pygame.MOUSEBUTTONDOWN and self.stage == GameStage.QUIZ:
                    mouse_pos = pygame.mouse.get_pos()
                    answer = self.handle_quiz_input(mouse_pos)
                    self.check_answer(answer)
                if event.type == pygame.KEYDOWN and self.stage in [GameStage.CORRECT, GameStage.INCORRECT]:
                    if event.key == pygame.K_RETURN:
                        self.stage = GameStage.QUIZ
                        self.q_number += 1
                if event.type == pygame.KEYDOWN and self.stage == GameStage.END:
                    if event.key == pygame.K_RETURN:
                        running = False
                        break
                if event.type == pygame.MOUSEBUTTONDOWN and self.stage == GameStage.END:
                    if event.button == 3:
                        self.stage = GameStage.TOPIC
                        self.player.score = 0
                        self.quizzes_data = Quizzes_data()

            if self.stage == GameStage.NAME:
                self.draw_text(self.font, "Welcome to the quiz game!", RED, 50, 50)
                self.draw_text(self.font, f"Please enter your name: {self.player.name}|", RED, 50, 80)
            elif self.stage == GameStage.TOPIC:
                self.draw_text(self.font, f"Hi! {self.player.name}", RED, 50, 50)
                self.draw_text(self.font, "What topic do you want to quiz?", RED, 50, 80)
                self.draw_text(self.font, f"Enter topic: {self.player.topic}|", RED, 50, 110)
            elif self.stage == GameStage.GENERATE_QUIZ:
                print(f"generating quizzes for {self.player.topic}, please wait...")
                self.draw_text(self.font, "generating quizzes, please wait...", RED, 50, 50)
                response = self.mistral_ai.call(self.player.topic)
                logger.info(response)
                self.extract_response(response=response)
                self.stage = GameStage.QUIZ
            elif self.stage == GameStage.QUIZ:
                if self.q_number < 5:
                    self.draw_interface()
                else:
                    self.stage = GameStage.UPDATE
            elif self.stage == GameStage.CORRECT:
                self.show_correct_interface()
            elif self.stage == GameStage.INCORRECT:
                self.show_incorrect_interface()
            elif self.stage == GameStage.UPDATE:
                self.update()
            elif self.stage == GameStage.END:
                self.end_game()

            pygame.display.flip()

        pygame.quit()

def main() -> None:
    gameplay = Gameplay()
    gameplay.start_game()

if __name__ == "__main__":
    main()
# End of file
