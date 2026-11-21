---
name: inizitech-video-studio
description: Produce videos verticales (Reels/TikTok, 1080x1920, 25-35 s) para Inizitech y marcas parecidas de accesorios tech. Dos rutas - (A) videos animados con el muñequito enchufe rosado, voz en español y subtítulos, sin que la dueña se grabe; (B) edición de clips que ella graba o recursos que manda (cortes, zoom, subtítulos palabra por palabra, música baja). Incluye motor de animación, pipeline de render, voz, reglas de marca y control de calidad. Usar cuando pidan crear, replicar o editar un video corto para redes, un guion animado, o "monta estos clips".
---

# Inizitech Video Studio

Fábrica de videos cortos para @inizitech (accesorios tech: audífonos, cargadores, cables, relojes, Sistecrédito). Todo sale vertical 1080x1920 a 30 fps, de 25 a 35 segundos, con voz y subtítulos o texto animado, y CTA final "Escríbenos por mensaje directo".

## Reglas de marca (no negociables)

Estas reglas salen de lo que ya se aprobó y de lo que se rechazó. Léelas antes de cada video.

- **Estilo por defecto: muñequito enchufe rosado.** Fondo rosa claro con puntos, títulos en pastilla rosa, contorno oscuro, textos grandes y centrados. Gustó. No gustaron el estilo neón ni el de fotos de banco tipo CapCut. No volver a ofrecerlos salvo que lo pida.
- **Letras estéticas, parejas y medidas.** Mismos tamaños en escenas equivalentes (título 76-110, subtítulo 46-60), todo centrado sobre la misma rejilla. **Nada de texto chiquito en gris** tipo "*ilustrativo".
- **Cero afirmaciones de calidad o seguridad que no se puedan probar.** No decir que un cable o cargador "se recalienta" ni que otro no. Los productos son réplicas 1:1; lo que se dice de uno se le puede aplicar a todos.
- **Sin nombres de marca ni logos** (Apple, AirPods, etc.) en pantalla ni en voz, y sin decir "original". Usar "audífonos", "cargador de 20W", "cable compatible".
- **Sistecrédito** solo como "sujeto a aprobación y condiciones". No inventar tasas, cuotas ni plazos.
- **Prueba social permitida:** "más de 150 clientes".
- **Zona segura de Instagram:** nada importante en los últimos ~250 px de abajo ni en los ~150 px de la derecha.
- **Respuestas al usuario: cortas, directas, en español casual.** Si hay dos caminos, ofrecer dos opciones (una corregida y otra más innovadora que conecte con la gente).

## Ruta A: video animado con el muñequito

Se usa cuando la dueña no puede grabar o el tema se explica mejor dibujado (educativos: cómo elegir audífonos, vatios de cargadores, cómo funciona Sistecrédito).

1. **Guion (25-30 s, 6-8 escenas, una idea por escena).** Gancho en pregunta, 3 ideas cortas, CTA. Frases de máximo ~12 palabras. Escribir para el oído: puntuación clara, sin siglas raras, números en palabras cuando se lean mejor ("tres cosas"). Ver `referencia/guiones_aprobados.md` como modelo de ritmo.
2. **Voz.** Sintetizar **una frase por escena** con Speko (herramienta `audio_synthesize`):
   `{"text": "<frase>", "intent": {"language": "es", "optimizeFor": "accuracy"}, "voice": "es-MX-Valeria:MAI-Voice-2", "constraints": {"allowedProviders": {"tts": ["azure"]}}}`.
   Es la voz aprobada (acento mexicano, buena dicción). Una voz colombiana requiere saldo en ElevenLabs. Guardar cada audio como `.wav`.
3. **Carpeta de trabajo.** Elegir `INIZI_OUT` (por ejemplo `/home/claude/work`). Crear `$INIZI_OUT/<nombre>/raw.json` con una clave por escena: `{"<nombre>_1": "/ruta/l1.wav", "<nombre>_2": "/ruta/l2.wav"}`.
4. **Definir el video.** Escribir `$INIZI_OUT/videos_extra.py` (se ejecuta dentro del motor, ya tiene `L`, `build`, `cta_scene`, `V`, `auto_pops`, `T` y los props `p_v2_*`, `p_v4_*`, `pc_*`). Modelo mínimo:
   ```python
   A1 = [L([("¿Vas a comprar", 'n')], 330, 70, 0.0), L([("audífonos?", 'h')], 480, 110, 0.12, 0.03)]
   A2 = [L([("Escríbenos", 'n')], 320, 80, 0.0), L([("directo", 'h')], 600, 120, 0.35, 0.03)]
   v['mivideo'] = [
       V(build(A1, p_v2_three, dict(mood='wink', arm='point'), first=True), auto_pops(A1, True), 'mivideo_1'),
       V(cta_scene(A2), auto_pops(A2, False), 'mivideo_2', [1.15]),
   ]
   ```
   `L(partes, y, tamaño, retraso, pulso)`: estilo `'n'` normal, `'h'` pastilla rosa, `'y'` pastilla amarilla. `build(líneas, prop, mascota, first=...)` arma la escena; `prop` es la función que dibuja el objeto (orejita, batería, balanza, documento…). Para un objeto nuevo, escribir una función `p_xxx(c, u, t)` con skia en el mismo archivo. Los retrasos de las líneas deben caer cuando la voz dice esa parte (la voz arranca 0.3 s dentro de cada escena).
   Ejemplos completos de 3 videos reales en `scripts/motor_muneco.py` (claves `c1`, `a2`, `s2`).
