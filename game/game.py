
# ----- Libraries ----- #
import pygame
import os
import dotenv
from mistralai import Mistral
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
    def __init__(self, name):
        self.name = name
        self.score = 0

class MistralAI:
    def __init__(self):
        self.model = "mistral-large-latest"
        self.client = Mistral(api_key=API_KEY)
        self.prompt = """
                        Some prompt
                        """
        self.questions = []
        self.correct_answers = []
    def call(self, topic):
        gen_prompt = self.prompt + topic
        response = self.client.chat.complete(
            model = self.model,
            messages = [
                {
                    "role": "user",
                    "content": gen_prompt,
                },
            ]
        )

class Gameplay:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 30)
        self.surface = pygame.display.set_mode((SURFACE_WIDHT,SURFACE_HEIGHT))
        self.clock = pygame.time.Clock()
        self.user_name = ""
        self.topic = ""

    def draw_text(self, text, color, x, y):
        img = self.font.render(text, True, color)
        self.surface.blit(img, (x, y))

    def start_game(self):
        running = True
        stage = "name"

        while running:
            self.surface.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if event.type == pygame.KEYDOWN:
                    if stage == "name":
                        if event.key == pygame.K_BACKSPACE:
                            self.user_name = self.user_name[:-1]
                        elif event.key == pygame.K_RETURN:
                            print(f"User's name: {self.user_name}")
                            stage = "topic"
                            player = Player(name=self.user_name)
                        else:
                            self.user_name += event.unicode 
                    elif stage == "topic":
                        if event.key == pygame.K_BACKSPACE:
                            self.topic = self.topic[:-1]
                        elif event.key == pygame.K_RETURN:
                            print(f"Topic chosen: {self.topic}")
                            stage = "Generating quiz"
                        else:
                            self.topic += event.unicode

            if stage == "name":
                self.draw_text("Welcome to the quiz game!", RED, 50, 50)
                self.draw_text(f"Please enter your name: {self.user_name}|", RED, 50, 80)
            elif stage == "topic":
                self.draw_text(f"Hi! {self.user_name}", RED, 50, 50)
                self.draw_text("What topic do you want to quiz?", RED, 50, 80)
                self.draw_text(f"Enter topic: {self.topic}|", RED, 50, 110)
            elif stage == "Generating quiz":
                Mt_ai = MistralAI()
                Mt_ai.call(self.topic)
            pygame.display.flip()
                
        pygame.quit()

def main():
    gameplay = Gameplay()
    gameplay.start_game()

if __name__ == "__main__":
    main()
# End of file

