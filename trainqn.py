import time
import pygame
import sys
import copy
import numpy as np
import random
import pickle


ADANCIME_MAX = 4

class InfoJoc:
    NR_COLOANE = 7
    NR_LINII = 6
    JMIN = None
    JMAX = None
    GOL = '#'

    @classmethod
    def initializeaza(cls, display, NR_COLOANE=7, NR_LINII=6, dim_celula=100):
        cls.display = display
        cls.dim_celula = dim_celula
        try:
            cls.x_img = pygame.image.load('ics.png')
            cls.x_img = pygame.transform.scale(cls.x_img, (dim_celula, dim_celula))
            cls.zero_img = pygame.image.load('zero.png')
            cls.zero_img = pygame.transform.scale(cls.zero_img, (dim_celula, dim_celula))
        except pygame.error as e:
            print(f"Nu se pot incarca imaginile: {e}")
            sys.exit(1)
        cls.celuleGrid = []
        for linie in range(NR_LINII):
            cls.celuleGrid.append([])
            for coloana in range(NR_COLOANE):
                patr = pygame.Rect(coloana * (dim_celula + 1), linie * (dim_celula + 1), dim_celula, dim_celula)
                cls.celuleGrid[linie].append(patr) #lista de liste care contine dreptunghiurile pygame corespunzatoare fiecarei celule din grila

    def deseneaza_grid(self, marcaj=None):
        for linie in range(InfoJoc.NR_LINII):
            for coloana in range(InfoJoc.NR_COLOANE):
                culoare = (255, 0, 0) if marcaj == (linie, coloana) else (255, 255, 255)
                pygame.draw.rect(self.__class__.display, culoare, self.__class__.celuleGrid[linie][coloana])
                if self.matr[linie][coloana] == 'x':
                    self.__class__.display.blit(self.__class__.x_img, (coloana * (self.__class__.dim_celula + 1),
                                                                       linie * (self.__class__.dim_celula + 1)))
                elif self.matr[linie][coloana] == '0':
                    self.__class__.display.blit(self.__class__.zero_img, (coloana * (self.__class__.dim_celula + 1),
                                                                          linie * (self.__class__.dim_celula + 1)))
        pygame.display.update()

    def __init__(self, tabla=None):
        #daca se furnizeaza o tabela de joc, se foloseste aceasta, altfel se initializeaza o matrice goala
        if tabla:
            self.matr = tabla
        else:
            self.matr = []
            for i in range(self.__class__.NR_LINII):
                self.matr.append([self.__class__.GOL] * self.__class__.NR_COLOANE)

    #returnez jucatorul opus celui dat ca argument
    @classmethod
    def jucator_opus(cls, jucator):
        return cls.JMAX if jucator == cls.JMIN else cls.JMIN

    #verific daca jocul s-a terminat
    def final(self):
        for linie in range(self.__class__.NR_LINII):
            for coloana in range(self.__class__.NR_COLOANE):
                if self.matr[linie][coloana] != self.__class__.GOL:
                    # orizontala
                    # verific daca cele patru elemente consecutive dintr-o linie sunt toate identice
                    # verific daca fiecare element din intervalul range(4) este egal cu primul element din acea secventa.
                    if coloana <= self.__class__.NR_COLOANE - 4 and \
                            all(self.matr[linie][coloana + i] == self.matr[linie][coloana] for i in range(4)):
                        return self.matr[linie][coloana]
                    # verticala
                    if linie <= self.__class__.NR_LINII - 4 and \
                            all(self.matr[linie + i][coloana] == self.matr[linie][coloana] for i in range(4)):
                        return self.matr[linie][coloana]
                    # diag "principala"
                    if coloana <= self.__class__.NR_COLOANE - 4 and linie <= self.__class__.NR_LINII - 4 and \
                            all(self.matr[linie + i][coloana + i] == self.matr[linie][coloana] for i in range(4)):
                        return self.matr[linie][coloana]
                    if coloana >= 3 and linie <= self.__class__.NR_LINII - 4 and \
                            all(self.matr[linie + i][coloana - i] == self.matr[linie][coloana] for i in range(4)):
                        return self.matr[linie][coloana]
        #daca nu s-a intrat pe niciun caz si nu mai am spatii goale, atunci e remiza
        if self.__class__.GOL not in sum(self.matr, []):
            return 'remiza'
        return False

    #generez toate mutarile posibile pentru jucatorul curent
    #incep de la partea de jos a fiecarei coloane si caut o celula libera pentru a plasa piesa
    def mutari(self, jucator):
        l_mutari = []
        for coloana in range(self.__class__.NR_COLOANE):
            for linie in range(self.__class__.NR_LINII - 1, -1, -1):
                if self.matr[linie][coloana] == self.__class__.GOL:
                    copie_matr = copy.deepcopy(self.matr)
                    copie_matr[linie][coloana] = jucator
                    l_mutari.append(InfoJoc(copie_matr))
                    break
        return l_mutari

    #linie deschisa = secventa de 4 celule consecutive care nu contine piese ale jucatorului opus
    #si poate fi completata de jucatorul curent pentru a castiga
    def linie_deschisa(self, lista, jucator):
        return lista.count(jucator) * (not self.jucator_opus(jucator) in lista)

    #numar liniile deschise pentru jucatorul dat
    def linii_deschise(self, jucator):
        linii = 0
        for linie in range(self.__class__.NR_LINII):
            for coloana in range(self.__class__.NR_COLOANE):
                if coloana <= self.__class__.NR_COLOANE - 4:
                    linii += self.linie_deschisa(self.matr[linie][coloana:coloana + 4], jucator)
                if linie <= self.__class__.NR_LINII - 4:
                    linii += self.linie_deschisa([self.matr[linie + i][coloana] for i in range(4)], jucator)
                if coloana <= self.__class__.NR_COLOANE - 4 and linie <= self.__class__.NR_LINII - 4:
                    linii += self.linie_deschisa([self.matr[linie + i][coloana + i] for i in range(4)], jucator)
                if coloana >= 3 and linie <= self.__class__.NR_LINII - 4:
                    linii += self.linie_deschisa([self.matr[linie + i][coloana - i] for i in range(4)], jucator)
        return linii

    def estimeaza_scor(self, adancime):
        t_final = self.final()
        if t_final == self.__class__.JMAX: # jmax a castigat
            return 99 + adancime
        elif t_final == self.__class__.JMIN:
            return -99 - adancime
        elif t_final == 'remiza':
            return 0
        else:
            #calculez diferenta dintre liniile deschise pentru jmax si jmin
            return self.linii_deschise(self.__class__.JMAX) - self.linii_deschise(self.__class__.JMIN)

    def sirAfisare(self):
        sir = "  |" + " ".join([str(i) for i in range(self.NR_COLOANE)]) + "\n"
        sir += "-" * (self.NR_COLOANE + 1) * 2 + "\n"
        for i in range(self.NR_LINII):
            sir += str(i) + " |" + " ".join([str(x) for x in self.matr[i]]) + "\n"
        return sir

    def __str__(self):
        return self.sirAfisare()

    def __repr__(self):
        return self.sirAfisare()

