## Import

import socket
import struct
import sys
import numpy as np          #rajouté
import time                 #rajouté
from random import randint  #rajouté


#-------------------------------------------------------------------------------------------------------
# Connexion au serveur

#Le script va prendre en ligne de commande le port et l'adresse IP

def send(sock, *messages):
    for message in messages:
        try:
            if isinstance(message, int):
                data = struct.pack('=B', message)
            elif isinstance(message,str):
                data = message.encode()
            else:
                data = message
            sock.send(data)
        except:
            print("Couldn't send message: ", message)



#Création de la socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connexion de la socket
try:
    sock.connect(("127.0.0.1", 5555)) #Changez ici l'adresse ip et le port
except Exception as error:
    print("Connection error: ", error)

#Envoi du nom
groupname = "Wolfgang" #mettez ici le nom de votre équipe
send(sock, "NME", len(groupname), groupname)





#-------------------------------------------------------------------------------------------------------
# AI


def attente(secondes = 0.5):
    '''Fonction d'attente pour que les mouvements soient perceptibles'''
    time.sleep(secondes)

def distance(node1,node2):
    '''Renvoie la distance entre deux points, c'est à dire le nombre de coups nécessaires pour aller d'un point à l'autre'''
    x1,y1 = node1
    x2,y2 = node2 
    return max([abs(y2-y1),abs(x2-x1)])

def set_positions(changes):
    '''Permet de prendre une liste des changements (ou positions initiales) et construit le dictionnaire d'état des positions'''
    #Dictionnaire vide
    states = {'humans':{},'me':{},'enemy':{}}
    #Stocke les cases qui sont devenues vides
    absence = []
    #Coupe l'ensemble des changements en une liste de changements
    changes = [changes[5*n:5*n+5] for n in range(int(len(changes)/5))]
    #Itération sur chaque changement, et attribution de la position à chaque espèce
    for change in changes:
        position = (change[0],change[1])
        if change[2] != 0:
            states['humans'][position] = change[2]
        elif change[3] != 0:
            states['me'][position] = change[3]
        elif change[4] != 0:
            states['enemy'][position] = change[4]
        else:
            absence += [position]
    return states,absence

def update_positions(old_position,new_position):
    '''Met à jour le dictionnaire d'état des positions avec les changements à chaque tour
       Prend en compte les changements de case et les attaques de groupes'''
    updated = old_position      #Anciennes positions
    new = new_position[0]       #Nouvelles positions
    absence = new_position[1]   #Absences 

    #Itération sur chaque espèce
    for species in new.keys():

        #Construction des positions des autres espèces pour vérifier que telle espèce ne s'est pas fait tuée
        other_species = [list(new[x].keys()) for x in ['humans','me','enemy'] if x!=species]
        other_species = [x for y in other_species for x in y]

        #Pour chaque nouvelle position on met à jour le dictionnaire des positions
        for position in new[species].keys():
            updated[species][position] = new[species][position]

        #Pour chaque position finale, on vérifie que cette position n'est pas sensée avoir disparue (case vide) ou si l'espèce n'est pas morte
        for position in list(updated[species]):
            if position in absence or position in other_species:
                updated[species].pop(position)
    return updated

def possible_move(x,y,a,b,positions,lignes,colonnes):
    '''Booléen vrai si un mouvement x->x+a y->y+b est possible (borne du terrain,immobile,déjà quelqu'un sur la case)'''    
    impossible = list(positions['humans'])
    impossible += list(positions['enemy'])
    impossible += list(positions['me'])
    if (a==0 and b ==0) or x+a<0 or x+a>=colonnes or y+b<0 or y+b>= lignes or (x+a,y+b) in impossible:
        return False
    else:
        return True

def random_move(x,y,positions,lignes,colonnes):
    '''Définit un mouvement aléatoire dans une case valide'''
    a = 0
    b = 0
    while possible_move(x,y,a,b,positions,lignes,colonnes) == False:
        a = randint(-1,1)
        b = randint(-1,1)
    print("mouvement de {0} {1}".format(a,b))
    print(x,y)
    print(a,b)
    print(x+a,y+b)
    return (x+a,y+b)


#--------------------------------------------------------------------------------------------------------------
# Fonctions d'Intelligences Artificielles


def ai_random_move_group(positions):
    '''Intelligence Artificielle qui déplace de manière aléatoire un ou plusieurs individus'''
    print('AI Random Move Group')
    groups = positions['me'].items()
    for group in groups:
        x,y=group[0]
        size = randint(1,group[1])
        xnew,ynew=x,y
        newmove = random_move(x,y,positions,lignes,colonnes)
        xnew,ynew = newmove[0],newmove[1]
        send(sock,"MOV",1,x,y,size,xnew,ynew)
    attente()

