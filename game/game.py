
# ----- Libraries ----- #
import os
import dotenv
import json
import pygame
from enum import Enum
from mistralai import Mistral
# ----- --------- ----- #

# ----- setup MistralAi ----- #
dotenv.load_dotenv()
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
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
# ------ ---- ----- #

# ----- PROMPTS ----- #
PROMPTS = """
            Generate 5 questions short quizzes for the topic provided.
            Target **university students aged 18–25**; ensure questions are challenging but fair.  
            Prioritize critical thinking (avoid simple recall; include application, analysis, or hypothetical scenarios).  
            Use **distractors (wrong choices)** that are plausible to avoid being obvious.
            The topic will be provided by the users prompt at the bottom of this prompt.
            I want you to summary the topic, for example, 
            if I ask "Please generate a quiz about a cat species that is in russia",
            the topic after summarize should be: "cat species in Russia" or the one that is appropiate.
            Note: Maximum of topic MUST BE LESS THAN 5 words
            IMPORTANT*: The topic you summarize must contains only character not special characters.
            Then start generating 5 quizzes for that topicm follow by 4 choices for the question from 1 to 4.
            Generate the questions then choices. Then, after generated all questions and choices,
            give the correct answer by the choice number. For example, if the correct answer is choice number 1,
            then you should output 1.

            The format for output I want:
                Replace 'question(number)' with the actual question text, followed by '///'.
                Replace 'choice(number)' with the actual choice text, followed by '..'.
                Replace 'topic' with the actual summarize topic text, followed by '[]'.
                Replace 'correct_answer_for_question(number)' with the actual correct answer number, followed by '..'.
                topic[]question1///choice1..choice2..choice3..choice4[]question2///choice1..choice2..choice3..choice4[]
                question3///choice1..choice2..choice3..choice4[]question4///choice1..choice2..choice3..choice4[]
                question5///choice1..choice2..choice3..choice4[]correct_answer_for_question1..correct_answer_for_question2..
                correct_answer_for_question3..correct_answer_for_question4..correct_answer_for_question5
            
            IMPORTANT*:Output must be in the format I provided.
            IMPORTANT*:Replace each fields with the real value, for example, replace question with the real question
            IMPORTANT*:Replace choices, topic, and correct answer with the real one as well.
            IMPORTANT*:Use `///` and `..` and `[]` as a seperator (as shown in the format).
            IMPORTANT*:When summarize the topic, DO NOT output and AVOID the unnecessary phase like "The summarized topic is: ",
            just output PURELY THE TOPIC.
            Below is the user's prompt (ABOVE IS ALL THE EXAMPLE, USE USERS PROMPT to generate the quizzes)
"""
# ----- ------- ----- #
class Player:
    def __init__(self):
        self.name = ""
        self.topic = ""
        self.score = 0

class Database:
    def __init__(self):
        pass

    def record_data(self):
        pass

    def get_data(self):
        pass

class MistralAI:
    def __init__(self):
        self.model = MODEL
        self.client = CLIENT
        self.prompt = PROMPT
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
