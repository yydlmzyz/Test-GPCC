import numpy as np
import os, glob, argparse
from tqdm import tqdm
import pandas as pd
from data_io import read_bin, read_ply, write_ply
from quantization import quantize_precision, quantize_resolution
from gpcc import gpcc_encode, gpcc_decode
from pc_error import pc_error

def print_log(p):
    c=p.stdout.readline()
    while c:
        print(c)
        c=p.stdout.readline()
        
    return 

def get_points_num(filedir):
    if filedir.endswith('ply'):
        plyfile = open(filedir)
        line = plyfile.readline()
        while line.find("element vertex") == -1:
            line = plyfile.readline()
        number = int(line.split(' ')[-1][:-1])
    elif filedir.endswith("bin"):
        number = len(np.fromfile(filedir, dtype='float32').reshape(-1, 4))

    return number

def test(in_dir, bin_dir, out_dir, posQuantscale, resolution, DBG=False):
    enc_log = gpcc_encode(in_dir, bin_dir, posQuantscale=posQuantscale)
    if DBG: print_log(enc_log)
    dec_log = gpcc_decode(bin_dir, out_dir)
    if DBG: print_log(dec_log)
    # bpp
    in_points_num = get_points_num(in_dir)
    out_points_num = get_points_num(out_dir)
    bytes = os.path.getsize(bin_dir)
    bpp = round(8*bytes/in_points_num, 4)
    # results
    results={'posQuantscale':posQuantscale, 'num_points':out_points_num, 'bytes':bytes, 'bpp':bpp}
    metric_log, metric_results = pc_error(in_dir, out_dir, resolution=resolution, normal=False)
    if DBG: print_log(metric_log)
    results.update(metric_results)

    return results

def test_multi_rates(filedir, outdir, posQuantscale_list, resolution=30000):
    # read data and quantize
    if filedir.endswith('ply'): 
        coords = read_ply(filedir)
    if filedir.endswith('bin'): 
        coords = read_bin(filedir)
        coords = quantize_precision(coords.copy(), precision=0.001)
        # coords = quantize_resolution(coords.copy(), resolution=65535)
    filename = os.path.split(filedir)[-1].split('.')[0]
    filename = os.path.join(outdir, filename)
    in_dir = filename+'.ply'
    write_ply(in_dir, coords)
    # test
    results_list = []
    for idx_rate, posQuantscale in enumerate(posQuantscale_list):
        bin_dir = filename + '_R'+str(idx_rate) + '.bin'
        out_dir = filename + '_R'+str(idx_rate) + '_dec.ply'
        results = test(in_dir, bin_dir, out_dir, posQuantscale, resolution=resolution)
        if True:
            print("="*8, 'R'+str(idx_rate), "="*8)
            for k, v in results.items(): print(k, ':\t', v)
        results_list.append(results)
    results_all={'filename':filedir, 'num_points':get_points_num(filedir), 'peak_value':coords.max()}
    for idx, results in enumerate(results_list):
        for k, v in results.items(): results_all['R'+str(idx)+'_'+k] = v
    
    return results_all


if __name__ == '__main__':
    """
    # ford
    python test_gpcc.py --dataset='./testdata/'
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--dataset", default='./testdata/')
    parser.add_argument("--outdir", default='./output')
    parser.add_argument("--resolution", type=int, default=30000)
    parser.add_argument("--resultdir", default='./csvfiles')
    parser.add_argument("--prefix", default='test')
    args = parser.parse_args()
    args.outdir = os.path.join(args.outdir, args.prefix)
    os.makedirs(args.outdir, exist_ok=True)
    os.makedirs(args.resultdir, exist_ok=True)

    # load dataset
    filedir_list = sorted(glob.glob(os.path.join(args.dataset,'**', f'*.bin'), recursive=True)) \
                + sorted(glob.glob(os.path.join(args.dataset,'**', f'*.ply'), recursive=True))
    # test 
    posQuantscale_list = np.array([1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128, 1/256, 1/512])

    for idx_file, filedir in enumerate(tqdm(filedir_list)):
        print('='*8, idx_file, filedir, '='*8)
        assert os.path.exists(filedir)
        results = test_multi_rates(filedir=filedir, outdir=args.outdir, 
                                posQuantscale_list=posQuantscale_list, resolution=args.resolution)
        results = pd.DataFrame([results])
        if idx_file==0: all_results = results.copy(deep=True)
        else: all_results = all_results.append(results, ignore_index=True)
        csvfile = os.path.join(args.resultdir, args.prefix+'_data'+str(len(filedir_list))+'_rates'+str(len(posQuantscale_list))+'.csv')        
        all_results.to_csv(csvfile, index=False)
    print('save results to ', csvfile)
    print(all_results.mean())
