import argparse
import base64
import json
import logging
import os
import shutil
import subprocess
import sys

OPENSSL = "openssl"
CERT_ROOT_DIR = "/usr/syno/etc/certificate"
PACKAGE_CERT_ROOT_DIR = "/usr/local/etc/certificate"
FULL_CERT_DIR = CERT_ROOT_DIR + "/_archive"

logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def renew_cert(cert_dir: str, domain: str, acme_path: str):
    logger.info("Replacing certificates from %r", acme_path)
    content: dict
    with open(acme_path, "r") as f:
        content = json.loads(f.read())
    if not content:
        sys.exit("failed to not found {}".format(acme_path))

    for cert in content["myresolver"]["Certificates"]:
        if cert["domain"]["main"] == domain:
            with open(f"{cert_dir}/cert.pem", "w") as ff:
                ff.write(base64.b64decode(cert["certificate"]).decode("utf-8"))
            with open(f"{cert_dir}/privkey.pem", "w") as ff:
                ff.write(base64.b64decode(cert["key"]).decode("utf-8"))
            break


def certificate_has_correct_subject(domain: str, certificate_filepath: str) -> bool:
    subject = subprocess.run([OPENSSL, "x509", "-in", certificate_filepath, "-subject", "-noout"],
                             stdout=subprocess.PIPE, check=True).stdout.decode("utf-8").strip()
    return subject.endswith(domain)


def copy_certs(source: str, target: str):
    for file in ["cert.pem", "privkey.pem"]:
        source_file = os.path.join(source, file)
        target_file = os.path.join(target, file)

        logger.info("Copying from %r to %r", source_file, target_file)
        shutil.copy(source_file, target_file)


def restart_app(app: str):
    logger.info("Restarting %r", app)
    subprocess.run(["/usr/syno/bin/synopkg", "restart", app])


def main(domain: str, acme_path: str):
    cert_dir = None
    # search main directory of the certificate we want to renew
    for root, dirs, files in os.walk(FULL_CERT_DIR):
        for file in files:
            if file == "cert.pem":
                curr_file = os.path.join(root, file)

                if certificate_has_correct_subject(domain, curr_file):
                    cert_dir = root
                    break

    # stop script if main certificate directory wasn"t found
    if cert_dir is None:
        sys.exit("Certificate for {} not found under {}".format(domain, FULL_CERT_DIR))
    else:
        logger.info("✔✔✔ Found cert for %r under %r ✔✔✔", domain, cert_dir)

    # Renew the certificate and override the one in the previously found certificate directory
    renew_cert(cert_dir, domain, acme_path)

    # find system apps which are using the certificate and replace it with the renewed one
    logger.info("♦♦♦ WORKING ON SYSTEM APPS ♦♦♦")
    for root, dirs, files in os.walk(CERT_ROOT_DIR):
        for file in files:
            if (not root.startswith(FULL_CERT_DIR)) and (file == "cert.pem"):  # find all not under _archive
                curr_file = os.path.join(root, file)

                if certificate_has_correct_subject(domain, curr_file):
                    copy_certs(cert_dir, root)

    # reload nginx to make sure the renewed certificate is used
    logger.info("♦♦♦ RELOADING NGINX ♦♦♦")
    subprocess.run(["/usr/syno/bin/synosystemctl", "reload", "nginx"])

    # find other apps which are using the certificate and replace it with the renewed one
    logger.info("♦♦♦ WORKING ON OTHER APPS ♦♦♦")
    for root, dirs, files in os.walk(PACKAGE_CERT_ROOT_DIR):
        for file in files:
            if file == "cert.pem":
                curr_file = os.path.join(root, file)

                if certificate_has_correct_subject(domain, curr_file):
                    app_name = os.path.basename(os.path.dirname(root))  # get app name by directory
                    logger.info("app: %r", app_name)
                    copy_certs(cert_dir, root)
                    restart_app(app_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", type=str, required=True)
    parser.add_argument("--acme-path", type=str, required=True)

    args = parser.parse_args()
    main(args.domain, args.acme_path)
