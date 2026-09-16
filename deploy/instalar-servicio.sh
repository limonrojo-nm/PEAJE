#!/bin/bash
# Deja peaje-core corriendo como servicio en la Raspberry: arranca solo al
# encenderla y se vuelve a levantar si se cae. Se corre una vez, desde la
# carpeta del repo, con el usuario que va a operar la impresora (no root):
#
#   ./deploy/instalar-servicio.sh
#
# Antes de correrlo tiene que existir el .env (copiar .env.example y ajustar).
# Se puede volver a correr las veces que haga falta: reinstala y reinicia.

set -e

DIR="$(cd "$(dirname "$0")/.." && pwd)"
USER_NAME="$(id -un)"

if [ "$USER_NAME" = "root" ]; then
  echo "Correlo con tu usuario normal, no con sudo: el servicio tiene que" >&2
  echo "imprimir con los mismos permisos con los que probaste la impresora." >&2
  exit 1
fi

if [ ! -f "$DIR/.env" ]; then
  cp "$DIR/.env.example" "$DIR/.env"
  echo "Creé $DIR/.env a partir del ejemplo. Revisá que los valores sean los"
  echo "de esta impresora y volvé a correr este script."
  exit 1
fi

# El Python del entorno que tenga activo la carpeta (pyenv, venv, lo que
# sea): systemd no conoce shims ni activaciones, necesita la ruta real.
PYTHON="$(cd "$DIR" && python3 -c 'import sys; print(sys.executable)')"
if ! "$PYTHON" -c 'import uvicorn, peaje_core' 2>/dev/null; then
  echo "$PYTHON no tiene instalado peaje-core. ¿Corriste 'pip install -e \".[dev]\"' en esta carpeta?" >&2
  exit 1
fi

# Si hay un uvicorn lanzado a mano en el 8000, el servicio no podría arrancar
# y el chequeo de abajo contestaría por el viejo, mintiendo que anduvo.
if ! systemctl is-active --quiet peaje-core && (ss -ltn 2>/dev/null | grep -q ':8000 '); then
  echo "Ya hay algo escuchando en el puerto 8000 (seguramente un uvicorn lanzado" >&2
  echo "a mano). Cerralo con Ctrl+C en su terminal y volvé a correr este script." >&2
  exit 1
fi

echo "→ usuario:  $USER_NAME"
echo "→ carpeta:  $DIR"
echo "→ python:   $PYTHON"

sed -e "s|{{USER}}|$USER_NAME|g" \
    -e "s|{{DIR}}|$DIR|g" \
    -e "s|{{PYTHON}}|$PYTHON|g" \
    "$DIR/deploy/peaje-core.service" | sudo tee /etc/systemd/system/peaje-core.service >/dev/null

sudo systemctl daemon-reload
sudo systemctl enable peaje-core >/dev/null
sudo systemctl restart peaje-core

sleep 3
if curl -fsS http://127.0.0.1:8000/health >/dev/null; then
  echo
  echo "Listo: peaje-core está corriendo como servicio y arranca solo al encender."
  echo "  ver estado:   systemctl status peaje-core"
  echo "  ver el log:   journalctl -u peaje-core -f"
  echo "  reiniciar:    sudo systemctl restart peaje-core"
  echo
  echo "Falta ver que imprima desde el servicio (no es lo mismo que a mano):"
  echo "  curl -X POST http://127.0.0.1:8000/printer/test-print"
  echo "Tiene que salir el ticket de prueba. Si no, mirá el log de arriba."
  echo
  echo "Para volver a como estaba antes: sudo systemctl disable --now peaje-core"
else
  echo
  echo "El servicio se instaló pero no responde. Mirá qué dice:" >&2
  echo "  journalctl -u peaje-core -n 30" >&2
  exit 1
fi
