# Peaje — peaje-core

Servidor de la instalación artística "Peaje": gestiona la interacción con los
clientes (celulares) y dispara la impresión térmica del ticket. Contexto y
decisiones de arquitectura completas en [`PEAJE.md`](PEAJE.md).

## Requisitos

- [pyenv](https://github.com/pyenv/pyenv) + [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
- Python 3.12

## Instalación

```bash
pyenv virtualenv 3.12.14 peaje-core   # una sola vez; el repo ya trae .python-version
pip install -e ".[dev]"
```

## Ejecutar el servidor

```bash
uvicorn peaje_core.main:app --reload --port 8000
```

Health check: `curl http://127.0.0.1:8000/health`

### Backend de impresora

Configurable por variables de entorno con prefijo `PEAJE_` (ver
[`src/peaje_core/config.py`](src/peaje_core/config.py)):

| Variable | Default | Descripción |
|---|---|---|
| `PEAJE_PRINTER_BACKEND` | `network` | `network` \| `usb` \| `serial` \| `dummy` |
| `PEAJE_PRINTER_HOST` | `127.0.0.1` | Backend `network`: host de la impresora o del simulador [escpresso](https://github.com/knuton/escpresso) |
| `PEAJE_PRINTER_PORT` | `9100` | Backend `network`: puerto |
| `PEAJE_PRINTER_USB_VENDOR_ID` | — | Backend `usb`: vendor ID (ver `GET /printer/connected`) |
| `PEAJE_PRINTER_USB_PRODUCT_ID` | — | Backend `usb`: product ID |
| `PEAJE_PRINTER_SERIAL_DEVFILE` | `/dev/serial0` | Backend `serial` |
| `PEAJE_PRINTER_SERIAL_BAUDRATE` | `19200` | Backend `serial` |

Sin impresora física ni simulador corriendo, usar `dummy` (descarta el output,
no falla):

```bash
PEAJE_PRINTER_BACKEND=dummy uvicorn peaje_core.main:app --reload --port 8000
```

## Rutas disponibles

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Estado del servidor |
| `GET` | `/` | Panel de pruebas HTML: botón para disparar una impresión de prueba |
| `GET` | `/printer/connected` | Impresoras USB detectadas en el host (vendor/product ID) — `503` si no hay backend USB nativo (`libusb`) disponible |
| `POST` | `/printer/test-print` | Envía un ticket de prueba a la impresora configurada — `502` si falla la comunicación |

## Comandos de terminal (CLI)

Misma lógica de negocio que las rutas HTTP, vía la capa `apis/cli`:

```bash
peaje-core printer test   # equivalente a POST /printer/test-print
```

## Arquitectura

Estructura por capas inspirada en el
[Django Styleguide de HackSoft](https://github.com/HackSoftware/Django-Styleguide),
adaptada a FastAPI: la lógica de negocio vive en `services/`, agnóstica a
cómo se la invoca; cada forma de invocarla (HTTP, CLI, a futuro una tarea de
cola) es una capa delgada bajo `apis/`. Detalle completo en
[`CLAUDE.md`](CLAUDE.md).
