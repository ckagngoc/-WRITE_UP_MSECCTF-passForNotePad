# [WRITE UP] pass_for_notepad by MSECCTF 2022


#### Sau cuộc thi căng thẳng hơn 8 tiếng và vượt qua cơn trầm cảm của bản thân vì quá nghèo nàn kiến thức, xốc lại tinh thần chia sẻ lại quá trình làm bài của mình, bài không quá cao siêu, cách làm còn nhiều lủng củng, ming mọi người đọc và cho nhận xét chứ đừng buông lời cay đắng !!!
Bài cho file nén PassForNotePad.rar giải nén ta được 3 file như hình:

![markdown](https://images.viblo.asia/518eea86-f0bd-45c9-bf38-d5cb119e947d.png)
 
Chạy thử chương trình trên *cmd* và nội dung file *README.txt* ta đoán đây là file mã hóa nội dung của file, và file *secret.txt.mta* là file đã được mã hóa:

 


Kiểm chứng bằng cách tạo 1 file *test.txt* với nội dung “conghoaxahoichunghiavietnam” chạy file .exe với đối số là *file = test.txt, password = ckagngoc*
 
Ta nhận được file có dạng *test.txt.mta* với nội dung có cấu trúc tương tự như file *secret.txt.mta*, đây chắc chắn là flag được mã hóa.
Ném file .exe vào IDA, trong subview String ta thấy hàng loạt Proc có *py_* ở đầu, đây là file được build bằng Python:
 
Sử dụng *pyinstxtrator.py* trích xuất nội dung file .exe:
Command: `python pyinstxtractor.py PassForNotePad.exe`
Nhận được được thông báo sau: 
```
[+] Processing C:\Users\acer\Desktop\BaiCho\PassForNotePad\PassForNotePad.exe
[+] Pyinstaller version: 2.1+
[+] Python version: 3.6
[+] Length of package: 5718785 bytes
[+] Found 64 files in CArchive
[+] Beginning extraction...please standby
[+] Possible entry point: pyiboot01_bootstrap.pyc
[+] Possible entry point: pyi_rth_subprocess.pyc
[+] Possible entry point: pyi_rth_pkgutil.pyc
[+] Possible entry point: pyi_rth_inspect.pyc
[+] Possible entry point: main.pyc
[!] Warning: This script is running in a different Python version than the one used to build the executable.
[!] Please run this script in Python 3.6 to prevent extraction errors during unmarshalling
[!] Skipping pyz extraction
[+] Successfully extracted pyinstaller archive: C:\Users\acer\Desktop\BaiCho\PassForNotePad\PassForNotePad.exe

You can now use a python decompiler on the pyc files within the extracted directory
```
File được build bằng python 3.6, thì tải về rồi chạy lại với python 3.6 cho chắc ăn hô hô, trước mình có decompile python thì thấy không đúng builder thường decompile sẽ thất bại:
Command: py -3.6 pyinstxtractor.py PassForNotePad.exe
Nhận được file main.pyc
Ta dùng uncompile6 để decompile code ra file main.py sẽ trông như thế này:
Command: undecompyle6 -o . main.pyc
 
Vào xem code ta thấy hai def fnEncrypt và dnDecrypt
```
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

```
Hàm main sẽ chạy hai def này tương ứng với hai đối số “-e|-d”, đọc def fnDecrypt ta thấy nó sẽ đọc 32 ký tự đầu của file mã hóa lưu vào password_in_file sau đó lấy 4 ký tự index là 6, 5, 0, 2 để mã hóa và so sánh với password_in_file:
```
password_in_file = d_inp[:32]
d_inp = d_inp[32:]
key = password[6] + password[5] + password[0] + password[2]
m = hashlib.md5(key.encode('utf-8'))
key = m.digest()
key = key.hex()
if key != password_in_file:
```
4 ký tự trên được nối vào xâu key sau đó mã hóa md5 lưu kết quả vào m rồi chuyển lại vào key => decrypt md5 32 ký tự đầu file secret.txt.mta ta sẽ nhận được 4 ký tự có index là 6, 5, 0, 2 của password:
 
Tiếp tục đọc code ta thấy key sẽ bằng “1234” + const SALT ở đầu sẽ là đối số để tạo crypter giải mã cho đoạn text còn lại của file secret.txt.mta từ đó ta có đoạn scrypt sau xử lý phần text còn lại: 
```
import hashlib, base64
from Crypto.Cipher import DES
writeFile = ''
SALT = '(«¼ÍÞï\x003'
d_intern = base64.b32decode('LFH7YTOQ3FGHYOBM5BHXL42ZW2FXYH4TWSKRTXS5JODMM766YVGUCTGIWAEVJ65ZB2T3F7NMSY77KR7LSV4BNPXEC2HDV5ZPZT3DC3NP473IKJIFYJT6EAMKTOV6FTJLZP2YKEEPETUCZP3DO3LBX5BCH34GODBV3YLTEKUP5WSCVGDJMQQNYNXLETA76EJR476YP5NXBJEBGK4PXM3VRIMBQG7ERGOIMM7GH6Z7W2OWFU6PKGFC57TQ5G5TF6IIP7CVTA2CPVX54YW75RXY2WDNQVGKIPMLMW3KH4Q2IRITN6N3XMF2UPWURA6MMSOK4P4I72CWVSRG2OP75T6ZY5H7N2QIP73JQBSZ62ANJAUXOOVLH2MC6PN2LQ3DWU7ECRACXA2REAILXJHLPN4WDPFIN3I6V4WEX6ZHKY5MBP3LJXIAN46YAHJOMOQFALXUA7XKKVNUNBYC2K5JX74NFGNEOZ3HA4APGHSHZBMLP2FILO3VDRDQQUOQGBYSTDXRSXSPRBEEBIYKGVETJIVKX5AABX32F2I2PSAXXPF7OZUJ5US5U3UFVUV6CCGI37D72DWBW7JQYHA6UGWKRYMLQNL3UUY3RTJ3K32AFLQONDNJTHPB76MZRCPSMKDVSWBXANMBZXFEYNQU5FMEZP2GK6HGXS3GGY5N2OZADPGKVO6IG2YB32SHJSUG4B4I3ACHQW24IPNOQXXC2OFRGZRJFZT3PKATB4DP2EWJ5KJ4GZVWOMWWSMISCLCBUAT46UYMGAJAHFSUGGTAY===')
key = '1' + '2' + '3' + '4' + SALT
m = hashlib.md5(key.encode('utf-8'))
key = m.digest()
dk, iv = key[:8], key[8:]
crypter = DES.new(dk, DES.MODE_CBC, iv)
d_out = crypter.decrypt(d_intern)
print(d_out)
```
flag: **MSEC{pl4y_h4rd_w0rk_h4rd}**

