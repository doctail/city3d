import sys, numpy as np
from PIL import Image
a=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int); b=np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(int)
d=np.abs(a-b).max(axis=2); print(sys.argv[2].split('/')[-1], a.shape==b.shape, 'mean %.2f'%np.abs(a-b).mean(), '%%>8 %.2f'%(100*(d>8).mean()), '%%>30 %.2f'%(100*(d>30).mean()))
