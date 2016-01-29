## Import

import socket
import struct
import sys
import numpy as np

def send(sock, *messages):
    """Send a given set of messages to the server."""
	for message in messages:
		try:
            data = struct.pack('=B', message) if isinstance(message, int) else message
            sock.send(data)
	except:
		print("Couldn't send message: ", message)
			
print "Entrez l'adresse du serveur"
host=raw.input()
print "Entrez le port du serveur"
port=raw.input()

#Creation de la socket

mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connexion
try:
	mySocket.connect((host,port)
except mySocket.error:
	print " connexion failed"
    sys.exit()
print "Connexion établie"

#Envoi du nom

groupName ="Wolfgang"
send(mySocket, "NME", len(groupName), groupName)

#Main Loop

While True:
       order = mySocket.recv(3)

    if not data:
        print("Bizarre, c'est vide")

    if order =="SET":
        lignes, colonnes = (struct.unpack('=B', self._s.recv(1))[0] for i in range(2))
		card = np.eye(colonnes,lignes)
		for i in range(len(card)):
			card[i]=0

	elif order == "HUM":
        n = struct.unpack('=B', self._s.recv(1))[0]
        maisons = []
        for i in range(n):
            maisons.append((struct.unpack('=B', self._s.recv(1))[0] for i in range(2)))

	 elif order == "HME":
        x, y = (struct.unpack('=B', self._s.recv(1))[0] for i in range(2))
		card[x][y]=1

    elif order == "UPD":
        n = struct.unpack('=B', self._s.recv(1))[0]
        changes = []
        for i in range(n):
            changes.append((struct.unpack('=B', self._s.recv(1))[0] for i in range(5)))

        #mettez à jour votre carte à partir des tuples contenus dans changes
        #calculez votre coup
        #préparez la trame MOV ou ATK
        #Par exemple:
        send(sock, "MOV", 1,2,1,1,3)

    elif order == "MAP":
        n = struct.unpack('=B', self._s.recv(1))[0]
        changes = []
        for i in range(n):
            changes.append((struct.unpack('=B', self._s.recv(1))[0] for i in range(
        #initialisez votre carte à partir des tuples contenus dans changes

    elif order == "END":
        #ici on met fin à la partie en cours
        #Réinitialisez votre modèle

    elif order == "BYE":
        break
    else:
        print("commande non attendue recue", order)

#Préparez ici la déconnexion

#Fermeture de la socket
    sock.close()
