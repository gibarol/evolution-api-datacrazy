#!/bin/bash
# Instala o proxy como serviço systemd — execute como root no VPS
# O proxy sobrevive a reinicializações. O tunnel ainda precisa ser reiniciado manualmente.

set -e

echo "=== Instalando proxy como serviço systemd ==="

# Garantir que o proxy está em /opt/evolution-api/proxy.py
if [ ! -f /opt/evolution-api/proxy.py ]; then
  echo "Baixando proxy..."
  mkdir -p /opt/evolution-api
  curl -fsSL https://raw.githubusercontent.com/gibarol/evolution-api-datacrazy/main/proxy.py \
    -o /opt/evolution-api/proxy.py
fi

# Criar serviço systemd para o proxy
cat > /etc/systemd/system/evolution-proxy.service << 'EOF'
[Unit]
Description=Evolution API v1->v2 Compatibility Proxy
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/evolution-api/proxy.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/evolution-proxy.log
StandardError=append:/var/log/evolution-proxy.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable evolution-proxy
systemctl start evolution-proxy

echo ""
echo "=== Status do serviço ==="
systemctl status evolution-proxy --no-pager

echo ""
echo "=== Proxy instalado e ativo ==="
echo "Log: /var/log/evolution-proxy.log"
echo "Ver log: journalctl -u evolution-proxy -f"
echo "Reiniciar: systemctl restart evolution-proxy"
