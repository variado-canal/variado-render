# VARIADO — AUDIO-FIRST DIRECTORIAL CONTRACT (30 FPS)

Este flujo NO cambia los workflows de producción existentes.

## Etapas obligatorias
1. **Narración final**: escribir y revisar el guion. Edge TTS `es-MX-JorgeNeural`, velocidad `+14%`, tono `+2Hz`.
2. **Bloquear audio**: ejecutar `python3 playbook30/audio_first.py <job.json>`. Emite `remotion/public/voz.wav`, `palabras.json`, `shot_timeline.json` y `audio.sha256`. Las posiciones de cada palabra proceden de los eventos WordBoundary de la voz realmente generada; no se calculan desde velocidad de lectura aproximada.
3. **Dirigir DESPUÉS del audio**: redactar el TSX de Remotion con escenas en el orden de `shot_timeline.json`. Cada acción debe referirse a la escena por ID y una o varias palabras de esa escena por índice, nunca a la primera ocurrencia global de artículos como «la», «el» o «y».
4. **Plan completo** para cada frase:
   - objeto/órgano/planeta claramente identificable;
   - estado inicial, acción causal y estado final;
   - distancia y trayectoria de cámara (posición, zoom, velocidad);
   - transiciones de entrada y salida ligadas a tiempo de palabra;
   - ubicación, escala, profundidad y capas delante/detrás;
   - SFX causales y subtítulos 2–4 palabras (sin una segunda capa de texto sobre ellos);
   - prohibido fondo con subtítulos como único contenido;
   - último encuadre conecta narrativamente con el primero.
5. **Render sin cambiar audio**: `python3 playbook30/render_locked30.py <job.json> <salida.mp4>`. Verifica SHA-256 antes y después del render; 30 FPS nativos en checkout efímero.
6. **QA, nunca aprobar por GitHub Success**: comprobar cortes contra marcas, extraer fotogramas (inicio/25%/50%/75% de cada escena), descartar escenas sin el objeto principal, comparar audio exportado, y revisar vídeo a 1x y en silencio. Si se ve mal, NO publicar. Antes de aprobar, verificar también la precisión de los hechos.

## Limitación importante
WordBoundary suele ser una buena alineación por palabra, pero no garantiza exactitud fonética de milisegundos; inspección del audio y ajuste puntual siguen siendo necesarios.