def ai_random_move_block(positions):
    '''Intelligence Artificielle qui déplace de manière aléatoire l'ensemble du groupe'''
    print('AI Random Move Block')
    group = list(positions['me'].items())[0]
    x,y = group[0]
    size = group[1]
    newmove = random_move(x,y,positions,lignes,colonnes)
    xnew,ynew = newmove[0],newmove[1]
    send(sock, "MOV", 1,x,y,size,xnew,ynew)
    attente()

def ai_weakest_attack_move(positions):
    '''Intelligence artificielle pour attaquer tout le monde (humains et ennemis) par ordre de faiblesse'''
    print('AI weakeast attack move')
    humans = list(positions['humans'].items())
    humans += list(positions['enemy'].items()) #à supprimer pour ne pas attaquer les ennemis 

    nb_villages = len(humans)
    #village = list(humans.items())[randint(0,nb_villages-1)]
    if nb_villages > 0:
        village = min(humans,key = lambda t:t[1]) 
        xh,yh = village[0][0],village[0][1]
        sizeh = village[1]

        group = list(positions['me'].items())[0]
        x,y = group[0]
        size = group[1]

        if size > sizeh:
            print('Attacking the village')
            while abs(xh-x)>=1 and abs(yh-y)>=1:
                xnew = x+1 if x<xh else x-1
                ynew = y+1 if y<yh else y-1
                send(sock,"MOV",1,x,y,size,xnew,ynew)
                x,y = xnew,ynew
            while abs(xh-x)>=1:
                xnew = x+1 if x<xh else x-1
                ynew = y
                send(sock,"MOV",1,x,y,size,xnew,ynew)
                x,y = xnew,ynew
            while abs(yh-y)>=1:
                xnew = x
                ynew = y+1 if y<yh else y-1
                send(sock,"MOV",1,x,y,size,xnew,ynew)
                x,y = xnew,ynew
            attente()

        else:
            print('Not attacking the village, too small')
    else:
        print('No more human villages')


def ai_closest_attack_move(positions):
    '''Attaque les ennemis les plus proches s'il est possible de les attaquer'''
    return True







#-------------------------------------------------------------------------------------------------------




#Main Loop
test = 0
while True:
    order = sock.recv(3)
    print('--------------------------------------------------------------------------------')
    print('New loop')
    order = order.decode(encoding = 'utf8')

    if not order:
        print("Bizarre, c'est vide")

    if order =="SET":
        print('set')
        lignes = struct.unpack('=B',sock.recv(1))[0]
        colonnes = struct.unpack('=B',sock.recv(1))[0]
        print('size')
        print(lignes,colonnes)
    elif order == "HUM":
        print('hum')
        n = struct.unpack('=B', sock.recv(1))[0]
        maisons = []
        for i in range(n):
            x = struct.unpack('=B',sock.recv(1))[0]
            y = struct.unpack('=B',sock.recv(1))[0]
            maisons.append((x,y))
    elif order == "HME":
        print('hme')
        x = struct.unpack('=B',sock.recv(1))[0]
        y = struct.unpack('=B',sock.recv(1))[0]
        print(x,y)
        #ajoutez le code ici (x,y) étant les coordonnées de votre
        #maison
    elif order == "UPD":    
        print('upd')
        n = struct.unpack('=B', sock.recv(1))[0]
        changes = []
        for i in range(n):
            for i in range(5):
                changes.append(struct.unpack('=B', sock.recv(1))[0])

        print(changes)
        

        
        '''Mise à jour des positions avec les changements du tour précédent'''
        new_positions = set_positions(changes)
        positions = update_positions(positions,new_positions)
        
        '''Intelligence Artificielle'''
        ''' - Choisir une des intelligences artificielles ci-dessous pour tester'''
        ai_weakest_attack_move(positions)
        #ai_random_move_group(positions)
        #ai_random_move_block(positions)

        print(positions)

    elif order == "MAP":
        print('map')
        n = struct.unpack('=B', sock.recv(1))[0]
        changes = []
        for i in range(n):
            for i in range(5):
                changes.append(struct.unpack('=B', sock.recv(1))[0])

        positions = set_positions(changes)[0]




        #initialisez votre carte à partir des tuples contenus dans changes
    elif order == "END":
        break
        #ici on met fin à la partie en cours
        #Réinitialisez votre modèle
    elif order == "BYE":
        break
    else:
        print("commande non attendue recue", order)

#Préparez ici la déconnexion

#Fermeture de la socket
sock.close()
