# usage: PASS=... python3 encrypt_build.py <items.json> <audio_dir> <out_dir> [salt_hex]
import os,sys,json,unicodedata
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
items_p,audio_d,out=sys.argv[1],sys.argv[2],sys.argv[3]
pw=unicodedata.normalize('NFC',os.environ['PASS']).encode()
ITER=600000
meta_p=os.path.join(out,'meta.json')
if len(sys.argv)>4: salt=bytes.fromhex(sys.argv[4])
elif os.path.exists(meta_p): salt=bytes.fromhex(json.load(open(meta_p))['salt'])
else: salt=os.urandom(16)
key=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=salt,iterations=ITER).derive(pw)
g=AESGCM(key)
def enc(b,path=None):
    # keep the existing file when its content is unchanged, so GitHub only stores what changed
    if path and os.path.exists(path):
        old=open(path,'rb').read()
        try:
            if g.decrypt(old[:12],old[12:],None)==b: return old
        except Exception: pass
    iv=os.urandom(12);return iv+g.encrypt(iv,b,None)
os.makedirs(os.path.join(out,'audio'),exist_ok=True)
items=json.load(open(items_p))
dp=os.path.join(out,'data.enc');d=enc(json.dumps(items,ensure_ascii=False,separators=(',',':')).encode(),dp);open(dp,'wb').write(d)
for it in items:
    ap=os.path.join(out,'audio',it['id']+'.enc');d=enc(open(os.path.join(audio_d,it['id']+'.mp3'),'rb').read(),ap);open(ap,'wb').write(d)
json.dump({'v':1,'salt':salt.hex(),'iter':ITER},open(meta_p,'w'))
print('items',len(items))
