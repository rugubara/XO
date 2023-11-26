

import pygame
import pygame.colordict
import random
import pygame_gui

import pfModel
import playfield


class XOApp:
    def __init__(self):
        pygame.init()
        random.seed()
        self.uiDebug = False

        # Set the width and height of the screen [width, height]
        size = 703
        g = int(size / 19)
        c = 5 * g
        # print(c, g)
        self.model = pfModel.pfModel((3,3))
        self.screen = pygame.display.set_mode([size] * 2)
        pygame.font.init()
        pygame.display.set_caption("Крестики Нолики")
        self.uimanager = pygame_gui.ui_manager.UIManager([size]*2)
        self.createUI()
        self.uimanager.set_visual_debug_mode(self.uiDebug)
        self.pf = playfield.PlayField(self.screen.get_size(), g, c, self.model)

        return
    def run(self):
        # Loop until the user clicks the close button.
        done = False
        clock = pygame.time.Clock()
        self.model.inGame = True
        # -------- Main Program Loop -----------
        while not done:
            delta = clock.tick(10)/1000;

            # --- Main event loop
            for event in pygame.event.get():
                # print(event)
                self.pf.dispatch(event)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                    self.uiDebug = not self.uiDebug
                    self.uimanager.set_visual_debug_mode(self.uiDebug)

                if event.type == pygame.QUIT:
                    done = True


            # self.uimanager.update(delta)
            # --- Drawing code should go here
            self.pf.draw(self.screen)
            # if not self.model.inGame:
            #     self.uimanager.draw_ui(self.screen)
            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 10 frames per second
        return
    def createUI(self):
        # поделим экран на 3 равных горизонтальных полосы
        baseRect = self.screen.get_bounding_rect()

        panelRect = baseRect.copy()
        panelRect.h = panelRect.h//3
        self.optionsPanel = pygame_gui.elements.UIPanel(baseRect, manager=self.uimanager)
        self.userConfigPanel = pygame_gui.elements.UIPanel(panelRect, manager=self.uimanager, container=self.optionsPanel,
                                                           anchors={'top':'top', 'centerx':'centerx'})
        self.scorePanel = pygame_gui.elements.UIPanel(panelRect, manager=self.uimanager, container=self.optionsPanel,
                                                      anchors={'bottom':'bottom', 'centerx':'centerx'})

        uclRect = panelRect.copy()
        uclRect.h = uclRect.h // 3
        self.userConfigLabelPanel = pygame_gui.elements.UIPanel(uclRect, manager=self.uimanager, container=self.userConfigPanel,
                                                                anchors={'top':'top', 'left':'left'})
        user1labelRect = uclRect.copy()
        user1labelRect.w = user1labelRect.w//3
        self.user1label = pygame_gui.elements.UILabel(user1labelRect, "Player 1", manager=self.uimanager,
                                                    container=self.userConfigLabelPanel, anchors={'top':'top', 'left':'left'},
                                                      text_kwargs=dict(en="Player 1", ru="Игрок 1"))
        self.user2label = pygame_gui.elements.UILabel(user1labelRect, "Player 2", manager=self.uimanager,
                                                    container=self.userConfigLabelPanel, anchors={'top':'top', 'right':'right'},
                                                      text_kwargs=dict(en="Player 2", ru="Игрок 2"))


        return




if __name__ == '__main__':
    app = XOApp()
    app.run()
    pygame.quit()


