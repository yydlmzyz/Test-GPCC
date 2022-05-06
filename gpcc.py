import os
import subprocess
rootdir = os.path.split(__file__)[0]

def gpcc_encode(filedir, bin_dir, posQuantscale=1, DBG=False):
    command=' --trisoupNodeSizeLog2=0' + \
            ' --neighbourAvailBoundaryLog2=8' + \
            ' --intra_pred_max_node_size_log2=6' + \
            ' --maxNumQtBtBeforeOt=4' + \
            ' --mergeDuplicatedPoints=1' + \
            ' --planarEnabled=1' + \
            ' --planarModeIdcmUse=0' + \
            ' --minQtbtSizeLog2=0'
    if posQuantscale==1: command+=' --inferredDirectCodingMode=1'
    subp=subprocess.Popen(
        rootdir+'/tmc3 --mode=0' + command + \
        ' --positionQuantizationScale='+str(posQuantscale) + \
        ' --uncompressedDataPath='+filedir + \
        ' --compressedStreamPath='+bin_dir, 
        shell=True, stdout=subprocess.PIPE)
    subp.wait()
    if DBG:
        c=subp.stdout.readline()
        while c:
            print(c)
            c=subp.stdout.readline()

    return subp

def gpcc_decode(bin_dir, dec_dir, DBG=False):
    subp=subprocess.Popen(
        rootdir+'/tmc3 --mode=1'+ \
        ' --compressedStreamPath='+bin_dir+ \
        ' --reconstructedDataPath='+dec_dir+ \
        ' --outputBinaryPly=0',
        shell=True, stdout=subprocess.PIPE)
    subp.wait()
    if DBG:
        c=subp.stdout.readline()
        while c:
            print(c)
            c=subp.stdout.readline()

    return subp