class Stare:

    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, estimare=None):
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent
        self.adancime = adancime
        self.estimare = estimare
        self.mutari_posibile = []
        self.stare_aleasa = None

    def mutari(self):
        l_mutari = self.tabla_joc.mutari(self.j_curent)
        juc_opus = InfoJoc.jucator_opus(self.j_curent)
        l_stari_mutari = [Stare(mutare, juc_opus, self.adancime - 1, parinte=self) for mutare in l_mutari]
        return l_stari_mutari

def alpha_beta(alpha, beta, stare):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.estimare = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare
    if alpha >= beta:
        return stare #puning
    stare.mutari_posibile = stare.mutari()
    if stare.j_curent == InfoJoc.JMAX:
        estimare_curenta = float('-inf') #calculeaza estimarea pentru starea noua, realizand subarborele
        for mutare in stare.mutari_posibile:
            stare_noua = alpha_beta(alpha, beta, mutare)
            if estimare_curenta < stare_noua.estimare:
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare
            if alpha < stare_noua.estimare:
                alpha = stare_noua.estimare
                if alpha >= beta:
                    break
    elif stare.j_curent == InfoJoc.JMIN:
        estimare_curenta = float('inf')
        for mutare in stare.mutari_posibile:
            stare_noua = alpha_beta(alpha, beta, mutare)
            if estimare_curenta > stare_noua.estimare:
                stare.stare_aleasa = stare_noua
                estimare_curenta = stare_noua.estimare
            if beta > stare_noua.estimare:
                beta = stare_noua.estimare
                if alpha >= beta:
                    break
    stare.estimare = stare.stare_aleasa.estimare
    return stare

