#!/usr/bin/env python3
"""Proxy de compatibilidade: converte respostas v1.x para formato v2.x que o DataCrazy espera."""
import json, urllib.request, urllib.error, sys
from http.server import HTTPServer, BaseHTTPRequestHandler

EVOLUTION = "http://localhost:8080"

def transform(data, path):
    try:
        parsed = json.loads(data)
    except Exception:
        return data

    # GET /instance/fetchInstances
    if '/instance/fetchInstances' in path:
        if not isinstance(parsed, list):
            return data
        out = []
        for item in parsed:
            inst = item.get('instance', item)
            owner = inst.get('owner', '') or ''
            out.append({
                "id": inst.get('instanceId', ''),
                "name": inst.get('instanceName', ''),
                "connectionStatus": inst.get('status', inst.get('connectionStatus', 'close')),
                "ownerJid": owner or None,
                "profileName": inst.get('profileName', None),
                "profilePicUrl": inst.get('profilePictureUrl', None),
                "number": owner.split('@')[0] if owner else None,
                "token": inst.get('apikey', ''),
                "clientName": "evolution_api",
                "integration": "WHATSAPP-BAILEYS",
                "disconnectionReasonCode": None,
                "disconnectionObject": None,
            })
        return json.dumps(out).encode()

    # GET /instance/connectionState/{name}
    if '/instance/connectionState' in path:
        inst = parsed.get('instance', parsed)
        state = inst.get('state', inst.get('connectionStatus', 'close'))
        result = {
            "instance": {
                "instanceName": inst.get('instanceName', ''),
                "state": state,
                "connectionStatus": state,
            }
        }
        return json.dumps(result).encode()

    return data

class Handler(BaseHTTPRequestHandler):
    def relay(self, body=None):
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ('host', 'content-length', 'transfer-encoding')}
        req = urllib.request.Request(EVOLUTION + self.path, data=body,
                                     headers=headers, method=self.command)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                raw_transformed = transform(raw, self.path)
                print(f"[{self.command}] {self.path} -> {r.status}", flush=True)
                if raw != raw_transformed:
                    print(f"  TRANSFORMADO: {raw_transformed[:300]}", flush=True)
                else:
                    print(f"  PASSTHROUGH: {raw[:300]}", flush=True)
                self.send_response(r.status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(raw_transformed)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(raw_transformed)
        except urllib.error.HTTPError as e:
            b = e.read()
            print(f"[{self.command}] {self.path} -> ERRO {e.code}: {b[:200]}", flush=True)
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b)
        except Exception as e:
            print(f"[{self.command}] {self.path} -> EXCECAO: {e}", flush=True)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_GET(self): self.relay()
    def do_DELETE(self): self.relay()
    def do_OPTIONS(self):
        print(f"[OPTIONS] {self.path}", flush=True)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        self.relay(self.rfile.read(n) if n else None)
    def do_PUT(self):
        n = int(self.headers.get('Content-Length', 0))
        self.relay(self.rfile.read(n) if n else None)
    def log_message(self, *a): pass

if __name__ == '__main__':
    s = HTTPServer(('0.0.0.0', 8090), Handler)
    print('Proxy v1->v2 rodando na porta 8090 (com debug)', flush=True)
    s.serve_forever()
