import pygame
 
pygame.init()

SURFACE_WIDHT = 1000
SURFACE_HEIGHT = 800
QUESTION_WIDTH = 1000
QUESTION_HEIGHT = 300
RECT_WIDTH = 500
RECT_HEIGHT = 200

surface = pygame.display.set_mode((SURFACE_WIDHT,SURFACE_HEIGHT))

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

text_font = pygame.font.SysFont(None, 30)

def draw_text(text, font, color, x1, y1, x2, y2):
    words = text.split(' ')
    space_width = font.size(' ')[0]  # Width of a space character
    max_width = x2 - x1
    x, y = x1, y1

    for word in words:
        word_width, word_height = font.size(word)
        if x + word_width > x2:  # If the word doesn't fit, go to a new line
            x = x1
            y += word_height
        if y + word_height > y2:  # If text goes beyond the box, stop rendering
            break
        img = font.render(word, True, color)
        surface.blit(img, (x, y))
        x += word_width + space_width  # Move to the next position

my_text = 'This is a long text that will wrap to a new line when it doesnt fit in the specified area.'

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()    
            print(f"Clicked: {pos}")
    pygame.draw.rect(surface, WHITE, pygame.Rect(0, 100, QUESTION_WIDTH, QUESTION_HEIGHT))
    pygame.draw.rect(surface, RED, pygame.Rect(0, 400, RECT_WIDTH, RECT_HEIGHT))
    pygame.draw.rect(surface, GREEN, pygame.Rect(0, 600, RECT_WIDTH, RECT_HEIGHT))
    pygame.draw.rect(surface, YELLOW, pygame.Rect(500, 400, RECT_WIDTH, RECT_HEIGHT))
    pygame.draw.rect(surface, BLUE, pygame.Rect(500, 600, RECT_WIDTH, RECT_HEIGHT))
    draw_text(my_text, text_font, (0, 0, 0), 0, 400, 500, 600)
    pygame.display.flip()

pygame.quit()
# End of file
