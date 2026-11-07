#!/usr/bin/env python3
"""Coleta semanal do YouTube: o que cada canal publicou e quanto rendeu.

Só leitura, pela YouTube Data API v3 com os tokens das lives (yt-pubx).
Autorizado pelo Nei em 07/11/2026 ("olhar semanalmente o que publicamos nos canais do YouTube pelo lives").
Não usa a YouTube Analytics API (sem escopo, não autorizada). Nunca imprime credenciais.

Saída: dados/youtube/AAAA-MM-DD.jsonl — uma linha por vídeo (canal, id, data, título, duração, tipo, views, likes, comentários).
"""
import json, os, re, subprocess, sys, urllib.parse, urllib.request
from datetime import date, datetime, timedelta, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.expanduser(os.environ.get('VR_CONFIG', '~/.config/yt-pubx/config.json'))
API = 'https://www.googleapis.com/youtube/v3/'
DIAS = int(os.environ.get('VR_DIAS', '60'))  # janela: vídeos publicados nos últimos N dias


def http(url, data=None, token=None):
    req = urllib.request.Request(url, data=data)
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def token_de(cmd):
    cred = json.loads(subprocess.run(os.path.expanduser(cmd), shell=True, capture_output=True, text=True, timeout=60).stdout)
    corpo = urllib.parse.urlencode({'client_id': cred['client_id'], 'client_secret': cred['client_secret'],
                                    'refresh_token': cred['refresh_token'], 'grant_type': 'refresh_token'}).encode()
    return http('https://oauth2.googleapis.com/token', data=corpo)['access_token']


def segundos(iso):
    m = re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso or '')
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def coleta_canal(nome, cmd, desde):
    tok = token_de(cmd)
    ch = http(API + 'channels?part=contentDetails,statistics,snippet&mine=true', token=tok)['items'][0]
    uploads = ch['contentDetails']['relatedPlaylists']['uploads']
    canal = {'janela_dias': DIAS, 'canal': nome, 'channel_id': ch['id'], 'titulo_canal': ch['snippet']['title'],
             'inscritos': int(ch['statistics'].get('subscriberCount', 0)),
             'videos_total': int(ch['statistics'].get('videoCount', 0))}
    ids, page = [], ''
    while True:
        r = http(API + f'playlistItems?part=contentDetails&maxResults=50&playlistId={uploads}{page}', token=tok)
        parar = False
        for it in r.get('items', []):
            pub = it['contentDetails'].get('videoPublishedAt')
            if pub and pub < desde:
                parar = True
                break
            ids.append(it['contentDetails']['videoId'])
        if parar or 'nextPageToken' not in r:
            break
        page = '&pageToken=' + r['nextPageToken']
    linhas = []
    for i in range(0, len(ids), 50):
        r = http(API + 'videos?part=snippet,statistics,contentDetails,status,liveStreamingDetails&id=' + ','.join(ids[i:i + 50]), token=tok)
        for v in r.get('items', []):
            dur = segundos(v['contentDetails'].get('duration'))
            st = v.get('statistics', {})
            linhas.append({**canal, 'video_id': v['id'], 'publicado': v['snippet']['publishedAt'],
                           'titulo': v['snippet']['title'], 'duracao_s': dur,
                           'tipo': 'live' if v['snippet'].get('liveBroadcastContent') != 'none' or 'liveStreamingDetails' in v
                           else ('short' if dur <= 180 else 'longo'),
                           'privacidade': v.get('status', {}).get('privacyStatus'),
                           'views': int(st.get('viewCount', 0)), 'likes': int(st.get('likeCount', 0)),
                           'comentarios': int(st.get('commentCount', 0))})
    return canal, linhas


def main():
    so = sys.argv[1:]  # opcional: só alguns canais
    cfg = json.load(open(CONFIG))['canais']
    desde = (datetime.now(timezone.utc) - timedelta(days=DIAS)).strftime('%Y-%m-%dT%H:%M:%SZ')
    sufixo = ('-' + '-'.join(so)) if so else ''  # coleta parcial não sobrescreve a completa do dia
    saida = os.path.join(RAIZ, 'dados', 'youtube', f'{date.today().isoformat()}{sufixo}.jsonl')
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    total, erros = 0, []
    with open(saida, 'w', encoding='utf-8') as f:
        for nome, c in cfg.items():
            if so and nome not in so:
                continue
            cmd = c.get('credenciais_cmd') if isinstance(c, dict) else None
            if not cmd:
                erros.append(f'{nome}: sem credenciais_cmd')
                continue
            try:
                canal, linhas = coleta_canal(nome, cmd, desde)
                f.write(json.dumps({'_canal': canal}, ensure_ascii=False) + '\n')
                for l in linhas:
                    f.write(json.dumps(l, ensure_ascii=False) + '\n')
                total += len(linhas)
                print(f'ok {nome}: {canal["inscritos"]} inscritos, {len(linhas)} vídeos em {DIAS} dias')
            except Exception as e:  # um canal com problema não derruba a coleta
                erros.append(f'{nome}: {type(e).__name__}: {str(e)[:120]}')
    for e in erros:
        print('ERRO', e)
    print(f'{total} vídeos -> {saida}')


if __name__ == '__main__':
    main()
