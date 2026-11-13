import io, ssl, urllib.request, zipfile, os
CA = '/root/.ccr/ca-bundle.crt'
CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
class RangeIO(io.RawIOBase):
    def __init__(self, url, size, block=4 << 20):
        self.url, self.size, self.block = url, size, block
        self.pos = 0; self.cache = {}
    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.pos
    def seek(self, off, whence=0):
        if whence == 0: self.pos = off
        elif whence == 1: self.pos += off
        else: self.pos = self.size + off
        return self.pos
    def _get(self, start, end):
        req = urllib.request.Request(self.url, headers={'Range': f'bytes={start}-{end}'})
        with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
            return r.read()
    def read(self, n=-1):
        if n is None or n < 0: n = self.size - self.pos
        out = bytearray()
        while n > 0 and self.pos < self.size:
            bi = self.pos // self.block
            if bi not in self.cache:
                s = bi * self.block; e = min(s + self.block, self.size) - 1
                self.cache[bi] = self._get(s, e)
                if len(self.cache) > 8:
                    for k in list(self.cache):
                        if k != bi: self.cache.pop(k); break
            blk = self.cache[bi]
            off = self.pos - bi * self.block
            chunk = blk[off:off + n]
            if not chunk: break
            out += chunk; self.pos += len(chunk); n -= len(chunk)
        return bytes(out)
    def readinto(self, b):
        data = self.read(len(b)); b[:len(data)] = data; return len(data)
def open_zip(url):
    import urllib.request as ur
    req = ur.Request(url, method='HEAD')
    with ur.urlopen(req, context=CTX, timeout=60) as r:
        size = int(r.headers['Content-Length'])
    return zipfile.ZipFile(io.BufferedReader(RangeIO(url, size), buffer_size=1 << 20)), size
