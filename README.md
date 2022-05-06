This is a python script to test G-PCC.

## usage
python test_gpcc.py --dataset='./testdata/'

### Dataset 
Now we only test KITTI sequences.

### Quantization

The raw KITTI point clouds are float32 numbers. In the testing, we quantize raw points to **1mm** by multiplying by **1000**, following the settings for Ford squences in G-PCC CTC. 
Other quantification methods lke 16 bits, 12 bits, etc, are also available. But different quantization strategies have a large impact on the bitrates, for example, the comparison of 1mm and 16 bits quantizeion can be found in `plot.ipynb`
Details can be found in `quantize.py`

### G-PCC cfg

We set 'positionQuantizationScale' to 1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128, 1/256, 1/512 to obtain 10 bitrate points, Other parameters are set to default values.
Details can be found in `gpcc.py`

### pc error
We set resolution to 30000, following the settings for Ford squences in G-PCC CTC.
Details can be found in `pc_error.py`



