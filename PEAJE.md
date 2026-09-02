# Proyecto: Peaje 🖨️

**Estado:** Activo
**Fuente:** Notion (workspace) — página "Peaje" dentro de la base "Proyectos"

## Síntesis

Jose está desarrollando una instalación artística multimedia para museos: una web app que presenta una serie de captchas que el público resuelve desde su celular, y al finalizar el recorrido, una impresora térmica imprime algo relacionado con ese proceso de resolución.

Hay que resolver la arquitectura de infraestructura del sistema (Nico asiste en esta parte).

## Decisiones y lineamientos acordados

- **Arquitectura cliente-servidor:** los celulares actúan como clientes; un servidor central gestiona las interacciones, las organiza y envía los trabajos correspondientes a la cola de impresión.
- La impresora térmica está conectada a una **Raspberry Pi Zero**, encargada de ejecutar la impresión.
- Se descartó que la Raspberry Zero sirva la web app y levante además una red WiFi local propia: combina dos problemas —recursos limitados para servir múltiples clientes, y la fricción/alertas de seguridad de pedirle a usuarios del museo que se conecten a una red desconocida.

### Solución adoptada: separar responsabilidades por modo de despliegue

**Modo prototípico / universidad** (público especializado, tolera fricción de red):
- La propia Raspberry Pi sirve la web app, gestiona la interacción con los clientes **y** maneja la cola de impresión (doble rol).
- Hardware: Raspberry Pi 4, 4 GB RAM, 64 GB de almacenamiento (de Nico).
- Se conecta a un router WiFi externo que da la red local.
- Concurrencia estimada: 50–100 usuarios livianos simultáneos sin comprometer la cola de impresión (el cuello de botella real es la impresora física, no la cantidad de usuarios).

**Modo museo** (requiere conectividad a internet real):
- La Raspberry Pi se dedica exclusivamente a la impresora.
- El servidor con la web app vive aparte, en la nube, accesible por la red del museo o los datos móviles de los visitantes (elimina la necesidad de conectarse a una red local).

### Stack tecnológica (modo prototípico)

- **Servidor:** Python
- **Cola de trabajos de impresión:** Redis (liviano, apropiado para el hardware de la Raspberry)
- Pendiente: definir si se usa una librería de más alto nivel como **RQ (Redis Queue)** o las listas de Redis directamente.

### Impresora térmica

- Modelo: **Aclas PP7**
- Protocolo: **ESC/POS** — lenguaje de comandos crudo y secuencial (no PostScript ni un lenguaje de descripción de página), heredero de ESC/P (estándar de Epson de 1980 para impresoras matriciales).
- Funcionamiento: se envía un flujo de bytes que la impresora ejecuta a medida que lo recibe, sin renderizar una página completa de antemano. Comando típico: byte de escape + identificador de instrucción (negrita, alineación, imprimir imagen convertida a mapa de bits, etc.).
- Librería Python sugerida: **python-escpos** (abstrae el armado de comandos ESC/POS).
- Simulador para desarrollo sin impresora física: **escpresso** (Windows/Mac/Linux) — expone un servidor TCP y muestra vista previa en tiempo real del ticket.

## Próximos pasos sugeridos

- [ ] Definir la estructura de la capa de servidor de forma agnóstica al entorno de despliegue (prototípico vs. museo).
- [ ] Resolver el protocolo de comunicación entre el servidor Python y Redis para el envío de trabajos a la cola de impresión.
- [ ] Decidir entre RQ o listas de Redis directas para gestionar la cola.
- [ ] Confirmar el mapa de comandos ESC/POS específico de la Aclas PP7 (manual del fabricante) para el diseño del ticket impreso.
- [x] Raspi: prueba de concepto de impresión — hecha en `raspinico` (Pi 4), impresora Aclas PP7 por USB, backend `usb` de python-escpos.
- [ ] Convertir `peaje-core` en servicio systemd en la Raspi (hoy corre como proceso `nohup` suelto en `raspinico`, sin arranque automático ni supervisión) — decisión deliberada de dejarlo pendiente por ahora.

## Apéndice: registro de la conversación (contexto de decisiones)

Nico explicó el proyecto de José: una pieza artística para museos con captchas resueltos vía celular y una impresora térmica que imprime al final del recorrido. Nico va a asistir en la arquitectura e infraestructura del sistema.

Se planteó inicialmente que la Raspberry Pi Zero, además de manejar la impresora, sirviera la web app y ofreciera una red WiFi local a la que los usuarios debían conectarse. Se identificaron dos problemas: la limitación de recursos de la Raspberry Zero para servir múltiples clientes, y la fricción/riesgo de abandono de pedirle a los usuarios conectarse a una red WiFi desconocida (con las alertas de seguridad que eso dispara en los celulares).

Se discutió si escalar a una Raspberry Pi 4 o 5 resolvía el problema: mejoraría el rendimiento pero no la fricción de conexión de red, por lo que separar el servidor de la Raspberry seguía siendo preferible en el escenario de museo. Además hay una restricción real de conectividad a internet en el entorno de prueba en la universidad, a diferencia del entorno final en el museo. De ahí surgió la propuesta de dos modos de despliegue diferenciados por audiencia y contexto.

Para el modo prototípico se definió usar la Raspberry Pi 4 de 4 GB de RAM de Nico, conectada a un router WiFi externo que da la red local, resolviendo desde ahí tanto el servicio de la web app y la interacción con los clientes como la gestión de la cola de impresión. Se evaluó la concurrencia posible (50–100 usuarios simultáneos como manejable), señalando que el verdadero cuello de botella es la impresora física y no la cantidad de usuarios conectados. Se definió Python para el servidor y Redis para la cola de impresión, quedando pendiente decidir la librería específica para gestionarla.

---
*Generado a partir de la página "Peaje" (y su subpágina "2-9") del workspace de Notion, base de datos "Proyectos". Última edición en Notion: 2026-09-02.*
