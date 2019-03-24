# -*- coding: utf-8 -*-
#==============================================================================
# Import des bibliothèques
#==============================================================================
import heapq as hq
import utils as ut
import numpy as np
import time

#==============================================================================
# Import des fonctions codées
#==============================================================================
from Strategy import Strategy
from algo_A import algo_A

class temporal_A(Strategy):
    """
    Stratégie coopérative avancée en prenant en compte le temps.
    """
    
    def __init__(self, game, iterations, verbose = True):
        """
        Stratégie coopérative avancée en prenant en compte le temps.
        """
        super(temporal_A,self).__init__(game, iterations, verbose)
        self.obs_fixe = {w.get_rowcol() for w in game.layers['obstacle']}
        self.obs_mob = {(j, 0) for j in self.initStates}
        self.tab_dist = [algo_A(self.goalStates[joueur], self.initStates[joueur], self.obs_fixe, self.taille) for joueur in range(self.nbPlayers)]
        
    def setGoalStates(self, goalStates):
        """
        Permet de changer l'ordre des goalStates. Attention, les nouveaux goalStates
        doivent être une permutation des précédents.
        """
        super().setGoalStates(goalStates)
        self.tab_dist = [algo_A(self.goalStates[joueur], self.initStates[joueur], self.obs_fixe, self.taille) for joueur in range(self.nbPlayers)]
        
        
    def cost(pos, pos_next, pos_fin):
        """
        Coût d'un pas utilisé dans l'algorithme A* en espace-temps.
        Le coût vaut toujours 1 sauf lorsque le joueur est déjà à sa fiole et
        y reste, auquel cas il vaut 0.
        """
        if pos[0] == pos_next[0] and pos_next[0] == pos_fin:
            return 0
        return 1
    
    def is_finished(self):
        """
        Teste si tous les joueurs sont déjà arrivés à leurs respectives fioles.
        """
        for i in range(self.nbPlayers):
            if self.players[i].get_rowcol() != self.goalStates[i]:
                return False
        return True
        
        
    def chemin(self, iden):
        """
        Implémentation de l'algorithme A* en espace-temps avec l'heuristique
        de la distance réelle (algorithme A* en espace calculé à partir de la
        fiole par la classe algo_A).
        """
        pos_init = (self.initStates[iden], 0)
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
            
            if pos[1] == self.iterations - 1:
                break
            
            voisin = ut.voisins_temp(pos, self.obs_fixe, self.obs_mob, self.taille)
            for pos_next in voisin:
                new_cost = cost_so_far[pos] + temporal_A.cost(pos, pos_next, pos_fin)
                if pos_next not in cost_so_far or new_cost < cost_so_far[pos_next]:
                    cost_so_far[pos_next] = new_cost
                    priority = new_cost + self.tab_dist[iden].distance(pos_next[0])
                    #priority = new_cost + ut.dist_man(pos_fin, pos_next[0])
                    hq.heappush(frontier,(priority, pos_next)) 
                    came_from[pos_next] = pos   
        
        chemin = []
        
        # Pour éviter les croisements, on utilise la solution de rajouter,
        # losque le joueur passe par la case (x, y) à l'instant t, les points
        # ((x, y), t) et ((x, y), t+1) au tableau de réservation obs_mob.
        try:
            while pos != pos_init:
                chemin.append(pos)
                self.obs_mob.add(pos)
                (x, y), t = pos
                self.obs_mob.add(((x,y), t+1))
                pos = came_from[pos]
        except KeyError:
            raise ut.ThereIsNoPath

        # Une fois que le joueur arrive à la fiole, on réserve sa position
        # sur la fiole jusqu'à la fin des itérations. Cela peut créer un
        # problème si un autre joueur ayant reservé avant lui a déjà pris cette
        # case.
#==============================================================================
#         for t in range(chemin[0][1] + 2, self.iterations):
#             if (chemin[0][0], t) in self.obs_mob:
#                 raise ut.ThereIsNoPath("Sorry :'( J'arrive à la fiole mais je ne peux pas y rester car quelqu'un d'autre veut passer ici après !")
#             self.obs_mob.add((chemin[0][0], t))
#==============================================================================
            
        chemin.reverse()
        return chemin
    
    def run(self):
        """
        Tourne l'algorithme.
        """
        if self.verbose:
            print("Init states:", self.initStates)
            print("Goal states:", self.goalStates)
        
        # Temps de calcul des chemins afin de comparer les deux heuristiques.
        start = time.process_time()
        # Calcul des chemins
        tab_chemins = []
        for i in range(self.nbPlayers):
            tab_chemins.append(self.chemin(i))
        if self.verbose:
            print("Temps de calcul :",time.process_time() - start)
        tours = 0
        # Boucle principale
        for i in range(self.iterations):
            if self.is_finished():
                break
            
            # Pour chaque joueur, on lui déplace s'il n'est pas encore sur sa
            # fiole.
            for j in range(self.nbPlayers):
                if len(tab_chemins[j]) == 0 :
                    continue
                (x, y), t = tab_chemins[j].pop(0)
                if (x, y) != self.goalStates[j]:
                    self.players[j].set_rowcol(x, y)
                    if self.verbose:
                        print ("pos :", j, x, y)
                else:
                    if self.verbose:
                        print ("Objet trouvé par le joueur ", j,"\n")
                    self.players[j].set_rowcol(self.goalStates[j][0],self.goalStates[j][1])
            if self.verbose:
                print()
            self.game.mainiteration()
            tours += 1
            if self.verbose:
                print("tour :", tours)

        if self.verbose:
            print("temps total pour la récupération de toutes les fioles : ", tours)