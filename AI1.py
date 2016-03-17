import numpy as np
import pandas as pd
import random
from sklearn import linear_model
from copy import deepcopy


possible_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

class Troup:
    def __init__(self,x = 0, y = 0, size = 0, species = ""):
        self.x = x
        self.y = y
        self.size = size
        self.species = species
        self.type = "monster" if self.species in ['me','enemy'] else "human"
        
    def position(self):
        return (self.x,self.y)
    
    def value(self):
        return {(self.x,self.y):self.size}
    
    def distance(self,other):
        return max([abs(other.x-self.x),abs(other.y-self.y)])
    
    def is_winning(self,other):
        factor = 1.5
        if other.type == 'human':
            factor = 1
        if self.size > factor*other.size:
            return True
    
    def describe(self):
        print('> position : {0}    taille : {1}    espèce : {2}'.format(self.position(),self.size,self.species))
    
    def set_move(self,a,b):
        setattr(self,"x",self.x+a)
        setattr(self,"y",self.y+b)
        
    def move_toward(self,other):
        move = (np.sign(other.x-self.x),np.sign(other.y-self.y))
        return (int(self.x+move[0]),int(self.y+move[1]))
    
    def flee_from(self,other):
        move = (-np.sign(other.x-self.x),-np.sign(other.y-self.y))
        return (int(self.x+move[0]),int(self.y+move[1]))
    
    def heuristic(self,other,board):
        ratio = self.size/other.size
        factor = 1 if other.type == "human" else 1.5
        if ratio > factor:
            p = 1
        elif factor >= ratio >=1:
            p = ratio - 0.5
        elif ratio < 1:
            p = ratio * 0.5

        risk_factor = 0 if p < 0.5 else p
        
        expected_size_self = self.size*(p**2) if other.type != 'human' else (self.size+other.size)*(p**2)
        expected_size_other = other.size*((1-p)**2)
        
        difference_size_self = expected_size_self - self.size

        difference_size_other = expected_size_other - other.size
        relative_difference = difference_size_self - difference_size_other
        
        total_size_self = board.totalsize(self.species)
        total_size_other = board.totalsize(other.species)
        
        left_size_self = total_size_self + difference_size_self
        left_size_other = total_size_other + difference_size_other
        
        distance = self.distance(other)
        distance = distance if distance > 0 else 0.1

        h = (self.size/total_size_self)
        h *= risk_factor                        
        h *= abs(difference_size_other/difference_size_self) if difference_size_self != 0 else abs(difference_size_other)   
        h *= (left_size_self/left_size_other) if left_size_other != 0 else left_size_self
        h *= (1/distance)                                          
        
        return h
        
        
    
        
    

