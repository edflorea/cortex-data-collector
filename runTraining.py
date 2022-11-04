import pygame
import threading
from emotivDataCollection import Train
from datetime import datetime

pygame.font.init()
width = 700
height = 700
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Emotiv Data Collection")

# Fonts
heeboBold = "./assets/fonts/Heebo/Heebo-ExtraBold.ttf"

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (51, 153, 255)
BLACK = (0, 0, 0)

# Keep a track of active variable



# custom user event to inflate defalte
# box
ON_READY = pygame.USEREVENT + 1
ON_TRAINING_DONE = pygame.USEREVENT + 2

userEvents = [ON_READY, ON_TRAINING_DONE]

# Init Train
your_app_client_id = 'jL4BOpvLmHsF0ypsOMKhYitdXuyCxfDFxo6XtA1J'
your_app_client_secret = 'sqQ5ttXBkRWiJSudvOB0c63ecz3Ucbziu1kRxA6gVw2yEXU26ZSLGFAtInHIfWYePoAhevWyoe8SxyMT8zoRGsV9lO42VtNuDaMFv6YwtRL9BS92Qdiaz5w5GWlloxib'

t = Train(your_app_client_id, your_app_client_secret, userEvents)
  

class Box:
    def __init__(self, x, y, width, height, thickness, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.thickness = thickness
        self.color = color

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), self.thickness)


class Button:
    def __init__(self, text, x, y, color, hover_color, enabled=True):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.hover_color = hover_color
        self.width = 150
        self.height = 80
        self.enabled = enabled

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 3)
        font = pygame.font.Font(heeboBold, 38)
        text = font.render(self.text, 1, self.color)
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))
    
    def draw_hover(self, win):
        pygame.draw.rect(win, self.hover_color, (self.x, self.y, self.width, self.height), 4)
        font = pygame.font.Font(heeboBold, 40)
        text = font.render(self.text, 1, self.hover_color)
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False
    
    def hover(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False



def start_game():
    run = True
    clock = pygame.time.Clock()

    startButton = Button("Start", 275, 300, WHITE, BLUE, False)
    feedbackBox = Box(275, 275, 150, 150, 6, BLUE)

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                if startButton.hover(pos):
                    if startButton.enabled: 
                        win.fill(BLACK)
                        startButton.draw_hover(win)
                        pygame.display.update()
                else: 
                    if startButton.enabled: 
                        win.fill(BLACK)
                        startButton.draw(win)
                        pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if startButton.click(pos):
                    if startButton.enabled: 
                        t.train('push')
                        startButton.enabled = False
                        win.fill(BLACK)
                        feedbackBox.draw(win)
                        pygame.display.update()

            
            if event.type == ON_READY:
                print('[GUI message] System ready for training.')
                startButton.draw(win)
                startButton.enabled = True
                pygame.display.update()
            
            if event.type == ON_TRAINING_DONE:
                print('[GUI message] Training done.')
                win.fill(BLACK)
                startButton.draw(win)
                startButton.enabled = True
                pygame.display.update()

            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                exit()    
        
        pygame.display.update()
    pygame.quit()    


def main():

    # threadName = "FrontEndThread:-{:%Y%m%d%H%M%S}".format(datetime.utcnow())
    # front_thread = threading.Thread(target=start_game, name=threadName)
    # front_thread.start() 
    profile_name = 'EricaTest' 

    t.setup(profile_name)    

    start_game()


if __name__ == '__main__':
    main()