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
    positions = {'humans':{},'vampires':{},'wolves':{}}
    for i in range(len(changes)):
        if changes[i] != 0 and (i==2 or i%5 ==2):
            positions['humans'][(changes[i-2],changes[i-1])] = changes[i]
        if changes[i] != 0 and (i==3 or i%5 ==3):
            positions['vampires'][(changes[i-3],changes[i-2])] = changes[i]
        if changes[i] != 0 and (i==4 or i%5 ==4):
            positions['wolves'][(changes[i-4],changes[i-3])] = changes[i]
    print(positions)
    return positions

def update_positions(old,new):
    for species in new:
        return "ok"


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

        new_positions = set_positions(changes)

        #mettez à jour votre carte à partir des tuples contenus dans changes
        #calculez votre coup
        #préparez la trame MOV ou ATK
        #Par exemple:
        test += 1
        if test%2 ==0:
            send(sock, "MOV", 1,3,3,1,4,3)
        else:
            send(sock, "MOV", 1,4,3,1,3,3)
    elif order == "MAP":
        print('map')
        n = struct.unpack('=B', sock.recv(1))[0]
        changes = []
        for i in range(n):
            for i in range(5):
                changes.append(struct.unpack('=B', sock.recv(1))[0])

        positions = set_positions(changes)




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
