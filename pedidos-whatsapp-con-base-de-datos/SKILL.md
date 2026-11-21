---
name: pedidos-whatsapp-con-base-de-datos
description: Método para montar un sistema de pedidos de una tienda pequeña que hoy copia pedidos a mano desde WhatsApp, Instagram, TikTok o Shopify. Cubre página de pedidos, base de datos en Supabase como fuente única, alertas y confirmaciones por Telegram, vencimiento automático de pedidos sin pagar, garantías, integración con Shopify, respuestas en WhatsApp Business, seguimiento de clientes que no compraron y reportes. Usar cuando el negocio pierde tiempo copiando pedidos, tiene precios o domicilios en varios lugares, cobra por varias formas de pago, o no sabe qué pedidos están pendientes, qué clientes faltan por comprar o qué garantías siguen abiertas.
---

# Sistema de pedidos: base de datos, alertas, seguimiento y garantías

## 1. El problema que resuelve

Muchas tiendas pequeñas venden por WhatsApp, Instagram o TikTok, y cada pedido pasa por las manos del dueño varias veces:

- Le escriben el pedido en un chat y lo copia a una hoja, una nota o la memoria.
- El precio y el domicilio cambian, y hay que acordarse de actualizarlos en cada lugar (chat, catálogo, hoja, publicación).
- Nadie sabe con certeza qué pedidos están pagados, cuáles esperan pago y cuáles ya se entregaron.
- Los pedidos que el cliente nunca paga se quedan para siempre en la lista.
- Los clientes que preguntaron o pidieron y no volvieron a escribir se pierden, porque nadie les hace seguimiento.
- Las garantías se pierden: no se sabe qué producto se cambió, cuándo, ni si venció el plazo.
- No se sabe cuánto se vende, qué margen queda, ni qué clientes dejaron de comprar.

Lo que hace falta es **un solo lugar donde viven productos, precios, pedidos, pagos y garantías**, y que todo lo demás (página, alertas, recordatorios, reportes) lea y escriba ahí.

## 2. Qué es la solución

Un sistema pequeño, sin servidor propio:

- **Página web** (un solo HTML, publicado en Netlify) donde el cliente elige productos, opciones, forma de pago y entrega.
- **Base de datos** en Supabase (Postgres) que guarda todo y pone las reglas: precios, domicilios, validaciones, estados.
- **Funciones** en Supabase que reaccionan a eventos: avisar pedidos nuevos, recibir botones de Telegram, recibir pedidos de Shopify.
- **Tareas programadas** en la base que corren solas (vencer pedidos sin pago, limpiar registros viejos).
- **Telegram** como el teléfono del dueño: avisos, botones de pagado y entregado, garantías.
- **WhatsApp Business** (la app, sin API) para respuestas automáticas y rápidas.
- **Vistas de reporte** para ventas, margen, seguimiento y cumpleaños.

## 3. Mapa: qué hace cada pieza

### 3.1 Página de pedidos
- Carga catálogo y zonas de domicilio desde la base con la clave pública. No guarda precios.
- Productos por categoría, pestaña de "lo más pedido", búsqueda, opciones obligatorias (color, modelo) y total en vivo.
- Pide nombre, celular, correo y la aceptación de datos. Si es domicilio, pide municipio y dirección. Si es retiro, no pide dirección, y nunca se publica la dirección de la casa del dueño.
- Forma de pago: efectivo, transferencia, crédito por cuotas y, si se decide, enlace de pago en línea.
- Al enviar llama a `crear_pedido` y muestra el número del pedido (por ejemplo INZ-1000, INZ-1001…).
- Si la base no responde en unos segundos, abre WhatsApp con el pedido escrito en texto. El cliente no se queda sin comprar.
- Respaldo: copia el pedido a un formulario oculto de Netlify.

### 3.2 Función `crear_pedido` (en la base)
- Valida campos y reglas de negocio.
- Calcula precios desde la tabla de productos. Nunca desde el navegador.
- Calcula el domicilio por municipio. Si el municipio es "Otro", el domicilio queda en 0 y se confirma por WhatsApp.
- Aplica códigos de descuento si existen.
- Anti-spam: límite de pedidos por celular en un periodo corto. Campo trampa: si un robot lo llena, el pedido se descarta.
- Guarda cliente, pedido y detalle en una sola transacción, con número consecutivo.
- Deja el pedido en **pendiente**, el punto de partida de todo lo demás.