class Board:
    def __init__(self,lines = 6,columns = 10,player_aggressivity = 0.5,enemy_aggressivity = 0.5):
        self.me = {}
        self.enemy = {}
        self.humans = {}
        self.absence = []
        self.lines = lines
        self.columns = columns
        self.neural = []
        self.player_aggressivity = player_aggressivity
        self.enemy_aggressivity = enemy_aggressivity

        
    def value(self):
        return {"me":self.me,"humans":self.humans,"enemy":self.enemy}
    
    def valuev(self):
        return {"me":{x[1].position():x[1].size for x in self.me.items()},
                "humans":{x[1].position():x[1].size for x in self.humans.items()},
                "enemy":{x[1].position():x[1].size for x in self.enemy.items()}}
    
    def initialize(self,changes,learning = False):
        changes = [changes[5*n:5*n+5] for n in range(int(len(changes)/5))]
        for change in changes:
            if change[2] != 0:
                species = 'humans'
                size = change[2]
            elif change[3] != 0:
                species = 'me'
                size = change[3]
            elif change[4] != 0:
                species = 'enemy'
                size = change[4]
            else:
                self.absence += [(change[0],change[1])]
                continue
            troup = {(change[0],change[1]):Troup(x = change[0],y = change[1],size = size,species = species)}
            self.add_troup(species,troup)
        if learning:
            self.initialize_learning()

    def initialize_learning(self,datas = "learning_datas.text"):
        datas = open(datas,"r").read()
        datas = [x[1:-1] for x in datas.split('\n')][:-1]
        datas = [[float(x) for x in y.split(',')] for y in datas[:-1]]
        datas = np.array(datas)
        self.neural = datas


    
    def positions(self,species):
        return list(getattr(self,species).keys())
    
    def other_positions(self,species):
        other_species = [x for x in ['me','enemy','humans'] if x!= species]
        l = []
        for name in other_species:
            l += self.positions(name)
        return l
    
    def update(self,other):
        for species in ['me','enemy','humans']:
            other_species = self.other_positions(species)
            troups = getattr(self,species)
            for troup in other_species+other.absence:
                if troup in troups:
                    troups.pop(troup)
            troups.update(getattr(other,species))            
            setattr(self,species,troups)
            
    def set_move(self,node,a,b):
        troup = self.me[node]
        self.me.pop(node)
        troup.set_move(a,b)
        troup = {troup.position():troup}
        self.add_troup("me",troup)
        # new_node = node[0]+a,node[1]+b
        # if new_node in self.positions("enemy"):
        #     attack = True
        #     self.enemy.pop(new_node)
        # elif new_node in self.positions("humans"):
        #     attack = True
        #     self.humans.pop(new_node)
        # return attack
            
        
    def set_move_enemy(self,node,a,b):
        troup = self.enemy[node]
        self.enemy.pop(node)
        troup.set_move(a,b)
        troup = {troup.position():troup}
        self.add_troup("enemy",troup)
        new_node = node[0]+a,node[1]+b
        # if new_node in self.positions("me"):
        #     attack = True
        #     self.me.pop(new_node)
        # elif new_node in self.positions("humans"):
        #     attack = True
        #     self.humans.pop(new_node)
        # return attack
        
        
    def add_troup(self,species,troup):
        troups = getattr(self,species)
        troups.update(troup)
        setattr(self,species,troups)
    
    def all(self,species = ''):
        if species != '':
            return list(getattr(self,species).values())
        else:
            l = []
            for species in ['me','humans','enemy']:
                l += self.all(species)
            return l
    
    def all_troups(self):
        all_troups = {}
        for species in ['me','humans','enemy']:
            troups = getattr(self,species)
            for troup in troups:
                all_troups[troup] = troups[troup]
        return all_troups
    
    def all_positions(self):
        return list(self.all_troups().keys())
    
    def describe(self):
        print('_______________________ Board {0} x {1} ______________________'.format(self.columns,self.lines))
        print('PLAYER - total : {0}'.format(self.totalsize('me')))
        for troup in self.all('me'):
              troup.describe()
        print('-------------------------------------------')
        print('ENEMY - total : {0}'.format(self.totalsize('enemy')))
        for troup in self.all('enemy'):
              troup.describe()
        print('-------------------------------------------')
        print('HUMANS - total : {0}'.format(self.totalsize('humans')))
        for troup in self.all('humans'):
              troup.describe()
        
    def totalsize(self,species):
        troups = getattr(self,species)
        return sum([x.size for x in troups.values()])
    
    def heuristic(self,species1 = '',species2 = '',player_aggressivity = 0.5,enemy_aggressivity = 0.5,just_score = True):
        if species1 != '':
            score = 0
            for attacker in self.all(species1):
                for defenser in self.all(species2):
                    score += attacker.heuristic(defenser,self)
            return score
        else:
            score = 0
            attack_heuristic_player = self.heuristic('me','enemy')
            attack_heuristic_enemy = self.heuristic('enemy','me')
            defense_heuristic_player = self.heuristic('me','humans')
            defense_heuristic_enemy = self.heuristic('enemy','humans')

            score += player_aggressivity*attack_heuristic_player
            score += (1-player_aggressivity)*defense_heuristic_player
            score -= (1-enemy_aggressivity)*defense_heuristic_enemy
            if just_score:
                return score
            else:
                return score,attack_heuristic_player,attack_heuristic_enemy,defense_heuristic_player,defense_heuristic_enemy,player_aggressivity,enemy_aggressivity

    def learning(self,writing = False,learning = False) :
        player_aggressivity = self.player_aggressivity
        enemy_aggressivity = self.enemy_aggressivity
        new_data = list(self.heuristic('','',player_aggressivity,enemy_aggressivity,False))
        if writing:
            with open("learning_datas.text", "a") as myfile:
                myfile.write(str(new_data)+"\n")
        if learning:
            new_data = new_data[:-2]
            clf = linear_model.LinearRegression()
            X = self.neural[:,:5]
            y = self.neural[:,5]
            z = self.neural[:,6]
            print(player_aggressivity,enemy_aggressivity)
            clf.fit(X,y)
            player_aggressivity = float(clf.predict([new_data]))
            clf.fit(X,z)
            enemy_aggressivity = float(clf.predict([new_data]))
            self.player_aggressivity = player_aggressivity
            self.enemy_aggressivity = enemy_aggressivity
            new_data = new_data + [player_aggressivity,enemy_aggressivity]
            self.neural = np.vstack([self.neural,new_data])


    def stronger_than_me(self,troup):
        return None
    
    def possible_move(self,node,a,b,depth = 0):
        x,y = node
        if (a == 0 and b == 0) or x+a<0 or x+a>=self.columns or y+b<0 or y+b>= self.lines:
            return False
