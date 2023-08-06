import socket
import threading
import struct
from queue import Queue # queue pour partager les données entre 2 thread

#-----------------------------------------------------
class Tcp_Client(threading.Thread):
    
    def __init__(self, host, port, _structSize, Queue, clientsocket):      # arguments du de la classe
        threading.Thread.__init__(self)  # ne pas oublier cette ligne
        # (appel au constructeur de la classe mère)
        self.clientsocket = clientsocket
        self.host = host
        self.port = port
        self.structSize = _structSize # taille de la structure de données envoyées par le client (2 floats) '<ff'   8 octets
        #self.connected = False
        self.queue = Queue
        print("[+] Nouveau thread pour %s %s" % (self.host, self.port, ))
        self.exit_event = threading.Event() # évenement pour arrêter le thread (serveur tcp qui reçoit les données de Blender)
    
    def run(self):
        print("Connexion de %s %s" % (self.host, self.port, ))
        while True:
            try:
                # receive data stream. it won't accept data packet greater than 1024 bytes
                data = self.clientsocket.recv(self.structSize[1])# Important taille du buffer de réception pour lire les données par 2 floats : 4*2
                print('lecture')
                if not data:
                    print("Client déconnecté...")
                    #print(self.queue.qsize())
                    break
                if data != "":
                            data =struct.unpack(self.structSize[0], data) # reception par 2 floats taille : 2*4 octets
                            print(data)
                            #print(str(data.decode("utf-8").strip('\r\n')))
                            self.queue.put(data) # sauvegarde des données dans un queue partagée entre 2 thread
                            #print("queue non vide")
                            #print("queue size : ")
                            #qa = self.queue.qsize()
                            #print(qa)                    
                            #print("réception & entré 1er sorti :")

            except:
                #pass
                print("exception pour TCP Client  ....")
            finally:
                if self.exit_event.is_set():# si événement d'arrêt du thread est envoyé on arrête le thread
                    print("on a arrêté le thread tcp client  ! ")   
                    self.close()
                    break

    def close(self):
        self.clientsocket.shutdown(socket.SHUT_RDWR)
        self.clientsocket.close()
        print ("server TCP client closed")

#-----------------------------------------------------
class tcp_server(threading.Thread):
    
    def __init__(self, hostServer, portServer, _SizeStruc=["<ff",8]):      # arguments du de la classe
        threading.Thread.__init__(self)  # ne pas oublier cette ligne
        # (appel au constructeur de la classe mère)
        tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #tcpsock.bind(("127.0.0.1",8080))
        # Initializing a queue
        self.QSizeMax = 2000 # taille maximale de la queue FIFO
        self.queue = Queue(maxsize = self.QSizeMax)# taille maximale de la queue FIFO
        self.exit_event = threading.Event() # évenement pour arrêter le thread (serveur tcp qui reçoit les données de Blender)
        self.clientsocket = tcpsock
        self.hostS = hostServer
        self.portS = portServer
        self.SizeStruc = _SizeStruc # taille de la structure de données envoyées par le client (2 floats) '<ff'   8 octets
        self.clientsocket.bind((self.hostS,self.portS))
        print("[+] Server TCP créé pour %s %s" % (self.hostS, self.portS, ))
    
    def run(self):
        newClient = None
        while True:
            try:
                if self.exit_event.is_set():# si événement d'arrêt du thread est envoyé on arrête le thread
                    Tcp_Client.exit_event.set()# on envoie l'événement d'arrêt au thread client
                    break
                self.clientsocket.listen(10)
                #don = Queue.get()
                #print(Queue.get())
                print( "En écoute...")
                (clientsoc, (ip, port)) = self.clientsocket.accept()# bloque ici si pas de client
                newClient = Tcp_Client(ip, port, self.SizeStruc, self.queue, clientsoc)# ip et port du client qui vient de se connecter
                newClient.start()
            except:
                #pass
                print("exception pour TCP server ....")
            finally:
                if self.exit_event.is_set():# si événement d'arrêt du thread est envoyé on arrête le thread
                    print("on a arrêté le thread TCP server ! ")
                    if newClient != None:
                        print("on ferme le socket")
                        newClient.exit_event.set()# on envoie l'événement d'arrêt au thread client
                        #newClient.close()
                    break

#-----------------------------------------------------