import numpy as np
import pfModel
#  модуль реализует 3 класса (+1 абстрактный), которые могут использоваться для реализации поведения игрока


class Player():
    def __init__(self, model, modelPlayerCode):
        self.UI = False
        self.model = model
        self.playerCode = modelPlayerCode  # параметр содержит число 1 (X) или -1 (O), которое будет заполняться в клетку при ходе игрока
        return

class HotseatPlayer(Player):
    def __init__(self, model, modelPlayerCode):
        super().__init__(model, modelPlayerCode)
        self.UI = True
        return
    def nextMove(self):
        return

class BotPlayer(Player):
    def __init__(self, model, modelPlayerCode):
        super().__init__(model, modelPlayerCode)
        return
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
        if np.count_nonzero(self.model.model) == 0:
            self.model.model[0,0] = self.playerCode
            self.model.evaluate()
            return

        for i in range(3):
            for j in range(3):
                if self.model.model[i, j] == 0:
                    cell_score = self.win(i, j, self.playerCode) * 10000 + self.win(i, j, -self.playerCode) * 500 + \
                                self.open_line_2(i, j, self.playerCode) * 40 + self.open_line_2(i,j,-self.playerCode)*30 \
                                     + self.open_line(i, j) * 9 - self.opForecastScore((i,j))*3//4

                    if cell_score > score:
                        score, maxScorePos = cell_score, (i, j)
        self.model.model[maxScorePos] = self.playerCode
        self.model.evaluate()


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
    def __init__(self, modelPlayerCode):
        super().__init__(modelPlayerCode)
        return
