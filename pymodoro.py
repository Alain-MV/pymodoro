#!/usr/bin/env python3
"""PyModoro - ciclo Pomodoro para la terminal.

Uso:
    pymodoro start      # ciclo Pomodoro completo (4x trabajo + descansos) en bucle
    pymodoro start -q   # sin alerta sonora entre fases

El ciclo son 4 bloques de trabajo de 25m. Tras los 3 primeros hay un descanso
de 5m; tras el cuarto, un descanso largo de 15m. Luego vuelve a empezar.
Se detiene con Ctrl+C.
"""
import argparse
import sys
import time

VERSION = "1.0.0"

# Codigos de color ANSI
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Fuente ASCII de dígitos grandes (5 filas de alto)
DIGITOS_GRANDES = {
    "0": [" ███ ", "█   █", "█   █", "█   █", " ███ "],
    "1": ["  █  ", " ██  ", "  █  ", "  █  ", " ███ "],
    "2": [" ███ ", "█   █", "  ██ ", " █   ", "█████"],
    "3": ["████ ", "    █", " ███ ", "    █", "████ "],
    "4": ["█   █", "█   █", "█████", "    █", "    █"],
    "5": ["█████", "█    ", "████ ", "    █", "████ "],
    "6": [" ███ ", "█    ", "████ ", "█   █", " ███ "],
    "7": ["█████", "    █", "   █ ", "  █  ", " █   "],
    "8": [" ███ ", "█   █", " ███ ", "█   █", " ███ "],
    "9": [" ███ ", "█   █", " ████", "    █", " ███ "],
    ":": ["   ", " █ ", "   ", " █ ", "   "],
}
ALTO_DIGITO = 5


def render_grande(texto):
    """Convierte una cadena como '12:34' en una lista de 5 lineas ASCII grandes."""
    filas = []
    for i in range(ALTO_DIGITO):
        partes = [DIGITOS_GRANDES.get(c, "     ")[i] for c in texto]
        filas.append(" ".join(partes))
    return filas


def formato_hms(segundos):
    """Formatea segundos como HH:MM:SS o MM:SS."""
    h, resto = divmod(segundos, 3600)
    m, s = divmod(resto, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def barra_progreso(transcurrido, total, ancho=30):
    """Dibuja una barra de progreso de texto."""
    fraccion = transcurrido / total if total else 1
    llenos = int(ancho * fraccion)
    return "[" + "#" * llenos + "-" * (ancho - llenos) + "]"


def cuenta_regresiva(total_segundos, etiqueta=None):
    """Ejecuta la cuenta regresiva mostrando el tiempo restante en grande."""
    inicio = time.monotonic()
    fin = inicio + total_segundos
    titulo = f" {etiqueta}" if etiqueta else ""

    # El bloque dibujado ocupa: 1 cabecera + ALTO_DIGITO + 1 barra = filas totales
    filas_bloque = ALTO_DIGITO + 2
    primera_vez = True

    # Oculta el cursor durante la cuenta
    sys.stdout.write("\033[?25l")

    try:
        while True:
            ahora = time.monotonic()
            restante = fin - ahora
            if restante <= 0:
                break
            restante_ent = int(restante + 0.5)
            transcurrido = total_segundos - restante
            barra = barra_progreso(transcurrido, total_segundos)
            reloj = render_grande(formato_hms(restante_ent))

            if not primera_vez:
                # Sube el cursor para redibujar sobre el bloque anterior
                sys.stdout.write(f"\033[{filas_bloque}A")
            primera_vez = False

            cabecera = f"{CYAN}{BOLD}PyModoro{RESET}{titulo}"
            lineas = [cabecera]
            lineas += [f"{GREEN}{BOLD}{fila}{RESET}" for fila in reloj]
            lineas.append(f"{YELLOW}{barra}{RESET}")

            # Cada linea limpia hasta el final con \033[K para evitar residuos
            sys.stdout.write("\r" + "\n".join(f"{l}\033[K" for l in lineas) + "\n")
            sys.stdout.flush()
            # Dormir hasta el proximo segundo entero para una cuenta limpia
            time.sleep(min(1.0, restante - int(restante) or 1.0))
    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h")  # restaura cursor
        sys.stdout.write("\n" + YELLOW + "Cancelado." + RESET + "\n")
        return False

    # Restaura el cursor y muestra el bloque final en cero
    if not primera_vez:
        sys.stdout.write(f"\033[{filas_bloque}A")
    reloj_cero = render_grande(formato_hms(0))
    cabecera = f"{GREEN}{BOLD}¡Tiempo!{RESET}{titulo}"
    lineas = [cabecera]
    lineas += [f"{GREEN}{BOLD}{fila}{RESET}" for fila in reloj_cero]
    lineas.append(f"{YELLOW}{barra_progreso(1, 1)}{RESET}")
    sys.stdout.write("\r" + "\n".join(f"{l}\033[K" for l in lineas) + "\n")
    sys.stdout.write("\033[?25h")  # restaura cursor
    sys.stdout.flush()
    return True


def alerta():
    """Suena la campana del terminal varias veces."""
    for _ in range(3):
        sys.stdout.write("\a")
        sys.stdout.flush()
        time.sleep(0.4)


# Parametros del ciclo Pomodoro clasico (en minutos)
TRABAJO_MIN = 25
DESCANSO_CORTO_MIN = 5
DESCANSO_LARGO_MIN = 15
BLOQUES_POR_CICLO = 4


def ciclo_pomodoro(silencioso=False):
    """Ejecuta el ciclo Pomodoro en bucle infinito.

    Cada ciclo son 4 bloques de trabajo de 25m. Tras los 3 primeros hay un
    descanso corto de 5m; tras el cuarto, un descanso largo de 15m. Luego
    vuelve a empezar. Se detiene con Ctrl+C.
    """
    ciclo = 1
    try:
        while True:
            for bloque in range(1, BLOQUES_POR_CICLO + 1):
                # Fase de trabajo
                etiqueta = f"Trabajo {bloque}/{BLOQUES_POR_CICLO} (ciclo {ciclo})"
                if not cuenta_regresiva(TRABAJO_MIN * 60, etiqueta):
                    return False
                if not silencioso:
                    alerta()

                # Fase de descanso
                if bloque == BLOQUES_POR_CICLO:
                    descanso = DESCANSO_LARGO_MIN
                    etiqueta = f"Descanso largo ({DESCANSO_LARGO_MIN}m)"
                else:
                    descanso = DESCANSO_CORTO_MIN
                    etiqueta = f"Descanso ({DESCANSO_CORTO_MIN}m)"
                if not cuenta_regresiva(descanso * 60, etiqueta):
                    return False
                if not silencioso:
                    alerta()
            ciclo += 1
    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h")  # restaura cursor
        sys.stdout.write("\n" + YELLOW + "Ciclo detenido." + RESET + "\n")
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="pymodoro",
        description="Ciclo Pomodoro para la terminal (4x trabajo + descansos, en bucle).",
    )
    parser.add_argument(
        "comando",
        choices=["start"],
        help="start: inicia el ciclo Pomodoro completo en bucle (Ctrl+C para detener).",
    )
    parser.add_argument(
        "-q", "--silencioso", action="store_true", help="No sonar la alerta entre fases."
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {VERSION}"
    )
    args = parser.parse_args(argv)

    completado = ciclo_pomodoro(silencioso=args.silencioso)
    return 0 if completado else 130


if __name__ == "__main__":
    sys.exit(main())
