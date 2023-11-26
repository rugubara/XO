import pygame
import cell
import pfModel
pfSize = 3
class PlayField(pygame.Surface):  # класс отвечает за отрисовку доски и отправку событий мыши клеткам
    def __init__(self, pfPixelSize, gutterWidth, cellSize, model):
        # global size
        super(PlayField, self).__init__(pfPixelSize)
        self.cells = []
        self.gameover_message_fontsize = 10
        self.font = pygame.font.SysFont("Serif", self.gameover_message_fontsize, bold=False, italic=False)
        self.gameover_message_fontsize *= int(
            0.8 * pfPixelSize[0] / self.font.render("Победили крестики", True, pygame.Color("tomato")).get_rect().width)
        self.font = pygame.font.SysFont("Serif", self.gameover_message_fontsize, bold=False, italic=False)
        self.model = model
        for i in range(self.model.pfSize[0]):
            self.cells.append([])
            for j in range(self.model.pfSize[1]):
                self.cells[i].append(cell.Cell((i, j), self.model, gutterWidth, cellSize))

    def draw(self, surface):
        surface.fill(pygame.Color("white"))
        for row in self.cells:
            for cell in row:
                cell.draw(surface)
        if self.model.GameOver:
            self.generate_end_screen()
            r = self.end_screen.get_rect()
            r.center = self.get_bounding_rect().center
            surface.blit(self.end_screen, r)

    def dispatch(self, event):
        if self.model.GameOver:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.model.RestartGame()
                self.update()
        else:
            for row in self.cells:
                for cell in row:
                    cell.mouse_action(event)





    def generate_end_screen(self):
        self.update()
        if self.model.win == "X":
            self.end_screen = self.font.render("Победили крестики", True, pygame.Color("tomato"))
        elif self.model.win == "O":
            self.end_screen = self.font.render("Победили нолики", True, pygame.Color("lightskyblue2"))
        else:
            self.end_screen = self.font.render("Ничья", True, pygame.Color("black"))




    def update(self):
        for r in self.cells:
            for c in r:
                c.update()