### 3.3 Disparador y función de alerta
- Al insertarse un pedido, un disparador llama a la función de alerta.
- La función lee el pedido completo (cliente, productos con opciones, subtotal, descuento, envío, total, entrega, forma de pago, notas) y lo envía a cada chat registrado de Telegram.
- Si el pedido está pendiente, el mensaje trae el botón **💰 Pagado**. Si ya está pagado, trae **📦 Entregado**.

### 3.4 Función de botones (Telegram)
Solo responde a chats registrados.
- **💰 Pagado:** pedido a confirmado y pagado. Avisa a todos. Confirmar = ya pagó, no ya se entregó.
- **📦 Entregado:** pedido a entregado, con fecha. Solo si antes estaba pagado. Avisa a todos.
- **🛡️ Garantía:** pide la falla como respuesta obligatoria y registra la garantía ligada al pedido.
- **✅ Resuelta:** cierra la garantía.
- **/garantias:** lista las abiertas, con días transcurridos y alerta si pasan el plazo.
- **/garantia NUMERO:** inicia el registro de una garantía de ese pedido.
- Otros mensajes devuelven la lista de comandos.

### 3.5 Tareas programadas (en la base)
- **Vencer pedidos sin pago:** cada 15 minutos, pedidos pendientes de más de 48 horas pasan a **cancelado**, con motivo registrado.
- **Limpiar intentos de envío:** una vez al día se borran registros viejos del anti-spam.

### 3.6 Función de Shopify (si aplica)
- Recibe los webhooks `orders/create` y `orders/paid`.
- Revisa el token de la URL y el dominio de la tienda. Sin token válido responde 401.
- `orders/create` registra el pedido. `orders/paid` lo marca como pagado y, si no existía, lo registra ya pagado.
- Si falla al guardar, responde 200 para que Shopify no reintente sin fin, y deja el error en los registros.

### 3.7 Vistas de reporte (en la base)
- **Vista pública de productos:** sin costo.
- **Resumen de ventas:** ventas, costo y margen por periodo, para Power BI.
- **Oportunidades de seguimiento:** clientes con autorización de datos que no tienen pedidos confirmados o entregados, y que están en alguno de estos casos: registrados sin compra; último pedido cancelado; último pedido pendiente desde hace más de 2 horas (pedido abandonado). Incluye el último producto, para escribirles.
- **Cumpleaños del mes:** para un mensaje de felicitación.

### 3.8 WhatsApp Business (app, sin API)
- **Bienvenida y ausencia:** responden solas. Dicen el horario y redirigen a la página de pedidos.
- **Respuestas rápidas (atajos con /):** precios, formas de pago, domicilio, garantía, enlace de la página. Se escriben una vez y se reutilizan.
- No usa la API oficial de Meta, que es de pago y exige verificación del negocio.

## 4. Ciclo de vida de un pedido

| Estado | Quién lo pone | Cómo sale |
|---|---|---|
| **pendiente** (sin pagar) | El cliente, al enviar la página o al llegar por Shopify | Pagado → confirmado. O 48 horas sin pago → cancelado automático |
| **confirmado** (pagado) | El dueño, con 💰 Pagado (o Shopify con `orders/paid`) | Entregado → entregado |
| **entregado** | El dueño, con 📦 Entregado | Fin. Desde aquí se registran garantías |
| **cancelado** | El sistema (48 horas) o el dueño | Fin |

`estado_pago` puede ser **pendiente** o **pagado**, y es lo que decide qué botón aparece en Telegram.

## 5. Cuando el cliente o el dueño tardan

### 5.1 El cliente no paga
- El pedido queda en pendiente y el dueño recibe la alerta con 💰 Pagado.
- A las 48 horas sin pago, el sistema lo cancela solo, con motivo.
- Antes de eso, el cliente aparece en oportunidades de seguimiento como pedido abandonado (desde las 2 horas), con lo que pidió. Sirve para escribirle.
- **Regla:** nada se confirma sin pago. Si el cliente dice que ya pagó, el dueño revisa la cuenta antes de tocar 💰 Pagado.

