import zmq
import os
import hashlib


def Entero(archivo):
    hash_object = hashlib.sha1(archivo)
    name = hash_object.hexdigest()
    # se convierte el nombre en un entero en base 16
    nameAsnum = int(name, 16)
    return nameAsnum


class Range:
    def __init__(self, lb, ub):
        self.lb = lb  # limite inferior
        self.ub = ub  # limite superior

    def isFirst(self):
        # limite inferior mayor que limite superior
        return self.lb > self.ub

    def member(self, id):
        # si es el primer rango entonces verifico si el sha1 esta del limite inferior al ultimo (2^160) o está desde 0 al limite superior
        if self.isFirst():
            return (id >= int(self.lb) and id < 1 << 160) or (id >= 0 and id < int(self.ub))
        else:
            return id >= int(self.lb) and id < int(self.ub)

    def limite(self):
        return str(self.ub)

    def toStr(self):
        if self.isFirst():
            # retorna los rangos
            return '[' + str(self.lb) + ', 2^160) U [' + '0 , ' + str(self.ub) + ')'
        else:
            return '[' + str(self.lb) + ' , ' + str(self.ub) + ')'


def upload(fileN):
    fileName = fileN.encode('utf-8')
    # Lista de servidores
    servers = []
    m = [b'name', fileName]
    # recorro los servidores y les pido su nombre
    for item in range(1, 4):
        context = zmq.Context()
        s = context.socket(zmq.REQ)
        s.connect('tcp://localhost:800{}'.format(item))
        s.send_multipart(m)
        Name = s.recv()
        servers.append(Name.decode())
    print(servers)
    servers.sort()
    print(servers)
    # lista de rangos
    ranges = []
    # n en la longitud de la lista de servidores
    for n in range(len(servers)-1):
        lb = servers[n]
        ub = servers[n+1]
        ranges.append(Range(lb, ub))
    # Este es para el rango especial, se le envía a la clase rango el limite inferior que es la ultima posición
    # de la lista de servidores y el limite superior que sería la primer posición
    ranges.append(Range(servers[2], servers[0]))
    for r in ranges:
        print(r.toStr())

    # Lectura de archivo
    index = fileN.split('.')[0]
    indexn = index + '.index'
    if os.path.isfile(fileN):
        with open(fileN, 'rb') as f:
            with open(indexn, 'a') as fn:
                fn.write(fileN + '\n')
                while True:
                    data = f.read(1024*1024)
                    if not data:
                        break
                    # la función entero convierte cada parte del archivo a entero
                    p = Entero(data)
                    # print(p)
                    for sr in ranges:
                        if sr.member(p):
                            fn.write(str(p)+'\n')
                            # print('{} -> {}'.format(p, sr.toStr()))
                            # print('limite superior: {}'.format(sr.limite()))
                            ls = sr.limite().encode('utf-8')
                            # file = str(p).encode('utf-8')

                            m = [b'upload', fileName, data, ls]
                            for item in range(1, 4):
                                context = zmq.Context()
                                s = context.socket(zmq.REQ)
                                s.connect('tcp://localhost:800{}'.format(item))
                                s.send_multipart(m)
                                message = s.recv()
                                # print(message)

    else:
        print('Error. No existe este archivo')

    hash_object = hashlib.sha1(indexn.encode())
    name = hash_object.hexdigest()
    print('El archivo se ha cargado exitosamente')
    print('Archivo index:{}'.format(name))


def download(fileN):
    lineas = []
    f = open(fileN, "r")
    while(True):
        linea = f.readline().rstrip()
        print(linea)
        lineas.append(linea)
        if not linea:
            break
    f.close()
    # print(lineas[0])
    file = open(lineas[0], 'ab')
    for n in range(1, len(lineas)-1):
        name = lineas[0].encode('utf-8')
        data = lineas[n].encode('utf-8')
        m = [b'download', name, data]
        for item in range(1, 4):
            context = zmq.Context()
            s = context.socket(zmq.REQ)
            s.connect('tcp://localhost:800{}'.format(item))
            s.send_multipart(m)
            rs = s.recv()
            if rs == b'0000':
                print('No se encuentra el archivo en el servidor {}'.format(item))
            else:
                file.write(rs)

    file.close()
    print("El archivo {} se ha descargado con exito".format(lineas[0]))


def main():
    print('Selecciona una opción:')
    opcion = int(input('1.Upload 2.Download 3.Sharelink: '))

    if opcion == 1:
        fileN = str(input('Ingrese el nombre del archivo: '))
        upload(fileN)

    elif opcion == 2:
        fileN = str(input('Ingrese el link del archivo: '))
        download(fileN)


if __name__ == "__main__":
    main()
