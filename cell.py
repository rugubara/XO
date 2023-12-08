import pygame
import pfModel

playerViews = ["O", "", "X"]

class gCell(pygame.Surface): # класс отвечает за рисование клетки по данным модели и собственного состояния (подсветка по mouseIn)
    def __init__(self, pos, modelPtr, gutterWidth, cellSize):
        super(gCell, self).__init__((cellSize, cellSize))
        self.mPos = pos  # это позиция клетки в модели игры
        self.gPos = (gutterWidth * (pos[1] + 1) + cellSize * pos[1], gutterWidth * (pos[0] + 1) + cellSize * pos[0]) # вычисление графической позиции клетки в окне
        self.rect = pygame.Rect(self.gPos, (cellSize, cellSize)) # ограничивающий pygame.rect для фильтрации событий мыши по координатам
        self.model = modelPtr  # ссылка на модель игры
        self.value = modelPtr.getCellRef(pos)  # ссылка на клетку модели, соответствующую данной графической клетке
        self.mouseIn = False
        self.gutterWidth = gutterWidth  #  пробел между клетками в пикселях
        self.cellSize = cellSize
        self.playerView = "X"  # строка для вывода очередности хода в заголовок
        self.update()           # обновим спрайт клетки

    def draw(self, surface): # собственно вывод подготовленного спрайта клетки
        surface.blit(self, self.gPos)

    def update(self): # метод обновляет спрайт клетки на основании данных модели и состояния UI. Отвечает за отрисовку пустой клетки, крестика или нолика
        cellRect = self.get_bounding_rect()
        if self.value[0] == 0:  # пустая клетка
            self.fill(
                pygame.Color("grey48") if self.mouseIn else pygame.Color("black"))  # pygame.Surface.fill(self, Color)
        elif self.value[0] == 1:  # Клетка с крестиком
            self.fill(pygame.Color("grey48"))
            pygame.draw.line(self, pygame.Color("tomato"), cellRect.topleft, cellRect.bottomright,
                             int(self.gutterWidth / 2))
            pygame.draw.line(self, pygame.Color("tomato"), cellRect.bottomleft, cellRect.topright,
                             int(self.gutterWidth / 2))
        else:                       # клетка с ноликом
            self.fill(pygame.Color("grey48"))
            pygame.draw.circle(self, pygame.Color("lightskyblue2"), cellRect.center,
                               int(self.cellSize / 2), int(self.gutterWidth / 2))

    def mouse_action(self, event): # метод отрабатывает события мыши - как движения, так и нажатия.
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN) and self.model.inGame:
            if event.type == pygame.MOUSEMOTION: # фильтруем по координатам и отрабатываем подсветку клетки под курсором
                if self.value[0] == 0:
                    if self.rect.collidepoint(event.dict['pos']):
                        self.mouseIn = True
                    else:
                        self.mouseIn = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.dict['button'] == 1 and self.rect.collidepoint(
                    event.dict['pos']) and self.value == 0 and self.model.getCurrentPlayer().UI:  # фильтруем по координатам и отрабатываем клик
                # self.value[0] = self.model.getCurrentPlayer().playerCode  # поставить крестик или нолик в зависимости от состояния модели
                self.model.evaluate(self.mPos)  # поставить ход и проверить победу.
                self.playerView = playerViews[self.model.player + 1]
            self.update()  # обновить спрайт по результатам изменений состояний

