import re

import numpy as np
# import pfModel
#  модуль реализует 3 класса (+1 абстрактный), которые могут использоваться для реализации поведения игрока


class Player():  #  это абстрактный класс с базовыми членами и методами.
    def __init__(self, model, modelPlayerCode):
        self.UI = False
        self.model = model
        self.playerCode = modelPlayerCode  # параметр содержит число 1 (X) или -1 (O), которое будет заполняться в клетку при ходе игрока
        return

class HotseatPlayer(Player):  # класс реализует поведение игрока, сидящего за компьютером
    def __init__(self, model, modelPlayerCode, socketStream=None):
        super().__init__(model, modelPlayerCode)
        self.UI = True
        return
    def nextMove(self):
        return (-1,-1)  # fake return, реальное заполнение делатеся в GUI cell.py



class BotPlayer(Player):  # класс реализует ИИ игрока
    def __init__(self, model, modelPlayerCode, socketStream=None):
        super().__init__(model, modelPlayerCode)
        return
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self
    def nextMove(self):
        score = -100000
        #   score для клетки рассчитывается так:
        #   обходим все незанятые клетки и для каждой считаем, если ход в эту клетку:
        #   приносит победу : + 10000
        #   блокирует победу оппонета на следующем ходу : + 500
        #   линии, проходящие через клетку, содержат только фишки игрока : +40 за каждую линию
        #   линии, проходящие через клетку, содержат только фишки оппонента : +30 за каждую линию
        #   клетка находится на полностью пустой линии : +9 за каждую пустую линию, проходящую через клетку
        #   вычтем 3/4*score лучшего прогнозного ответного хода оппонента

        #  Эвристика первого хода. Поставить надо в любой угол, так как ход в центр слишком очевиден и все знают, как с ним бороться
        maxScorePos = (None, None)
        if np.count_nonzero(self.model.model) == 0:
            maxScorePos = (0, 0)
        else:
            for i in range(3):
                for j in range(3):
                    if self.model.model[i, j] == 0:
                        cell_score = self.win(i, j, self.playerCode) * 10000 + self.win(i, j, -self.playerCode) * 1000 + \
                                    self.open_line_2(i, j, self.playerCode) * 100 + self.open_line_2(i,j,-self.playerCode)*50 \
                                         + self.open_line(i, j) * 10 - self.opForecastScore((i,j))*3//4

                        if cell_score > score:
                            score, maxScorePos = cell_score, (i, j)
            #self.model.model[maxScorePos] = self.playerCode
            #self.model.evaluate()
        return maxScorePos


    def win(self, i, j, move):
        count = 0
        if j == i:
            if np.sum(self.model.model.diagonal()) == move*2:
                count += 1
        if j + i == 2:
            if np.sum(np.flipud(self.model.model).diagonal()) == move*2:
                count += 1
        if np.sum(self.model.model[i, :]) == move*2:
            count += 1
        if np.sum(self.model.model[:, j]) == move*2:
            count += 1
        return count


    def open_line_2(self, i, j, move):   #  возвращает количестово линий, которые содержат только клетки игрока (т.е. не блокированы клетками оппонента)
        count = 0
        XO = -1 if move == "O" else 1
        if j == i:
            if np.sum(self.model.model.diagonal()) == XO:
                count += 1
        if j + i == 2:
            if np.sum(np.flipud(self.model.model).diagonal()) == XO:
                count += 1
        if np.sum(self.model.model[i, :]) == XO:
            count += 1
        if np.sum(self.model.model[:, j]) == XO:
            count += 1
        return count

    def open_line(self, i, j):  # возвращает количество полностью пустых линий, проходящих через клетку i, j
        count = 0
        if j == i:
            if np.count_nonzero(self.model.model.diagonal()) == 0:
                count += 1
        if j + i == 2:
            if np.count_nonzero(np.flipud(self.model.model).diagonal()) == 0:
                count += 1
        if np.count_nonzero(self.model.model[i, :]) == 0:
            count += 1
        if np.count_nonzero(self.model.model[:, j]) == 0:
            count += 1
        return count
    def opForecastScore(self, move):  # коррекция score на вес лучшего хода оппонента
        score = -1000000

        self.model.model[move] = self.playerCode  #  предположим, мы пошли сюда....
        for i in range(3):  #  посмотрим, куда лучше пойти оппоненту
            for j in range(3):
                if self.model.model[i, j] == 0:
                    cell_eval = self.win(i, j, -self.playerCode) * 10000 + self.win(i, j, self.playerCode) * 500 + \
                                self.open_line_2(i, j,-self.playerCode) * 40 + \
                                self.open_line(i, j) * 9
                    if cell_eval > score:
                        score, bestMove = cell_eval, (i, j)

        self.model.model[move] = 0 #  отменим наше предположение
        # return 40 * self.open_line_2(bestMove[0], bestMove[1], "X")
        return score



class NetworkPlayer(Player):
    decodeTable = {'A':0, 'B': 1, 'C':2, '1':0, '2':1, '3':2}
    def __init__(self, model, modelPlayerCode, socketStream):
        super().__init__(model, modelPlayerCode)
        self.socketStream = socketStream
        return

    async def nextMove(self):
        validInput = False
        while not validInput:
            await self.socketStream.send_all(b':')
            input = (await self.socketStream.receive_some(10)).decode().upper()  # получить строку на 2 байта

            # декодировать строку и вернуть кортеж
            reMatch = re.match("([A-C])([1-3])", input)
            if reMatch:
                move = (self.decodeTable[reMatch.group(2)], self.decodeTable[reMatch.group(1)])
                print(move)
                validInput = self.model.model[move] == 0  # проверим, что клетка свободна
                if not validInput:
                    await self.socketStream.send_all(f"Клетка {input} занята. Ходите в свободную клетку.\r\n".encode('utf-8'))
            else:
                await self.socketStream.send_all('Ввод неверен. Введите координаты вашего хода, например B1\r\n'.encode('utf-8'))
        return move
    def __iter__(self):
        return self
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    def __await__(self):
        return self