### 5.2 El cliente escribe por WhatsApp y no responde
- Si el dueño no contesta, el mensaje de ausencia indica el horario y lleva a la página.
- Si el cliente nunca hizo pedido en la página, aparece como registrado sin compra (si autorizó datos).
- Los atajos de WhatsApp evitan repetir el mismo texto.

### 5.3 El cliente tarda en recoger o en la entrega
- El pedido sigue en confirmado hasta que el dueño toca 📦 Entregado.
- El sistema no calcula tiempos de entrega. Si la página promete un tiempo, tiene que ser uno que el dueño cumpla. Si no, mejor no prometerlo.

### 5.4 El dueño tarda en confirmar pagos
- El aviso de alerta solo sale cuando se crea el pedido. **No hay recordatorio de pendientes.** Es la mejora más útil que suele faltar: un recordatorio periódico en Telegram con los pedidos pendientes.
- Lo que sí hace el sistema: los vence a las 48 horas, así que nunca quedan para siempre.

### 5.5 Garantía que tarda
- Queda abierta y aparece en `/garantias` con los días transcurridos.
- Pasado el plazo, aparece con alerta.
- Se cierra con ✅ Resuelta cuando el producto ya se cambió o reparó.

### 5.6 Shopify que no entrega el aviso
- Shopify reintenta los avisos que no le confirmaron. Si la URL o el token cambiaron, hay que actualizar la dirección en Shopify.
- Si un pedido no aparece, se revisan los registros de la función y Shopify, y se carga a mano si hace falta.

## 6. Garantías
- Se registran desde Telegram, ligadas al número de pedido.
- Cada una tiene falla, fecha de apertura, fecha de resolución y estado (abierta o resuelta).
- El plazo se define con el dueño y se configura en el código.
- Una tabla de garantías vacía al principio es normal.

## 7. Principios del método
1. **Una sola fuente de verdad.** Precios y domicilios viven solo en la base.
2. **El navegador no decide precios ni estados.** Validación y cambios de estado ocurren en la base o en las funciones.
3. **Lo privado no se publica.** Costos y direcciones particulares nunca aparecen en la página.
4. **Pagado y entregado son cosas distintas.** Cada botón hace una sola cosa.
5. **Nada se confirma sin pago, y nada queda pendiente para siempre.**
6. **Ninguna clave dentro del código.** Tokens y claves van en secretos del servicio.
7. **Si algo falla, el cliente no se queda sin comprar.** WhatsApp sirve de respaldo.
8. **Cambios pequeños, publicados de una vez.** Cada `push` a la rama principal publica la página.

## 8. Cómo se construye, paso a paso

### Paso 1. Entender el negocio
- **Qué:** productos, precios, costos, formas de pago, zonas de domicilio, política de garantía, horario, dirección que se publica.
- **Por qué:** casi todos los errores vienen de reglas que nadie escribió.
- **Entregable:** un documento corto con las reglas, que el dueño confirma.

### Paso 2. Modelar la base
- **Qué:** productos (con costo privado y opciones en JSON), clientes, pedidos, detalle, domicilios por zona, códigos de descuento, intentos de envío, garantías, contactos de Telegram.
- **Por qué:** el detalle copia nombre y precio del momento de la venta. Si el precio cambia después, los pedidos viejos no cambian.

### Paso 3. Crear `crear_pedido`
- Valida, calcula, aplica descuento y anti-spam, y guarda todo en una transacción.

### Paso 4. Construir la página
- Una sola página HTML que lee de la base y llama a `crear_pedido`.
- Rápida, barata de publicar y fácil de cambiar.

### Paso 5. Seguridad, antes de conectar nada más
- RLS activo en todas las tablas.
- Quitar al público los permisos por defecto. Darle solo: leer productos sin costo, leer zonas activas y ejecutar `crear_pedido`.
- Vistas públicas con `security_invoker`, no `security definer`.
- Funciones internas (disparadores, webhooks) sin permiso para `anon` ni `authenticated`.
- **Verificación:** el asesor de seguridad del servicio, y una llamada sin clave que responda 401.

