py-caption
==========

|Build Status|

``pycaption`` is a caption reading/writing module. Use one of the given
Readers to read content into a CaptionSet object,
and then use one of the Writers to output the CaptionSet into
captions of your desired format.

Turn a caption into multiple caption outputs:

::

    srt_caps = '''1
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

    caps = '''1
    00:00:01,500 --> 00:00:12,345
    Small caption'''

    reader = detect_format(caps)
    if reader:
        print SAMIWriter().write(reader().read(caps))

Or if you expect to have only a subset of the supported input formats:

::

    caps = '''1
    00:00:01,500 --> 00:00:12,345
    Small caption'''

    if SRTReader().detect(caps):
        print SAMIWriter().write(SRTReader().read(caps))
    elif DFXPReader().detect(caps):
        print SAMIWriter().write(DFXPReader().read(caps))
    elif SCCReader().detect(caps):
        print SAMIWriter().write(SCCReader().read(caps))

Supported Formats
-----------------

Read: - DFXP/TTML - SAMI - SCC - SRT - WebVTT

Write: - DFXP/TTML - SAMI - SRT - Transcript - WebVTT

See the `examples
folder <https://github.com/pbs/pycaption/tree/master/examples/>`__ for
example captions that currently can be read correctly.

Python Usage
------------

Example: Convert from SAMI to DFXP

::

    from pycaption import SAMIReader, DFXPWriter

    sami = '''<SAMI><HEAD><TITLE>NOVA3213</TITLE><STYLE TYPE="text/css">
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

Extensibility
-------------

Different readers and writers are easy to add if you would like to: -
Read/Write a previously unsupported format - Read/Write a supported
format in a different way (more styling?)

Simply follow the format of a current Reader or Writer, and edit to your
heart's desire.

SAMI Reader / Writer :: `spec <http://msdn.microsoft.com/en-us/library/ms971327.aspx>`__
----------------------------------------------------------------------------------------

Microsoft Synchronized Accessible Media Interchange. Supports multiple
languages.

Supported Styling: - text-align - italics - font-size - font-family -
color

If the SAMI file is not valid XML (e.g. unclosed tags), will still
attempt to read it.

DFXP/TTML Reader / Writer :: `spec <http://www.w3.org/TR/ttaf1-dfxp/>`__
-------------------------------------------------------------------

The W3 standard. Supports multiple languages.

Supported Styling: - text-align - italics - font-size - font-family -
color

SRT Reader / Writer :: `spec <http://matroska.org/technical/specs/subtitles/srt.html>`__
----------------------------------------------------------------------------------------

SubRip captions. If given multiple languages to write, will output all
joined together by a 'MULTI-LANGUAGE SRT' line.

Supported Styling: - None

Assumes input language is english. To change:

::

    pycaps = SRTReader().read(srt_content, lang='fr')

SCC Reader :: `spec <http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/SCC_FORMAT.HTML>`__
-----------------------------------------------------------------------------------------------

Scenarist Closed Caption format. Assumes Channel 1 input.

Supported Styling: - italics

By default, the SCC Reader does not simulate roll-up captions. To enable
roll-ups:

::

    pycaps = SCCReader().read(scc_content, simulate_roll_up=True)

Also, assumes input language is english. To change:

::

    pycaps = SCCReader().read(scc_content, lang='fr')

Now has the option of specifying an offset (measured in seconds) for the
timestamp. For example, if the SCC file is 45 seconds ahead of the
video:

::

    pycaps = SCCReader().read(scc_content, offset=45)

The SCC Reader handles both dropframe and non-dropframe captions, and
will auto-detect which format the captions are in.

Transcript Writer
-----------------

Text stripped of styling, arranged in sentences.

Supported Styling: - None

The transcript writer uses natural sentence boundary detection
algorithms to create the transcript.

WebVTT Reader / Writer `spec <http://dev.w3.org/html5/webvtt/>`__
-----------------------------------------------------------------

Web Video Text Tracks format.

Supported Styling - None (yet)


License
-------

This module is Copyright 2012 PBS.org and is available under the `Apache
License, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0>`__.

.. |Build Status| image:: https://travis-ci.org/pbs/pycaption.png?branch=master
   :target: https://travis-ci.org/pbs/pycaption
