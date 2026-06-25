from funciones import crear_tablero, registro, turno_computadora, turno_local


def main():
    while True:
        print("\nJUEGO DAMAS CHINAS")
        print("1. Comenzar Juego")
        print("2. Jugar vs Computadora")
        print("3. Juegos realizados")
        print("0. Salir")

        opcion = input("Opcion: ")

        if opcion == "1":
            tablero = crear_tablero()
            turno_local(tablero)
        elif opcion == "2":
            tablero = crear_tablero()
            turno_computadora(tablero)
        elif opcion == "3":
            registro()
        elif opcion == "0":
            break
        else:
            print("Opcion invalida, vuelva a intentarlo")

    print("Esperamos se haya divertido")


if __name__ == "__main__":
    main()
