# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Estado del repositorio

Este directorio todavía no contiene código: por ahora solo existe `PEAJE.md`, un resumen de decisiones de arquitectura para el proyecto "Peaje" (importado desde Notion). No hay build, lint, tests ni comandos de ejecución que documentar porque no hay implementación aún. Cuando se agregue código a este repo, esta sección debe actualizarse con los comandos reales.

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
