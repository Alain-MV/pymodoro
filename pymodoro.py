#!/usr/bin/env python3
"""PyModoro - un cronómetro de cuenta regresiva simple para la terminal.

Uso:
    pymodoro 10m        # 10 minutos
    pymodoro 30s        # 30 segundos
    pymodoro 1h         # 1 hora
    pymodoro 1h30m      # 1 hora y 30 minutos
    pymodoro 25m -l "Enfoque"   # con etiqueta
    pymodoro 90         # numero sin sufijo = minutos
"""
import argparse
import re
import sys
import time

VERSION = "1.0.0"

# Codigos de color ANSI
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def parse_duration(texto):
    """Convierte una cadena como '1h30m', '10m', '45s' o '90' a segundos."""
    texto = texto.strip().lower()
    if not texto:
        raise ValueError("duracion vacia")

    # Un numero puro se interpreta como minutos
    if re.fullmatch(r"\d+", texto):
        return int(texto) * 60

    patron = re.findall(r"(\d+)\s*([hms])", texto)
    if not patron:
        raise ValueError(f"no se pudo interpretar la duracion: '{texto}'")

    # Verifica que no haya texto sobrante que no coincida
    if re.sub(r"\d+\s*[hms]", "", texto).strip():
        raise ValueError(f"formato invalido: '{texto}'")

    unidades = {"h": 3600, "m": 60, "s": 1}
    total = sum(int(valor) * unidades[unidad] for valor, unidad in patron)
    if total <= 0:
        raise ValueError("la duracion debe ser mayor que cero")
    return total


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
    """Ejecuta la cuenta regresiva mostrando el tiempo restante."""
    inicio = time.monotonic()
    fin = inicio + total_segundos
    titulo = f" {etiqueta}" if etiqueta else ""

    try:
        while True:
            ahora = time.monotonic()
            restante = fin - ahora
            if restante <= 0:
                break
            restante_ent = int(restante + 0.5)
            transcurrido = total_segundos - restante
            barra = barra_progreso(transcurrido, total_segundos)
            linea = (
                f"\r{CYAN}{BOLD}PyModoro{RESET}{titulo}  "
                f"{GREEN}{formato_hms(restante_ent)}{RESET}  "
                f"{YELLOW}{barra}{RESET}"
            )
            sys.stdout.write(linea)
            sys.stdout.flush()
            # Dormir hasta el proximo segundo entero para una cuenta limpia
            time.sleep(min(1.0, restante - int(restante) or 1.0))
    except KeyboardInterrupt:
        sys.stdout.write("\n" + YELLOW + "Cancelado." + RESET + "\n")
        return False

    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.write(f"{GREEN}{BOLD}¡Tiempo!{RESET}{titulo} ({formato_hms(total_segundos)})\n")
    sys.stdout.flush()
    return True


def alerta():
    """Suena la campana del terminal varias veces."""
    for _ in range(3):
        sys.stdout.write("\a")
        sys.stdout.flush()
        time.sleep(0.4)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="pymodoro",
        description="Un cronometro de cuenta regresiva para la terminal.",
    )
    parser.add_argument(
        "duracion",
        help="Duracion del cronometro, ej: 10m, 30s, 1h, 1h30m, o un numero (minutos).",
    )
    parser.add_argument(
        "-l", "--etiqueta", default=None, help="Etiqueta opcional para el cronometro."
    )
    parser.add_argument(
        "-q", "--silencioso", action="store_true", help="No sonar la alerta al terminar."
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {VERSION}"
    )
    args = parser.parse_args(argv)

    try:
        total = parse_duration(args.duracion)
    except ValueError as e:
        parser.error(str(e))
        return 2

    completado = cuenta_regresiva(total, args.etiqueta)
    if completado and not args.silencioso:
        alerta()
    return 0 if completado else 130


if __name__ == "__main__":
    sys.exit(main())