#         elif depth > 0 and (x+a,y+b) in self.all_positions():
#             return False
        else:
            return True
    
    def most_dangerous_enemy(self):
        if len(self.enemy) > 0:
            return max(self.enemy.items(),key = lambda t:t[1].size)
        else:
            return ()


    def tree(self,node,max_depth = 0,player_aggressivity = 0.5,enemy_aggressivity = 0.5,depth = 0):
        tree = {node:{'score':self.heuristic('','',player_aggressivity,enemy_aggressivity),'leaves':{}}}
        species = self.all_troups()[node].species
        if (species == "enemy" and len(self.all('me'))>0) or (species == "me" and len(self.most_dangerous_enemy())>0):
            next_node = self.most_dangerous_enemy()[0] if species == "me" else self.all('me')[0].position()
        else:
            return tree
        for move in [(a,b) for (a,b) in possible_moves if self.possible_move(node,a,b,depth)]:
            temp = deepcopy(self)
            if species == "me":
                attack = temp.set_move(node,move[0],move[1])
            else:
                attack = temp.set_move_enemy(node,move[0],move[1])
            tree[node]['leaves'].update({move:{'score':temp.heuristic('','',player_aggressivity,enemy_aggressivity),'leaves':{}}})
            if depth < max_depth:
                tree[node]['leaves'][move]['leaves'] = temp.tree(next_node,max_depth,player_aggressivity,enemy_aggressivity,depth+1)
        return tree
        
    def minmax(self,tree,max_depth,depth = 0,type_choice = "max"):
        choices = list(tree.values())
        if choices == [] or depth > max_depth or len(choices[0]['leaves'])==0:
            if type_choice == "min":
                return ("",{"score":1})
            else:
                return ("",{"score":0})
        else:
            choices = choices[0]['leaves']
            if type_choice == "max":
                choice = max(choices.items(),key = lambda t:(min((t[1]['score'],self.minmax(t[1]['leaves'],max_depth,depth + 1,"min")[1]['score'])),random.random()))
            else:
                choice = min(choices.items(),key = lambda t:(max((t[1]['score'],self.minmax(t[1]['leaves'],max_depth,depth + 1,"max")[1]['score'])),random.random()))
            return choice
        
    def choices(self,max_depth = 0,player_aggressivity = 0.5,enemy_aggressivity = 0.5):
        node = self.all('me')[0].position()
        tree = self.tree(node,max_depth,player_aggressivity,enemy_aggressivity)
        best_move = []
        for i in range(max_depth+1):
            best_move += [self.minmax(tree,i)[0]]
        return best_move
    
    def best_choice(self,max_depth = 0,player_aggressivity = 0.5,enemy_aggressivity = 0.5):
        node = self.all('me')[0].position()
        tree = self.tree(node,max_depth,player_aggressivity,enemy_aggressivity)
        return self.minmax(tree,max_depth)
    
    def AI(self,sock,max_depth = 0):
        player_aggressivity = self.player_aggressivity
        enemy_aggressivity = self.enemy_aggressivity
        print('AI')
        best_move = self.best_choice(max_depth,player_aggressivity,enemy_aggressivity)
        score = best_move[1]['score']
        best_move = best_move[0]
        # print("{0} score : {1}".format(best_move,score))
        me = self.all('me')[0]
        x,y,size = me.x,me.y,me.size
        xnew,ynew = x+best_move[0],y+best_move[1]
        order = [(x,y,size,xnew,ynew)]
        return order
        # attente(0.5)
        # return best_move

        
def attente(secondes = 0.5):
    '''Fonction d'attente pour que les mouvements soient perceptibles'''
    time.sleep(secondes)