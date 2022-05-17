import os
import subprocess

def gpcc_encode(filedir, bin_dir, posQuantscale=1, tmc3dir='./tmc3', cfgdir='encoder.cfg', DBG=False):
    cmd = tmc3dir + ' --mode=0 ' \
        + ' --config='+cfgdir \
        + ' --positionQuantizationScale='+str(posQuantscale) \
        + ' --uncompressedDataPath='+filedir \
        + ' --compressedStreamPath='+bin_dir
    if posQuantscale==1: 
        cmd+=' --inferredDirectCodingMode=3'
        # https://github.com/MPEGGroup/mpeg-pcc-tmc13/blob/c3c9798a0f63970bd17ce191900ded478a8aa0f6/cfg/octree-raht-ctc-lossless-geom-lossy-attrs.yaml#L39
    subp=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    subp.wait()
    if DBG: print_log(subp)

    return subp

def gpcc_decode(bin_dir, dec_dir, tmc3dir='./tmc3', DBG=False):
    cmd = tmc3dir + ' --mode=1 ' \
        + ' --compressedStreamPath='+bin_dir \
        + ' --reconstructedDataPath='+dec_dir \
        + ' --outputBinaryPly=0'
    subp=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    subp.wait()
    if DBG: print_log(subp)

    return subp

def print_log(p):
    c=p.stdout.readline()
    while c:
        print(c)
        c=p.stdout.readline()
        
    return 