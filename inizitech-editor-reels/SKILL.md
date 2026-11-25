---
name: "inizitech-editor-reels"
description: "Edita los clips grabados por Mauxy en reels verticales de Inizitech: subtítulos, stickers, fotos, grabaciones de pantalla, sonidos y cierre de marca."
---

# Editor de reels (Inizitech)

Mauxy graba clips hablando a cámara (.mov de iPhone) y manda grabaciones de pantalla, fotos de producto y adornos. Claude los convierte en reels 1080×1920 listos para Instagram/TikTok. Ella decide; Claude edita, muestra y corrige.

## Reglas que ella ya fijó (no romperlas)
1. **En pantalla solo va lo que ella dice.** Nada de títulos inventados. Un solo estilo de subtítulo en todo el video.
2. **Cero datos personales:** nombre, celular, cédula, correo, dirección, precios de pedidos privados. Taparlos (recuadro blanco) o cortar ese tramo de la grabación. Revisar cuadro por cuadro mientras hace scroll, no solo el cuadro inicial.
3. **Cada ilustración debe corresponder a la frase exacta** (enchufe en "cable", bolso en "bolso", 1 y 2 en "la primera / la segunda"). Revisar que los stickers no hereden contenido de otro video (p. ej. un calendario con "+3").
4. **Stickers y fotos nunca tapan la cara.** Van en la franja superior (y ≈ 40–200) o a los lados, alineados entre sí; nunca sobre el subtítulo.
5. **Sonidos que acompañen lo que dice**, sincronizados con las palabras de ESE video (nunca reusar tiempos de otro).
6. Muletillas, trabadas y palabras mal dichas: se cortan. Si el corte se nota, se tapa con un zoom rápido o una imagen grande que entra y sale (sin tapar su cara más de un instante).
7. Reglas de marca (las mismas de inizitech-copywriter): sin marcas ni "original" en texto (decir "audífonos", no "AirPods"); Sistecrédito siempre con "Sujeto a aprobación y condiciones"; no inventar precios, cuotas ni plazos.
8. Si la transcripción de una frase es dudosa, escribir la mejor lectura y **preguntarle cuál dijo**; no adivinar en silencio.

## Estilo visual
- Paleta: rosa #FF5FAE, amarillo #FFD93D, azul marino #243556 (bordes), blanco. Fuente Poppins 800/900.
- Subtítulos grandes, máx. 3 palabras / ~16 caracteres por bloque, a la altura del pecho (y ≈ 1100–1200 de 1920), blanco con borde marino; palabras clave en rosa; precios como texto gigante ("$109.000").
- Stickers planos tipo dibujo (SVG con borde marino), entran con rebote y salen con escala.
- Fotos de producto recortadas con borde blanco tipo sticker y sombra.
- Grabaciones de pantalla en tarjeta con esquinas redondeadas; si ella pide espacio al lado, tarjeta pequeña a un lado.
- Leve zoom continuo y "golpe" de zoom en cada corte; cambio de clip con transición de zoom/rotación/blur.
- Cierre (~3 s): fondo del collage de Pinterest de Mauxy (megáfono y globo) si lo manda de nuevo, si no fondo #334667; texto "Escríbenos por mensaje directo" + "@inizitech" + logo. Nota "Sujeto a aprobación y condiciones" solo si el video menciona Sistecrédito o cuotas.

## Flujo
1. **Inventario:** ffprobe a cada archivo (duración, resolución, rotación). Si un archivo tiene el mismo nombre que otro ya recibido, comparar con `cmp`.
2. **Transcribir:** Speko `audio_transcribe` si hay URL pública; si no, sherpa-onnx + `sherpa-onnx-whisper-small` (release `asr-models` de GitHub k2-fsa/sherpa-onnx), por tramos de habla (silencedetect -32 dB, d≈0.15). Whisper deforma marcas (Bold, Sistecrédito, Inizitech): corregir a mano. Mostrarle a Mauxy la transcripción de frases dudosas.
3. **Plan de cortes:** lista de (clip, inicio, fin, texto). Quitar muletillas y repeticiones. Para ubicar una palabra exacta, transcribir ventanas cortas (0.4–1 s) y mirar la envolvente de volumen cada 10 ms.
4. **Base de video (ffmpeg):** por tramo `-ss/-t`, encuadrar la cara (OpenCV haar) en el mismo punto en todos los tramos (cara ≈ 430 px de alto, centro en 540,800), escalar a 1080×1920, fundidos de audio de 12 ms, concat, loudnorm -16 LUFS, 30 fps.
5. **Tiempos de palabras:** repartir cada tramo de habla por sílabas (pesos extra a números y precios); agrupar en bloques de subtítulo.
6. **Composición:** HyperFrames (`npx --yes hyperframes@0.9.84`): HTML + GSAP con timeline pausada en `window.__timelines["main"]`, 1080×1920. Videos y audios como elementos estáticos con id. `snapshot --at t1,t2…` para revisar cuadros; **mirar siempre los cuadros más cargados antes de renderizar**.
7. **Render:** uno a la vez (en paralelo se cancelan), `render -o out.mp4 -q standard`; ~10 min por minuto de video.
8. **Sonidos:** mezclar después del render con efectos generados en numpy según lo que se dice (pop al entrar stickers, destello, tic-tac, clic, caja registradora en precios, campanas, notificación en "escríbeme", whoosh en transiciones), volumen bajo, limitador.
9. **Entrega:** `ffmpeg -c:v libx264 -crf 22 -preset veryfast -pix_fmt yuv420p -c:a copy -movflags +faststart`, nombre `tema_vN.mp4`, enviar con SendUserFile.

## Recortar fondos de fotos
- PNG con transparencia: usar tal cual.
- Producto blanco sobre blanco o personas: modelo `u2netp.onnx` (release v0.0.0 de danielgatis/rembg en GitHub) con onnxruntime; quedarse con la región más grande y rellenar huecos.
- Producto oscuro con fondo cuadriculado falso: umbral de brillo.
- Videos de Pinterest: usar solo los cuadros sin la marca de agua.

## Al entregar
Mensaje corto en español casual: qué cambió, en qué frase aparece cada cosa nueva y máximo 2–3 preguntas concretas (frases dudosas, precios que no cuadran, material que falta). Avisar con honestidad si algo tiene riesgo: fotos oficiales de marcas, memes de personas o películas (derechos en Instagram), o si el video no vende el producto.

## Antes de publicar
Ofrecer la descripción con la skill inizitech-copywriter, usando solo los datos que ella dice en el video.