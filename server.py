#!/usr/bin python3

import socket
import random
import pickle
import json
import time
import threading


#   Configuracion del servidor
HOST = "127.0.0.1"  # Direccion de la interfaz de loopback estándar (localhost)
#HOST = "10.0.2.15"
PORT = 65432  # Puerto que usa el cliente (los puertos sin provilegios son > 1023)
buffer_size = 2048
dato = b" " # Dato nos servira para la restricción
i = 0

# Arreglo de la lista de conexiones
listaConexiones = []

#   Dificultad del juego
principiante = (9, 9, 10)
avanzado = (16, 16, 40)

# Esta función lo que hará es aceptar el cliente que se conecte y se crea un hilo
def clientes(socketTcp, listaConexiones):
    try:
        while True:
            Client_conn, Client_addr = socketTcp.accept() # Una vez que el evento de solicitud de conexion pasa
            print("Conectado a", Client_addr) # Imprimimos la conección e información del cliente

            listaConexiones.append(Client_conn) # Lo agrega a la lista de conexiones

            # Para cada cliente que se conecta se crea un hilo
            # Invoca la función recibir_datos() para manejar la comunicación de los datos
            thread_read = threading.Thread(target=recibir_datos, args=[Client_conn, Client_addr])
            thread_read.start()
            gestion_conexiones(listaConexiones) # Llamamos a la función getion_conexiones y le pasamos el arreglo listaConexiones
    except Exception as e:
        print(e)

def gestion_conexiones(listaConexiones):
    for conn in listaConexiones:
        if conn.fileno() == -1:
            listaConexiones.remove(conn)
    print("hilos activos:", threading.active_count())  # Imprimimos los hilos activos
    print("enum", threading.enumerate())
    print("conexiones: ", len(listaConexiones))  # Imprimimos las conexiones que tenemos en el arreglo "listaconexiones"
    print(listaConexiones)  # Imprime las conexiones

