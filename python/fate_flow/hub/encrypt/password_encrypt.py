import base64

from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher


def rsa_key_generate():  # 生成密钥对， RSA 密钥对生成
    random_generator = Random.new().read
    rsa = RSA.generate(2048, random_generator)
    private_pem = rsa.exportKey().decode()
    public_pem = rsa.publickey().exportKey().decode()
    with open('private_key.pem', "w") as f:
        f.write(private_pem)
    with open('public_key.pem', "w") as f:
        f.write(public_pem)
    return private_pem, public_pem


def encrypt_data(public_key, msg):  # 使用公钥对明文进行加密生成密文
    cipher = PKCS1_cipher.new(RSA.importKey(public_key))
    encrypt_text = base64.b64encode(cipher.encrypt(bytes(msg.encode("utf8"))))
    return encrypt_text.decode('utf-8')


def pwdecrypt(private_key, encrypt_msg):  # 使用私钥对密文进行解密返回明文
    try:
        cipher = PKCS1_cipher.new(RSA.importKey(private_key))
        back_text = cipher.decrypt(base64.b64decode(encrypt_msg), 0)
        return back_text.decode('utf-8')
    except Exception as e:
        raise RuntimeError(f"passwd decrypt failed: {e}")


def test_encrypt_decrypt():
    msg = "fate"
    private_key, public_key = rsa_key_generate()
    encrypt_text = encrypt_data(public_key, msg)
    print(encrypt_text)
    decrypt_text = pwdecrypt(private_key, encrypt_text)
    print(msg == decrypt_text)
