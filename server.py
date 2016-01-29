## Import

import socket
import struct
import sys
import numpy as np

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

def set_positions(changes):
    states = {'humans':{},'me':{},'enemy':{}}
    abscence = []
    changes = [changes[5*n:5*n+5] for n in range(int(len(changes)/5))]
    for change in changes:
        position = (change[0],change[1])
        if change[2] != 0:
            states['humans'][position] = change[2]
        elif change[3] != 0:
            states['me'][position] = change[3]
        elif change[4] != 0:
            states['enemy'][position] = change[4]
        else:
            abscence += [position]
    return states,abscence

def update_positions(old_position,new_position):
    updated = old_position
    new = new_position[0]
    absence = new_position[1]
    print(absence)
    for species in new.keys():
        for position in new[species].keys():
            updated[species][position] = new[species][position]
        for position in list(updated[species]):
            if position in absence:
                updated[species].pop(position)


    return updated


#Main Loop
test = 0
while True:
    order = sock.recv(3)
    print('test')
    order = order.decode(encoding = 'utf8')

    if not order:
        print("Bizarre, c'est vide")

    if order =="SET":
        print('set')
        lignes = struct.unpack('=B',sock.recv(1))[0]
        colonnes = struct.unpack('=B',sock.recv(1))[0]

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
        

        #mettez à jour votre carte à partir des tuples contenus dans changes
        #calculez votre coup
        #préparez la trame MOV ou ATK
        #Par exemple:
        test += 1
        if test%2 ==0:
            send(sock, "MOV", 1,3,3,1,4,3)
        else:
            send(sock, "MOV", 1,4,3,1,3,3)

        new_positions = set_positions(changes)
        states = update_positions(states,new_positions)
        print(states)


    elif order == "MAP":
        print('map')
        n = struct.unpack('=B', sock.recv(1))[0]
        changes = []
        for i in range(n):
            for i in range(5):
                changes.append(struct.unpack('=B', sock.recv(1))[0])

        states = set_positions(changes)[0]




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
