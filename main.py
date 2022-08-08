# uncompyle6 version 3.8.0
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.10.0 (tags/v3.10.0:b494f59, Oct  4 2021, 19:00:18) [MSC v.1929 64 bit (AMD64)]
# Embedded file name: main.py
from sys import argv, exit
from Cryptodome.Cipher import DES
import hashlib, base64
SALT = '(«¼ÍÞï\x003'
path_inp_txt = ''
path_out_txt = ''
mode = ''
password = ''

def fnEncrypt(path_inp_txt, path_out_txt):
    f_inp = open(path_inp_txt, 'rb')
    f_out = open(path_out_txt, 'w')
    d_inp = f_inp.read()
    d_intern = b''
    d_out = b''
    key = password[6] + password[5] + password[0] + password[2]
    m = hashlib.md5(key.encode('utf-8'))
    key = m.digest()
    key = key.hex()
    f_out.write(key)
    key = password[6] + password[5] + password[0] + password[2] + SALT
    m = hashlib.md5(key.encode('utf-8'))
    key = m.digest()
    dk, iv = key[:8], key[8:]
    crypter = DES.new(dk, DES.MODE_CBC, iv)
    d_inp += b'\x00' * (8 - len(d_inp) % 8)
    d_intern = crypter.encrypt(d_inp)
    d_out = base64.b32encode(d_intern)
    f_out.write(d_out.decode('utf-8'))
    f_inp.close()
    f_out.close()


def fnDecrypt(path_inp_txt, path_out_txt):
    f_inp = open(path_inp_txt, 'r')
    f_out = open(path_out_txt, 'wb')
    d_inp = f_inp.read()
    d_intern = b''
    d_out = b''
    password_in_file = d_inp[:32]
    d_inp = d_inp[32:]
    key = password[6] + password[5] + password[0] + password[2]
    m = hashlib.md5(key.encode('utf-8'))
    key = m.digest()
    key = key.hex()
    if key != password_in_file:
        print('Wrong password!')
        return
    d_intern = base64.b32decode(d_inp)
    key = password[6] + password[5] + password[0] + password[2] + SALT
    m = hashlib.md5(key.encode('utf-8'))
    key = m.digest()
    dk, iv = key[:8], key[8:]
    crypter = DES.new(dk, DES.MODE_CBC, iv)
    d_out = crypter.decrypt(d_intern)
    f_out.write(d_out)
    f_inp.close()
    f_out.close()


def fnInfo():
    print('use [-e|-d] file password')
    print('Your password must be at least 8 characters')
    print('-e: encrypt')
    print('-d: decrypt')


def fnIsPassWordValid(psswrd):
    if len(psswrd) < 8:
        return False
    else:
        return True


if __name__ == '__main__':
    if len(argv) != 4:
        fnInfo()
        exit(0)
    else:
        mode = argv[1]
        path_inp_txt = argv[2]
        password = argv[3]
        if fnIsPassWordValid(password) == False:
            print('Your password must be at least 8 characters')
            exit(0)
        try:
            f = open(path_inp_txt, 'r')
            f.close()
        except FileNotFoundError:
            print('File not found. Check the path variable and filename')
            exit(0)

    if mode == '-e':
        path_out_txt = path_inp_txt + '.mta'
        fnEncrypt(path_inp_txt, path_out_txt)
        exit(0)
    else:
        if mode == '-d':
            path_out_txt = path_inp_txt[:-4]
            fnDecrypt(path_inp_txt, path_out_txt)
            exit(0)
        else:
            print('e: encrypt')
            print('d: decrypt')
            exit(0)