py-caption
==========

`py-caption` is a caption reading/writing module.

Turn a caption into multiple caption outputs:

    srt_caps = '''1
    00:00:09,209 --> 00:00:12,312
    ( clock ticking )
    '''
    
    caps = SRTReader().read(srt_caps)
    sami = SAMIWriter().write(caps)
    dfxp = DFXPWriter().write(caps)
    transcript = TranscriptWriter().write(caps)
    
Not sure what format the caption is in? Detect it:

    if SRTReader().detect(caps):
        sami = SAMIWriter().write(SRTReader().read(caps))
    elif DFXPReader().detect(caps):
        sami = SAMIWriter().write(DFXPReader().read(caps))
    elif SCCReader().detect(caps):
        sami = SAMIWriter().write(SCCReader().read(caps))


Supported Formats
-----------------

Read:
 - SCC
 - SRT
 - SAMI
 - DFXP

Write:
 - Transcript
 - SRT
 - SAMI
 - DFXP

Python Usage
------------

After installing nltk, the appropriate Punkt tokenizer info must be downloaded.    

Example: Convert from SAMI to DFXP

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

Which will output the following:

    <?xml version="1.0" encoding="utf-8"?>
    <tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml">
     <head>
      <styling xmlns:tts="http://www.w3.org/ns/ttml#styling">
       <style id="p" tts:color="#fff" tts:fontfamily="Arial" tts:fontsize="10pt" tts:textAlign="center"/>
      </styling>
     </head>
     <body id="p">
      <div xml:lang="fr-cc">
       <p begin="00:00:09.209" end="00:00:14.848">
        FRENCH LINE 1!
       </p>
       <p begin="00:00:14.848" end="00:00:18.848">
        FRENCH LINE 2?
       </p>
      </div>
      <div xml:lang="en-US">
       <p begin="00:00:09.209" end="00:00:12.312">
        ( clock ticking )
       </p>
       <p begin="00:00:14.848" end="00:00:18.848">
        MAN:<br/>
        <span tts:textAlign="center" tts:fontsize="10">When <span tts:fontStyle="italic">we</span> think</span><br/>
        of E equals m c-squared,
       </p>
      </div>
     </body>
    </tt>

License
-------

The python code is Copyright 2012 PBS.org and is available under the [Apache License, Version 2.0][1].

[1]: http://www.apache.org/licenses/LICENSE-2.0