# Recibe los datos enviados por los clientes y se les envia una respuesta
# Recibe los datos del cliente e le enviará el menu o en caso contrario él tablero
def recibir_datos(Client_conn, addr):
    # Estas variables que vamos a estar cambiando en el transcurso del uso del servidor
    global dato
    global gano
    global perdio
    global conteo
    global tablero_v
    global tablero
    global tablero_vista
    global fila_letra
    global columna_letra
    global columna
    global fila
    global i
    try:
        print("Esperando a recibir datos... ")

        # En caso de que sea la primera conexión dato va a tener el dato b"" por lo tanto le enviará el menu para ver que nivel quiere el cliente
        if (dato == b" "):
            print("Enviando mensaje y solicitud")
            Client_conn.sendall(b"1") # Esto nos sirve como bandera para saber que le enviara el menú con los niveles
            dato = Client_conn.recv(buffer_size).decode() # Espera la respuesta del cliente
            Client_conn.sendall(b"Bienvenido al Buscaminas \n (P) Principiante \n (A) Avanzado \nElige la dificultad: ") # El servidor le envía el menu al cliente
            print("El usuario eligira el nivel")
            dato = Client_conn.recv(buffer_size).decode()  # Recibe el nivel que escogio el cliente
            print("Eligio el nivel " + dato)  # Imprime el nivel que escogio

            # En caso de que el dato recibido sea una "P" minuscula o mayuscula, significa que el usuario escogio el nivel de principiante
            if dato == "p" or dato == "P":
                print("Dificultad principiante \n")  # Se imprimira la dificultad
                filas, columnas, minas = principiante  # Se asignara a fila = 9, columna = 9 y minas = 10
                dificultad = "p"  # La dificultad va a ser igual a "p" (principiante)
                Client_conn.sendall(b"p") # Esto nos funcionará como bandera para que el cliente sepa que si entro a la dificultad principiante
                tablero_vista = "A B C D E F G H I"
            elif dato == "a" or dato == "A":
                print("Dificultad avanzado \n")  # Se imprime la dificultad
                filas, columnas, minas = avanzado  # Se asignara a fila = 16, columna = 16 y minas = 40
                dificultad = "a"  # La dificultad va a ser igual a "a" (avanzado)
                Client_conn.sendall(b"a") # Esto nos funcionará como bandera para que el cliente sepa que si entro a la dificultad avanzado
                tablero_vista = " A B C D E F G H I J K L M N Ñ O"
            else:
                print("Esta opción no existe \n") # En caso de que eligio una opción no valida

            #   Generamos el juego y colocamos las minas
            tablero = [[0 for j in range(columnas)] for i in range(filas)]  # genera el tablero
            minas_colocadas = 0
            while minas_colocadas < minas:
                fila = random.randint(0, filas - 1)
                columna = random.randint(0, columnas - 1)
                if tablero[fila][columna] != -1:
                    tablero[fila][columna] = -1
                    minas_colocadas += 1

            tablero_vista = [[0 for j in range(columnas)] for i in range(filas)]  # genera el tablero que se va a ver
            coordenada = []

            #   A todos los elementos de la matriz les vamos a poner un "-" (Recordar que esto se verá como el tablero)
            for i in range(filas):
                for j in range(columnas):
                    tablero_vista[i][j] = "- "
        # En caso de que ya se haya escogido un nivel, el proximo cliente entrara a esta opción en caso de que escoja el nivel principiante
        elif dato == "p" or dato == "P":
            dificultad = "p" # Igualamos la variable dificultad a "p"
            print("Enviando mensaje que ya esta en principiante") # Imprimimos que se esta enviando el mensaje que se le esta enviando al nuevo cliente que esta en el nivel principiante
            Client_conn.sendall(b"Estas en principiante") # Le enviamos al nuevo cliente que esta en el nivel principiante
            Client_conn.sendall(b"p") # Le enviamos al ciente la letra "p" como una bandera de que entro al nivel principiante, que ya había elegido el cliente anterior
        # En caso de que el primer cliente haya escogido un nivel, los proximos clientes entraran a esta opción en caso de que se haya escojado el nivel avanzado
        elif (dato == "a" or dato == "A"):
            dificultad = "a" # Igualamos la variable dificultad a "a"
            print("Enviando mensaje que ya esta en avanzado") # Imprimimos que se esta enviando el mensaje al cliente
            Client_conn.sendall(b"Estas en avanzado") # Le enviamos al nuevo cliente que esta en el nivel principianta
            Client_conn.sendall(b"a") # Le enviamos al cliente la letra "p" como una bandera de que entro al nivel avanzado
        # En caso de que el primer cliente haya elegido una dificultad no aceptada
        else:
            print("No tiene dificultad")



        # En caso de que la dificultad sea principiante
        if dificultad == "p":
            #   Declaramos variables
            gano = 0
            perdio = 0
            mismo = 0
            llave = 0
            repetir = 0
            conteo = 0

            # Esto se repetira hasta que la variable gano o perdio sea diferente de 1
            while gano != 1 or perdio != 1:

                # Enviamos el tablero
                tablero_v = "\n".join([" ".join(fila) for fila in tablero_vista])  # Aqui se almacenara todos los elementos de la matriz en forma de tablero
                Client_conn.sendall(tablero_v.encode())  # Enviamos la matriz al cliente

                # ------------------------------------------------------------------------------------------------------------
                # Recibe la coordenada
                print("Esperando a recibir coordenadas...")

                #   Se recibe la columna que envio el cliente
                columna_letra = Client_conn.recv(buffer_size).decode()  # No va a avanzar el programa hasta que se reciba la columna
                print(columna_letra)

                # Se recibe la fila que envio el cliente
                fila_letra = Client_conn.recv(buffer_size).decode()  # No va a avanzar el programa hasta que se reciba la fila
                print(fila_letra)

                # Dependiendo de la letra que envio el cliente es lo que valdra la variable fila
                if fila_letra == "1":
                    fila = 0
                elif fila_letra == "2":
                    fila = 1
                elif fila_letra == "3":
                    fila = 2
                elif fila_letra == "4":
                    fila = 3
                elif fila_letra == "5":
                    fila = 4
                elif fila_letra == "6":
                    fila = 5
                elif fila_letra == "7":
                    fila = 6
                elif fila_letra == "8":
                    fila = 7
                elif fila_letra == "9":
                    fila = 8
                else:
                    print("Esta opcion no es valida")  # En caso de que no sea ninguna de las opciones anteriores

                # Dependiendo de la letra que envio el cliente es lo que valdra la variable columna
                if columna_letra == "A" or columna_letra == "a":
                    columna = 0
                elif columna_letra == "B" or columna_letra == "b":
                    columna = 1
                elif columna_letra == "C" or columna_letra == "c":
                    columna = 2
                elif columna_letra == "D" or columna_letra == "d":
                    columna = 3
                elif columna_letra == "E" or columna_letra == "e":
                    columna = 4
                elif columna_letra == "F" or columna_letra == "f":
                    columna = 5
                elif columna_letra == "G" or columna_letra == "g":
                    columna = 6
                elif columna_letra == "H" or columna_letra == "h":
                    columna = 7
                elif columna_letra == "I" or columna_letra == "i":
                    columna = 8
                else:
                    print("Esta opcion no es valida")  # En caso de que no sea ninguna de las opciones anteriores

                mismo = 0
                print("\n",mismo)
                print("columna:")
                print(columna)  # Se imprime el valor de la variable columna la cual va a ser la columna que cambiara en la matriz
                print("fila:")
                print(fila)  # Se imprime el valor de la variable fila, la cual sera la fila que cambiara en la matriz

                # En caso de que el cliente elija una casilla que ya fua abierta

                if tablero_vista[fila][columna] == "X ":
                    mismo = 1

                tablero_vista[fila][columna] = "X "

                # Le asignaremos una x a esa coordenada en la matriz

                # En caso de que sea igual a -1 significa que perdio
                if tablero[fila][columna] == -1:
                    perdio = 1
                    Client_conn.sendall(b"p")  # Se le envia una p al cliente para que sepa que perdio
                # En caso de que ya abrio todas las casillas y ninguna era una mina
                elif conteo == 71:
                    Client_conn.sendall(b"g")  # Se le envia una g al cliente para que sepa que perdio
                # En caso de que ya se haya puesto la misma casilla
                elif mismo == 1:
                    Client_conn.sendall(b"m") # En caso de que haya puesto la misma casilla
                    mismo = 0
                    print(mismo)
                # En este caso no piso ninguna mina y tampoco a completado en abrir todas las casillas
                else:
                    Client_conn.sendall(b"s")  # Se le envia una s al cliente para que sepa que perdio
                    conteo = conteo + 1  # Se le sumará un 1 a la variable conteo
        else:
            gano = 0
            perdio = 0
            mismo = 0
            llave = 0
            repetir = 0
            conteo = 0
            while gano != 1 or perdio != 1:
                # Enviamos el tablero
                tablero_v = "\n".join([" ".join(fila) for fila in tablero_vista])
                Client_conn.sendall(tablero_v.encode())

                # --------------------------------------------------------------------------------
                # Recibe la coordenada
                print("Esperando a recibir coordenadas...")

                # Se recibe la columna que envio el cliente
                columna_letra = Client_conn.recv(buffer_size).decode().strip().lower()
                print(columna_letra)

                # Se recibe la fila que envio el cliente
                fila_letra = Client_conn.recv(buffer_size).decode().strip().lower()
                print(fila_letra)

                if fila_letra == "1":
                    fila = 0
                elif fila_letra == "2":
                    fila = 1
                elif fila_letra == "3":
                    fila = 2
                elif fila_letra == "4":
                    fila = 3
                elif fila_letra == "5":
                    fila = 4
                elif fila_letra == "6":
                    fila = 5
                elif fila_letra == "7":
                    fila = 6
                elif fila_letra == "8":
                    fila = 7
                elif fila_letra == "9":
                    fila = 8
                elif fila_letra == "10":
                    fila = 9
                elif fila_letra == "11":
                    fila = 10
                elif fila_letra == "12":
                    fila = 11
                elif fila_letra == "13":
                    fila = 12
                elif fila_letra == "14":
                    fila = 13
                elif fila_letra == "15":
                    fila = 14
                elif fila_letra == "16":
                    fila = 15
                else:
                    print("Esta opcion no es valida")

                if columna_letra == "A" or columna_letra == "a":
                    columna = 0
                elif columna_letra == "B" or columna_letra == "b":
                    columna = 1
                elif columna_letra == "C" or columna_letra == "c":
                    columna = 2
                elif columna_letra == "D" or columna_letra == "d":
                    columna = 3
                elif columna_letra == "E" or columna_letra == "e":
                    columna = 4
                elif columna_letra == "F" or columna_letra == "f":
                    columna = 5
                elif columna_letra == "G" or columna_letra == "g":
                    columna = 6
                elif columna_letra == "H" or columna_letra == "h":
                    columna = 7
                elif columna_letra == "I" or columna_letra == "i":
                    columna = 8
                elif columna_letra == "J" or columna_letra == "j":
                    columna = 9
                elif columna_letra == "K" or columna_letra == "k":
                    columna = 10
                elif columna_letra == "L" or columna_letra == "l":
                    columna = 11
                elif columna_letra == "M" or columna_letra == "m":
                    columna = 12
                elif columna_letra == "N" or columna_letra == "n":
                    columna = 13
                elif columna_letra == "Ñ" or columna_letra == "ñ":
                    columna = 14
                elif columna_letra == "O" or columna_letra == "o":
                    columna = 15

                else:
                    print("Esta opcion no es valida")

                print("columna:")
                print(columna)
                print("fila:")
                print(fila)

                # En caso de que el cliente elija una casilla que ya fua abierta

                if tablero_vista[fila][columna] == "X ":
                    mismo = 1


                tablero_vista[fila][columna] = "X "

                if tablero[fila][columna] == -1:
                    perdio = 1
                    Client_conn.sendall(b"p")
                elif conteo == 216:
                    Client_conn.sendall(b"g")
                elif mismo == 1:
                    Client_conn.sendall(b"m")
                    mismo = 0
                else:
                    Client_conn.sendall(b"s")
                    conteo = conteo + 1

        print("El juego ha terminado")  # Imprimira que el juego ha terminado

    # Si ocurre alguna excepción durante la comunicación se cierra la conexión
    except Exception as e:
        print(e)
    finally:
        Client_conn.close()




with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:  # Creamos el mismo tipo de socket
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Establece las opciones de socket de un socket existente para ajustar su comportamiento y configuración
    TCPServerSocket.bind((HOST, PORT)) # Nos va a ser la liga entre el scoket y la dirección IP
    TCPServerSocket.listen() # Para poder aceptar conexciones
    print("Servidor de Buscaminas activo")
    clientes(TCPServerSocket, listaConexiones) # Llamamos a la función clientes para poder crear el hilo


