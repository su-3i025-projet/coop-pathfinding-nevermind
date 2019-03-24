# -*- coding: utf-8 -*-
#==============================================================================
# Import des bibliothèques
#==============================================================================
import numpy as np
import utils as ut

#==============================================================================
# Import des fonctions codées
#==============================================================================
from Strategy import Strategy

class Slicing(Strategy):
    """
    Stratégie de slicing.
    """
	
    def __init__(self, game, iterations, m = 3, n = 2, max_slice = 10, verbose = True):
        """
        Stratégie de slicing.
        m : longueur qu'on regarde dans le futur pour le slicing.
        n : nombre de pas de temps entre deux slicing. On doit avoir m > n.
        max_slice : la taille maximale du nouveau slice ne doit pas dépasser max_slice * m.
        Si cela arrive, on recalcule le chemin directement vers la fiole.
        """
        super(Slicing,self).__init__(game, iterations, verbose)
        self.m = m
        self.n = n
        self.max_slice = max_slice
        
    
    def ajouter_obstacles(self, obstacles, chemin):
        """
        Ajoute les points de la liste chemin dans la liste d'obstacles.
        """
        for i in range(self.m):
            if i >= len(chemin):
                break
            obstacles.append(chemin[i])
    
    def modifie_slice(self, obstacles, pos_curr, chemin, target):
        """
        Modifie un chemin entre les cases 0 et self.m afin de contourner un
        obstacle rencontré.
        obstacles : liste d'obstacles.
        pos_curr : position initiale (chemin[0] contient la prochaine case).
        chemin : chemin à modifier.
        target : position de la fiole.
        """
        # Si le chemin est plus long que self.m, on modifie uniquement les m
        # premières cases.
        if self.m < len(chemin):
            sli = chemin[:self.m]
            reste = chemin[self.m:]
        # Sinon, on modifie tout.
        else:
            sli = chemin
            reste = []
        # S'il y a une collision, on modifie le chemin.
        if ut.detecte_collision(obstacles, sli):
            if self.verbose:
                print("Calcul d'un nouveau chemin de ",pos_curr," à ",sli[-1],".",sep = "")
            detourFound = True
            try:
                # Essaie de trouver un chemin de la position courante à sli[-1]
                detour = ut.calcul_chemin(pos_curr, sli[-1], obstacles, self.taille)
            except ut.ThereIsNoPath:
                detourFound = False
            if (not detourFound) or (len(detour) >= self.max_slice * self.m):
                # Si impossible ou si le detour serait trop long, calculer un chemin direct jusqu'au bout.
                try:
                    return ut.calcul_chemin(pos_curr, target, obstacles,self.taille)
                except ut.ThereIsNoPath:
                    # Si ce n'est possible, on reste arrête les n prochaines itérations
                    return [pos_curr]*self.n + chemin
            else:
                return detour + reste
        # S'il n'y a pas de collision, on renvoie le chemin de départ
        else:
            return chemin

    def execute(self, dico_indices):
        """
        Execute l'algorithme de slicing.
        dico_indices : dictionnaire indexé par les entiers où chaque valeur
                       correspond a un triplet [player, goalState, chemin].
        """
        tours = 0
        # Bornes maximales et minimales sur le temps en nombre de pas.
        b_max = sum([len(dico_indices[k][2]) for k in dico_indices])
        b_min = max([len(dico_indices[k][2]) for k in dico_indices])
        
        # fini[i] == True si et seulement si le joueur i est déjà sur sa fiole.
        fini = np.zeros(self.nbPlayers, dtype = bool)
        # Position courante des joueurs.
        current_pos = self.initStates.copy()
        
        for i in range(self.iterations):
            if np.all(fini):
                break
        
            # Toutes les self.n itérations, on vérifie s'il faut recalculer.
            if i % self.n == 0:
                obstacles = self.wallStates.copy()
                for k in range(self.nbPlayers):
                    obstacles.append(current_pos[k])
                
                # Pour chaque joueur, on vérifie s'il faut modifier sa trajectoire
                # sur les self.m prochains pas de temps.
                for k in dico_indices:
                    chemin = dico_indices[k][2]
                    target = dico_indices[k][1]
                    if fini[k]:
                        continue
                    dico_indices[k][2] = self.modifie_slice(obstacles, current_pos[k], chemin, target)
                    self.ajouter_obstacles(obstacles, dico_indices[k][2])
            
            # On exécute les actions des joueurs pour un pas de temps.
            for k in dico_indices:
                if fini[k]:
                    continue
                player = dico_indices[k][0]
                (x,y) = dico_indices[k][2][0]
                current_pos[k] = (x, y)
                del dico_indices[k][2][0]
                player.set_rowcol(x, y) 
                if self.verbose:
                    print ("pos :", k, x, y)
                
                if (x, y) == dico_indices[k][1]:
                    fini[k] = True
                    
            if self.verbose:
                print()
            self.game.mainiteration()
            tours += 1
            if self.verbose:
                print("tour :", tours)
                
        if self.verbose:
            print("temps total pour la récupération de toutes les fioles : ", tours)
            print("borne superieure de temps : ", b_max)
            print("borne inferieure de temps : ", b_min)
            
    def run(self):
        """
        Tourne l'algorithme.
        """
        if self.verbose:
            print("Init states:", self.initStates)
            print("Goal states:", self.goalStates)
        
        # Construction de dico_indices.
        # k : [player, goalState, chemin]
        dico_indices = {i:[] for i in range(self.nbPlayers)}
        
        for i in range(self.nbPlayers):
            dico_indices[i].append(self.players[i])
            dico_indices[i].append(self.goalStates[i])
            dico_indices[i].append(ut.calcul_chemin(self.initStates[i], self.goalStates[i], self.wallStates, self.taille))

        self.execute(dico_indices)