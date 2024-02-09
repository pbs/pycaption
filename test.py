
from pycaption.srt import SRTReader
from pycaption.scenarist import ScenaristDVDWriter


srtReader = SRTReader()
c = srtReader.read(content=open("a.srt", "rb").read().decode('UTF-8-SIG'), lang='zh-Hans')
w = ScenaristDVDWriter()
w.write(c)
