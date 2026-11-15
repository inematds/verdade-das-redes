#!/usr/bin/env bash
# Coleta diária do Instagram e do TikTok pelo conector MCP metricool-inematds (só leitura).
# Autorizado pelo Nei em 07/11/2026 ("pode criar e liberar o metricool").
# Uma chamada `claude -p` (assinatura) por marca × conjunto de métricas; janela móvel de 14 dias,
# uma foto por dia em dados/metricool/AAAA-MM-DD/<marca>-<conjunto>.json — assim dá para ver o crescimento de cada peça.
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:/usr/bin:/bin"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
HOJE=$(date +%F)
FUSO=${VR_FUSO:--03:00}   # seu fuso horário
DE=$(date -d '14 days ago' +%F)T00:00:00$FUSO
ATE=${HOJE}T23:59:59$FUSO
OUT="$RAIZ/dados/metricool/$HOJE"
mkdir -p "$OUT"

# marca:nome (IDs do Metricool; descubra os seus pedindo ao Claude Code "chame getBrandSettings do conector Metricool")
MARCAS=${VR_MARCAS:-"7797870:inema-tds 7800440:eventosextremos 7908265:ftd"}
# nome do conector MCP do Metricool no seu Claude Code (claude mcp list)
MCP=${VR_MCP:-metricool-inematds}
# conjunto:métricas (a 1ª é a data, a 2ª o texto — o texto traz "No YouTube: <link>", que liga a peça entre as redes)
CONJ=(
  "tiktok:TKPO02,TKPO05,TKPO06,TKPO07,TKPO08,TKPO09,TKPO10,TKPO11,TKPO15,TKPO16,TKPO21,TKPO03"
  "ig-reels:IGRE02,IGRE03,IGRE23,IGRE11,IGRE24,IGRE10,IGRE07,IGRE21,IGRE12,IGRE06"
  "ig-posts:IGPO02,IGPO03,IGPO07,IGPO28,IGPO14,IGPO13,IGPO08,IGPO27,IGPO15,IGPO29,IGPO06"
)

falhas=0
for m in $MARCAS; do
  id=${m%%:*}; nome=${m#*:}
  for c in "${CONJ[@]}"; do
    conj=${c%%:*}; met=${c#*:}
    arq="$OUT/$nome-$conj.json"
    met_json=$(printf '"%s",' ${met//,/ }); met_json="[${met_json%,}]"
    pedido="Somente leitura. Chame getBrandSettings e confirme a conta, depois UMA vez getAnalyticsDataByMetrics no servidor MCP $MCP, brandId=\"$id\", from=\"$DE\", to=\"$ATE\", metrics=$met_json. Devolva exatamente o resultado JSON da ferramenta, sem resumir ou mudar os valores, dentro de {\"ok\":true,\"dados\":<JSON da ferramenta>,\"linhas\":<quantidade original de rows>}. Erro: ok=false. Não escreva arquivos e não publique."
    if printf '%s' "$pedido" | timeout 900 python3 "$RAIZ/auto/ia_motor.py" executar metricool_analise --agente --pasta "$OUT" \
      --ferramentas "mcp__${MCP}__getBrandSettings mcp__${MCP}__getAnalyticsDataByMetrics" --saida "$arq.resposta.json" >/dev/null 2>&1 \
      && python3 "$RAIZ/auto/salvar_metricas.py" "$arq.resposta.json" "$arq"; then :
    else
      echo "FALHA $nome $conj: executor/contagem não confirmados"; falhas=$((falhas+1)); continue
    fi
    if python3 -I -c "import json,sys; d=json.load(open(sys.argv[1])); assert 'rows' in d; print(len(d['rows']))" "$arq" 2>/dev/null >"$arq.n"; then
      echo "ok $nome $conj: $(cat "$arq.n") linhas"
    else
      echo "FALHA $nome $conj"; falhas=$((falhas+1))
    fi
    rm -f "$arq.n"
  done
done
echo "fim: $falhas falha(s) -> $OUT"
exit $falhas
