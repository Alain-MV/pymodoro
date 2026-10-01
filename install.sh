#!/usr/bin/env bash
#
# Instalador de PyModoro
#
# Uso:
#   git clone https://github.com/<usuario>/PyModoro.git
#   cd PyModoro
#   ./install.sh
#
# Instala el comando `pymodoro` en ~/.local/bin (no requiere sudo).
# Puedes cambiar el destino con:  PREFIX=/usr/local ./install.sh
#
set -euo pipefail

# Directorio donde vive este script (y por tanto pymodoro.py)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/pymodoro.py"

# Destino de instalacion
PREFIX="${PREFIX:-$HOME/.local}"
BIN_DIR="$PREFIX/bin"
DEST="$BIN_DIR/pymodoro"

info()  { printf '\033[96m==>\033[0m %s\n' "$1"; }
ok()    { printf '\033[92m==>\033[0m %s\n' "$1"; }
warn()  { printf '\033[93m==>\033[0m %s\n' "$1"; }
error() { printf '\033[91m==>\033[0m %s\n' "$1" >&2; }

# 1. Verificar que exista Python 3
if ! command -v python3 >/dev/null 2>&1; then
    error "No se encontro python3. Instalalo antes de continuar."
    exit 1
fi
info "Python 3 encontrado: $(python3 --version)"

# 2. Verificar que el fuente exista
if [ ! -f "$SRC" ]; then
    error "No se encontro pymodoro.py junto a install.sh."
    exit 1
fi

# 3. Crear el directorio bin si hace falta
mkdir -p "$BIN_DIR"

# 4. Copiar y hacer ejecutable
info "Instalando en $DEST"
cp "$SRC" "$DEST"
chmod +x "$DEST"
ok "PyModoro instalado."

# 5. Comprobar que el destino este en el PATH
case ":$PATH:" in
    *":$BIN_DIR:"*)
        ok "Listo. Ejecuta:  pymodoro 10m"
        ;;
    *)
        warn "$BIN_DIR no esta en tu PATH."
        # Detectar shell para sugerir el archivo correcto
        shell_rc="$HOME/.bashrc"
        case "${SHELL:-}" in
            *zsh)  shell_rc="$HOME/.zshrc" ;;
            *bash) shell_rc="$HOME/.bashrc" ;;
        esac
        echo
        echo "    Agregalo con:"
        echo "      echo 'export PATH=\"$BIN_DIR:\$PATH\"' >> $shell_rc"
        echo "      source $shell_rc"
        echo
        echo "    Mientras tanto puedes ejecutarlo asi:  $DEST 10m"
        ;;
esac
