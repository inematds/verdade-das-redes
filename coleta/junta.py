#!/usr/bin/env python3
"""Junta YouTube + Instagram + TikTok pela mesma peça e escreve relatorios/semana-AAAA-MM-DD.md.

A ligação entre redes: o texto dos posts no Instagram/TikTok traz "No YouTube: https://www.youtube.com/shorts/<id>".
Só lê dados/ (coletados por youtube.py e metricool.sh), o histórico do yt-pubx e os inventários
em dados/producao/<canal>.jsonl (ex.: eventosextremospub/auto/inventario.py); não chama nenhuma API.
"""
import glob, json, os, re, statistics as st
from collections import defaultdict
from datetime import date, timedelta

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
    canais, por_canal = {}, defaultdict(list)
    dia = os.path.basename(f)[:-6]
    # a coleta completa e, por cima, as parciais do mesmo dia ou depois (canal recoletado após renovar o token)
    arqs = [f] + [p for p in sorted(glob.glob(os.path.join(D, 'youtube', '????-??-??-*.jsonl')))
                  if os.path.basename(p)[:10] >= dia]
    for a in arqs:
        novos, cs = defaultdict(list), {}
        for l in open(a, encoding='utf-8'):
            x = json.loads(l)
            if '_canal' in x:
                cs[x['_canal']['canal']] = x['_canal']
            else:
                novos[x['canal']].append(x)
        canais.update(cs)
        for c in set(cs) | set(novos):
            por_canal[c] = novos[c]
    videos = [v for vs in por_canal.values() for v in vs]
    return canais, videos, dia


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


def carrega_historico():
    """Uploads feitos pelo yt-pubx (todos os canais), com a data local do envio."""
    f = os.path.expanduser(os.environ.get('VR_HISTORICO', '~/.local/share/yt-pubx/historico.jsonl'))
    out = []
    if os.path.exists(f):
        for l in open(f, encoding='utf-8'):
            try:
                x = json.loads(l)
            except ValueError:
                continue
            if x.get('canal') and x.get('data'):
                out.append(x)
    return out


def carrega_producao():
    """Inventário por edição: {canal: [linhas]} de dados/producao/<canal>.jsonl."""
    out = {}
    for f in sorted(glob.glob(os.path.join(D, 'producao', '*.jsonl'))):
        out[os.path.basename(f)[:-6]] = [json.loads(l) for l in open(f, encoding='utf-8') if l.strip()]
    return out


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

    # 5) quantos vídeos cada canal publicou por dia (yt-pubx, últimos 7 dias)
    dias = [(date.today() - timedelta(days=i)).isoformat() for i in range(7, 0, -1)]
    hist = carrega_historico()
    cont = defaultdict(lambda: defaultdict(int))
    for x in hist:
        if x['data'][:10] in dias:
            cont[x['canal']][x['data'][:10]] += 1
    if cont:
        lin = [[c] + [cont[c].get(d, '') for d in dias] + [sum(cont[c].values())]
               for c in sorted(cont, key=lambda c: -sum(cont[c].values()))]
        partes += ['## Quantos vídeos cada canal publicou por dia (YouTube, via yt-pubx)', '',
                   tabela(['canal'] + [d[8:10] + '/' + d[5:7] for d in dias] + ['total'], lin), '',
                   'Conta envios ao YouTube (16:9 e 9:16 da mesma peça contam 2). Publicação manual fora do yt-pubx não entra.', '']

    # 6) o que cada canal produziu: material disponível × o que foi para a tela, com as views
    def maduro(v):  # vídeo com menos de 2 dias no ar ainda não tem views para comparar
        return v.get('publicado', '9')[:10] <= (date.fromisoformat(dia_yt) - timedelta(days=2)).isoformat() if dia_yt else False

    for canal, regs in carrega_producao().items():
        regs = [r for r in regs if r['data'] in dias]
        if not regs:
            continue
        porDia = defaultdict(list)
        for r in regs:
            porDia[r['data']].append(r)
        lin = []
        for d in sorted(porDia):
            rs = porDia[d]
            lin.append([d[8:10] + '/' + d[5:7], len({r['peca'] for r in rs}), sum(1 for r in rs if r['final']),
                        sum(1 for r in rs if r['youtube_id']), sum(1 for r in rs if r['ig_tiktok']),
                        sum(1 for r in rs if r['final'] and not r['youtube_id'] and not r['ig_tiktok'])])
        partes += [f'## O que o {canal} produziu', '',
                   tabela(['dia', 'peças', 'vídeos prontos', 'no YouTube', 'no IG/TikTok', 'prontos e parados'], lin), '',
                   'Peça = uma ideia; 16:9 + 9:16 ou uma refação (-av1, -v2) são vídeos da mesma peça. Dia = data da edição.', '']
        lin = []
        for r in sorted(regs, key=lambda r: r['edicao']):
            if not r['final']:
                continue
            t, disp = r.get('na_tela'), r['disponivel']
            y = yt.get(r['youtube_id'] or '')
            g = grupo.get(r['youtube_id'] or '', {})
            tela = (f"clipe {t['clipe_real']:.0f} · ilustr. {t['ilustracao']:.0f} · satél. {t['satelite_real']:.0f} · mapa {t['mapa']:.0f}"
                    if t else 'vídeo de câmera / outro motor')
            tem = f"{disp['fotos_reais']} fotos · {disp['clipes_reais']} clipes · {disp['quadros_de_clipe']} quadros"
            lin.append([r['data'][8:10] + '/' + r['data'][5:7], r['serie'], int(r['duracao_s'] or 0), tela, tem,
                        (f"{y['views']}" + (' (recém)' if not maduro(y) else '')) if y else ('—' if not r['youtube_id'] else '?'),
                        int(g['instagram']) if 'instagram' in g else '—', int(g['tiktok']) if 'tiktok' in g else '—'])
        partes += [f'### Cada vídeo do {canal}: o que tinha e o que mostrou', '',
                   tabela(['dia', 'série', 's', 'na tela (segundos)', 'material coletado', 'YouTube', 'Instagram', 'TikTok'], lin), '',
                   '"Na tela": clipe = vídeo real do evento; ilustr. = imagem gerada; satél. = foto de satélite; mapa = mapa animado. '
                   '`—` = não publicado ali; `?` = publicado, sem coleta ainda; (recém) = menos de 2 dias no ar, fora das comparações.', '']
        ok = [r for r in regs if r.get('na_tela') and r['youtube_id'] in yt and maduro(yt[r['youtube_id']])]
        com = [yt[r['youtube_id']]['views'] for r in ok if r['na_tela']['clipe_real'] > 0]
        sem = [yt[r['youtube_id']]['views'] for r in ok if r['na_tela']['clipe_real'] == 0]
        if com and sem:
            partes += [f'- **Com clipe real na tela**: {len(com)} vídeos, mediana {int(st.median(com))} views no YouTube; '
                       f'**só mapa/ilustração**: {len(sem)} vídeos, mediana {int(st.median(sem))}. Poucos dados: é pista, não regra.', '']

    saida = os.path.join(RAIZ, 'relatorios', f'semana-{hoje}.md')
    open(saida, 'w', encoding='utf-8').write('\n'.join(partes))
    print(f'{len(videos)} vídeos YT, {len(pecas)} peças IG/TikTok, {len(grupo)} ligadas -> {saida}')


if __name__ == '__main__':
    main()
