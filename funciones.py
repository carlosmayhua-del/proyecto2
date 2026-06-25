import json
import os
import random
from datetime import datetime

from colorama import Fore, Style, init

init(autoreset=True)

PARTIDAS_PATH = os.path.join(os.path.dirname(__file__), "partidas.json")
ULTIMO_TABLERO = None

COLOR_PIEZAS = {
    "X": Fore.RED,
    "O": Fore.CYAN,
    "_": Fore.WHITE,
}

RESULTADOS_TEXTO = {
    "X": "X ganÃ³",
    "O": "O ganÃ³",
    "Empate": "Empate",
    "Cancelado": "Cancelado",
}


def guardar_partida(jugador1, jugador2, fecha, resultado):
    """Guarda un juego en el archivo local de partidas."""
    global ULTIMO_TABLERO
    partidas = cargar_partidas()
    partida = {
        "jugador1": jugador1,
        "jugador2": jugador2,
        "fecha": fecha,
        "resultado": resultado,
        "tablero": ULTIMO_TABLERO if ULTIMO_TABLERO is not None else [],
    }
    partidas.append(partida)
    with open(PARTIDAS_PATH, "w", encoding="utf-8") as handle:
        json.dump(partidas, handle, indent=2)


def registro():
    """Muestra una lista tabular de los juegos realizados y permite ver el tablero final."""
    partidas = cargar_partidas()
    if not partidas:
        print("No hay juegos realizados todavÃ­a.")
        return

    print("\nJuegos realizados")
    print("Idx  Jugador 1                Jugador 2                Fecha y hora      Resultado")
    print("---  ------------------------  ------------------------  ----------------  ----------")
    for idx, partida in enumerate(partidas, start=1):
        jugadores = f"{partida['jugador1']} vs {partida['jugador2']}"
        resultado = RESULTADOS_TEXTO.get(partida["resultado"], partida["resultado"])
        print(
            f"{idx:<3}  {partida['jugador1']:<24}  {partida['jugador2']:<24}  {partida['fecha']:<16}  {resultado}"
        )

    while True:
        seleccion = input("\nSeleccione un juego para ver el tablero final (0 para volver): ")
        if seleccion == "0":
            return
        if not seleccion.isdigit():
            print("Entrada invÃ¡lida. Ingrese un nÃºmero.")
            continue

        index = int(seleccion) - 1
        if 0 <= index < len(partidas):
            mostrar_tablero(partidas[index]["tablero"], titulo=f"Tablero final del juego {seleccion}")
            return
        print("NÃºmero de juego invÃ¡lido.")


