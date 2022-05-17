import numpy as np


def read_bin(filedir, dtype="float32"):
    assert filedir.endswith("bin")
    data = np.fromfile(filedir, dtype=dtype).reshape(-1, 4)
    coords = data[:,:3]
    
    return coords

def read_ply(filedir, dtype="float32"):
    files = open(filedir, 'r')
    data = []
    for _, line in enumerate(files):
        wordslist = line.split(' ')
        try:
            line_values = []
            for i, v in enumerate(wordslist):
                if v == '\n': continue
                line_values.append(float(v))
        except ValueError: continue
        data.append(line_values)
    data = np.array(data)
    coords = data[:,0:3].astype(dtype)

    return coords


def write_ply(filedir, coords, normal=None, dtype='int32'):
    f = open(filedir,'w')
    f.writelines(['ply\n','format ascii 1.0\n'])
    f.write('element vertex '+str(coords.shape[0])+'\n')
    f.writelines(['property float x\n','property float y\n','property float z\n'])
    if normal is not None:
        f.writelines(['property float nx\n','property float ny\n','property float nz\n'])
    f.write('end_header\n')
    coords = coords.astype(dtype)
    if normal is None:
        for p in coords:
            f.writelines([str(p[0]), ' ', str(p[1]), ' ',str(p[2]), '\n'])
    else:
        for p, n in zip(coords, normal):
            f.writelines([str(p[0]), ' ', str(p[1]), ' ',str(p[2]), ' ',
                            str(n[0]), ' ', str(n[1]), ' ',str(n[2]), '\n'])
    f.close() 

    return