def afis_daca_final(stare_curenta):
    final = stare_curenta.tabla_joc.final()
    if final:
        if final == "remiza":
            print("Remiza!")
        else:
            print("A castigat " + final)
        return True
    return False

class QLearningAgent:
    def __init__(self, rata_inv=0.1, discount=0.9, rata_explorare=0.2, q_table_file="q_table.pkl"):
        self.rata_inv = rata_inv  # cat de des se actualizeaza valorile Q la fiecare pas
        self.discount = discount  # importanta recompenselor viitoare
        self.rata_explorare = rata_explorare  # cat de des alege agentul sa faca explorari aleatoare
        self.q_table = {}
        self.q_table_file = q_table_file
        self.load_q_table()

    def get_cheie_stare(self, stare):
        return str(stare)

    def choose_action(self, cheie_stare, actiuni_posibile):
        if cheie_stare not in self.q_table or len(self.q_table[cheie_stare]) == 0:
            # Înlocuiește cu o acțiune aleatoare dacă cheia de stare nu există în q_table sau lista este goală
            return random.choice(actiuni_posibile)

        if random.uniform(0, 1) < self.rata_explorare:
            return random.choice(actiuni_posibile)
        else:
            # Asigurăm că dimensiunea listei de valori Q corespunde cu dimensiunea listei de acțiuni posibile
            if len(self.q_table[cheie_stare]) != len(actiuni_posibile):
                self.q_table[cheie_stare] = [0] * len(actiuni_posibile)
            return actiuni_posibile[np.argmax(self.q_table[cheie_stare])]

    def update_q_value(self, cheie_stare, action, reward, next_cheie_stare, next_actiuni_posibile):

        # q_table[cheie_stare] are dimensiunea corectă pentru acțiune
        if cheie_stare not in self.q_table:
            self.q_table[cheie_stare] = [0] * len(next_actiuni_posibile)
        elif len(self.q_table[cheie_stare]) < len(next_actiuni_posibile):
            self.q_table[cheie_stare].extend([0] * (len(next_actiuni_posibile) - len(self.q_table[cheie_stare])))

        #  q_table[next_cheie_stare] are dimensiunea corectă
        if next_cheie_stare not in self.q_table:
            self.q_table[next_cheie_stare] = [0] * len(next_actiuni_posibile)
        elif len(self.q_table[next_cheie_stare]) < len(next_actiuni_posibile):
            self.q_table[next_cheie_stare].extend(
                [0] * (len(next_actiuni_posibile) - len(self.q_table[next_cheie_stare])))

        best_next_action = np.argmax(self.q_table[next_cheie_stare])
        td_target = reward + self.discount * self.q_table[next_cheie_stare][best_next_action]

        # Asigurăm că acțiunea este în limitele listei q_table[cheie_stare]
        if len(self.q_table[cheie_stare]) > action:
            td_error = td_target - self.q_table[cheie_stare][action]
            self.q_table[cheie_stare][action] += self.rata_inv * td_error
        else:
            print(
                f"Action {action} out of range for state key '{cheie_stare}'. Q table length: {len(self.q_table[cheie_stare])}")

    def save_q_table(self):
        with open(self.q_table_file, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load_q_table(self):
        try:
            with open(self.q_table_file, 'rb') as f:
                self.q_table = pickle.load(f)
        except FileNotFoundError:
            self.q_table = {}


MAX_REWARD = 1000
BLOCK_WIN_REWARD = 100
CREATE_THREE_REWARD = 20
BLOCK_THREE_REWARD = 10
CREATE_TWO_REWARD = 5
LOSE_REWARD = - 100

def calculate_reward(board, linie, coloana, jucator):
    points = 0
    tabla = board.matr
    oponent = InfoJoc.jucator_opus(jucator)

    # Verificare completare proprie linie deschisă, ducând la 4 pe linie
    if check_four_in_a_row(tabla, linie, coloana, jucator):
        points += MAX_REWARD

    # Penalizare pentru neblocarea unei linii de 3 a oponentului
    if check_fail_to_block_three(tabla, oponent):
        points += LOSE_REWARD

    # Verificare blocare câștig jucător opus
    if check_block_three_in_a_row(tabla, linie, coloana, jucator):
        points += BLOCK_WIN_REWARD

    # Verificare formare secvență de 3 pentru jucătorul curent
    if check_three_in_a_row(tabla, linie, coloana, jucator):
        points += CREATE_THREE_REWARD

    # Verificare blocare linie deschisă a adversarului cu trei piese
    if check_block_two_in_a_row(tabla, linie, coloana, jucator):
        points += BLOCK_THREE_REWARD

    # Verificare formare secvență de 2 pentru jucătorul curent
    if check_two_in_a_row(tabla, linie, coloana, jucator):
        points += CREATE_TWO_REWARD

    return points



def check_block_three_in_a_row(board, linie, coloana, jucator):
    oponent = InfoJoc.jucator_opus(jucator)

    # Verificare orizontală (dreapta)
    if coloana <= InfoJoc.NR_COLOANE - 4:
        if all(board[linie][coloana + i] == oponent for i in range(1, 4)):  # Verificare xxxo
            print("Blocare castig orizontala dupa")
            return True
    if coloana >= 3:
        if all(board[linie][coloana - i] == oponent for i in range(1, 4)):  # Verificare oxxx
            print("Blocare castig orizontala inainte")
            return True

    # Verificare verticală (jos)
    if linie <= InfoJoc.NR_LINII - 4:
        if all(board[linie + i][coloana] == oponent for i in range(1, 4)):  # Verificare xxxo
            print("Blocare castig verticala")
            return True

    # Verificare diagonală principală (jos dreapta)
    if linie <= InfoJoc.NR_LINII - 4 and coloana <= InfoJoc.NR_COLOANE - 4:
        if all(board[linie + i][coloana + i] == oponent for i in range(1, 4)):  # Verificare xxxo
            print("Blocare castig diag princ in jos")
            return True
    # Verificare diagonală principală (sus stanga)
    if linie >= 3 and coloana >= 3:
        if all(board[linie - i][coloana - i] == oponent for i in range(1, 4)):  # Verificare oxxx
            print("Blocare castig diag princ in sus")
            return True


    # Verificare diagonală secundară (jos stanga)
    if linie <= InfoJoc.NR_LINII - 4 and coloana >= 3:
        if all(board[linie + i][coloana - i] == oponent for i in range(1, 4)):  # Verificare oxxx
            print("Blocare castig diag sec in sus")
            return True
    # Verificare diagonală secundară (sus dreapta)
    if linie >= 3 and coloana <= InfoJoc.NR_COLOANE - 4:
        if all(board[linie - i][coloana + i] == oponent for i in range(1, 4)):  # Verificare xxxo
            print("Blocare castig diag sec in jos")
            return True
    if coloana > 0 and coloana < InfoJoc.NR_COLOANE - 2:
        if board[linie][coloana - 1] == oponent and board[linie][coloana + 1] == oponent and board[linie][
            coloana + 2] == oponent:
            print("Blocare orizontala xoxx")
            return True

    if coloana > 1 and coloana < InfoJoc.NR_COLOANE - 1:
        if board[linie][coloana - 2] == oponent and board[linie][coloana + 1] == oponent and board[linie][
            coloana - 1] == oponent:
            print("Blocare orizontala xxox")
            return True

    if linie > 0 and linie < InfoJoc.NR_LINII - 2 and coloana < InfoJoc.NR_COLOANE - 3:
        if board[linie + 1][coloana + 1] == oponent and board[linie - 1][coloana - 1] == oponent and board[linie + 2][
            coloana + 2] == oponent:
            print("Blocare dp xoxx de sus in jos")
            return True

    if linie > 1 and linie < InfoJoc.NR_LINII - 1 and coloana < InfoJoc.NR_COLOANE - 1:
        if board[linie + 1][coloana + 1] == oponent and board[linie - 1][coloana - 1] == oponent and board[linie - 2][
            coloana - 2] == oponent:
            print("Blocare dp xxox de sus in jos")
            return True

    if linie > 1 and linie < InfoJoc.NR_LINII - 2 and coloana <= InfoJoc.NR_COLOANE - 3:
        if board[linie - 1][coloana + 1] == oponent and board[linie + 1][coloana - 1] == oponent and board[linie - 2][
            coloana + 2] == oponent:
            print("Blocare ds xoxx de jos in sus")
            return True

    if linie > 0 and linie < InfoJoc.NR_LINII - 3 and coloana <= InfoJoc.NR_COLOANE - 2:
        if board[linie - 1][coloana + 1] == oponent and board[linie + 1][coloana - 1] == oponent and board[linie + 2][
            coloana - 2] == oponent:
            print("Blocare ds xxox de jos in sus")
            return True

    return False

def check_fail_to_block_three(board, jucator):
    for linie in range(InfoJoc.NR_LINII):
        for coloana in range(InfoJoc.NR_COLOANE):
            if board[linie][coloana] == jucator:
                # Verificare orizontală
                if coloana <= InfoJoc.NR_COLOANE - 4:
                    if all(board[linie][coloana + i] == jucator for i in range(3)):
                        if (coloana > 0 and board[linie][coloana - 1] == InfoJoc.GOL) or (
                                coloana + 3 < InfoJoc.NR_COLOANE and board[linie][coloana + 3] == InfoJoc.GOL):
                            return True

                # Verificare verticală
                if linie <= InfoJoc.NR_LINII - 4:
                    if all(board[linie + i][coloana] == jucator for i in range(3)):
                        if linie + 3 < InfoJoc.NR_LINII and board[linie + 3][coloana] == InfoJoc.GOL:
                            return True

                # Verificare diagonală principală
                if coloana <= InfoJoc.NR_COLOANE - 4 and linie <= InfoJoc.NR_LINII - 4:
                    if all(board[linie + i][coloana + i] == jucator for i in range(3)):
                        if (coloana > 0 and linie > 0 and board[linie - 1][coloana - 1] == InfoJoc.GOL) or (
                                coloana + 3 < InfoJoc.NR_COLOANE and linie + 3 < InfoJoc.NR_LINII and board[linie + 3][
                            coloana + 3] == InfoJoc.GOL):
                            return True

                # Verificare diagonală secundară
                if coloana >= 3 and linie <= InfoJoc.NR_LINII - 4:
                    if all(board[linie + i][coloana - i] == jucator for i in range(3)):
                        if (coloana < InfoJoc.NR_COLOANE - 1 and linie > 0 and board[linie - 1][
                            coloana + 1] == InfoJoc.GOL) or (
                                coloana - 3 >= 0 and linie + 3 < InfoJoc.NR_LINII and board[linie + 3][
                            coloana - 3] == InfoJoc.GOL):
                            return True
    return False


def check_block_two_in_a_row(board, linie, coloana, jucator):
    oponent = InfoJoc.jucator_opus(jucator)

    # Verificare orizontală
    if coloana <= InfoJoc.NR_COLOANE - 3:
        if all(board[linie][coloana + i + 1] == oponent for i in range(2)):
            print("Blocare doua orizontala dupa")
            return True
    if coloana >= 2:
        if all(board[linie][coloana - i - 1] == oponent for i in range(2)):
            print("Blocare doua orizontala inainte")
            return True

    # Verificare verticală
    if linie <= InfoJoc.NR_LINII - 3:
        if all(board[linie + i + 1][coloana] == oponent for i in range(2)):
            print("Blocare doua verticala")
            return True

    # Verificare diagonală principală (jos)
    if linie <= InfoJoc.NR_LINII - 3 and coloana <= InfoJoc.NR_COLOANE - 3:
        if all(board[linie + i + 1][coloana + i + 1] == oponent for i in range(2)):
            print("Blocare doua dp in jos")
            return True

    # Verificare diagonală principală (sus)
    if linie >= 2 and coloana >= 2:
        if all(board[linie - i - 1][coloana - i - 1] == oponent for i in range(2)):
            print("Blocare doua dp in sus")
            return True

    # Verificare diagonală secundară (jos)
    if linie <= InfoJoc.NR_LINII - 3 and coloana >= 2:
        if all(board[linie + i + 1][coloana - i - 1] == oponent for i in range(2)):
            print("Blocare doua ds in jos")
            return True

    # Verificare diagonală secundară (sus)
    if linie >= 2 and coloana <= InfoJoc.NR_COLOANE - 3:
        if all(board[linie - i - 1][coloana + i + 1] == oponent for i in range(2)):
            print("Blocare doua ds in sus")
            return True

    return False


def check_four_in_a_row(board, linie, coloana, jucator):
    if board[linie][coloana] == jucator:
        if coloana <= InfoJoc.NR_COLOANE - 4 and all(board[linie][coloana + i] == jucator for i in range(4)):
            return True
        if linie <= InfoJoc.NR_LINII - 4 and all(board[linie + i][coloana] == jucator for i in range(4)):
            return True
        if coloana <= InfoJoc.NR_COLOANE - 4 and linie <= InfoJoc.NR_LINII - 4 and all(board[linie + i][coloana + i] == jucator for i in range(4)):
            return True
        if coloana >= 3 and linie <= InfoJoc.NR_LINII - 4 and all(board[linie + i][coloana - i] == jucator for i in range(4)):
            return True
    return False
def check_three_in_a_row(board, linie, coloana, jucator):
    if board[linie][coloana] == jucator:
        # Verificare orizontală
        if coloana <= InfoJoc.NR_COLOANE - 4:
            if all(board[linie][coloana + i] == jucator for i in range(3)):
                if (coloana > 0 and board[linie][coloana - 1] == InfoJoc.GOL) or (coloana + 3 < InfoJoc.NR_COLOANE and board[linie][coloana + 3] == InfoJoc.GOL):
                    return True

        # Verificare verticală
        if linie <= InfoJoc.NR_LINII - 4:
            if all(board[linie + i][coloana] == jucator for i in range(3)):
                if linie + 3 < InfoJoc.NR_LINII and board[linie + 3][coloana] == InfoJoc.GOL:
                    return True

        # Verificare diagonală principală
        if coloana <= InfoJoc.NR_COLOANE - 4 and linie <= InfoJoc.NR_LINII - 4:
            if all(board[linie + i][coloana + i] == jucator for i in range(3)):
                if (coloana > 0 and linie > 0 and board[linie - 1][coloana - 1] == InfoJoc.GOL) or (coloana + 3 < InfoJoc.NR_COLOANE and linie + 3 < InfoJoc.NR_LINII and board[linie + 3][coloana + 3] == InfoJoc.GOL):
                    return True

                # Verificare diagonală secundară
        if coloana >= 3 and linie <= InfoJoc.NR_LINII - 4:
            if all(board[linie + i][coloana - i] == jucator for i in range(3)):
                if (coloana < InfoJoc.NR_COLOANE - 1 and linie > 0 and board[linie - 1][coloana + 1] == InfoJoc.GOL) or (coloana - 3 >= 0 and linie + 3 < InfoJoc.NR_LINII and board[linie + 3][coloana - 3] == InfoJoc.GOL):
                    return True
    return False

def check_two_in_a_row(board, linie, coloana, jucator):
    # Verificare orizontală
    if coloana <= InfoJoc.NR_COLOANE - 2:
        if all(board[linie][coloana + i] == jucator for i in range(2)):
            if coloana + 2 < InfoJoc.NR_COLOANE and board[linie][coloana + 2] == InfoJoc.GOL:
                return True
            if coloana > 0 and board[linie][coloana - 1] == InfoJoc.GOL:
                return True

    # Verificare verticală
    if linie <= InfoJoc.NR_LINII - 2:
        if all(board[linie + i][coloana] == jucator for i in range(2)):
            if linie + 2 < InfoJoc.NR_LINII and board[linie + 2][coloana] == InfoJoc.GOL:
                return True

    # Verificare diagonală principală
    if coloana <= InfoJoc.NR_COLOANE - 2 and linie <= InfoJoc.NR_LINII - 2:
        if all(board[linie + i][coloana + i] == jucator for i in range(2)):
            if coloana + 2 < InfoJoc.NR_COLOANE and linie + 2 < InfoJoc.NR_LINII and board[linie + 2][coloana + 2] == InfoJoc.GOL:
                return True
            if coloana > 0 and linie > 0 and board[linie - 1][coloana - 1] == InfoJoc.GOL:
                return True

    # Verificare diagonală secundară
    if coloana >= 1 and linie <= InfoJoc.NR_LINII - 2:
        if all(board[linie + i][coloana - i] == jucator for i in range(2)):
            if coloana - 2 >= 0 and linie + 2 < InfoJoc.NR_LINII and board[linie + 2][coloana - 2] == InfoJoc.GOL:
                return True
            if coloana < InfoJoc.NR_COLOANE - 1 and linie > 0 and board[linie - 1][coloana + 1] == InfoJoc.GOL:
                return True

    return False


def main():
    pygame.init()
    pygame.display.set_caption("Connect Four")
    ecran = pygame.display.set_mode((700, 600))
    InfoJoc.initializeaza(ecran)
    tabla_curenta = InfoJoc()
    print("Tabla initiala")
    print(str(tabla_curenta))

    InfoJoc.JMIN = '0'
    InfoJoc.JMAX = 'x'
    tabla_curenta.deseneaza_grid()
    stare_curenta = Stare(tabla_curenta, 'x', ADANCIME_MAX)

    agent = QLearningAgent()
    end = 0
    # Antrenarea pe episoade
    for episod in range(250):
        end += 1
        time.sleep(1)
        print(f"Episodul {episod + 1}")
        stare_curenta.tabla_joc = InfoJoc()  # Resetarea tablei la începutul fiecărui episod
        stare_curenta.j_curent = InfoJoc.JMAX
        while True:
            if stare_curenta.j_curent == InfoJoc.JMIN:
                t1_inainte = int(round(time.time() * 1000))
                cheie_stare = agent.get_cheie_stare(stare_curenta.tabla_joc.matr)
                actiuni_posibile = [c for c in range(InfoJoc.NR_COLOANE) if
                                    stare_curenta.tabla_joc.matr[0][c] == InfoJoc.GOL]

                action = agent.choose_action(cheie_stare, actiuni_posibile)
                # Se face mutarea pe tabla de joc
                linie = 0
                coloana = 0
                for l in range(InfoJoc.NR_LINII - 1, -1, -1):
                    if stare_curenta.tabla_joc.matr[l][action] == InfoJoc.GOL:
                        stare_curenta.tabla_joc.matr[l][action] = InfoJoc.JMIN
                        linie = l
                        coloana = action
                        break
                print("Tabla dupa mutarea QAgentului")
                print(str(stare_curenta.tabla_joc))
                stare_curenta.tabla_joc.deseneaza_grid()
                # Calculează recompensa pentru mutarea curentă
                reward = calculate_reward(stare_curenta.tabla_joc, linie, coloana, InfoJoc.JMIN)
                print(f"Reward: {reward}")
                next_actiuni_posibile = [c for c in range(InfoJoc.NR_COLOANE) if
                                         stare_curenta.tabla_joc.matr[0][c] == InfoJoc.GOL]
                next_cheie_stare = agent.get_cheie_stare(stare_curenta.tabla_joc.matr)
                agent.update_q_value(cheie_stare, action, reward, next_cheie_stare, next_actiuni_posibile)
                print(f"Q-values: {agent.q_table[cheie_stare]}")
                if afis_daca_final(stare_curenta):
                    agent.save_q_table()
                    if end == 250:
                        sys.exit()
                    break
                stare_curenta.j_curent = InfoJoc.jucator_opus(stare_curenta.j_curent)
                t1_dupa = int(round(time.time() * 1000))
                print("QAgentul a „gandit” timp de " + str(t1_dupa - t1_inainte) + " milisecunde.")


            else:
                t_inainte = int(round(time.time() * 1000))
                stare_actualizata = alpha_beta(-500, 500, stare_curenta)
                stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
                print("Tabla dupa mutarea alfa-beta")
                print(str(stare_curenta.tabla_joc))
                stare_curenta.tabla_joc.deseneaza_grid()
                if afis_daca_final(stare_curenta):
                    agent.save_q_table()
                    if end == 250:
                        sys.exit()
                    break
                stare_curenta.j_curent = InfoJoc.jucator_opus(stare_curenta.j_curent)
                t_dupa = int(round(time.time() * 1000))
                print("Alfa-beta a „gandit” timp de " + str(t_dupa - t_inainte) + " milisecunde.")



    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    main()

