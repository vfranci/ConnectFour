import time
import pygame
import sys
import copy

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
        return stare #pruning
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

def main():
    pygame.init()
    pygame.display.set_caption("Connect Four")
    ecran = pygame.display.set_mode((700, 600))
    InfoJoc.initializeaza(ecran)
    tabla_curenta = InfoJoc()
    print("Tabla initiala")
    print(str(tabla_curenta))

    jucator = None
    while jucator not in ['x', '0']:
        jucator = input("Alegeti simbolul dorit pentru dumneavoastra (x sau 0): ")
    InfoJoc.JMIN = jucator
    InfoJoc.JMAX = '0' if jucator == 'x' else 'x'
    tabla_curenta.deseneaza_grid()
    stare_curenta = Stare(tabla_curenta, 'x', ADANCIME_MAX)
    linie = -1
    coloana = -1

    while True:
        if stare_curenta.j_curent == InfoJoc.JMIN:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for linie in range(InfoJoc.NR_LINII):
                        for coloana in range(InfoJoc.NR_COLOANE):
                            if InfoJoc.celuleGrid[linie][coloana].collidepoint(pos):
                                #caut cel mai de jos rand liber pe coloana aleasa
                                for l in range(InfoJoc.NR_LINII - 1, -1, -1):
                                    if stare_curenta.tabla_joc.matr[l][coloana] == InfoJoc.GOL:
                                        stare_curenta.tabla_joc.matr[l][coloana] = InfoJoc.JMIN
                                        break
                    print("Tabla dupa mutarea jucatorului")
                    print(str(stare_curenta.tabla_joc))
                    stare_curenta.tabla_joc.deseneaza_grid()
                    if afis_daca_final(stare_curenta):
                        break
                    #schimb jucatorul
                    stare_curenta.j_curent = InfoJoc.jucator_opus(stare_curenta.j_curent)
        else:
            #mutare calculator
            t_inainte = int(round(time.time() * 1000))
            stare_actualizata = alpha_beta(-500, 500, stare_curenta)
            stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
            print("Tabla dupa mutarea calculatorului")
            print(str(stare_curenta.tabla_joc))
            stare_curenta.tabla_joc.deseneaza_grid()
            if afis_daca_final(stare_curenta):
                break
            stare_curenta.j_curent = InfoJoc.jucator_opus(stare_curenta.j_curent)
            t_dupa = int(round(time.time() * 1000))
            print("Calculatorul a „gandit” timp de " + str(t_dupa - t_inainte) + " milisecunde.")

    #nu vreau sa se inchida programul cand se termina jocul
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    main()
