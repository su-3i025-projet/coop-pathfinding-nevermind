# -*- coding: utf-8 -*-
class Strategy():
    """
    Classe de base pour les stratégies implémentées.
    """
    def __init__(self, game, iterations, verbose = True):
        """
        game : objet du jeu
        iterations : nombre maximal d'itérations
        verbose : Si True, fait des affichages.
        """
        self.game = game
        self.iterations = iterations
        self.verbose = verbose
        pos_play = [(o.get_rowcol(), o) for o in self.game.layers['joueur']]
        #Comme cela on peut trier les joueurs et être certain de leur ordre 
        #à n'importe quel OS.
        pos_play.sort()
        self.players = [play for (pos, play) in pos_play]
        self.nbPlayers = len(self.players)
        self.goalStates = [o.get_rowcol() for o in self.game.layers['ramassable']]
        self.initStates = [pos for (pos, play) in pos_play]
        self.wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
        self.taille = (game.spriteBuilder.rowsize, game.spriteBuilder.colsize)
        
    
    def setGoalStates(self, goalStates):
        """
        Permet de changer l'ordre des goalStates. Attention, les nouveaux goalStates
        doivent être une permutation des précédents.
        """
        if {o for o in self.goalStates} != {o for o in goalStates}:
            raise Exception("Le noveau goalStates n'est pas une permutation de l'ancien.\nself.goalStates : "+str(self.goalStates)+"\ngoalStates :"+str(goalStates))
        self.goalStates = goalStates