import os
import struct

poses = [156, 160, 188, 196, 200, 228, 360, 424]

def get_params(carspath):
    result = {}
    for subdir, dirs, files in os.walk(carspath):
        if dirs:
            continue
        carname = subdir.split('\\')[-1]
        with open(subdir + '\\avto.par', 'rb') as f:
            data = f.read()
            params = []
            for i in poses:
                params.append(data[i:i+4])
            result[carname] = params
            
    return result

def replace_params(car, params):
    with open(car + '/avto.par', 'r+b') as f:
        for n, i in enumerate(poses):
            f.seek(i)
            f.write(struct.pack('f', params[n]))
            if n > 5:
                f.seek(i+4)
                f.write(struct.pack('f', params[n]))

if __name__ == "__main__":
    # print(get_params('C:\\Games\\YD\\Cars'))
    replace_params('.', [0, 0, 0, 0, 0, 0, 0, 0])