# La verdad de las redes

[![La verdad de las redes](guia/assets/banner-es.jpg)](https://inematds.github.io/verdade-das-redes/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

La verdad de las redes es un estudio abierto que reúne las cifras reales de los canales de INEMA en YouTube, Instagram y TikTok. Sirve a quienes crean contenido y quieren saber qué funciona de verdad, con datos y no con promesas de gurús. Un robot recopila las cifras todos los días y todas las semanas, reúne la misma pieza en las tres redes y genera un informe. Si solo quieres aprender, basta con leer los hallazgos; para usarlo en tus canales, necesitas Python y acceso a tus propias cuentas.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/verdade-das-redes/guia/es/**

---

Datos reales de 17 canales de YouTube y de las cuentas de Instagram y TikTok de INEMA, reunidos todos los días y todas las semanas,
para descubrir **qué funciona de verdad** en las redes sociales. Sin fórmulas, sin gurús y sin «playbook de celebridades»: cifras con fecha,
incluidos los fracasos.

> «Tengo 17 canales en YouTube. Solo uno crece. Lo que me enseñó.»

## Lo que ya descubrimos (07/11/2026)

- **El mismo contenido da resultados opuestos en cada red.** El Top 10 de GitHub tuvo 138.677 visualizaciones en Instagram, 460 en TikTok y 33 en YouTube.
  El clima de eventosextremos hace el camino inverso: 7.400 de mediana en YouTube y ~150 en Instagram.
- **YouTube premia lo que la gente busca y vuelve a ver**; Instagram premia lo que se guarda y se comparte; TikTok, lo que mantiene la atención hasta el final.
- **Publicar demasiado perjudica**: los días con 3–4 shorts rindieron entre 17 y 31 mil por video; los días con 8–9, entre 2 y 4 mil.
- **9 canales de IA se reparten el escaso público**: 1.520 videos, solo 24 superaron las 500 visualizaciones. Lo que funcionó: tutoriales que resuelven un problema e IA para mayores de 40.

Informe completo: [relatorios/2026-11-07.md](relatorios/2026-11-07.md) (en portugués). Pruebas en curso: [testes.md](testes.md) (en portugués).

## El proceso, de principio a fin

| # | Paso | Comando | Quién |
|---|---|---|---|
| 1 | Recopilación diaria de Instagram y TikTok (3 marcas de Metricool, ventana de 14 días, una captura por día) | `coleta/metricool.sh` | ⚙️ timer `verdade-metricool` 06:30 → 🤖 `claude -p` con el conector `metricool-inematds` |
| 2 | Recopilación semanal de YouTube (todo lo que publicaron los canales en los últimos 60 días, con visualizaciones, likes y comentarios) | `coleta/youtube.py` | ⚙️ timer `verdade-youtube` lunes 07:00 |
| 3 | Inventario de lo que produjo cada canal: videos por día, material recopilado (fotos, clips, imágenes satelitales) y lo que apareció en pantalla (segundos de clips reales, ilustraciones, mapas) | `~/projetos/eventosextremospub/auto/inventario.py > dados/producao/eventosextremos.jsonl` | ⚙️ se ejecuta al final del paso 2 |
| 4 | Reunir las redes a partir de la misma pieza (el texto de Instagram/TikTok incluye el enlace de YouTube) y preparar las cifras de la semana | `coleta/junta.py` | ⚙️ se ejecuta al final del paso 2 |
| 5 | Leer las cifras, registrar reglas confirmadas e hipótesis | `relatorios/AAAA-MM-DD.md` | 🧠 sesión con Nei |
| 6 | Abrir o cerrar una prueba (p. ej., ≤ 4 shorts por día) con fecha de inicio y fin | `testes.md` | 🧠 sesión con Nei |
| 7 | Convertirlo en contenido: «La verdad de las redes» de la semana (carrusel, video, tema INEMA.VIBE) | skills de video/carrusel | 🧠 + 🤖 |

## Fuentes y límites

- **YouTube**: YouTube Data API v3, solo lectura, con los tokens de las transmisiones en vivo de `yt-pubx`. La retención, el origen del tráfico y el CTR **no** se incluyen
  (requieren YouTube Analytics API, sin alcance en los tokens).
- **Instagram y TikTok**: Metricool (conector `metricool-inematds`): marcas inema.tds, eventosextremos y FTD (inema.tech).
- **Facebook**: todavía no hay fuente.
- Los datos sin procesar están en `dados/` y **no se suben al repositorio**; solo los informes y el código.

## Ejecución manual

```bash
python3 coleta/autorizar.py client_secret.json ~/minhas-credenciais.json  # credencial de lectura de YouTube
python3 coleta/youtube.py            # todos los canales
python3 coleta/youtube.py lives10    # un canal
bash coleta/metricool.sh             # Instagram + TikTok
python3 coleta/junta.py              # tabla de la semana
```