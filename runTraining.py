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
    def __init__(self, x, y, side, thickness, color):
        self.x = x
        self.y = y
        self.side = side
        self.thickness = thickness
        self.color = color
        self.enabled = False 
        self.shrink = True
        self.grow = True
        self.delta = 0.2

    def draw(self, win, command):
        self.command = command
        pygame.draw.rect(win, self.color, (self.x, self.y, self.side, self.side), self.thickness)
    
    def animate(self, win):
        if self.command == 'push':
            if self.side < 50:
                self.shrink = False
            else: 
                self.shrink = True 
                self.side -= self.delta
                self.x += self.delta/2
                self.y += self.delta/2
                win.fill(BLACK)
                pygame.draw.rect(win, self.color, (self.x, self.y, self.side, self.side), self.thickness)

        elif self.command == 'pull':
            if self.side > 250:
                self.grow = False
            else: 
                self.grow = True
                self.side += self.delta
                self.x -= self.delta/2
                self.y -= self.delta/2
                win.fill(BLACK)
                pygame.draw.rect(win, self.color, (self.x, self.y, self.side, self.side), self.thickness)

class Cross:
    def __init__(self, x, y, side, width, color):
        self.x = x
        self.y = y
        self.side = side
        self.width = width
        self.color = color 
        self.offset = self.side/2 - self.width/2
        self.enabled = False 
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x+self.offset, self.y, self.width, self.side))
        pygame.draw.rect(win, self.color, (self.x, self.y+self.offset, self.side, self.width))


class Radio: 
    def __init__(self, text, x, y, color, fontsize, background, outline):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.select_color = BLUE
        self.fontsize = fontsize
        self.background = background
        self.outline = outline 
        self.clicked = False 

    def draw(self, win):
        font = pygame.font.Font(heeboBold, self.fontsize)
        text = font.render(self.text, 1, self.color)
        self.side = text.get_height()*0.25
        self.offset = self.y + (text.get_height()/2 - self.side/2)
        pygame.draw.circle(win, self.color, (self.x, self.offset), self.side)

        win.blit(text, (self.x+self.side+15, self.y))
    
    def draw_select(self, win, drawClick):
        if drawClick: 
            pygame.draw.circle(win, self.select_color, (self.x, self.offset), self.side*0.75)
        else: 
            pygame.draw.circle(win, self.color, (self.x, self.offset), self.side)
    
    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.side and self.offset <= y1 <= self.offset + self.side:
            return True
        else:
            return False


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
        pygame.draw.rect(win, BLACK, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 3)
        font = pygame.font.Font(heeboBold, 38)
        text = font.render(self.text, 1, self.color)
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))
    
    def draw_hover(self, win):
        pygame.draw.rect(win, BLACK, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(win, self.hover_color, (self.x, self.y, self.width, self.height), 3)
        font = pygame.font.Font(heeboBold, 38)
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

def redrawStart(win, *args):
    win.fill(BLACK)
    for arg in args: 
        arg.draw(win)

    pygame.display.update() 



def start_game():
    run = True
    clock = pygame.time.Clock()

    startButton = Button("Start", 275, 300, WHITE, BLUE, False)
    feedbackBox = Box(275, 275, 150, 6, BLUE)
    feedbackCross = Cross(300, 300, 100, 15, BLUE)
    neutral = Radio("Neutral", 300, 425, WHITE, 28, None, None)
    push = Radio("Push", 300, 475, WHITE, 28, None, None)
    pull = Radio("Pull", 300, 525, WHITE, 28, None, None)
    

    while run:
        clock.tick(60)
        if feedbackBox.enabled: 
            feedbackBox.animate(win), 

        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                if startButton.hover(pos):
                    if startButton.enabled: 
                        startButton.draw_hover(win)
                        pygame.display.update()
                else: 
                    if startButton.enabled: 
                        startButton.draw(win)
                        pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if startButton.click(pos):
                    if startButton.enabled: 
                        win.fill(BLACK)

                        if (neutral.clicked):
                            command = 'neutral'
                            feedbackCross.draw(win)
                            feedbackCross.enabled = True
                        elif (push.clicked):
                            command = 'push'
                            feedbackBox.draw(win, command)
                            feedbackBox.enabled = True
                        elif (pull.clicked):
                            command = 'pull'
                            feedbackBox.draw(win, command)
                            feedbackBox.enabled = True 
                        
                        t.train(command)

                        startButton.enabled = False
                        
                        pygame.display.update()

                # If user clicks on the 'neutral' radio button
                elif neutral.click(pos):                  
                    if not neutral.clicked and push.clicked: 
                        neutral.draw_select(win, True)
                        push.draw_select(win, False)
                        neutral.clicked = True
                        push.clicked = False
                    elif not neutral.clicked and pull.clicked: 
                        neutral.draw_select(win, True)
                        pull.draw_select(win, False)
                        neutral.clicked = True
                        pull.clicked = False
                    elif not neutral.clicked and not push.clicked and not pull.clicked: 
                        neutral.draw_select(win, True)
                        neutral.clicked = True
                    else: 
                        neutral.draw_select(win, False)
                        neutral.clicked = False

                # If user clicks on the 'push' radio button
                elif push.click(pos):
                    if not push.clicked and neutral.clicked: 
                        push.draw_select(win, True)
                        neutral.draw_select(win, False)
                        push.clicked = True
                        neutral.clicked = False 
                    elif not push.clicked and pull.clicked: 
                        push.draw_select(win, True)
                        pull.draw_select(win, False)
                        push.clicked = True
                        pull.clicked = False                         
                    elif not push.clicked and not neutral.clicked and not pull.clicked: 
                        push.draw_select(win, True)
                        push.clicked = True                        
                    else: 
                        push.draw_select(win, False)
                        push.clicked = False 

                # If user clicks on the 'pull' radio button
                elif pull.click(pos):
                    if not pull.clicked and neutral.clicked: 
                        pull.draw_select(win, True)
                        neutral.draw_select(win, False)
                        pull.clicked = True
                        neutral.clicked = False 
                    elif not pull.clicked and push.clicked: 
                        pull.draw_select(win, True)
                        push.draw_select(win, False)
                        pull.clicked = True
                        push.clicked = False                         
                    elif not pull.clicked and not neutral.clicked and not push.clicked: 
                        pull.draw_select(win, True)
                        pull.clicked = True                        
                    else: 
                        pull.draw_select(win, False)
                        pull.clicked = False                         


            
            if event.type == ON_READY:
                print('[GUI message] System ready for training.')
                startButton.draw(win)
                neutral.draw(win)
                neutral.draw_select(win, True)
                neutral.clicked = True 
                push.draw(win)
                pull.draw(win)
                startButton.enabled = True
                pygame.display.update()
            
            if event.type == ON_TRAINING_DONE:
                print('[GUI message] Training done.')
                redrawStart(win, startButton, neutral, push, pull)
                if neutral.clicked: 
                    neutral.draw_select(win, True)
                elif push.clicked: 
                    push.draw_select(win, True)
                elif pull.clicked: 
                    pull.draw_select(win, True)

                startButton.enabled = True
                feedbackCross.enabled = False 
                feedbackBox.enabled = False
                feedbackBox.side = 150 
                feedbackBox.x = 275
                feedbackBox.y = 275
                

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