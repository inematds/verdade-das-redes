# A verdade das redes

[![A verdade das redes](guia/assets/banner.jpg)](https://inematds.github.io/verdade-das-redes/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

A verdade das redes é um estudo aberto que junta os números reais dos canais da INEMA no YouTube, no Instagram e no TikTok. Serve para quem cria conteúdo e quer saber o que funciona de verdade, com dados, e não com promessa de guru. Um robô coleta os números todo dia e toda semana, junta a mesma peça nas três redes e gera um relatório. Para só aprender, basta ler os achados; para rodar nos seus canais, você precisa de Python e de acesso às suas próprias contas.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/verdade-das-redes/guia/**

---

Dados reais de 17 canais do YouTube e das contas de Instagram e TikTok da INEMA, juntados todo dia e toda semana,
para descobrir **o que funciona de verdade** nas redes sociais. Sem fórmula, sem guru e sem "playbook de celebridade": número com data,
inclusive dos fracassos.

> "Tenho 17 canais no YouTube. Só um cresce. O que ele me ensinou."

## O que já descobrimos (07/11/2026)

- **O mesmo conteúdo dá resultados opostos em cada rede.** O Top 10 do GitHub teve 138.677 views no Instagram, 460 no TikTok e 33 no YouTube.
  O clima do eventosextremos faz o caminho inverso: 7.400 de mediana no YouTube e ~150 no Instagram.
- **YouTube premia o que as pessoas procuram e voltam para ver**; Instagram premia o que se salva e se manda; TikTok, o que prende até o fim.
- **Postar demais derruba**: dias com 3–4 shorts renderam 17–31 mil por vídeo; dias com 8–9, 2–4 mil.
- **9 canais de IA dividem o pouco público**: 1.520 vídeos, só 24 passaram de 500 views. O que funcionou: tutorial que resolve um problema e IA para 40+.

Relatório completo: [relatorios/2026-11-07.md](relatorios/2026-11-07.md). Testes em andamento: [testes.md](testes.md).

## O processo, do início ao fim

| # | Passo | Comando | Quem |
|---|---|---|---|
| 1 | Coleta diária do Instagram e do TikTok (3 marcas do Metricool, janela de 14 dias, uma foto por dia) | `coleta/metricool.sh` | ⚙️ timer `verdade-metricool` 06:30 → 🤖 `claude -p` com o conector `metricool-inematds` |
| 2 | Coleta semanal do YouTube (tudo o que os canais publicaram nos últimos 60 dias, com views, likes e comentários) | `coleta/youtube.py` | ⚙️ timer `verdade-youtube` segunda 07:00 |
| 3 | Inventário do que cada canal produziu: vídeos por dia, material coletado (fotos, clipes, satélite) e o que foi para a tela (segundos de clipe real, ilustração, mapa) | `~/projetos/eventosextremospub/auto/inventario.py > dados/producao/eventosextremos.jsonl` (um arquivo por canal em `dados/producao/`) | ⚙️ roda no fim do passo 2 |
| 4 | Juntar as redes pela mesma peça (o texto do Instagram/TikTok traz o link do YouTube) e montar os números da semana | `coleta/junta.py` | ⚙️ roda no fim do passo 2 |
| 5 | Ler os números, registrar regras confirmadas e hipóteses | `relatorios/AAAA-MM-DD.md` | 🧠 sessão com o Nei |
| 6 | Abrir ou fechar um teste (ex.: ≤ 4 shorts por dia) com data de início e fim | `testes.md` | 🧠 sessão com o Nei |
| 7 | Virar conteúdo: "A verdade das redes" da semana (carrossel, vídeo, tópico INEMA.VIBE) | skills de vídeo/carrossel | 🧠 + 🤖 |

## Fontes e limites

- **YouTube**: YouTube Data API v3, só leitura, com os tokens das lives do `yt-pubx`. Retenção, origem do tráfego e CTR **não** entram
  (exigem a YouTube Analytics API, sem escopo nos tokens).
- **Instagram e TikTok**: Metricool (conector `metricool-inematds`): marcas inema.tds, eventosextremos e FTD (inema.tech).
- **Facebook**: sem fonte ainda.
- Os dados brutos ficam em `dados/` e **não vão para o repositório**; só os relatórios e o código.

## Rodar à mão

```bash
python3 coleta/autorizar.py client_secret.json ~/minhas-credenciais.json  # credencial de leitura do YouTube
python3 coleta/youtube.py            # todos os canais
python3 coleta/youtube.py lives10    # um canal
bash coleta/metricool.sh             # Instagram + TikTok
python3 ~/projetos/eventosextremospub/auto/inventario.py > dados/producao/eventosextremos.jsonl  # o que o canal produziu
python3 coleta/junta.py              # tabela da semana (+ vídeos por dia de cada canal, pelo histórico do yt-pubx)
```
