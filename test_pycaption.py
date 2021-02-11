
from pycaption import SCCReader
from pycaption import WebVTTWriter
from pycaption import SCCWriter
from pycaption import CaptionConverter
from pycaption import TechnoleadsReader

from pprint import pprint

# file=open('journal.scc','r') 
# scc_content = data=file.read()



# pycaps = SCCReader().read(scc_content, lang='fr')

# converter = CaptionConverter()
# converter.read(scc_content, SCCReader())
# print (converter.write(SCCWriter()))
# print (converter.write(WebVTTWriter()))

# pprint(pycaps)



file=open('conseiller_Le_GA00120742_MF0HP.txt','r', encoding='iso-8859-1') 
technoleads_content = data = file.read()
converter = CaptionConverter()
converter.read(technoleads_content, TechnoleadsReader(lang='fr'))
# print (converter.write(WebVTTWriter()))
print (converter.write(SCCWriter()))