def cargar_partidas():
    if not os.path.exists(PARTIDAS_PATH):
        return []
    try:
        with open(PARTIDAS_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return []


def crear_tablero():
    tablero = []
    for fil in range(8):
        filasT = []
        for colum in range(8):
            suma = fil + colum
            if fil in [0, 1]:
                filasT.append("O" if suma % 2 == 1 else "_")
            elif fil in [6, 7]:
                filasT.append("X" if suma % 2 == 1 else "_")
            else:
                filasT.append("_")
        tablero.append(filasT)
    return tablero


def colorizar_pieza(pieza):
    return COLOR_PIEZAS.get(pieza, Fore.WHITE) + pieza + Style.RESET_ALL


def mostrar_tablero(tablero, titulo=None):
    if titulo:
        print(f"\n{titulo}")
    print("  A B C D E F G H")
    for valor in range(8):
        linea = valor + 1
        print(linea, end=" ")
        for temporal in range(8):
            pieza = tablero[valor][temporal]
            print(colorizar_pieza(pieza), end=" ")
        print(linea)
    print("  A B C D E F G H")


def traductor(jugada):
    if jugada == str(-1):
        return "Cancelado"
    if len(jugada) != 4:
        return False

    Columnas = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
    letra_original = jugada[0].upper()
    if not jugada[1].isdigit():
        return False
    numero_original = int(jugada[1]) - 1

    letra_final = jugada[2].upper()
    if not jugada[3].isdigit():
        return False
    numero_final = int(jugada[3]) - 1

    if letra_original not in Columnas or letra_final not in Columnas:
        return False
    if not (0 <= numero_original <= 7 and 0 <= numero_final <= 7):
        return False

    return (numero_original, Columnas[letra_original]), (numero_final, Columnas[letra_final])


def traductor_inverso(coordenadasbs):
    (filaOR, columnaOR), (filaFI, columnaFI) = coordenadasbs
    diccionarioOG = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
    diccionarioInvertido = {valor: clave for clave, valor in diccionarioOG.items()}
    return "".join(
        [diccionarioInvertido[columnaOR], str(filaOR + 1), diccionarioInvertido[columnaFI], str(filaFI + 1)]
    )


def verificador(tuplaoriginal, tuplafinal, tablero_actual, turno):
    posibles = [1, 2, 4, 6]
    filaOR, columnaOR = tuplaoriginal
    filaFI, columnaFI = tuplafinal

    if tablero_actual[filaOR][columnaOR] != turno:
        return False
    if tablero_actual[filaFI][columnaFI] != "_":
        return False

    distancia_fil = abs(filaFI - filaOR)
    distancia_col = abs(columnaFI - columnaOR)
    if distancia_col != distancia_fil:
        return False
    if distancia_fil not in posibles:
        return False
    if distancia_fil == 1:
        return True
    return validar_camino_salto(tablero_actual, tuplaoriginal, tuplafinal, distancia_fil)


def hay_ganador(tablero):
    ganador_x = 0
    ganador_o = 0

    for columna in range(8):
        if tablero[0][columna] == "X":
            ganador_x += 1
        if tablero[1][columna] == "X":
            ganador_x += 1
        if tablero[6][columna] == "O":
            ganador_o += 1
        if tablero[7][columna] == "O":
            ganador_o += 1

    if ganador_x == 8:
        return "X"
    if ganador_o == 8:
        return "O"
    return None


def posibles_jugadas(tablero, ficha):
    respuesta = []
    combinaciones = [1, 2, 4, 6]
    direcciones = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
    for filas in range(8):
        for columnas in range(8):
            if tablero[filas][columnas] != ficha:
                continue
            original = (filas, columnas)
            for dir_f, dir_c in direcciones:
                for variable in combinaciones:
                    filacp = filas + dir_f * variable
                    columnacp = columnas + dir_c * variable
                    if not (0 <= filacp <= 7 and 0 <= columnacp <= 7):
                        continue
                    temporales = (filacp, columnacp)
                    if variable == 1:
                        if tablero[filacp][columnacp] == "_":
                            respuesta.append((original, temporales))
                    else:
                        if validar_camino_salto(tablero, original, temporales, variable):
                            if tablero[filacp][columnacp] == "_":
                                respuesta.append((original, temporales))
    return respuesta


def validar_camino_salto(tablero, tuplaoriginal, tuplafinal, salto):
    filaOR, columnaOR = tuplaoriginal
    filaFI, columnaFI = tuplafinal
    comparar = (filaFI - filaOR) // abs(filaFI - filaOR)
    comparar2 = (columnaFI - columnaOR) // abs(columnaFI - columnaOR)
    direcciones = [(1, 1), (-1, 1), (1, -1), (-1, -1)]

    for simbolo_fil, simbolo_col in direcciones:
        if simbolo_fil == comparar and simbolo_col == comparar2:
            break

    chequeo = salto // 2
    calc_temp_fil = filaOR + simbolo_fil
    calc_temp_col = columnaOR + simbolo_col
    while chequeo > 0:
        if tablero[calc_temp_fil][calc_temp_col] == "_":
            return False
        calc_temp_fil += 2 * simbolo_fil
        calc_temp_col += 2 * simbolo_col
        chequeo -= 1

    chequeo = salto // 2
    calc_temp_fil = filaOR + 2 * simbolo_fil
    calc_temp_col = columnaOR + 2 * simbolo_col
    while chequeo > 1:
        if tablero[calc_temp_fil][calc_temp_col] != "_":
            return False
        calc_temp_fil += 2 * simbolo_fil
        calc_temp_col += 2 * simbolo_col
        chequeo -= 1
    return True


def elegir_jugada_computadora(tablero, ficha):
    jugadas = posibles_jugadas(tablero, ficha)
    meta = [6, 7]
    pendientes = []
    for valor in jugadas:
        (Fil_or, _), _ = valor
        if Fil_or not in meta:
            pendientes.append(valor)
    if pendientes:
        jugadas = pendientes

    multiples = []
    for valor in jugadas:
        (Fil_or, _), (Fil_fi, _) = valor
        distancia_fil = abs(Fil_fi - Fil_or)
        if distancia_fil in [4, 6] and Fil_fi > Fil_or:
            multiples.append(valor)
    if multiples:
        return random.choice(multiples)
    return random.choice(jugadas)


def pedir_nombre_jugador():
    while True:
        Jugador_1 = input("Nombre jugador 1 : ")
        Jugador_2 = input("Nombre jugador 2 : ")
        if Jugador_1.strip() == "" and Jugador_2.strip() == "":
            print("Error, nombres no pueden estar vacios")
            continue
        if Jugador_1 == Jugador_2:
            print("No se aceptan nombres iguales, disculpe las molestias")
            continue
        if Jugador_1.strip() == "":
            print('Error, nombre vacio en "Jugador 1"')
            continue
        if Jugador_2.strip() == "":
            print('Error, nombre vacio en "Jugador 2"')
            continue

        while True:
            flag = input("Confirmar nombres (S/N): ").strip().upper()
            if flag == "S":
                return Jugador_1, Jugador_2
            if flag == "N":
                break
            print("OpciÃ³n invalÃ­da")


def jugador_turno():
    while True:
        Jugador = input("Nombre del jugador : ")
        if Jugador.strip() == "":
            print("Error, nombre no puede estar vacios")
            continue
        if Jugador.lower() == "computador":
            print("Error, nombre inviable. Hagame el favor de cambiarlo")
            continue
        while True:
            flag = input("Confirmar nombre (S/N): ").strip().upper()
            if flag == "S":
                while True:
                    turno = input("Juega primero? (S/N): ").strip().upper()
                    if turno in ["S", "N"]:
                        return Jugador, turno
                    print("OpciÃ³n invalÃ­da")
            elif flag == "N":
                break
            else:
                print("OpciÃ³n invalÃ­da")


def turno_local(tablero):
    global ULTIMO_TABLERO
    print("Jugador 1, comienza la partida")
    Jugador_1, Jugador_2 = pedir_nombre_jugador()
    fichas = {Jugador_1: "X", Jugador_2: "O"}
    Jugador = Jugador_1
    turno_actual = fichas[Jugador]
    fecha = datetime.now().strftime("%d/%m/%y %H:%M")
    print(f"Juego {Jugador_1} vs {Jugador_2} {fecha}")
    print("âˆ’1: Cancelar juego")

    while True:
        if hay_ganador(tablero) == "X":
            print(f"Ganador: {Jugador_1}")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador_1, Jugador_2, fecha, Jugador_1)
            break
        if hay_ganador(tablero) == "O":
            print(f"Ganador: {Jugador_2}")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador_1, Jugador_2, fecha, Jugador_2)
            break

        mostrar_tablero(tablero)
        if not posibles_jugadas(tablero, turno_actual):
            print("partida terminada por rey ahogado")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador_1, Jugador_2, fecha, "Empate")
            break

        movimiento_realizado = input(f"{Jugador} Movimiento(formato A8C6): ")
        coordenadas = traductor(movimiento_realizado)
        if coordenadas == "Cancelado":
            print("Juego cancelado")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador_1, Jugador_2, fecha, "Cancelado")
            break
        if coordenadas is False:
            print("Jugada invalÃ­da, formato A8C6")
            continue

        tuplaoriginal, tuplafinal = coordenadas
        if verificador(tuplaoriginal, tuplafinal, tablero, turno_actual):
            filaOR, columnaOR = tuplaoriginal
            filaFI, columnaFI = tuplafinal
            tablero[filaFI][columnaFI] = turno_actual
            tablero[filaOR][columnaOR] = "_"
            Jugador = Jugador_2 if Jugador == Jugador_1 else Jugador_1
            turno_actual = fichas[Jugador]
        else:
            print("Movimiento invÃ¡lido.")


