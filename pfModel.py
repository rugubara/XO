import numpy as np
import pygame
import Player


class pfModel():
    def __init__(self, pfSize):
        self.model = np.full(pfSize, 0)
        self.winStat = [0]*3  #  список статистики побед по игрокам
        self.inGame = False     #  флаг разрешает коду поля и клеток обрабатывать события мыши.
        self.Player = []    #  список содержит 2 объекта игрока. 0 = для крестиков, 1 = для ноликов
        self.Player.append( Player.HotseatPlayer(self, 1))  # кто играет за X
        self.Player.append( Player.BotPlayer(self, -1))  # кто играет за O
        self.player = 0 #  индекс текущего игрока. Первым ходят крестики
        self.pfSize = pfSize   # playfield size = 3
        self.winRow = 3         # сколько надо поставить в ряд для выигрыша
        self.GameOver = False   # флаг конца игры
        self.Player[self.player].nextMove()     # вызов кода для получения хода  очередного игрока
        return
    def RestartGame(self):
        r = self.model.reshape(self.pfSize[0]*self.pfSize[1])
        for i in range(self.pfSize[0]*self.pfSize[1]):
            r[i] = 0
        self.player = 0  # традиционно первыми ходят крестики
        self.GameOver = False
        self.Player[self.player].nextMove()
    def getCellRef(self, pos):
        return self.model[pos[0]:pos[0]+1, pos[1]:pos[1]+1]   #  для получения ссылки на ячейку модели и сохранения в UI объекте cell

    def getCurrentPlayer(self):
        return self.Player[self.player]

    def evaluate(self): # это метод вызывается в конце очередного хода для оценки позиции на предмет выигрыша или ничьей
        for i in range(self.pfSize[0]):
            if np.sum(self.model[i, :]) == 3 or np.sum(self.model[:, i]) == 3:
                self.endgame("X")
                break
            elif np.sum(self.model[i, :]) == -3 or np.sum(self.model[:, i]) == -3:
                self.endgame("O")
                break
        else:
            if np.sum(self.model.diagonal()) == -self.winRow or np.sum(np.flipud(self.model).diagonal()) == -self.winRow:
                self.endgame("O")
            elif np.sum(self.model.diagonal()) == self.winRow or np.sum(np.flipud(self.model).diagonal()) == self.winRow:
                self.endgame("X")
            elif np.prod(self.model) != 0:  # ни одной свободной клетки и условия победы не сработали  = ничья
                self.endgame("")
            else:
                self.player = (self.player + 1) % 2
                pygame.display.set_caption("Крестики Нолики - ход " + ("X" if self.player == 0 else "O"))
                self.Player[self.player].nextMove()




    def endgame(self, win):  #  объявление победы и обновление статистики
        self.GameOver = True
        # self.inGame = False
        self.win = win
        if win == "O":
            print("Победили нолики")
            self.winStat[0] += 1
        elif win == "X":
            print("Победили крестики")
            self.winStat[2] += 1
        else:
            print("Ничья")
            self.winStat[1] += 1
