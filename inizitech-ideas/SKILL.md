---
name: inizitech-ideas
description: Generador de ideas de contenido para Inizitech (accesorios tech, Instagram/TikTok). Analiza las cuentas de referencia que elige la dueña (capturas, transcripciones o resúmenes), saca qué formatos y temas repiten, por qué funcionan y las convierte en ideas de video o carrusel para Inizitech, con reglas de marca. Usar cuando pidan ideas de contenido, "qué publico", "analiza estas cuentas/reels", "qué le funciona a otros en mi nicho" o cuando falten ideas para llenar el calendario.
---

# Ideas de contenido (Inizitech)

Convierte lo que ya funciona en cuentas de su nicho en ideas propias, listas para pasar al skill `inizitech-copywriter` (que las vuelve guion) y a `inizitech-content-manager` (que las pone en el calendario). No inventa tendencias: parte siempre de material real que la dueña le pasa.

## Entrada

La dueña elige las cuentas a mirar ("tú eliges a quién mirar"). Pedir lo que falte, sin repetir lo que ya se dio:
1. **3 a 5 cuentas de referencia** (nicho: accesorios tech, relojes inteligentes, audífonos, cargadores, tiendas pequeñas en Colombia/Latam; también cuentas de otro nicho si el formato sirve).
2. **Material de cada una**, por el chat: capturas de sus mejores reels, screen recording del reel, o el pie de foto y lo que se dice. Instagram bloquea que Claude abra enlaces desde aquí, así que un enlace solo no basta.
3. Una nota corta de la dueña: qué le gustó de cada una.

Si llega un screen recording con voz, extraer el audio con ffmpeg y transcribirlo con Speko `audio_transcribe` (con tiempos) para ver cómo está construido el guion.

## Método

1. **Qué suben.** Por cada cuenta: formatos que más repite (hablando a cámara, texto sobre producto, comparación, pantalla grabada, listas de "3 cosas"…) y temas.
2. **Por qué funcionan.** Detectar en cada reel: el gancho (primeros 2 s), el ritmo (cuánto dura cada idea), la promesa, el cierre/CTA y qué lo hace guardable o compartible. Separar lo que se ve de lo que se supone: si solo hay una captura, decir que es una lectura parcial.
3. **Ideas para Inizitech.** Convertir cada patrón en una idea concreta con productos y datos reales de Inizitech. Mínimo 5, máximo 10 por tanda; mejor pocas buenas. Cada idea lleva:
   - nombre corto, pilar (confianza, producto, comunidad, oferta, educativo), formato (con la dueña, animado, carrusel);
   - referencia de donde sale y qué se toma (estructura y ritmo, no contenido);
   - por qué funcionaría para Inizitech;
   - qué hace falta para producirla (fotos, clips, datos en [corchetes]).
4. **Filtro de marca** (obligatorio): sin nombres de marca ni "original" (los productos son réplicas 1:1), sin promesas de calidad o seguridad no demostrables, Sistecrédito solo "sujeto a aprobación y condiciones", sin copiar frases, nombres ni identidad de otra cuenta.
5. **Priorizar.** Marcar las 3 ideas que más conviene grabar o animar primero y por qué (ventas, esfuerzo bajo, encaja con el calendario).
6. **Entregar** como tabla corta en el chat. Solo si la dueña lo pide, guardar en documento. Decirle a la dueña qué cuentas quedaron analizadas, para sumarlas a `referencia/referentes.md` (lista de cuentas ya revisadas: consultarla antes de analizar para no repetir).

## Reglas
- Ser honesto con los límites: Claude no ve métricas privadas de otras cuentas, no puede abrir Instagram desde aquí y un reel viral de otro nicho no garantiza resultado en Inizitech.
- No inflar la lista para parecer productivo. Si el material no da para 5 ideas buenas, entregar menos.
- Variedad: no repetir el mismo formato más de 2 veces seguidas en la tanda (rotar muñequito, texto animado, comparación, grabación de pantalla, la dueña a cámara).
- Lo que ya se descartó (no volver a proponer): Trial Reels como sistema, PDFs gratis o lead magnets (Inizitech vende productos, no guías), carpetas de más.
