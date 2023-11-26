

import pygame
import pygame.colordict
import random
import pygame_gui
import playfield


class XOApp:
    def __init__(self):
        pygame.init()
        random.seed()

        # Set the width and height of the screen [width, height]
        size = 703
        g = int(size / 19)
        c = 5 * g
        print(c, g)
        self.screen = pygame.display.set_mode([size] * 2)
        pygame.font.init()
        pygame.display.set_caption("Крестики Нолики - ход Х")
        self.pf = playfield.PlayField(self.screen.get_size(), g, c)

        return
    def run(self):
        # Loop until the user clicks the close button.
        done = False
        clock = pygame.time.Clock()

        # -------- Main Program Loop -----------
        while not done:
            # --- Main event loop
            for event in pygame.event.get():
                # print(event)
                self.pf.dispatch(event)
                if event.type == pygame.QUIT:
                    done = True



            # --- Drawing code should go here
            self.pf.draw(self.screen)
            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 10 frames per second
            clock.tick(10)
        return
    def createUI(self):
        return


# # Define some colors
# BLACK = (0, 0, 0)
# WHITE = (255, 255, 255)
# GREEN = (0, 255, 0)
# RED = (255, 0, 0)

if __name__ == '__main__':
    app = XOApp()
    app.run()
    pygame.quit()



# Close the window and quit.
