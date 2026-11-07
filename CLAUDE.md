# CLAUDE.md — verdade-das-redes

Projeto que junta dados reais das redes da INEMA (YouTube, Instagram, TikTok) para descobrir o que funciona. Ver README ("O processo, do início ao fim").

## Autorizações (Nei, 07/11/2026) — não pedir de novo
- **Metricool (conector MCP `metricool-inematds`)**: leitura diária automática das métricas de Instagram e TikTok, para este projeto. Só leitura; não publica nem apaga.
- **YouTube Data API v3 com os tokens das lives (`~/.config/yt-pubx/lives-cred.py`)**: leitura semanal do que os canais publicaram. Só leitura.
- **NÃO autorizado**: YouTube Analytics API (retenção/tráfego) — os tokens nem têm o escopo.

## Regras
- Conta GitHub: `inematds` (autor `inematds <inematds@gmail.com>`).
- `dados/` fica fora do git (dados das contas). Só código, relatórios e `testes.md` vão ao repo.
- Todo teste nas redes entra em `testes.md` com data de início ANTES de começar, senão os dados se misturam.
- Hipótese só vira "regra confirmada" com número de pelo menos 2 semanas.
- Os tokens do YouTube vencem 7 dias depois de autorizados (app OAuth em modo teste). Canal com `invalid_grant` = reautorizar; ver FALHAS.md do wifi.

## Self-learning
When I correct you, or you catch yourself making a mistake: before continuing, add the lesson as a one-line rule at the TOP of the Lessons section below.

## Lessons
- `youtube.py <canal>` gravava por cima da coleta completa do dia; agora a parcial vai em AAAA-MM-DD-<canal>.jsonl. (07/11/2026)
- Não editar `coleta/metricool.sh` enquanto ele roda (o bash lê o script aos poucos): conferir `pgrep -af metricool.sh` antes. (07/11/2026)
- `claude -p` repassando resultado de ferramenta é mediado pelo modelo: conferir contagem de linhas e um número conhecido depois de mudar a coleta. (07/11/2026)
