import zmq
import os
import json
import hashlib
from hashlib import md5

context = zmq.Context()  # black box

# crea un socket y lo conecta a través de un protocolo tcp con el equipo local en el puerto 8001
s = context.socket(zmq.REQ)
s.connect('tcp://localhost:8001')


def upload(fileN):
    fileName = fileN.encode('utf-8')
    if os.path.isfile(fileName.decode('utf-8')):
        # Utilizamos os.stat para saber el estado de un path en particular
        #file_stats = os.stat(fileName.decode('utf-8'))
        #print(f'File Size in Bytes {file_stats.st_size}')
        #fileSize = file_stats.st_size
        #file = open(fileN, 'rb')
        #fileBytes = file.read(fileSize)
        with open(fileN, 'rb') as f:
            while True:
                data = f.read(1024*1024)
                if not data:
                    break
                m = [b'upload', fileName, data]
                s.send_multipart(m)
                r = s.recv()

    else:
        print('Error. No existe este archivo')
        fileBytes = b'error'

    #m = [b'upload', fileName, fileBytes]

    # s.send_multipart(m)
    #r = s.recv()
    print('{}'.format(r.decode('utf-8')))


def download(fileN):
    fileName = fileN.encode('utf-8')
    m = [b'download', fileName]
    s.send_multipart(m)
    r = s.recv()
    message = ''
    if r == b'00000':
        print('El archivo no se encuentra disponible para descargar')
    else:
        file = open(fileN, 'wb')
        file.write(r)
        file.close()
        print('El archivo {} se ha descargado exitosamente'.format(
            m[1].decode('utf-8')))
        message = 'ok'

    return message


def sharelink(fileN):
    fileName = fileN.encode('utf-8')
    m = [b'sharelink', fileName]
    s.send_multipart(m)
    r = s.recv()
    if r == b'00000':
        print('El archivo no se encuentra disponible para descargar')
    else:
        print('Copia y comparte este link:')
        print(md5(r).hexdigest())


def links(link):
    filelink = link.encode('utf-8')
    m = [b'downloadlink', filelink]
    s.send_multipart(m)
    r = s.recv()
    archivo = r.decode('utf-8')
    download(archivo)


def list():
    # Lista los archivos en el servidor
    m = [b'list']
    s.send_multipart(m)
    r = s.recv()
    print(r)


def main():
    userName = input('Ingresa tu nombre  de usuario:')
    print('Selecciona una opción:')
    opcion = int(
        input('1.Upload 2.Download 3.Sharelink 4.Downloadlink 5.List : '))

    if opcion == 1:
        fileN = str(input('Ingrese el nombre del archivo: '))
        upload(fileN)

    elif opcion == 2:
        fileN = str(input('Ingrese el nombre del archivo: '))
        download(fileN)

    elif opcion == 3:
        fileN = str(
            input('Ingrese el nombre del archivo que quiere compartir: '))
        sharelink(fileN)

    elif opcion == 4:
        link = str(input('Ingrese el link del archivo: '))
        links(link)

    elif opcion == 5:
        list()


if __name__ == "__main__":
    main()
