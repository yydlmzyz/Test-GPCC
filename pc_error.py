import os
import subprocess
rootdir = os.path.split(__file__)[0]

def number_in_line(line):
    wordlist = line.split(' ')
    for _, item in enumerate(wordlist):
        try: number = float(item) 
        except ValueError: continue
        
    return number

def pc_error(infile1, infile2, resolution, normal=False, DBG=False):
    headers = ["mseF      (p2point)", "mseF,PSNR (p2point)"]
    command = str(rootdir+'/pc_error_d' + 
        ' -a '+infile1+ 
        ' -b '+infile2+ 
        ' --hausdorff=1 '+ 
        ' --resolution='+str(resolution))
    if normal:
        headers +=["mseF      (p2plane)", "mseF,PSNR (p2plane)"]
        command = str(command + ' -n ' + infile1)
    results = {}   
    subp=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    subp.wait()
    c=subp.stdout.readline()
    while c:
        if DBG: print(c)
        line = c.decode(encoding='utf-8')
        for _, key in enumerate(headers):
            if line.find(key) != -1:
                value = number_in_line(line)
                results[key] = value
        c=subp.stdout.readline() 

    return subp, results
