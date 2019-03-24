# -*- coding: utf-8 -*-
#==============================================================================
# Import des bibliothèques
#==============================================================================
import heapq as hq
import utils as ut

#==============================================================================
# Import des fonctions codées
#==============================================================================
from Strategy import Strategy
from algo_A import algo_A

class temporal_A_D(Strategy):
    """
    Stratégie coopérative avancée en prenant en compte le temps et avec profondeur
    de recherche fixée.
    """
    
    def __init__(self, game, iterations, d, verbose = True):
        """
        Stratégie coopérative avancée en prenant en compte le temps et avec
        profondeur de recherche fixée.
        d : profondeur de recherche.
        """
        super(temporal_A_D,self).__init__(game, iterations, verbose)
        self.d = d
        self.obs_fixe = {w.get_rowcol() for w in game.layers['obstacle']}
        self.obs_mob = {(self.initStates[p], t):p for p in range(self.nbPlayers) for t in [0, 1]}
        self.tab_dist = [algo_A(self.goalStates[joueur], self.initStates[joueur], self.obs_fixe, self.taille) for joueur in range(self.nbPlayers)]
        
    def setGoalStates(self, goalStates):
        """
        Permet de changer l'ordre des goalStates. Attention, les nouveaux goalStates
        doivent être une permutation des précédents.
        """
        super().setGoalStates(goalStates)
        self.tab_dist = [algo_A(self.goalStates[joueur], self.initStates[joueur], self.obs_fixe, self.taille) for joueur in range(self.nbPlayers)]

    def execute(self):
        """
        Pour cet algorithme, le calcul de trajectoire et l'exécution sont faits
        de façon simultanée dans cette fonction.
        """
        # Initialisation des trajectoires pour les joueurs.
        # À chaque étape, on calculera la trajectoire d'un joueur aux d prochains
        # pas. Pour éviter que les recalculs de trajectoires ne soient pas
        # toujours synchronisés, le premier calcul de trajectoire est fait
        # avec une longueur différente pour chaque trajectoire. Cela permet
        # en particulier de modifier l'ordre de priorité à chaque recalcul.
        # La longueur des trajectoires a été choisie comme d + 2*k pour
        # augmenter de 2 la longueur de la trajectoire calculée pour chaque
        # joueur par rapport au précédent. La valeur de 2 a été choisie car
        # dans obs_mob on rajoute toujours ((x, y), t) et ((x, y), t + 1).
        tab_joueur = [self.chemin(k, 0, self.d + 2*k) for k in range(self.nbPlayers)]
        
        # Boucle principale
        for it in range(self.iterations):
            # Arrête les itérations dès que tout le monde est arrivé.
            if self.is_finished():
                break
            # Pour chaque joueur
            for j in range(self.nbPlayers):
                # Si on a déjà exécuté toute sa trajectoire, on calcule les d
                # prochaines étapes.
                if tab_joueur[j] == []:
                    self.initStates[j] = self.players[j].get_rowcol()
                    tab_joueur[j] = self.chemin(j, it, self.d)
                    # Si le joueur est dans une situation de bloquage, on essaie
                    # de lui débloquer en lui donnant la priorité maximale.
                    if tab_joueur[j] == []:
                        # On oublie les chemins de tout le monde et on recommence !
                        self.obs_mob = {(self.players[p].get_rowcol(), it + dt):p for p in range(self.nbPlayers) for dt in [0, 1]}
                        tab_joueur = [[] for k in range(self.nbPlayers)]
                        # On recalcule les chemins de tout le monde à partir du joueur courant
                        for k in range(j, j + self.nbPlayers):
                            kk = k % self.nbPlayers
                            self.initStates[kk] = self.players[kk].get_rowcol()
                            tab_joueur[kk] = self.chemin(kk, it, self.d + kk)
                        # Si le joueur est vraiment vraiment vraiment bloqué
                        # (même avec la priorité maximale il n'a pas trouvé un chemin possible).
                        if tab_joueur[j] == []:
                            raise ut.ThereIsNoPath("Wow, I'm completely stuck! Where am I??")
            # Maintenant qu'on a garanti que tous les joueurs ont un prochain
            # état déjà calculé, on joue un pas.
            for j in range(self.nbPlayers):
                pos,_ = tab_joueur[j].pop(0)
                self.players[j].set_rowcol(pos[0], pos[1])
                if self.verbose:
                    print ("pos :",j,pos[0], pos[1])
            if self.verbose:
                print()
            self.game.mainiteration()
            if self.verbose:
                print("tour :", it)
        
    def is_finished(self):
        """
        Teste si tous les joueurs sont déjà arrivés à leurs respectives fioles.
        """
        for i in range(self.nbPlayers):
            if self.players[i].get_rowcol() != self.goalStates[i]:
                return False
        return True
    
    def cost(pos, pos_next, pos_fin):
        """
        Coût d'un pas utilisé dans l'algorithme A* en espace-temps.
        Le coût vaut toujours 1 sauf lorsque le joueur est déjà à sa fiole et
        y reste, auquel cas il vaut 0.
        """
        if pos[0] == pos_next[0] and pos_next[0] == pos_fin:
            return 0
        return 1
        
    def chemin(self, iden, t0, d):
        """
        Implémentation de l'algorithme A* en espace-temps avec l'heuristique
        de la distance réelle (algorithme A* en espace calculé à partir de la
        fiole par la classe algo_A).
        t0 : instant initial
        d : nombre de pas de temps à calculer.
        """
        pos_init = (self.initStates[iden], t0)
        pos_fin = self.goalStates[iden]
        
        pos = pos_init
        frontier =  []
        hq.heappush(frontier,(0, pos)) 
        came_from = {}
        cost_so_far = {}
        came_from[pos] = None
        cost_so_far[pos] = 0
    
        while len(frontier) != 0:
            _,pos = hq.heappop(frontier)
            
            # On s'arrête lorsque t = t0 + d.
            if pos[1] == t0 + d:
                break
            
            voisin = ut.voisins_tempD(iden, pos, self.obs_fixe, self.obs_mob, self.taille)
            for pos_next in voisin:
                new_cost = cost_so_far[pos] + temporal_A_D.cost(pos, pos_next, pos_fin)
                if pos_next not in cost_so_far or new_cost < cost_so_far[pos_next]:
                    cost_so_far[pos_next] = new_cost
                    priority = new_cost + self.tab_dist[iden].distance(pos_next[0])
                    hq.heappush(frontier,(priority, pos_next)) 
                    came_from[pos_next] = pos   
        
        # On évite les croisements comme dans temporal_A.
        chemin = []
        try:
            while pos != pos_init:
                chemin.append(pos)
                self.obs_mob[pos] = iden
                (x, y), t = pos
                self.obs_mob[((x,y), t+1)] = iden
                pos = came_from[pos]
        except KeyError:
            raise ut.ThereIsNoPath
            
        chemin.reverse()
        
        return chemin
    
    def run(self):
        """
        Tourne l'algorithme.
        """
        if self.verbose:
            print("Init states:", self.initStates)
            print("Goal states:", self.goalStates)
        self.execute()