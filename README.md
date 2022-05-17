This is a python script to test G-PCC. Now we only test KITTI sequences.

## usage
chmod 777 tmc3 pc_error_d

python test_kitti.py --dataset='./testdata/' --mode='lossless' --prefix='lossless'
python test_kitti.py --dataset='./testdata/' --mode='lossy' --prefix='lossy'
python test_kitti.py --dataset='./testdata/' --mode='lossy' --test_d2 --prefix='lossy'


### Quantization

The raw KITTI point clouds are float32 numbers. In the testing, we quantize raw points to **1mm** by multiplying by **1000**, following the settings for Ford squences in G-PCC CTC. Other quantification methods lke 16 bits, 12 bits, etc, are also available.

Details can be found in `quantize.py`

### G-PCC cfg

We set 'positionQuantizationScale' to [0.25, 0.125, 0.03125, 0.015625, 0.00390625, 0.001953125] to obtain 6 bitrate points, Other parameters are set to default values, 

Details can be found in `gpcc.py` and `encoder.cfg`

### pc error
We set resolution to 30000, following the settings for Ford squences in G-PCC CTC.
Details can be found in `pc_error.py`

## Update
202205017: add d2 psnr; add config file.