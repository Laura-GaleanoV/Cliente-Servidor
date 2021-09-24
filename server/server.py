import zmq
import os
from os import listdir
from os.path import isfile, join
import hashlib


context = zmq.Context()
s = context.socket(zmq.REP)
s.bind('tcp://*:8001')

while True:
    print("Esperando solicitud")
    m = s.recv_multipart()
    res = ''
    if m[0] == b'download':
        print(isfile(m[1].decode('utf-8')))
        if isfile(m[1].decode('utf-8')):

            file = open(m[1].decode("utf-8"), 'rb')

            # Utilizamos os.stat para saber el estado de un path en particular
            file_stats = os.stat(m[1])

            print(f'File Size in Bytes is {file_stats.st_size}')

            fileSize = file_stats.st_size

            res = file.read(fileSize)

            s.send(res)
            print('El archivo se ha descargado con exito')

        else:
            s.send_string('00000')

    elif m[0] == b'upload':

        if m[2] == b'error':
            res = 'Intenta de nuevo con un archivo valido'

        else:
            file = open(m[1].decode("utf-8"), 'ab')

            file.write(m[2])
            file.close()
            print('El archivo {} se ha cargado con exito'.format(m[1]))

            res = 'El archivo se ha cargado con exito'
        s.send_string(res)

    elif m[0] == b'sharelink':
        if isfile(m[1].decode('utf-8')):
            s.send(m[1])
        else:
            s.send_string('00000')

    elif m[0] == b'downloadlink':

        mypath = r'D:\USUARIO\Documentos\Universidad\Semestre11\Cliente-Servidor\drive\server2'
        contenido = os.listdir(mypath)
        for fichero in contenido:
            if os.path.isfile(os.path.join(mypath, fichero)):
                # comparo los archivos del servidor con el link del archivo
                hash = hashlib.md5(fichero.encode('utf-8')).hexdigest()
                if m[1].decode('utf-8') == hash:
                    archivo = fichero.encode('utf-8')
                    s.send(archivo)

            else:
                s.send_string('Archivo no encontrado')

    elif m[0] == b'list':
        # listar todos los archivos:
        mypath = r'D:\USUARIO\Documentos\Universidad\Semestre11\Cliente-Servidor\drive\server2'
        res = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        s.send_string(str(res))
        print(res)
    else:
        res = 'Error. Intenta de nuevo con una solicitud valida'
        s.send_string(res)
