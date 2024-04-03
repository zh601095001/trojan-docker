import base64
import json
import os

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# 找出所有匹配的环境变量
prefix = 'CONFIG_'
matching_env_vars = {key[len(prefix):].lower().replace("__", "."): json.loads(value) if value.strip().startswith(('[', '{')) else value for key, value in os.environ.items() if
                     key.startswith(prefix)}

# 修改为你的 acme.json 文件路径
ACME_JSON_FILE = os.environ.get("ACME_JSON_FILE")
# 修改为证书和密钥的输出路径
CERT_FILE = '/certificates/cert.pem'
KEY_FILE = '/certificates/privkey.pem'
# 修改为你的域名
DOMAIN = os.environ.get("DOMAIN")


def create_cert():
    with open(ACME_JSON_FILE, 'r') as f:
        data = json.load(f)

    certs = data['le']['Certificates']
    for cert in certs:
        cert_domain = cert['domain']['main']
        if cert_domain == DOMAIN:
            # Base64 解码证书和私钥
            decoded_cert = base64.b64decode(cert['certificate'])
            decoded_key = base64.b64decode(cert['key'])

            # 提取和保存证书
            with open(CERT_FILE, 'wb') as f:
                f.write(x509.load_pem_x509_certificate(decoded_cert, default_backend()).public_bytes(serialization.Encoding.PEM))
            # 提取和保存密钥
            with open(KEY_FILE, 'wb') as f:
                f.write(serialization.load_pem_private_key(decoded_key, password=None, backend=default_backend()).private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            print(f"证书和密钥已保存至 {CERT_FILE} 和 {KEY_FILE}")
            return

    print("未找到域名的证书。请检查域名是否正确或证书是否存在。")
    return


raw_config = json.load(open("/config/config.json"))


def set_value(config, path, value):
    keys = path.split(".")
    for key in keys[:-1]:  # 遍历路径中的键，除了最后一个
        config = config.setdefault(key, {})
    if "port" in keys[-1]:
        value = int(value)
    config[keys[-1]] = value


set_value(raw_config, "ssl.cert", CERT_FILE)
set_value(raw_config, "ssl.key", KEY_FILE)
for path, value in matching_env_vars.items():
    set_value(raw_config, path, value)

with open("/config/config.json", "w+") as fp:
    json.dump(raw_config, fp)

create_cert()