### Paso 6. Alertas y botones de Telegram
- Disparador → función de alerta → mensaje con botón. Función de botones → cambio de estado → aviso a todos.
- Solo chats registrados pueden tocar botones. Usar el chat de la persona, no el del bot.

### Paso 7. Vencimiento y tareas programadas
- Tarea cada 15 minutos que cancela pedidos pendientes de más de 48 horas.
- Tarea diaria que limpia intentos viejos.

### Paso 8. Garantías
- Tabla ligada al pedido, comandos, botón de resuelta, alerta por plazo.

### Paso 9. Shopify (si aplica)
- Webhooks `orders/create` y `orders/paid` a una función, con token en la URL y revisión del dominio.
- Responder 200 aunque falle el guardado, para que no haya reintentos sin fin.

### Paso 10. Seguimiento y reportes
- Vista de oportunidades, vista de cumpleaños, vista de ventas y margen para Power BI.

### Paso 11. Publicar y desplegar
- **Página:** `push` a la rama principal. El hosting la publica sola.
- **Funciones:** el servicio **no** las actualiza desde GitHub. Se despliegan a mano. El código queda en el repositorio como respaldo.
- **Orden seguro al cambiar una clave:**
  1. Crear o cambiar el secreto en el servicio.
  2. Desplegar la función que lee el secreto del entorno.
  3. Si es Telegram, registrar el webhook de nuevo.
  4. Si es Shopify, cambiar la URL en Shopify.
  5. Probar con un pedido de prueba y borrarlo.
- Si se cambia la clave en el servicio externo antes de desplegar, los avisos dejan de llegar.

### Paso 12. Probar sin ensuciar la base real
- Interceptar en el navegador todas las llamadas que no sean de lectura, con una sola regla.
- Probar la base en una instancia local con los mismos roles.
- Pruebas mínimas: pedido válido, cada error de validación, límite de envíos, campo trampa, cliente repetido, permisos del público, vencimiento a 48 horas, garantía registrada y resuelta, llamada sin clave responde 401.
- Si se hace un pedido real de prueba, anotar el número y borrar pedido, detalle, cliente, intentos y garantías juntos.

### Paso 13. Entregar y operar
- **Al dueño se le enseña:** dónde ver las tablas, cómo cambiar un precio, cómo confirmar pago y entrega, cómo registrar y cerrar garantías, qué significa cada estado, cómo exportar CSV.
- **Cada semana:** pedidos pendientes, costos sin llenar, garantías abiertas, oportunidades de seguimiento, créditos del hosting.

## 9. Errores que pasaron y la lección
- **Un intercept de pruebas mal ordenado dejó escribir en producción.** Una sola regla para todo el tráfico.
- **El bot de Telegram respondió 403 "bot can't send messages to the bot".** El `chat_id` debe ser el de la persona.
- **Telegram rechazó el webhook con "HTTPS URL must be provided".** La URL pública va fija en el código.
- **Una clave quedó escrita dentro de la función desplegada.** Revisar también el código que está en la nube, y mover toda clave a secretos.
- **Una vista pública fue marcada como error por el asesor de seguridad.** `security_invoker` y permisos por columna.
- **El hosting omitió un despliegue por falta de créditos.** Revisar créditos antes de entregar.
- **Pedidos de prueba quedaron como reales.** Probar contra base aislada, y borrar lo que se crea.
- **El panel de secretos se pausó y no guardó nada.** Se agregan a mano en la sección de secretos de funciones.
- **Un cambio de clave en Shopify dejó pedidos sin entrar** hasta actualizar la URL. Cambiar clave y URL en el mismo momento.

## 10. Preguntas que hay que resolver antes de construir
Estas las decide el dueño del negocio, no la persona que construye:
- Productos, precios y costos. Sin costos, el margen sale mal.
- Zonas de domicilio y montos, y qué pasa con municipios fuera de la lista.
- Formas de pago y datos de cuenta.
- Política de garantía y plazo.
- Qué dirección se publica, y si se usa retiro en tienda.
- Quién tiene acceso a la base, al hosting, al bot de Telegram, a WhatsApp y a la tienda.
- Política de privacidad (revisar con un abogado).
- Si quiere recordatorio de pedidos pendientes y con qué frecuencia.