def turno_computadora(tablero):
    global ULTIMO_TABLERO
    print("El futuro estÃ¡ en tus manos")
    Jugador, turno = jugador_turno()
    fichas = {Jugador: "X", "Computador": "O"}
    Partida = Jugador if turno == "S" else "Computador"
    turno_actual = fichas[Partida]
    fecha = datetime.now().strftime("%d/%m/%y %H:%M")
    print(f"Juego {Jugador} vs Computador (Alias Mechanus Calsen) {fecha}")
    print("âˆ’1: Cancelar juego")

    while True:
        if hay_ganador(tablero) == "X":
            print(f"Ganador: {Jugador}")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador, "Computador", fecha, Jugador)
            break
        if hay_ganador(tablero) == "O":
            print("Ganador: Computador")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador, "Computador", fecha, "Computador")
            break

        mostrar_tablero(tablero)
        if not posibles_jugadas(tablero, turno_actual):
            print("partida terminada por rey ahogado")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador, "Computador", fecha, "Empate")
            break

        if Partida == "Computador":
            coordenadas = elegir_jugada_computadora(tablero, turno_actual)
            redaccion = traductor_inverso(coordenadas)
            print(f"{Partida} ? {redaccion}")
        else:
            movimiento_realizado = input(f"{Partida} ?(formato A8C6): ")
            coordenadas = traductor(movimiento_realizado)

        if coordenadas == "Cancelado":
            print("Juego cancelado")
            ULTIMO_TABLERO = [fila.copy() for fila in tablero]
            guardar_partida(Jugador, "Computador", fecha, "Cancelado")
            break
        if coordenadas is False:
            print("Jugada invalÃ­da, formato A8C6")
            continue

        tuplaoriginal, tuplafinal = coordenadas
        if verificador(tuplaoriginal, tuplafinal, tablero, turno_actual):
            filaOR, columnaOR = tuplaoriginal
            filaFI, columnaFI = tuplafinal
            tablero[filaFI][columnaFI] = turno_actual
            tablero[filaOR][columnaOR] = "_"
            Partida = "Computador" if Partida == Jugador else Jugador
            turno_actual = fichas[Partida]
        else:
            print("Movimiento invÃ¡lido.")


