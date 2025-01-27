
# ----- Libraries ----- #
import pygame
import os
import dotenv
from mistralai import Mistral
from enum import Enum
# ----- --------- ----- #

# ----- Environment config ----- #
dotenv.load_dotenv()
pygame.init()

# ----- Constant ----- #
SURFACE_WIDHT = 1000
SURFACE_HEIGHT = 800
QUESTION_WIDTH = 1000
QUESTION_HEIGHT = 300
RECT_WIDTH = 500
RECT_HEIGHT = 200
API_KEY = os.environ["MISTRAL_API_KEY"]
# ----- -------- ----- #

# ----- Color ----- #
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
# ------ ---- ----- #



class Player:
    def __init__(self):
        self.name = ""
        self.topic = ""
        self.score = 0

class MistralAI:
    def __init__(self):
        self.model = "mistral-large-latest"
        self.client = Mistral(api_key=API_KEY)
        self.prompt = """
                        Some prompt
                        """
        self.questions = []
        self.choices = []
        self.correct_answers = []
    def call(self, topic):
        gen_prompt = self.prompt + topic
        try:
            response = self.client.chat.complete(
                model = self.model,
                messages = [
                    {
                        "role": "user",
                        "content": gen_prompt,
                    },
                ]
            )
        except Exception as error:
            print(f"Error calling Mistral API: {error}")
            return ""

class GameStage(Enum):
    NAME = "name"
    TOPIC = "topic"
    GENERATE_QUIZ = "generate_quiz"
    QUIZ = "quiz"

class Gameplay:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 30)
        self.surface = pygame.display.set_mode((SURFACE_WIDHT,SURFACE_HEIGHT))
        self.clock = pygame.time.Clock()
        self.mistral_ai = MistralAI()
        self.stage = GameStage.NAME
        self.player = Player()

    def handle_name_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.player.name = self.player.name[:-1]
        elif event.key == pygame.K_RETURN:
            print(f"User's name: {self.player.name}")
            self.stage = GameStage.TOPIC
        else:
            self.player.name += event.unicode
    
    def handle_topic_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.player.topic = self.player.topic[:-1]
        elif event.key == pygame.K_RETURN:
            print(f"Topic chosen: {self.player.topic}")
            self.stage = GameStage.GENERATE_QUIZ
        else:
            self.player.topic += event.unicode

    def draw_text(self, text, color, x, y):
        img = self.font.render(text, True, color)
        self.surface.blit(img, (x, y))

    def start_game(self):
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

            if self.stage == GameStage.NAME:
                self.draw_text("Welcome to the quiz game!", RED, 50, 50)
                self.draw_text(f"Please enter your name: {self.player.name}|", RED, 50, 80)
            elif self.stage == GameStage.TOPIC:
                self.draw_text(f"Hi! {self.player.name}", RED, 50, 50)
                self.draw_text("What topic do you want to quiz?", RED, 50, 80)
                self.draw_text(f"Enter topic: {self.player.topic}|", RED, 50, 110)
            elif self.stage == GameStage.GENERATE_QUIZ:
                self.draw_text(f"generating quizzes, please wait...", RED, 50, 50)
                self.mistral_ai.call(self.player.topic)
                self.stage = GameStage.QUIZ
            elif self.stage == GameStage.QUIZ:
                self.draw_text(f"Name: {self.player.name}", RED, 50, 50)
                self.draw_text(f"Topic: {self.player.topic}", RED, 50, 80)
                self.draw_text(f"here is your quizzes", RED, 50, 110)

            pygame.display.flip()
                
        pygame.quit()

def main():
    gameplay = Gameplay()
    gameplay.start_game()

if __name__ == "__main__":
    main()
# End of file

