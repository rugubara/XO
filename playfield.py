import asyncio
import inspect

import trio
import pygame
import cell
import pfModel

pfSize = 3
import telnetlib3
import contextvars
import Player

Xplayer = contextvars.ContextVar('Xplayer')
Oplayer = contextvars.ContextVar('Oplayer')

class gPlayField(pygame.Surface):  # класс отвечает за отрисовку доски и отправку событий мыши клеткам
    def __init__(self, pfPixelSize, gutterWidth, cellSize, model):
        # global size
        super(gPlayField, self).__init__(pfPixelSize)
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
                self.cells[i].append(cell.gCell((i, j), self.model, gutterWidth, cellSize))

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

async def tnGameSession(socketStream):
    # каждое новое соединение запустит trio.task c этой функцией - т.е локальные переменные будут содержать состояние
    # игры.


    # инициализируем данные игрового движка
    model = pfModel.pfModel((pfSize, pfSize), Xplayer.get(), Oplayer.get(), socketStream)
    tnPF = tnPlayField(18, 3, 5, model)
    await socketStream.send_all('Добро пожаловать в игру Крестики-Нолики\r\n'.encode('utf-8'))
    if Xplayer.get() == 'network':
        await socketStream.send_all('Вы играете Крестиками\r\n'.encode('utf-8'))
    elif Oplayer.get() == 'network':
        await socketStream.send_all('Вы играете Ноликами\r\n'.encode('utf-8'))
    await socketStream.send_all('Для хода введите координаты свободной клетки латинскими буквами, например B2\r\n'.encode('utf-8'))
    await tnPF.draw(socketStream)
    # Цикл, пока не обнаружен конец игры
    while not model.GameOver:
        #   нарисовать доску
    #   выполнить или запросить ход
        cPlayer = model.getCurrentPlayer()
        if inspect.isawaitable(cPlayer):
            move = await cPlayer.nextMove()
        else:
            move = cPlayer.nextMove()
        print(move, cPlayer)
        model.evaluate(move)
        await tnPF.draw(socketStream)
    else:
        await socketStream.send_all(f"Победили {model.win}\r\n".encode('utf-8'))

    # завершиться и закрыть соединение
async def tnGame(port, Xp, Op):
    Xplayer.set(Xp)
    Oplayer.set(Op)
    print('about to start tcp server')
    await trio.serve_tcp(tnGameSession, port,  host='127.0.0.1')
    print('tcp server ended')

class tnPlayField():  # класс отвечает за отрисовку доски и отправку ввода пользователя клеткам
    def __init__(self, pfPixelSize, gutterWidth, cellSize, model):
        # global size
        # super(tnPlayField, self).__init__()
        self.model = model
        self.cellWidth = cellSize
        self.gutterWidth = gutterWidth


    async def draw(self, writer):
        XOstr = ["O", " ", "X"]
        cW = self.cellWidth
        gW = self.gutterWidth
        cH = 3  # column height
        await writer.send_all(b'\r\n')
        await writer.send_all("{0:^{gW}} {1:^{cW}} {2:^{cW}} {3:^{cW}}\r\n".format("","A", "B", "C", gW=gW, cW=cW).encode('utf-8'))
        await writer.send_all("{0:<{gW}}{1:-<{cW}}{1:-<{cW}}{1:-<{cW}}+\r\n".format("", "+", gW=gW, cW=cW+1).encode('utf-8'))
        for row in range(pfSize):  # итерация по строкам модели
            for cellline in range(cH):   # итерация по строкам экрана, на которых располагается row строка модели
                await writer.send_all("{0:^3}|".format(row+1 if cellline == cH//2 else " ").encode('utf-8'))  # печатаем номер строки только на средней линии
                for col in range(pfSize):
                    await writer.send_all("{0:^{cW}}|".format(XOstr[self.model.model[row,col]+1] if cellline == cH//2 else " ", cW=cW).encode('utf-8'))
                await writer.send_all(b'\r\n')
            await writer.send_all("{0:<{gW}}{1:-<{cW}}{1:-<{cW}}{1:-<{cW}}+\r\n".format("", "+", gW=gW, cW=cW+1).encode('utf-8'))







