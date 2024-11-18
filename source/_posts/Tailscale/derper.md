# Install custom DERP on severs


## Run DERP server on a server
```bash
DERP_HOST=derp.example.com
STUN_PORT=12345
DERP_PORT=12346

~/go/bin/derper \
    -c ~/.derper.key \
    -a :${DERP_PORT} -http-port -1 \
    -stun-port ${STUN_PORT} \
    -hostname ${DERP_HOST} \
    --certmode manual \
    -certdir ~/.acme.sh/${DERP_HOST} \
    --verify-clients

echo "[Unit]
Description=Tailscale derp service
After=network.target

[Service]
ExecStart=/${USER}/go/bin/derper \
    -c /${USER}/.derper.key \
    -a :${DERP_PORT} -http-port -1 \
    -stun-port ${STUN_PORT} \
    -hostname ${DERP_HOST} \
    --certmode manual \
    -certdir ~/.acme.sh/${DERP_HOST} \
    --verify-clients
Restart=always
User=${USER}

[Install]
WantedBy=multi-user.target" \
	| sudo tee /etc/systemd/system/derp.service
```

## Acknowledgements
- https://tailscale.com/kb/1118/custom-derp-servers
- https://kiprey.github.io/2023/11/tailscale-derp/
- https://blog.angustar.com/archives/Tailscale-DERP.html
