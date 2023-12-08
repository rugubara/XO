import argparse

import pygame
import pygame.colordict
import random
import pygame_gui

import Player
import pfModel
import playfield
import trio


class XOApp:
    def __init__(self):
        pygame.init()
        random.seed()
        self.uiDebug = False
        self.args = argparse.ArgumentParser(prog="XO", description="играет в крестики-нолики на графическом терминале или через telnet", epilog="автор - Губарьков А.A.")

        self.args.add_argument('-t', '--type', choices=['graphics', 'telnet'], default='graphics')
        self.args.add_argument('-O', '--Oplayer', choices=['bot', 'human', 'network'], default='bot')
        self.args.add_argument('-X', '--Xplayer', choices=['bot', 'human', 'network'], default='human')

        self.parsedArgs = self.args.parse_args()
        print(self.parsedArgs)
        self.gameType = self.parsedArgs.type


        if self.parsedArgs.type == 'graphics':
            # Set the width and height of the screen [width, height]
            size = 703
            g = int(size / 19)
            c = 5 * g

            self.screen = pygame.display.set_mode([size] * 2)
            pygame.font.init()
            pygame.display.set_caption("Крестики Нолики")
            # self.uimanager = pygame_gui.ui_manager.UIManager([size ] *2)
            # self.createUI()
            # self.uimanager.set_visual_debug_mode(self.uiDebug)
            self.model = pfModel.pfModel((3, 3), self.parsedArgs.Xplayer, self.parsedArgs.Oplayer)
            self.pf = playfield.gPlayField(self.screen.get_size(), g, c, self.model)
        elif self.parsedArgs.type == 'telnet':
            # telnet server использует совершенно иной event loop - и инициализация модели будет отложена до
            # формирования telnet сессии.
            pass
        else:
            raise RuntimeError('Я не понял, в какою игру вы хотите поиграть')

        return
    def run(self):
        # Loop until the user clicks the close button.
        if self.gameType == 'graphics':
            done = False
            clock = pygame.time.Clock()
            self.model.inGame = True
            # -------- Main Event Loop -----------
            while not done:
                delta = clock.tick(10 ) /1000;

                # --- Main event loop
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True
                        break
                    if self.model.getCurrentPlayer().UI or self.model.GameOver:
                        self.pf.dispatch(event)
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                            self.uiDebug = not self.uiDebug
                            self.uimanager.set_visual_debug_mode(self.uiDebug)
                    else:
                        if self.model.evaluate(self.model.getCurrentPlayer().nextMove()):
                            self.pf.generate_end_screen()
                            # в случае окончания игры ходом бота - вернуть управление человеку



                # self.uimanager.update(delta)
                # if not self.model.inGame:
                #     self.uimanager.draw_ui(self.screen)
                # --- Drawing code should go here
                self.pf.draw(self.screen)
                # --- Go ahead and update the screen with what we've drawn.
                pygame.display.flip()
        else:       #  telnet game
            trio.run(playfield.tnGame, 8023, self.parsedArgs.Xplayer, self.parsedArgs.Oplayer)
        return
    def createUI(self):
        # поделим экран на 3 равных горизонтальных полосы
        baseRect = self.screen.get_bounding_rect()
        baseRect.width = baseRect.width
        zeroRect = pygame.Rect(0 ,0 ,0 ,0)
        gutterRect = pygame.Rect(0 ,0 ,18 ,18)
        antigutterRect= pygame.Rect(0 ,0 ,-18 ,-18)

        panelRect = baseRect.copy()
        panelRect.h = panelRect. h//3
        # panelRect.w = panelRect.w - 36
        self.optionsPanel = pygame_gui.elements.UIPanel(baseRect, manager=self.uimanager)
        self.userConfigPanel = pygame_gui.elements.UIPanel(panelRect, manager=self.uimanager,
                                                           container=self.optionsPanel,
                                                           anchors={'top': 'top',
                                                                    'left': 'left'})
        #
        # self.scorePanel = pygame_gui.elements.UIPanel(panelRect, manager=self.uimanager, container=self.optionsPanel,
        #                                               anchors={'bottom' :'bottom', 'centerx' :'centerx'})
        #
        # uclRect = panelRect.copy()
        # uclRect.size = (uclRect.w -20, uclRect.h // 3)
        #
        # self.userConfigLabelPanel = pygame_gui.elements.UIPanel(uclRect, manager=self.uimanager,
        #                                                         container=self.userConfigPanel,
        #                                                         anchors={'top' :'top', 'centerx' :'centerx'})
        # user1labelRect = uclRect.copy()
        # user1labelRect.width = user1labelRect.width // 3
        # self.user1label = pygame_gui.elements.UILabel(user1labelRect, "Player 1", manager=self.uimanager,
        #                                               container=self.userConfigLabelPanel,
        #                                               anchors={'top' :'top', 'left' :'left'},
        #                                               text_kwargs=dict(en="Player 1", ru="Игрок 1"))
        # self.user2label = pygame_gui.elements.UILabel(user1labelRect, "Player 2", manager=self.uimanager,
        #                                               container=self.userConfigLabelPanel,
        #                                               anchors={'bottom' :'bottom', 'right' :'right'},
        #                                               text_kwargs=dict(en="Player 2", ru="Игрок 2"))


        return




if __name__ == '__main__':
    app = XOApp()
    app.run()
    pygame.quit()
