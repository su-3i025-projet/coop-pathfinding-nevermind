# -*- coding: utf-8 -*-

#==============================================================================
# Import des bibliothèques
#==============================================================================
import heapq as hq

#==============================================================================
# Afichages
#==============================================================================
def afficher_liste(l):
    """
    Affiche une liste avec un élément par ligne.
    """
    for e in l:
        print(e)

def afficher_matrice(m):
    """
    Affiche une matrice avec un élément par ligne.
    """
    for i in range(len(m)):
        print(m[i])

def afficher_dico(d):
    """
    Affiche un dictionnaire avec une paire clé-valeur par ligne.
    """
    for k in d:
        print(k,":", d[k])

def affiche_monde(wallStates, tab_chemins, taille):
    """
    Affiche un monde 2D carré de taille taille et les chemins de tab_chemin 
    (maximum 10 chemins). Les murs sont affichés comme '#', les chemins avec
    le nombre correspondant a son indice en tab_chemin.
    """
    monde = [[' ']*taille for i in range(taille)]
    chem = "0123456789"
    
    # wallsates
    for x,y in wallStates:
        monde[x][y] = '#'
    # chemins
    for i in range (len(tab_chemins)):
        for x,y in tab_chemins[i]:
            monde[x][y] = chem[i]
    
    # affichage
    for i in range(taille):
        str = ""
        for j in range(taille):
            str += monde[i][j]
        print(str)
    print()

#==============================================================================
# Heuristique pour les distances
#==============================================================================
def dist_man(pos1, pos2):
    """
    Calcule la distance de Manhattan entre 2 points 2D.
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

#==============================================================================
# Liste de pas possibles
#==============================================================================
def voisins(pos, obstacles, taille):
    """
    Retourne la liste de positions voisines possibles a partir de pos et 
    le tableau des obstacles.
    taille : duplet contenant le nombre de lignes et de colonnes du monde.
    """
    res = []
    x, y = pos
    for i, j in [(0,1),(0,-1),(1,0),(-1,0)]:
        if ((x + i,y + j) not in obstacles) and (x + i) >= 0 and (x + i) < taille[0] and (y + j) >= 0 and (y + j) < taille[1]:
            res.append((x+i, y + j))
    return res

def voisins_temp(pos, obs_fixe, obs_mob, taille):
    """
    Retourne la liste de positions voisines possibles a partir de pos et 
    l'ensemble des obstacles fixes (obs_fixe) et mobiles (obs_mob).
    obs_fixe : ensemble de duplets de coordonnées spatiales.
    obs_mob : ensemble de duplets de la forme ((x, y), t).
    taille : duplet contenant le nombre de lignes et de colonnes du monde.
    """
    res = []
    (x, y), t = pos
    for i, j in [(0,1),(0,-1),(1,0),(-1,0), (0,0)]:
        if ((x + i,y + j) not in obs_fixe) and (((x + i,y + j), t + 1) not in obs_mob) and (x + i) >= 0 and (x + i) < taille[0] and (y + j) >= 0 and (y + j) < taille[1]:
            res.append(((x + i, y + j), t + 1))
    return res

def voisins_tempD(iden, pos, obs_fixe, obs_mob, taille):
    """
    Retourne la liste de positions voisines possibles a partir de pos et 
    l'ensemble des obstacles fixes (obs_fixe) et mobiles (obs_mob).
    Prend en compte dans le calcul si l'obstacle mobile a été réservé par le
    joueur iden lui-même ou pas.
    iden : identifiant du joeur.
    obs_fixe : ensemble de duplets de coordonnées spatiales.
    obs_mob : dictionnaire indexé par duplets de la forme ((x, y), t) et
              contenant comme valeur l'identifiant du joueur ayant réservé.
    taille : duplet contenant le nombre de lignes et de colonnes du monde.
    """
    res = []
    (x, y), t = pos
    for i, j in [(0,1),(0,-1),(1,0),(-1,0), (0,0)]:
        # On vérifie d'abord si on est à l'intérieur de la grille
        if (x + i) >= 0 and (x + i) < taille[0] and (y + j) >= 0 and (y + j) < taille[1]:
            # On vérifie que ce n'est pas un obstacle fixe
            if (x + i,y + j) not in obs_fixe:
                # On vérifie si le seuls obstacles mobiles dans les deux prochains instants
                # de temps sont le joueur lui-même
                if ((x + i,y + j), t + 1) not in obs_mob or obs_mob[((x + i,y + j), t + 1)]==iden:
                    if ((x + i,y + j), t + 2) not in obs_mob or obs_mob[((x + i,y + j), t + 2)]==iden :
                        res.append(((x + i, y + j), t + 1))
    return res


def detecte_collision(obstacles, chemin):
    """
    Détecte si le chemin collide avec un des obstacles.
    """
    for pos in chemin:
        if pos in obstacles:
            return True
    return False

def recalcule_obs_fixe(obstacles, iterations):
    """
    Manière naïve de transformer les obstacles fixes 2D (x, y) en obstacles
    avec le temps.
    """
    return {(obs, i) for i in range(iterations) for obs in obstacles}

#==============================================================================
# Algorithme A*
#==============================================================================
    
class ThereIsNoPath(Exception):
    """
    Exception levée lorsque l'algorithme ne trouve pas de chemin.
    """
    pass

def calcul_chemin(pos_init, pos_fin, obstacles, taille):
    """
    Algorithme A* pour le calcul du chemin le plus court en utilisant comme
    heuristique la distance de Manhattan.
    pos_init : point de départ
    pos_fin : point d'arrivée
    obstacles : tableau d'obstacles
    taille : duplet contenant le nombre de lignes et de colonnes du monde.
    Utilisée dans les stratégies stratSlicing et stratCoopBase.
    """
    pos = pos_init
    frontier =  []
    hq.heappush(frontier,(0, pos)) 
    came_from = {}
    cost_so_far = {}
    came_from[pos] = None
    cost_so_far[pos] = 0

    while len(frontier) != 0:
        _,pos = hq.heappop(frontier)
        
        if pos == pos_fin:
            break
        
        voisin = voisins(pos, obstacles, taille)
        for pos_next in voisin:
            new_cost = cost_so_far[pos] + dist_man(pos, pos_next)
            if pos_next not in cost_so_far or new_cost < cost_so_far[pos_next]:
                cost_so_far[pos_next] = new_cost
                priority = new_cost + dist_man(pos_fin, pos_next)
                hq.heappush(frontier,(priority, pos_next)) 
                came_from[pos_next] = pos   
    
    chemin = []
    pos = pos_fin
    try:
        while pos != pos_init:
            chemin.append(pos)
            pos = came_from[pos]
    except KeyError:
        raise ThereIsNoPath
    chemin.reverse()
    return chemin