
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
LOG_PATH=os.environ["LOG_PATH"] + "//game.log"
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
GREEN = (0, 255, 0)
YELLOW = (253, 208, 23)
BLUE = (58, 93, 156)
LIGHT_PURPLE = (203, 195, 227)
# ------ ---- ----- #

# ----- PROMPTS ----- #
PROMPT = """
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

            The format for output you MUST USE NO EXCEPTION:
                REPLACE 'question(number)' with the actual question text, followed by '///'.
                REPLACE 'choice(number)' with the actual choice text, followed by '..'.
                REPLACE 'topic' with the actual summarize topic text, followed by '[]'.
                REPLACE 'correct_answer_for_question(number)' with the actual correct answer number, followed by '..'.
                topic[]question1///choice1..choice2..choice3..choice4[]question2///choice1..choice2..choice3..choice4[]
                question3///choice1..choice2..choice3..choice4[]question4///choice1..choice2..choice3..choice4[]
                question5///choice1..choice2..choice3..choice4[]correct_answer_for_question1..correct_answer_for_question2..
                correct_answer_for_question3..correct_answer_for_question4..correct_answer_for_question5
            Example output (YOU MUST NOT COPY THIS OUTPUT EVENTHOUGH IT IS THE SAME TOPIC):
            football player[]Which football player is known for their significant impact on the field despite their relatively short stature, often being cited as an example of how height is not a critical factor in football success?///Lionel Messi..Cristiano Ronaldo..Diego Maradona..Zinedine Zidane[]Which player is renowned for their exceptional free-kick abilities, often scoring from long distances with remarkable accuracy?///David Beckham..Roberto Carlos..Juninho Pernambucano..Andrea Pirlo[]Imagine a scenario where a football team is down by one goal with only five minutes left in the game. Which player would you want on your team for their known ability to score crucial late goals?///Sergio Aguero..Robert Lewandowski..Didier Drogba..Zlatan Ibrahimovic[]Which player is famous for their dribbling skills and is often compared to a "magician" on the field for their ability to create scoring opportunities out of seemingly impossible situations?///Ronaldinho..Neymar..Eden Hazard..Luis Suarez[]Which player is recognized for their leadership and defensive prowess, often being the backbone of their team's defense and a key figure in organizing the team's strategy?///Franz Beckenbauer..Paolo Maldini..Sergio Ramos..Virgil van Dijk[]1..3..2..1..4
            IMPORTANT*:Output must be in the format I provided.
            IMPORTANT*:REPLACE each fields with the real value, for example, REPLACE question with the real question
            IMPORTANT*:REPLACE choices, topic, and correct answer with the real one as well.
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
        self.database = {}

    def record_data(self):
        pass

    def get_data(self):
        pass

class MistralAI:
    def __init__(self):
        self.model = MODEL
        self.client = CLIENT
        self.prompt = PROMPT

    def call(self, topic):
        full_prompt = self.prompt + topic
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
    END = "end"
class Gameplay:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 30)
        self.surface = pygame.display.set_mode((SURFACE_WIDHT,SURFACE_HEIGHT))
        self.clock = pygame.time.Clock()
        self.mistral_ai = MistralAI()
        self.stage = GameStage.NAME
        self.player = Player()
        self.questions = []
        self.choices = []
        self.correct_answers = []
        self.topic = ""
        self.q_number = 0

    def extract_response(self, response):
        response = response.split('[]')
        self.topic = response[0]
        self.correct_answers = response[6].split('..')
        tmp_questions = response[1:6]

        for qt in tmp_questions:
            question, answer = qt.split('///')
            self.questions.append(question)
            self.choices.append(answer.split('..'))

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

    def handle_quiz_input(self, mouse_pos):
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
    
    def check_answer(self, answer):
        if answer == int(self.correct_answers[self.q_number]):
            self.player.score += 1
            self.stage = GameStage.CORRECT
        else:
            self.stage = GameStage.INCORRECT

    def show_correct_interface(self):
        self.draw_text("CORRECT!", BLACK, 320, 330)
        self.draw_text("RIGHT-CLICK TO CONTINUE", BLACK, 360, 470)

    def show_incorrect_interface(self):
        self.draw_text("INCORRECT!", BLACK, 300, 330)
        correct_choice = int(self.correct_answers[self.q_number]) - 1
        text = f"Correct answer is: {self.choices[self.q_number][correct_choice]}"
        self.draw_text(text, RED, 300, 400, 740, 600)
        self.draw_text("RIGHT-CLICK TO CONTINUE", BLACK, 360, 500)

    def draw_rotated_square(self, surface, color, center, size, angle):
        square_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(square_surface, color, (0, 0, size, size))  
        rotated_square = pygame.transform.rotate(square_surface, angle)
        rect = rotated_square.get_rect(center=center)
        surface.blit(rotated_square, rect.topleft)

    def draw_text(self, text, color, x1, y1, x2=0, y2=0):
        if text in ["CORRECT!", "INCORRECT!"]:
            tmp_font = pygame.font.SysFont(None, 100)
            img = tmp_font.render(text, True, color)
            self.surface.blit(img, (x1, y1))
        elif x2 == 0 and y2 == 0:
            img = self.font.render(text, True, color)
            self.surface.blit(img, (x1, y1))
        else:
            words = text.split(' ')
            space_width = self.font.size(' ')[0]  # Width of a space character
            max_width = x2 - x1
            x, y = x1, y1

            for word in words:
                word_width, word_height = self.font.size(word)
                if x + word_width > x2:
                    x = x1
                    y += word_height
                if y + word_height > y2:
                    break
                img = self.font.render(word, True, color)
                self.surface.blit(img, (x, y))
                x += word_width + space_width

    def draw_decorative(self):
        triangle_points = [(50, 470), (20, 530), (80, 530)]
        pygame.draw.polygon(self.surface, WHITE, triangle_points)
        pygame.draw.circle(self.surface, WHITE, (50, 700), 30)
        pygame.draw.rect(self.surface, WHITE, pygame.Rect(520, 670, 60, 60))
        self.draw_rotated_square(self.surface, WHITE, (552, 500), 60, 45)

    def draw_interface(self):
        pygame.draw.rect(self.surface, LIGHT_PURPLE, pygame.Rect(0, 100, QUESTION_WIDTH, QUESTION_HEIGHT))
        pygame.draw.rect(self.surface, RED, pygame.Rect(0, 400, RECT_WIDTH, RECT_HEIGHT))
        pygame.draw.rect(self.surface, YELLOW, pygame.Rect(0, 600, RECT_WIDTH, RECT_HEIGHT))
        pygame.draw.rect(self.surface, BLUE, pygame.Rect(500, 400, RECT_WIDTH, RECT_HEIGHT))
        pygame.draw.rect(self.surface, GREEN, pygame.Rect(500, 600, RECT_WIDTH, RECT_HEIGHT))
        
        self.draw_decorative()

        self.draw_text(f"Name: {self.player.name}", RED, 50, 30)
        # self.draw_text(f"Topic: {self.player.topic}", RED, 400, 30)
        self.draw_text(f"Score: {self.player.score}", RED, 850, 30)

        self.draw_text(self.questions[self.q_number], WHITE, 50, 150, 950, 350)
        self.draw_text(self.choices[self.q_number][0], WHITE, 100, 450, 450, 550)
        self.draw_text(self.choices[self.q_number][1], WHITE, 600, 450, 950, 550)
        self.draw_text(self.choices[self.q_number][2], WHITE, 100, 650, 450, 750)
        self.draw_text(self.choices[self.q_number][3], WHITE, 600, 650, 950, 750)
    
    def show_result(self):
        self.draw_text(f"Name: {self.player.name}", RED, 50, 30)
        self.draw_text(f"Topic: {self.player.topic}", RED, 50, 100)
        self.draw_text(f"Final Score: {self.player.score}", RED, 50, 200)

        self.draw_text("RIGHT-CLICK TO CONTINUE PLAYING", BLACK, 320, 550)
        self.draw_text("PRESS-ENTER TO END GAME", BLACK, 360, 600)

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
                if event.type == pygame.MOUSEBUTTONDOWN and self.stage == GameStage.QUIZ:
                    mouse_pos = pygame.mouse.get_pos()
                    answer = self.handle_quiz_input(mouse_pos)
                    self.check_answer(answer)
                if event.type == pygame.MOUSEBUTTONDOWN and self.stage in [GameStage.CORRECT, GameStage.INCORRECT]:
                    if event.button == 3:
                        self.stage = GameStage.QUIZ
                        self.q_number += 1
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN] and self.stage == GameStage.END:
                    if event.key == pygame.K_RETURN:
                        running = False
                        break
                    if event.button == 3:
                        self.stage = GameStage.TOPIC


            if self.stage == GameStage.NAME:
                self.draw_text("Welcome to the quiz game!", RED, 50, 50)
                self.draw_text(f"Please enter your name: {self.player.name}|", RED, 50, 80)
            elif self.stage == GameStage.TOPIC:
                self.draw_text(f"Hi! {self.player.name}", RED, 50, 50)
                self.draw_text("What topic do you want to quiz?", RED, 50, 80)
                self.draw_text(f"Enter topic: {self.player.topic}|", RED, 50, 110)
            elif self.stage == GameStage.GENERATE_QUIZ:
                print("generating quizzes, please wait...")
                self.draw_text("generating quizzes, please wait...", RED, 50, 50)
                response = self.mistral_ai.call(self.player.topic)
                logger.info(response)
                self.extract_response(response=response)
                self.stage = GameStage.QUIZ
            elif self.stage == GameStage.QUIZ:
                if self.q_number < 5:
                    self.draw_interface()
                else:
                    self.stage = GameStage.END
            elif self.stage == GameStage.CORRECT:
                self.show_correct_interface()
            elif self.stage == GameStage.INCORRECT:
                self.show_incorrect_interface()
            elif self.stage == GameStage.END:
                self.show_result()

            pygame.display.flip()

        pygame.quit()

def main():
    gameplay = Gameplay()
    gameplay.start_game()

if __name__ == "__main__":
    main()
# End of file
