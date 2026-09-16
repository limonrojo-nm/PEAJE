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
| `PEAJE_PRINTER_HOST` | `127.0.0.1` | Backend `network`: host de la impresora o del simulador [escpresso](https://github.com/jflaflamme/escpresso) |
| `PEAJE_PRINTER_PORT` | `9100` | Backend `network`: puerto |
| `PEAJE_PRINTER_USB_VENDOR_ID` | — | Backend `usb`: vendor ID (ver `GET /printer/connected`) |
| `PEAJE_PRINTER_USB_PRODUCT_ID` | — | Backend `usb`: product ID |
| `PEAJE_PRINTER_USB_IN_EP` | `0x81` | Backend `usb`: endpoint bulk IN (default calibrado para la Aclas PP7) |
| `PEAJE_PRINTER_USB_OUT_EP` | `0x03` | Backend `usb`: endpoint bulk OUT (default calibrado para la Aclas PP7) |
| `PEAJE_PRINTER_SERIAL_DEVFILE` | `/dev/serial0` | Backend `serial` |
| `PEAJE_PRINTER_SERIAL_BAUDRATE` | `19200` | Backend `serial` |
| `PEAJE_PRINTER_DOTS_WIDTH` | `384` | Ancho del cabezal en puntos (58 mm ≈ 384, 80 mm ≈ 576). El dibujo se reescala a esta medida |
| `PEAJE_PRINTER_IMAGE_IMPL` | `bitImageColumn` | Comando ESC/POS para mandar el dibujo: `bitImageColumn` (`ESC *`) \| `bitImageRaster` (`GS v 0`) \| `graphics` (`GS ( L`). La Aclas PP7 no entiende `GS v 0`: imprime basura y se apaga. Probar con `peaje-core printer image-test` |
| `PEAJE_ALLOWED_ORIGINS` | — | Orígenes que pueden mandar un dibujo (CORS), separados por coma. Ej: `https://usuario.github.io` |

Sin impresora física ni simulador corriendo, usar `dummy` (descarta el output,
no falla):

```bash
PEAJE_PRINTER_BACKEND=dummy uvicorn peaje_core.main:app --reload --port 8000
```

Para ver el ticket renderizado sin hardware, usar el simulador
[escpresso](https://github.com/jflaflamme/escpresso) (requiere
[Rust](https://rustup.rs/)):

```bash
cargo install escpresso
escpresso   # abre una ventana con vista previa y escucha en 127.0.0.1:9100
```

Con `escpresso` corriendo, el backend `network` (default) ya apunta a ese
host/puerto — no hace falta configurar nada extra.

## En la Raspberry: correr como servicio

En sala, `peaje-core` no se lanza a mano: es un servicio de systemd que
arranca solo al encender la Raspberry y se vuelve a levantar si se cae. La
configuración vive en un `.env` en la carpeta del repo (pydantic-settings lo
lee también al correr a mano, así los dos caminos usan los mismos valores).

```bash
cp .env.example .env          # y ajustar: IDs USB, ancho del papel, origen de la app
./deploy/instalar-servicio.sh # una vez; se puede repetir, reinstala y reinicia
```

El script rellena `deploy/peaje-core.service` con el usuario, la carpeta y el
Python del entorno instalado, y lo activa. Después:

```bash
systemctl status peaje-core          # ¿está corriendo?
journalctl -u peaje-core -f          # el log en vivo (cada dibujo que llega)
sudo systemctl restart peaje-core    # tras un git pull o un cambio en .env
```

El servicio escucha sólo en `127.0.0.1:8000`; hacia internet lo publica
Tailscale Funnel (`tailscale funnel --bg 8000`), que también persiste al
reiniciar. Si tras un reinicio la estación no responde desde afuera, mirar
primero `tailscale status`.

## Rutas disponibles

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Estado del servidor |
| `GET` | `/` | Panel de pruebas HTML: listado de impresoras USB conectadas y botón para disparar una impresión de prueba |
| `GET` | `/printer/connected` | Impresoras USB detectadas en el host (vendor/product ID) — `503` si no hay backend USB nativo (`libusb`) disponible |
| `POST` | `/printer/test-print` | Envía un ticket de prueba a la impresora configurada — `502` si falla la comunicación |
| `POST` | `/printer/drawing` | Recibe el dibujo de un visitante y lo imprime como ticket — ver *Contrato con la app* |

## Contrato con la app

La instalación **El Peaje** (repo `am3-el-peaje-v2`, React) es hoy el único
consumidor de `peaje-core`. Al llegar al final del recorrido, el teléfono del
visitante manda su dibujo:

| | |
|---|---|
| Método y ruta | `POST /printer/drawing` |
| Cuerpo | `multipart/form-data` |
| Campos | **`drawing`**: un PNG (canvas de celular, ~1000 px, fondo blanco opaco). **`header`** y **`footer`**: el texto del ticket, hasta 500 caracteres cada uno. El encabezado se imprime en fuente A (32 caracteres por renglón a 58 mm) y el pie en fuente B (42) |
| Respuesta | `200` si la impresora aceptó el trabajo; `400` si no es una imagen, `413` si excede 5 MB, `502` si falló la impresión |

**Renombrar la ruta o el campo deja la obra muda**: la app no le avisa nada al
visitante si la impresión falla —es una decisión de la obra, para no mandarlo a
esperar frente a una impresora vacía—, así que una ruptura de contrato no se
nota hasta que alguien recorre la pieza entera. Avisar antes de cambiarlo.

La app se sirve por HTTPS desde GitHub Pages (lo exigen la cámara y el
micrófono de su última sección) y `peaje-core` desde un túnel, así que son
orígenes distintos: sin `PEAJE_ALLOWED_ORIGINS` el navegador bloquea el envío.

**El texto del ticket lo manda la app, no lo decide `peaje-core`.** La voz de la
obra vive en el repo de la obra; la estación imprime lo que le dan y no sabe qué
dice el comprobante. Por eso `header`/`footer` son parámetros y no configuración.

Nada de lo que llega es dato del visitante: el dibujo es anónimo y los textos son
fijos, iguales en cada ticket.

## Comandos de terminal (CLI)

Misma lógica de negocio que las rutas HTTP, vía la capa `apis/cli`:

```bash
peaje-core printer test                       # equivalente a POST /printer/test-print
peaje-core printer image-test                 # figura de prueba con el modo de imagen configurado
peaje-core printer image-test --impl graphics # ...o con otro, para ver cuál entiende la impresora

El ticket de prueba incluye una línea con acentos y eñes a propósito. El texto
del ticket real los lleva, y `python-escpos` los resuelve cambiando de página de
códigos por su cuenta (emite `ESC t`). Si la PP7 numera sus páginas distinto,
esa línea sale con glifos equivocados y el resto bien — **conviene que sea lo
primero que se imprima en la impresora física**, porque es la única forma de
saberlo. Si falla, se arregla fijando el perfil de la impresora o sacándole las
tildes al texto del ticket.
```

## Arquitectura

Estructura por capas inspirada en el
[Django Styleguide de HackSoft](https://github.com/HackSoftware/Django-Styleguide),
adaptada a FastAPI: la lógica de negocio vive en `services/`, agnóstica a
cómo se la invoca; cada forma de invocarla (HTTP, CLI, a futuro una tarea de
cola) es una capa delgada bajo `apis/`. Detalle completo en
[`CLAUDE.md`](CLAUDE.md).
