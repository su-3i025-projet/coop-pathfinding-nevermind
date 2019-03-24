# -*- coding: utf-8 -*-
#==============================================================================
# Import des bibliothèques
#==============================================================================
import heapq as hq
import utils as ut

class algo_A():
    """
    Algorithme A* pour le calcul de la distance réelle dans les algorithmes
    coopératifs avancés.
    L'implémentation de A* est décomposée en deux parties. L'initialisation des
    variables est faite dans __init__. La fonction distance calcule la distance
    réelle entre pos_init et la cible en faisant tourner l'algorithme jusqu'à
    ce que la cible soit fermée.
    """
    def __init__(self, pos_init, pos_fin, obs_fixe, taille):
        """
        pos_init : position de la fiole cible (on fait le chemin inverse).
        pos_fin : position initiale du joueur.
        obs_fixe : ensemble des obstacles fixes.
        taille : duplet contenant le nombre de lignes et de colonnes du monde.
        """
        self.pos_init = pos_init
        self.pos_fin = pos_fin
        self.obs_fixe = obs_fixe
        self.taille = taille
        
        # Initialisation du tas
        self.frontier =  []
        hq.heappush(self.frontier,(0, self.pos_init)) 

        # Dictionnaire avec les distances à chaque point déjà calculées.
        self.cost_so_far = {}
        self.cost_so_far[self.pos_init] = 0
        
        # Ensemble contenant les points dont la distance est connue.
        self.ferme = set()

    
    
    def distance(self, cible):
        """
        Version modifiée de l'algorithme A*. Tourne jusqu'à ce que la distance
        de self.pos_init à cible soit connue.
        """
        while cible not in self.ferme:
            _,pos = hq.heappop(self.frontier)
            self.ferme.add(pos)
            
            voisin = ut.voisins(pos, self.obs_fixe, self.taille)
            for pos_next in voisin:
                new_cost = self.cost_so_far[pos] + 1
                if pos_next not in self.cost_so_far or new_cost < self.cost_so_far[pos_next]:
                    self.cost_so_far[pos_next] = new_cost
                    priority = new_cost + ut.dist_man(self.pos_fin, pos_next)
                    hq.heappush(self.frontier,(priority, pos_next)) 

        return self.cost_so_far[cible]