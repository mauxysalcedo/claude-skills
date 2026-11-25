---
name: "agente-ventas-inizitech"
description: "Úsala cuando Mauxy quiera diseñar, construir o mejorar el agente de IA de ventas de Inizitech (WhatsApp e Instagram con Supabase y n8n)."
---

# Agente de IA de ventas de Inizitech

Guía para construir con Mauxy un agente de IA que atiende clientes de Inizitech por WhatsApp e Instagram, registra pedidos en una base de datos y le avisa a ella para confirmar el pago.

## Por qué existe este proyecto

- En dos semanas de noviembre de 2026, Mauxy perdió unos 7 clientes solo por tardar en responder mensajes. El cuello de botella del negocio es el tiempo de respuesta, no conseguir clientes.
- La propuesta de valor de Inizitech es "te atiende una persona, no un bot". El agente no reemplaza eso: atiende lo repetitivo al instante y le pasa a Mauxy lo que necesita criterio humano.
- Forma parte del plan de estructuración de Inizitech (documento "Inizitech — Reestructuración y manual de operación": https://claude.ai/artifact/MAzYyYKNnsDHZSANfqpJMY) y de su sistema de gestión (hoja central: https://claude.ai/artifact/9og1dgG1nJsRtqRLzkQDxJ). Lee ambos antes de diseñar: ahí están productos, precios, políticas y decisiones pendientes.

## Cómo trabajar con Mauxy

- Español casual, directo y conciso. Ella prefiere honestidad radical, con reconocimiento concreto de lo que hace bien.
- **Por partes.** Una cosa a la vez y una decisión por mensaje. Si la saturas, se pierde; cuando dice "calma" o "no entiendo", baja el ritmo y explica más simple.
- **Nombra y explica cada concepto** la primera vez que aparezca (webhook, API, RLS, nodo, etc.). Ella quiere aprender, no solo recibir el resultado.
- **Ella decide.** Propón con tu recomendación, pero las decisiones de negocio (precios, políticas, tono) son suyas.
- Contexto de tiempo: tiene Claude Code por **un solo mes**. Diciembre es su mes más fuerte de ventas y en enero entra a prácticas.

## Términos (para explicárselos)

- **Automatización:** algo que pasa solo cuando ocurre algo (si pasa X, haz Y).
- **Bot o chatbot:** una automatización que conversa. Puede ser de reglas (menús, palabras clave) o con IA (entiende lenguaje natural).
- **Agente de IA:** un bot con IA que además hace acciones: consulta la base de datos, registra pedidos, avisa. Lo que se construye aquí es un agente que vive dentro de una automatización.

## Arquitectura decidida

**Claude Code construye; n8n queda.** Como Claude Code solo dura un mes, el agente vive en n8n, que Mauxy puede mantener visualmente sin programar. Claude Code se usa para lo difícil:

- Crear la base de datos en Supabase, con seguridad por filas (RLS) activada.
- Cargar el catálogo y los clientes desde la hoja central.
- Instalar n8n en un servidor gratis de la nube (n8n es gratis si se instala uno mismo; en el computador de ella no sirve, porque se apaga).
- Escribir los flujos de n8n en JSON para que ella solo los importe.
- Dejar un manual de cómo funciona y cómo modificar cada pieza.

Alternativa si n8n se complica: Edge Functions de Supabase escritas con Claude Code. Su costo fijo es cero, pero después cuesta más modificarlas sin Claude Code.

## Base de datos (Supabase), borrador

- **clientes:** id, nombre, telefono, usuario_instagram, ciudad, canal_origen, autorizo_datos (bool), fecha_autorizacion, bot_activo (bool, para pausar el bot cuando Mauxy toma la conversación), creado_en.
- **productos:** id, nombre, linea, costo, precio_lista, precio_minimo, descuento_max, garantia, descripcion, activo.
- **pedidos:** id, numero (INZ-0001…), cliente_id, producto_id, precio, costo_real, medio_pago, estado, fecha_prometida, fecha_entrega, revisado (bool), guia, notas, creado_en.
  - Estados: pendiente_pago, pagado, comprado, revisado, enviado, entregado, cerrado, cancelado.
- **conversaciones:** id, cliente_id, canal (whatsapp/instagram), rol (cliente/agente/mauxy), mensaje, creado_en.

Ajusta los nombres con ella antes de crear nada. Son datos personales: RLS activada y solo el backend (n8n con la clave de servicio) escribe.

## Flujo del agente

1. Llega un mensaje y Meta lo envía al webhook de n8n.
2. n8n busca o crea al cliente y carga el historial de la conversación. Si `bot_activo` es falso, no responde (Mauxy está atendiendo).
3. Primera vez: saludo, se presenta como "el asistente de Inizitech" y pide la autorización de datos personales (Ley 1581 de 2012).
4. Entiende qué necesita el cliente y recomienda, consultando la tabla productos.
5. Cotiza con el precio de lista. Si el cliente pide descuento, solo aplica hasta `descuento_max`, y nunca en combos.
6. Explica las cuotas con Sistecrédito cuando aplique.
7. Si quiere comprar: pide nombre, producto, ciudad, dirección y medio de pago, y crea el pedido en estado pendiente_pago.
8. Envía los datos de pago. Cuando el cliente manda el comprobante, alerta a Mauxy con el número de pedido.
9. **Mauxy confirma el pago** con un toque; el estado pasa a pagado y el agente le confirma al cliente con la fecha prometida.

## Reglas del agente (no negociables)

- Nunca confirma un pago por su cuenta: los comprobantes falsos son comunes.
- Los precios salen siempre de la base de datos; nunca los inventa.
- No promete fechas ni garantías fuera de las políticas escritas.
- Siempre se identifica como asistente; no se hace pasar por Mauxy.
- No usa marcas ajenas para productos que no son de esa marca.
- **Pasa la conversación a Mauxy** (pone `bot_activo` en falso y le avisa) cuando: el cliente se molesta, pide garantía o devolución, quiere negociar fuera de las reglas, pregunta algo que el agente no sabe, o pide hablar con una persona.

## Requisitos externos

- **WhatsApp:** API oficial de Meta (WhatsApp Cloud API) con el negocio verificado. **La verificación se inicia el día 1**, porque es lo más lento y no depende de ella. Revisa con ella qué número usar: puede que el número conectado a la API no se pueda seguir usando igual en la app normal.
- **Instagram:** cuenta profesional vinculada a una página de Facebook, y los permisos de mensajería de Meta.
- **IA:** API de un modelo; para un bot de ventas basta un modelo económico.

## Costos de operación (verifica antes de lanzar)

- Supabase: plan gratis.
- n8n: gratis si se instala en un servidor propio (servidor gratis de la nube o unos 5 dólares al mes).
- IA: del orden de 1 a 5 centavos de dólar por conversación; unos 3 a 15 dólares al mes con su volumen (estimado).
- WhatsApp: desde el 1 de octubre de 2026, Meta cobra por mensaje las respuestas dentro de la ventana de 24 horas, con unos 1.000 mensajes de servicio gratis al mes por número. Revisa la tarifa de Colombia en la tabla de precios de Meta.
- Instagram: por lo que se sabe, no cobra por mensaje; confírmalo al montarlo.
- Total estimado: entre 5 y 25 dólares al mes.

## Plan del mes

| Semana | Qué se hace |
| --- | --- |
| 1 | Diseñar el flujo y los textos del agente con ella. Crear la base de datos y cargar el catálogo. Iniciar la verificación con Meta |
| 2 | Instalar n8n. Agente de WhatsApp que responde, pasa casos difíciles y avisa. Pruebas con amigos que se hacen pasar por clientes |
| 3 | Registro de pedidos y confirmación de pago. Lanzamiento suave en WhatsApp con respaldo humano |
| 4 | Instagram, ajustes con conversaciones reales y manual final |

Si el tiempo no alcanza, recorta Instagram y los seguimientos automáticos; lo esencial es WhatsApp respondiendo y avisándole.

No lances algo sin probar en plena temporada de diciembre. Mientras el agente no esté probado, ella atiende con la capa gratis: mensaje de bienvenida, mensaje de ausencia, respuestas rápidas y catálogo en WhatsApp Business, más respuestas guardadas y preguntas frecuentes en Instagram.

## Antes de que se acabe Claude Code

El último día del mes:
- Pide a Claude Code un manual en lenguaje simple: qué hace cada flujo de n8n, cómo cambiar precios y textos, cómo pausar el bot, y qué hacer si falla.
- Exporta todos los flujos de n8n y el esquema de la base de datos.
- Repasa cada pieza con Mauxy hasta que la entienda.

## Primer paso en un chat nuevo

Empieza por el **diseño del flujo**, sin abrir Claude Code: qué hace el agente paso a paso, qué textos usa, qué datos pide y cuándo pasa la conversación. Revisa primero las decisiones pendientes del documento de reestructuración (garantía, tiempos de entrega, horario, descuentos), porque el agente las necesita para responder.