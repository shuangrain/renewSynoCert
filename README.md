# Python script for automatically renewing Let's Encrypt certificates on Synology NAS using acme.json of traefik

## Example
```
python /var/services/homes/admin/renewSynoCert.py --domain "*.exfast.me" --acme-path /volume1/docker/traefik/acme.json
```

### Results
```
[2023-02-16 23:27:55] ✔✔✔ Found cert for '*.exfast.me' under '/usr/syno/etc/certificate/_archive/fbv75P' ✔✔✔
[2023-02-16 23:27:55] Replacing certificates from '/volume1/docker/traefik/acme.json'
[2023-02-16 23:27:55] ♦♦♦ WORKING ON SYSTEM APPS ♦♦♦
[2023-02-16 23:27:55] ♦♦♦ RELOADING NGINX ♦♦♦
[nginx] reloaded.
[2023-02-16 23:27:55] ♦♦♦ WORKING ON OTHER APPS ♦♦♦
[2023-02-16 23:27:55] app: 'SynologyDrive'
[2023-02-16 23:27:55] Copying from '/usr/syno/etc/certificate/_archive/fbv75P/cert.pem' to '/usr/local/etc/certificate/SynologyDrive/SynologyDrive/cert.pem'
[2023-02-16 23:27:55] Copying from '/usr/syno/etc/certificate/_archive/fbv75P/privkey.pem' to '/usr/local/etc/certificate/SynologyDrive/SynologyDrive/privkey.pem'
[2023-02-16 23:27:55] Restarting 'SynologyDrive'
restart package [SynologyDrive] successfully
```