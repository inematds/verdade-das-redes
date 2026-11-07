#!/usr/bin/env python3
"""Junta YouTube + Instagram + TikTok pela mesma peça e escreve relatorios/semana-AAAA-MM-DD.md.

A ligação entre redes: o texto dos posts no Instagram/TikTok traz "No YouTube: https://www.youtube.com/shorts/<id>".
Só lê dados/ (coletados por youtube.py e metricool.sh); não chama nenhuma API.
"""
import glob, json, os, re, statistics as st
from collections import defaultdict
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(RAIZ, 'dados')
YT_ID = re.compile(r'youtube\.com/(?:shorts/|watch\?v=)([\w-]{11})')

# ordem das colunas pedidas em metricool.sh
COLS = {
    'tiktok': ['data', 'texto', 'duracao', 'views', 'likes', 'comentarios', 'compart', 'alcance', 'tempo_medio', 'pct_parau', 'pct_busca', 'url'],
    'ig-reels': ['data', 'texto', 'views', 'alcance', 'tempo_medio', 'likes', 'comentarios', 'compart', 'salvos', 'url'],
    'ig-posts': ['data', 'texto', 'tipo', 'views', 'alcance', 'likes', 'comentarios', 'compart', 'salvos', 'seguidores', 'url'],
}


def num(x):
    try:
        return float(str(x).replace(',', '.'))
    except (TypeError, ValueError):
        return 0.0


def ultimo(padrao):
    fs = sorted(glob.glob(padrao))
    return fs[-1] if fs else None


def carrega_youtube():
    f = ultimo(os.path.join(D, 'youtube', '????-??-??.jsonl'))  # só coletas completas
    if not f:
        return {}, [], None
    canais, videos = {}, []
    for l in open(f, encoding='utf-8'):
        x = json.loads(l)
        if '_canal' in x:
            canais[x['_canal']['canal']] = x['_canal']
        else:
            videos.append(x)
    return canais, videos, os.path.basename(f)[:-6]


def carrega_metricool():
    pasta = ultimo(os.path.join(D, 'metricool', '*'))
    pecas = []
    if not pasta:
        return pecas, None
    for f in glob.glob(os.path.join(pasta, '*.json')):
        base = os.path.basename(f)[:-5]
        conj = next((c for c in COLS if base.endswith('-' + c)), None)
        if not conj:
            continue
        marca = base[:-len(conj) - 1]
        try:
            rows = json.load(open(f)).get('rows') or []
        except Exception:
            continue
        for r in rows:
            p = dict(zip(COLS[conj], r))
            m = YT_ID.search(p.get('texto') or '')
            pecas.append({'marca': marca, 'rede': 'tiktok' if conj == 'tiktok' else 'instagram', 'formato': conj,
                          'data': str(p.get('data'))[:10], 'titulo': (p.get('texto') or '').split('\n')[0][:80],
                          'views': num(p.get('views')), 'salvos': num(p.get('salvos')), 'compart': num(p.get('compart')),
                          'yt': m.group(1) if m else None})
    return pecas, os.path.basename(pasta)


def tabela(cab, linhas):
    out = ['| ' + ' | '.join(cab) + ' |', '|' + '---|' * len(cab)]
    out += ['| ' + ' | '.join(str(c) for c in l) + ' |' for l in linhas]
    return '\n'.join(out)


def main():
    canais, videos, dia_yt = carrega_youtube()
    pecas, dia_mc = carrega_metricool()
    hoje = date.today().isoformat()
    partes = [f'# A verdade das redes — semana até {hoje}', '',
              f'Fontes: YouTube {dia_yt or "—"} (últimos {next(iter(canais.values()), {}).get("janela_dias", 60)} dias) · Metricool {dia_mc or "—"} (últimos 14 dias).', '']

    # 1) YouTube por canal e formato
    por = defaultdict(list)
    for v in videos:
        por[(v['canal'], v['tipo'])].append(v['views'])
    lin = []
    for (c, t), vs in sorted(por.items(), key=lambda x: -st.median(x[1])):
        lin.append([c, canais.get(c, {}).get('inscritos', '?'), t, len(vs), int(st.median(vs)), max(vs)])
    partes += ['## YouTube — mediana de views por canal e formato', '',
               tabela(['canal', 'inscritos', 'formato', 'vídeos', 'mediana', 'máximo'], lin), '']

    # 2) posts por dia × mediana (o teste dos 4 por dia)
    for c in sorted({v['canal'] for v in videos}):
        dia = defaultdict(list)
        for v in videos:
            if v['canal'] == c and v['tipo'] == 'short':
                dia[v['publicado'][:10]].append(v['views'])
        if len(dia) >= 5:
            faixa = defaultdict(list)
            for vs in dia.values():
                faixa['1–4 por dia' if len(vs) <= 4 else '5+ por dia'].append(st.median(vs))
            if len(faixa) == 2:
                partes.append(f'- **{c}**: dias com 1–4 shorts → mediana {int(st.median(faixa["1–4 por dia"]))}; '
                              f'dias com 5+ → {int(st.median(faixa["5+ por dia"]))}')
    partes.append('')

    # 3) a mesma peça nas três redes
    yt = {v['video_id']: v for v in videos}
    grupo = defaultdict(dict)
    for p in pecas:
        if p['yt']:
            g = grupo[p['yt']]
            g[p['rede']] = max(g.get(p['rede'], 0), p['views'])
            g.setdefault('titulo', p['titulo']); g.setdefault('marca', p['marca'])
    lin = []
    for vid, g in grupo.items():
        y = yt.get(vid)
        lin.append([g['titulo'][:60], g['marca'], int(g.get('instagram', 0)), int(g.get('tiktok', 0)),
                    y['views'] if y else '?', y['canal'] if y else '?'])
    lin.sort(key=lambda l: -max(l[2], l[3], l[4] if isinstance(l[4], int) else 0))
    partes += ['## A mesma peça em cada rede', '',
               tabela(['peça', 'marca', 'Instagram', 'TikTok', 'YouTube', 'canal YT'], lin[:25]), '',
               '`?` no YouTube = canal sem coleta nesta semana (token vencido) ou peça fora da janela.', '']

    # 4) campeões do Instagram/TikTok
    top = sorted(pecas, key=lambda p: -p['views'])[:10]
    partes += ['## Top 10 do Instagram e TikTok', '',
               tabela(['peça', 'marca', 'rede', 'views', 'salvos', 'compart.'],
                      [[p['titulo'][:60], p['marca'], p['rede'], int(p['views']), int(p['salvos']), int(p['compart'])] for p in top]), '']

    saida = os.path.join(RAIZ, 'relatorios', f'semana-{hoje}.md')
    open(saida, 'w', encoding='utf-8').write('\n'.join(partes))
    print(f'{len(videos)} vídeos YT, {len(pecas)} peças IG/TikTok, {len(grupo)} ligadas -> {saida}')


if __name__ == '__main__':
    main()
