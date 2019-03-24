# -*- coding: utf-8 -*-
#==============================================================================
# Import des bibliothèques
#==============================================================================
import operator
import numpy as np
import utils as ut

#==============================================================================
# Import des fonctions codées
#==============================================================================
from Strategy import Strategy

class CoopBase(Strategy):
    """
    Stratégie coopérative de base.
    """
    
    def __init__(self, game, iterations, verbose = True):
        """
        Stratégie coopérative de base.
        """
        super(CoopBase,self).__init__(game, iterations, verbose)
        for state in self.initStates:    # éviter les collisions au début
            self.wallStates.append(state)

    
    def liste_collisions_chemins(chemin1, chemin2):
        """
        Retourne une liste avec toutes les positions en commun entre chemin1 et chemin2.
        """
        liste_collisions = []
        for pos in chemin1:
            if pos in chemin2:
                liste_collisions.append(pos)
        return liste_collisions


    def matrice_collisions(tab_chemins):
        """
        Crée une matrice n x n, ou n est la quantité de chemins en tab_chemins.
        La case i x j de la matrice contient 1 s'il y a de collisions entre les 
        chemins i et j, 0 sinon et -1 si i = j. 
        """
        n = len(tab_chemins)
        mat = np.eye(n, dtype = int) * -1   
        for i in range(n):
            for j in range(i + 1, n):
                chemin1 = tab_chemins[i]
                chemin2 = tab_chemins[j]
                liste_collisions = CoopBase.liste_collisions_chemins(chemin1, chemin2)
                if liste_collisions != []: 
                    mat[i,j] = 1
                    mat[j,i] = 1
        return mat

    def compteur_0_collisions(matrice_collisions):
        """
        Retourne un dictionnaire comptabilisant le nombre de '0' pour chaque chemin.
        Le chemin c1 a 3 '0' => c1 ne croise pas 3 autres chemins.
        """
        n = matrice_collisions.shape[0]
        dico = {i:0 for i in range(n)}
        for i in range(n):
            dico[i] = (matrice_collisions[i,:] == 0).sum()
        return dico

    def get_argmax_key(dico):
        """ 
        Retourne la clé ayant la plus grande valeur associée.
        """
        return max(dico.items(), key = operator.itemgetter(1))[0]

    def path_doesnt_intersect(matrice_collisions, p1, lPath):
        """ 
        Intersection d'un chemin avec une liste de chemins.
        """
        for path in lPath:
            if matrice_collisions[p1, path] > 0:
                return False
        return True

    def get_parallel_paths_to(matrice_collisions, path, dico_cpt_0_collisions):
        """ 
        Retourne une liste de chemins qui ne se croisent pas, dinstingués par
        leurs indices. Cette liste commence en ne contenant que path et ensuite
        d'autres chemins sont ajoutés successivement si ils ne croisent pas les
        chemins déjà présents.
        """
        lPath = [path]
        n = matrice_collisions.shape[0]
        for i in range(n):
            if matrice_collisions[path, i] == 0:
                if i in dico_cpt_0_collisions:
                    if CoopBase.path_doesnt_intersect(matrice_collisions, i, lPath):
                        lPath.append(i)
        return lPath

    def indices_groupes(matrice_collisions, dico):
        """ 
        Retourne tous les chemins pouvant etre joués ensemble (regroupés par
        groupes), dinstingués par leurs indices.
        On commence chaque groupe avec le chemin ayant le plus petit nombre de
        croisements (plus grand nombre de zéros dans matrice_collisions).
        """
        parallel_groups = []
        while (bool(dico)):
            mx = CoopBase.get_argmax_key(dico)
            parallel_group = CoopBase.get_parallel_paths_to(matrice_collisions, mx, dico)
            parallel_groups.append(parallel_group)
            for k in parallel_group:
                del dico[k]
        return parallel_groups

    def execution_groupes(self, index_groups, dico_indices):
        """ 
        Execution séquentielle des groupes de index_groups.
        Tous les chemins d'un groupe sont joués en paralèlle.
        """
        tours = 0
        # Bornes maximales et minimales sur le temps en nombre de pas.
        b_max = sum([len(dico_indices[k][2]) for k in dico_indices])
        b_min = max([len(dico_indices[k][2]) for k in dico_indices])
        
        # Exécution d'un groupe
        for index_group in index_groups:
            # Nombre de joueurs dans le groupe
            nbPlayers = len(index_group)
            # score détermine si chaque joueur du groupe est à sa fiole.
            score = {k:0 for k in index_group}
            # Boucle principale pour ce groupe
            for i in range(self.iterations):
                # Boucle sur les chemins
                for path_index in index_group:
                    player = dico_indices[path_index][0]
                    # Si le chemin est déjà fini, on passe au prochain.
                    if len(dico_indices[path_index][2]) == 0 :
                        continue
                    (x,y) = dico_indices[path_index][2][0]
                    del dico_indices[path_index][2][0]
                    if (x, y) != dico_indices[path_index][1]:
                        player.set_rowcol(x,y) 
                        if self.verbose:
                            print ("pos :",path_index,x,y)
                    else:
                        if self.verbose:
                            print ("Objet trouvé par le joueur ", path_index,"\n")
                        player.set_rowcol(dico_indices[path_index][1][0], dico_indices[path_index][1][1])
                        score[path_index]+=1
                if self.verbose:
                    print()
                self.game.mainiteration()
                tours += 1
                if sum(score.values()) == nbPlayers:
                    break
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
        # k : [player, goalState, path]
        dico_indices = {i:[] for i in range(self.nbPlayers)}
        
        tab_chemin = []
        for i in range(self.nbPlayers):
            dico_indices[i].append(self.players[i])
            dico_indices[i].append(self.goalStates[i])
            obstacles =  self.wallStates + [self.goalStates[j] for j in range(self.nbPlayers) if j != i]
            tab_chemin.append(ut.calcul_chemin(self.initStates[i], self.goalStates[i], obstacles, self.taille))
            dico_indices[i].append(tab_chemin[-1])
    
        mc = CoopBase.matrice_collisions(tab_chemin)
        d = CoopBase.compteur_0_collisions(mc)
        indice_groupes = CoopBase.indices_groupes(mc, d)
        self.execution_groupes(indice_groupes, dico_indices)
