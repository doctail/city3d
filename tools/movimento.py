import sys, subprocess, numpy as np, json
f=sys.argv[1]; W,H=160,90
raw=subprocess.run(['ffmpeg','-loglevel','error','-i',f,'-vf',f'fps=2,scale={W}:{H},format=gray','-f','rawvideo','-'],capture_output=True).stdout
a=np.frombuffer(raw,np.uint8).reshape(-1,H,W).astype(np.float32)
d=np.abs(a[1:]-a[:-1]).mean(axis=(1,2))   # change per half-second
br=a.mean(axis=(1,2)); sd=a.std(axis=(1,2))
json.dump({'d':d.round(2).tolist(),'br':br.round(1).tolist(),'sd':sd.round(1).tolist()},open(sys.argv[2],'w'))
print(f, len(a)/2,'s', 'change mean %.2f median %.2f p90 %.2f'%(d.mean(),np.median(d),np.percentile(d,90)), 'contrast(sd) %.1f'%sd.mean())