5. **Ver antes de renderizar.** `INIZI_OUT=... scripts/pipeline.sh <nombre> solo_stills` deja un PNG por escena. Revisar: textos dentro del cuadro, nada encimado, tamaños parejos, mascota con la expresión correcta, sin texto gris chiquito. Si el motor imprime `AVISO desborde`, acortar la línea o bajar el tamaño.
6. **Render completo.** `INIZI_OUT=... scripts/pipeline.sh <nombre>` hace voz alineada, escenas con transiciones, efectos de sonido (pop, ding, whoosh), mezcla y `final.mp4`. Un video de 30 s renderiza en pocos minutos.
7. **Control de calidad** (ver abajo) y entrega.

Requisitos: `python3`, `skia-python`, `numpy`, `ffmpeg`. La fuente Poppins Bold viene incluida (licencia OFL). Ejecutar con `python3 -I`.

## Ruta B: clips de la dueña o recursos que ella manda

Se usa cuando ella se graba (hablando a cámara, mostrando producto) o pasa clips y capturas.

1. **Recibir material.** Pedir clips en vertical si puede (si no, el script recorta al centro). Si hay recursos de Pinterest/otras fuentes, usarlos solo si ella los trae o tiene derecho de uso; los bancos gratis (Pexels, Unsplash) sirven como complemento, nunca como protagonista de un producto que no es el suyo.
2. **Guion corto de edición.** Qué se queda, orden, gancho de los primeros 2 s, CTA al final.
3. **Cortar y transcribir.** Unir el audio ya cortado y transcribirlo con Speko `audio_transcribe` (con tiempos por palabra). Pasar los tiempos al video final (si se corta un clip, los tiempos se corren).
4. **Escribir `edicion.json`** y correr `python3 -I scripts/editar_clips.py edicion.json` (formato en la cabecera del script). Hace recorte vertical, zoom opcional por clip, gancho grande, subtítulos palabra por palabra con la palabra activa en pastilla rosa, y música baja opcional.
5. **Revisar 3 fotogramas** (gancho, mitad, final) y entregar.

Ideas de edición que suben retención: corte cada 2-3 s, zoom de 1.1 en la frase clave, gancho en texto en el segundo 0, subtítulos siempre, CTA hablado y escrito.

## Control de calidad antes de entregar

- Duración 25-35 s; resolución 1080x1920; audio pico cerca de -1 dB (`ffmpeg -i f.mp4 -af volumedetect -f null -`).
- Voz clara y sin cortes; efectos de sonido no tapan la voz.
- Cada escena: texto completo visible, sin desbordes, sin letras chiquitas, tamaños consistentes.
- Sin marcas, sin "original", sin promesas de calidad o seguridad, Sistecrédito con su condición.
- Último cuadro con CTA y @inizitech.
- Revisar en el celular antes de publicar (la zona inferior la tapa la interfaz).

## Entrega

Enviar el `.mp4` con una línea de contexto. Decir qué se puede cambiar fácil (textos, colores, tiempos) y qué requiere material nuevo (fotos o clips reales del producto). Guardar guion, `raw.json` y `videos_extra.py` del video para poder replicarlo o ajustarlo.

## Archivos

- `scripts/motor_base.py`, `motor_estilo.py`, `motor_muneco.py`: motor de dibujo y escenas.
- `scripts/pipeline.sh`: voz, escenas, sonidos, mezcla y mux.
- `scripts/editar_clips.py`: edición de clips con subtítulos.
- `scripts/Poppins-Bold.ttf`: fuente (SIL Open Font License).
- `referencia/guiones_aprobados.md`: tres guiones aprobados y sus tiempos.
- `referencia/lecciones.md`: qué se probó, qué gustó y qué no.
