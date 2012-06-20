After installing nltk, the appropriate Punkt tokenizer info must be downloaded.

Suggested usage:

from pycaption.sami import SAMIReader
from pycaption.dfxp import DFXPWriter

sami = '''<SAMI><HEAD><TITLE>NOVA3213</TITLE><STYLE TYPE="text/css">
<!--
P {	margin-left:  1pt;
    margin-right: 1pt;
    margin-bottom: 2pt;
    margin-top: 2pt;
    text-align: center;
    font-size: 10pt;
    font-family: Arial;
    font-weight: normal;
    font-style: normal;
    color: #ffffff; }

.ENCC {Name: English; lang: en-US; SAMI_Type: CC;}
.FRCC {Name: French; lang: fr-cc; SAMI_Type: CC;}

--></STYLE></HEAD><BODY>
<SYNC start="9209"><P class="ENCC">
       ( clock ticking )
</P><P class="FRCC">
       FRENCH LINE 1!
</P></SYNC>
<SYNC start="12312"><P class="ENCC">&nbsp;</P></SYNC>
<SYNC start="14848"><P class="ENCC">
              MAN:<br/>
         <span style="text-align:center;font-size:10">When <i>we</i> think</span><br/>
    of E equals m c-squared,
</P><P class="FRCC">
       FRENCH LINE 2?
</P></SYNC>'''


print DFXPWriter().write(SAMIReader().read(sami))