import numpy as np
import os, glob, argparse
from tqdm import tqdm
import pandas as pd
from data_io import read_bin, read_ply, write_ply
from quantization import quantize_precision, quantize_resolution
from gpcc import gpcc_encode, gpcc_decode, print_log
from pc_error import pc_error


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

def test_one(filedir, bin_dir, out_dir, posQuantscale, DBG=False):
    enc_log = gpcc_encode(filedir, bin_dir, posQuantscale=posQuantscale)
    if DBG: print_log(enc_log)
    dec_log = gpcc_decode(bin_dir, out_dir)
    if DBG: print_log(dec_log)
    # bpp
    in_points_num = get_points_num(filedir)
    out_points_num = get_points_num(out_dir)
    file_size = os.path.getsize(bin_dir)*8
    bpp = round(file_size/in_points_num, 6)
    # results
    results={'filename':out_dir, 'posQuantscale':posQuantscale, 
            'num_points':out_points_num, 'file_size':file_size, 'bpp':bpp}
    metric_log, metric_results = pc_error(filedir, out_dir, resolution=30000, test_d2=args.test_d2)
    if DBG: print_log(metric_log)
    results.update(metric_results)

    print('DBG!!!', results)

    return results

def test_all(filedir, posQuantscale_list):
    filename = os.path.split(filedir)[-1].split('.')[0]
    filename = os.path.join(args.outdir, filename)
    # test
    results_list = []
    for idx_rate, posQuantscale in enumerate(posQuantscale_list):
        bin_dir = filename + '_R'+str(idx_rate) + '.bin'
        out_dir = filename + '_R'+str(idx_rate) + '_dec.ply'
        results = test_one(filedir, bin_dir, out_dir, posQuantscale)
        results_list.append(results)
    results_all={'filename':filedir, 'num_points':get_points_num(filedir)}
    for idx, results in enumerate(results_list):
        for k, v in results.items(): results_all['R'+str(idx)+'_'+k] = v
    
    return results_all

def quantize(filedir, quant_mode='precision', precision=0.001, resolution=65525):
    if filedir.endswith('ply'): points = read_ply(filedir)
    elif filedir.endswith('bin'): points = read_bin(filedir)
    if quant_mode=='precision':
        pointsQ = quantize_precision(points.copy(), precision=precision)
    elif quant_mode=='resolution':
        pointsQ = quantize_resolution(points.copy(), resolution=resolution)
    pointsQ = np.unique(pointsQ, axis=0)
    filename = os.path.split(filedir)[-1].split('.')[0]
    filedirQ = os.path.join(args.outdir, filename+'_q.ply')
    if not args.test_d2:
        write_ply(filedirQ, pointsQ)
    else:
        import point_cloud_utils as pcu # pip install point_cloud_utils
        _, normal = pcu.estimate_point_cloud_normals_knn(pointsQ.astype('float32'), 16)
        write_ply(filedirQ, pointsQ, normal=normal)

        # write_ply_o3d(filedirQ, pointsQ, normal=True, knn=16)

    print('quantize '+filedir+' to '+filedirQ)

    return filedirQ

    return 
if __name__ == '__main__':
    """
    python test_kitti.py --dataset='./testdata/' --mode='lossless' --prefix='lossless'
    python test_kitti.py --dataset='./testdata/' --mode='lossy' --prefix='lossy'
    python test_kitti.py --dataset='./testdata/' --mode='lossy' --test_d2 --prefix='lossy'
    python test_kitti.py --dataset='./testdata/' --mode='lossy' --quant_mode='resolution' --test_d2 --prefix='lossy_q16bit'
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--mode", default="lossless")
    parser.add_argument("--quant_mode", default="precision")
    parser.add_argument("--dataset", default='./testdata/')
    parser.add_argument("--outdir", default='./output')
    parser.add_argument("--resultdir", default='./csvfiles')
    parser.add_argument("--prefix", default='test')
    parser.add_argument("--test_d2", action="store_true", help="test d2 or not.")
    args = parser.parse_args()
    args.outdir = os.path.join(args.outdir, args.prefix)
    os.makedirs(args.outdir, exist_ok=True)
    os.makedirs(args.resultdir, exist_ok=True)

    # load dataset
    filedir_list = sorted(glob.glob(os.path.join(args.dataset,'**', f'*.bin'), recursive=True)) \
                + sorted(glob.glob(os.path.join(args.dataset,'**', f'*.ply'), recursive=True))
    # test conditions 
    if args.mode=='lossless':
        posQuantscale_list = [1]
    elif args.mode=='lossy':
        posQuantscale_list = np.array([0.25, 0.125, 0.03125, 0.015625, 0.00390625, 0.001953125])
    # test
    for idx_file, filedir in enumerate(tqdm(filedir_list)):
        print('='*8, idx_file, filedir, '='*8)
        assert os.path.exists(filedir)
        # quantize
        filedir = quantize(filedir, quant_mode=args.quant_mode)
        # test
        results = test_all(filedir=filedir, posQuantscale_list=posQuantscale_list)
        results = pd.DataFrame([results])
        if idx_file==0: all_results = results.copy(deep=True)
        else: all_results = all_results.append(results, ignore_index=True)
        csvfile = os.path.join(args.resultdir, args.prefix+'.csv')        
        all_results.to_csv(csvfile, index=False)
    print('save results to ', csvfile)
    print(all_results.mean())
