import zmq
import hashlib
import os

context = zmq.Context()
s = context.socket(zmq.REP)
s.bind('tcp://*:8001')

Name = "server1"
hash_object = hashlib.sha1(Name.encode())
name = hash_object.hexdigest()
# se convierte el nombre en un entero en base 16
nameAsnum = int(name, 16)

while True:
    print("Esperando solicitud")
    # print(hash_object)
    # print(name)
    # print(nameAsnum)
    print('______________________________________________________________')
    m = s.recv_multipart()
    res = ''

    if m[0] == b'name':
        s.send_string(str(nameAsnum))

    if m[0] == b'upload':
        ub = int(m[3].decode('utf-8'))
        #print('este es el limite superior: {}'.format(ub))
        if ub == nameAsnum:
            file = open(m[1].decode("utf-8"), 'ab')
            file.write(m[2])
            file.close()
            s.send_string('El archivo se ha cargado con exito')
        else:
            s.send_string('No se ha guardado ningun archivo')

    if m[0] == b'download':
        file = m[1].decode('utf-8')
        h = m[2].decode('utf-8')
        print("***********************************")
        print(h)
        print("***********************************")
        if os.path.isfile(file):
            with open(file, 'rb') as f:
                while True:
                    data = f.read(1024*1024)
                    if not data:
                        break
                    hash = hashlib.sha1(data)
                    archivo = hash_object.hexdigest()
                    num = int(archivo, 16)
                    print(num)
                    if h == num:
                        s.send(data)
                    else:
                        s.send_string('0000')
        else:
            s.send_string('0000')
