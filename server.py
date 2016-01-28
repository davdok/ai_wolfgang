## Import

import socket
import struct
import sys
import numpy as np

host="127.0.0.1"
port="5555"

#Creation de la socket

mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connexion
try:
	mySocket.connect((host,port)
except mySocket.error:
	print " la connexion a ecouhe."
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
		
