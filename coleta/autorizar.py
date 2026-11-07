#!/usr/bin/env python3
"""Gera o arquivo de credenciais de leitura do YouTube (escopo youtube.readonly).

Uso:  python3 coleta/autorizar.py client_secret.json ~/minhas-credenciais.json

client_secret.json = o arquivo que o Google Cloud deixa baixar ao criar o "ID do cliente OAuth" (tipo app para computador).
O script abre um link; você entra com a conta do canal e autoriza; ele grava client_id, client_secret e refresh_token.
"""
import http.server, json, os, sys, threading, urllib.parse, urllib.request, webbrowser

ESCOPO = 'https://www.googleapis.com/auth/youtube.readonly'
PORTA = 8765


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    c = json.load(open(sys.argv[1]))
    c = c.get('installed') or c.get('web') or c
    cid, csec = c['client_id'], c['client_secret']
    redir = f'http://127.0.0.1:{PORTA}/'
    url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode({
        'client_id': cid, 'redirect_uri': redir, 'response_type': 'code', 'scope': ESCOPO,
        'access_type': 'offline', 'prompt': 'consent'})
    codigo = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            codigo['v'] = (q.get('code') or [None])[0]
            self.send_response(200); self.end_headers()
            self.wfile.write('Pronto. Pode fechar esta aba e voltar ao terminal.'.encode())

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(('127.0.0.1', PORTA), H)
    print('Abra este link, entre com a conta do canal e autorize:\n\n' + url + '\n')
    threading.Thread(target=lambda: webbrowser.open(url), daemon=True).start()
    while 'v' not in codigo:
        srv.handle_request()
    if not codigo['v']:
        sys.exit('O Google não devolveu o código (autorização recusada?).')
    corpo = urllib.parse.urlencode({'code': codigo['v'], 'client_id': cid, 'client_secret': csec,
                                    'redirect_uri': redir, 'grant_type': 'authorization_code'}).encode()
    tok = json.loads(urllib.request.urlopen('https://oauth2.googleapis.com/token', data=corpo, timeout=60).read())
    if 'refresh_token' not in tok:
        sys.exit('O Google não devolveu refresh_token. Rode de novo.')
    saida = os.path.expanduser(sys.argv[2])
    with open(saida, 'w') as f:
        json.dump({'client_id': cid, 'client_secret': csec, 'refresh_token': tok['refresh_token']}, f)
    os.chmod(saida, 0o600)
    print('Credenciais gravadas em', saida)


if __name__ == '__main__':
    main()
