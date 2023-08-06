from nacl import pwhash, secret

"""
Cryptographic constants required by cryptbuddy
"""

chunksize = 64 * 1024
macsize = secret.SecretBox.MACBYTES
ops = pwhash.argon2i.OPSLIMIT_SENSITIVE
mem = pwhash.argon2i.MEMLIMIT_SENSITIVE
kdf = pwhash.argon2i.kdf
keysize = secret.SecretBox.KEY_SIZE
saltbytes = pwhash.argon2i.SALTBYTES
noncesize = secret.SecretBox.NONCE_SIZE
all = (kdf, ops, mem,
       keysize, chunksize, macsize)
delimiter = b'\xFF\xFF\xFF\xFF'
escape_sequence = b'\xAA\xAA\xAA\xAA'
