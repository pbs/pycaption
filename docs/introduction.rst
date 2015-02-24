Introduction
============

``pycaption`` is a caption reading/writing module. Use one of the given
Readers to read content into a CaptionSet object,
and then use one of the Writers to output the CaptionSet into
captions of your desired format.

Requires Python 2.7.

Turn a caption into multiple caption outputs:

::

    srt_caps = u'''1
    00:00:09,209 --> 00:00:12,312
    This is an example SRT file,
    which, while extremely short,
    is still a valid SRT file.
    '''

    converter = CaptionConverter()
    converter.read(srt_caps, SRTReader())
    print converter.write(SAMIWriter())
    print converter.write(DFXPWriter())
    print converter.write(pycaption.transcript.TranscriptWriter())

Not sure what format the caption is in? Detect it:

::

    from pycaption import detect_format

    caps = u'''1
    00:00:01,500 --> 00:00:12,345
    Small caption'''

    reader = detect_format(caps)
    if reader:
        print SAMIWriter().write(reader().read(caps))

Or if you expect to have only a subset of the supported input formats:

::

    caps = u'''1
    00:00:01,500 --> 00:00:12,345
    Small caption'''

    if SRTReader().detect(caps):
        print SAMIWriter().write(SRTReader().read(caps))
    elif DFXPReader().detect(caps):
        print SAMIWriter().write(DFXPReader().read(caps))
    elif SCCReader().detect(caps):
        print SAMIWriter().write(SCCReader().read(caps))

Python Usage
------------

Example: Convert from SAMI to DFXP

::

    from pycaption import SAMIReader, DFXPWriter

    sami = u'''<SAMI><HEAD><TITLE>NOVA3213</TITLE><STYLE TYPE="text/css">
    <!--
    P { margin-left:  1pt;
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

::

    <?xml version="1.0" encoding="utf-8"?>
    <tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
     <head>
      <styling>
       <style id="p" tts:color="#fff" tts:fontfamily="Arial" tts:fontsize="10pt" tts:textAlign="center"/>
      </styling>
     </head>
     <body>
      <div xml:lang="fr-cc">
       <p begin="00:00:09.209" end="00:00:14.848" style="p">
        FRENCH LINE 1!
       </p>
       <p begin="00:00:14.848" end="00:00:18.848" style="p">
        FRENCH LINE 2?
       </p>
      </div>
      <div xml:lang="en-US">
       <p begin="00:00:09.209" end="00:00:12.312" style="p">
        ( clock ticking )
       </p>
       <p begin="00:00:14.848" end="00:00:18.848" style="p">
        MAN:<br/>
        <span tts:fontsize="10" tts:textAlign="center">When</span> <span tts:fontStyle="italic">we</span> think<br/>
        of E equals m c-squared,
       </p>
      </div>
     </body>
    </tt>