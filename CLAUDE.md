# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos

Entorno: pyenv-virtualenv `peaje-core` (Python 3.12), fijado en `.python-version`. Instalar/reinstalar dependencias tras tocar `pyproject.toml`:

```bash
pip install -e ".[dev]"
```

Levantar el servidor de desarrollo (con recarga automática):

```bash
uvicorn peaje_core.main:app --reload --port 8000
```

Ejecutar un comando de la capa CLI (equivalente en terminal a una acción HTTP, misma lógica de negocio):

```bash
peaje-core printer test
```

Sin impresora física ni simulador `escpresso` corriendo, usar el backend `dummy` (no falla, descarta el output):

```bash
PEAJE_PRINTER_BACKEND=dummy peaje-core printer test
```

No hay lint ni test suite configurados todavía.

## Arquitectura de peaje-core (capas, inspirado en el Django Styleguide de HackSoft)

La lógica de negocio vive en `services/` y es agnóstica a cómo se la invoca. Cada forma de invocarla (HTTP, CLI, y en el futuro un worker de la cola Redis) es una capa de API delgada bajo `apis/` que solo traduce su formato de entrada/salida y llama al servicio — nunca contiene lógica propia:

```
src/peaje_core/
  config.py            # Settings (pydantic-settings, prefijo de env PEAJE_)
  main.py              # ensambla la app FastAPI, incluye los routers de apis/http
  services/            # lógica de negocio, sin saber de HTTP/CLI
    printer.py          # run_print_test()
  printers/             # capa de infraestructura: adapta config.Settings al
    client.py            # backend real de python-escpos (network/usb/serial/dummy)
  apis/
    http/                # routers de FastAPI (solo request/response)
      printer.py          # POST /printer/test-print
      pages.py            # GET / — vista HTML con el botón de prueba
      templates/index.html
    cli/                  # comandos de terminal (Typer), mismo patrón
      main.py              # entry point `peaje-core` (ver pyproject.toml [project.scripts])
      printer.py           # `peaje-core printer test`
```

Al agregar una funcionalidad nueva: la lógica va en `services/`, y cada forma de dispararla (HTTP, CLI, futura tarea RQ) es un archivo delgado en el `apis/<tipo>/` correspondiente que la invoca. Si el negocio necesita hablarle a la impresora, pasa por `printers/client.get_printer()` — nunca instanciar `python-escpos` directamente fuera de esa capa, así el backend (red/USB/serie/dummy) se controla solo por `config.Settings`.

## Qué es el proyecto

Instalación artística multimedia para museos (de Jose): una web app presenta una serie de captchas que el público resuelve desde su celular, y al finalizar el recorrido una impresora térmica imprime algo relacionado con ese proceso. Nico asiste en la arquitectura de infraestructura.

## Arquitectura acordada

Cliente-servidor: los celulares son clientes; un servidor central gestiona las interacciones y envía trabajos a una cola de impresión. La impresora térmica está conectada a una Raspberry Pi Zero dedicada a imprimir. Se descartó que la Raspberry Zero sirva la web app y levante una red WiFi propia (recursos limitados + fricción/alertas de seguridad al pedirle a usuarios del museo conectarse a una red desconocida).

Dos modos de despliegue, según audiencia y conectividad disponible:

- **Modo prototípico / universidad** (sin internet real disponible, público tolera fricción): la Raspberry Pi 4 (4 GB RAM, 64 GB, hardware de Nico) sirve la web app, gestiona clientes **y** la cola de impresión, conectada a un router WiFi externo. Concurrencia estimada 50–100 usuarios simultáneos sin comprometer la impresión — el cuello de botella real es la impresora física, no la cantidad de usuarios.
- **Modo museo** (con conectividad a internet real): la Raspberry Pi se dedica exclusivamente a la impresora; el servidor con la web app vive en la nube, accesible por la red del museo o los datos móviles de los visitantes.

Cualquier diseño de la capa de servidor debe ser agnóstico a cuál de los dos modos está activo (ver "Próximos pasos" en `PEAJE.md`).

## Stack (modo prototípico)

- **Servidor:** Python
- **Cola de trabajos de impresión:** Redis — pendiente decidir si se usa RQ (Redis Queue) o listas de Redis directamente
- **Impresora:** Aclas PP7, protocolo ESC/POS (flujo de bytes secuencial, no PostScript/PDL). Librería sugerida: `python-escpos`. Simulador para desarrollar sin hardware físico: **escpresso** (expone un servidor TCP con vista previa en tiempo real del ticket).

## Referencia

El detalle completo de decisiones, el registro de la conversación que las originó, y los próximos pasos pendientes están en `PEAJE.md`. Ese archivo se regenera desde Notion (workspace, base "Proyectos", página "Peaje") — al editar contexto de producto/decisiones, considerar si corresponde actualizarlo también ahí en vez de solo en este repo.
