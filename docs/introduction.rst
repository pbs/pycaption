Introduction
============

``pycaption`` is a caption reading/writing module. Use one of the given
Readers to read content into a CaptionSet object,
and then use one of the Writers to output the CaptionSet into
captions of your desired format.

Requires Python 3.6.

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
    print(converter.write(SAMIWriter()))
    print(converter.write(DFXPWriter()))
    print(converter.write(pycaption.transcript.TranscriptWriter()))
    print(converter.write(MicroDVDWriter()))

Not sure what format the caption is in? Detect it:

::

    from pycaption import detect_format

    caps = '''1
    00:00:01,500 --> 00:00:12,345
    Small caption'''

    reader = detect_format(caps)
    if reader:
        print(SAMIWriter().write(reader().read(caps)))

Or if you expect to have only a subset of the supported input formats:

::

    caps = '''1
    00:00:01,500 --> 00:00:12,345
    Small caption'''

    if SRTReader().detect(caps):
        print(SAMIWriter().write(SRTReader().read(caps)))
    elif DFXPReader().detect(caps):
        print(SAMIWriter().write(DFXPReader().read(caps)))
    elif SCCReader().detect(caps):
        print(SAMIWriter().write(SCCReader().read(caps)))
    elif MicroDVDReader().detect(caps)
        print(SAMIWriter().write(MicroDVDReader().read(caps)))

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

Default Language
----------------

If language is not detected you can set a default one in your environment.
If there is no default language we use 'und' ( a special identifier for an undetermined language according to ISO 639-2 )

::

   PYCAPTION_DEFAULT_LANG = "en-US"



Positioning
-----------

Some caption formats support positioning information and PyCaption tries to preserve it when possible. In the process, some adjustments are made. Some of these adjustments can be customized by properly initializing the Writer class.

.. py:class:: BaseWriter(relativize=True, video_width=None, video_height=None, fit_to_screen=True)

    :param relativize: If True (default), converts absolute positioning
            values (e.g. px) to percentage. ATTENTION: WebVTT does not support
            absolute positioning. If relativize is set to False and it finds
            an absolute positioning parameter for a given caption, it will
            ignore all positioning for that cue and show it in the default
            position.
    :param video_width: The width of the video for which the captions being
            converted were made. This is necessary for relativization.
    :param video_height: The height of the video for which the captions
            being converted were made. This is necessary for relativization.
    :param fit_to_screen: If extent is not set or if origin + extent > 100%,
            (re)calculate it based on origin. It is a pycaption fix for caption
            files that are technically valid but contains inconsistent settings
            that may cause long captions to be cut out of the screen.

Examples
~~~~~~~~

* DFXP to WebVTT

::

    from pycaption import DFXPReader, WebVTTWriter
    dfxp = u"""<?xml version="1.0" encoding="utf-8"?>
    <tt xml:lang="en-us"
        xmlns="http://www.w3.org/ns/ttml"
        xmlns:tts='http://www.w3.org/ns/ttml#styling'
        >
    <head>
        <layout>
            <region xml:id="fourthQuadrant" tts:textAlign='left' tts:origin='320px 180px' tts:extent='320px 180px'/>
        </layout>
    </head>
    <body>
        <div>
            <p region="fourthQuadrant" begin='00:00:01.000' end='00:00:03.000'>
            I'm in the fourth quadrant!
            </p>
        </div>
    </body>
    </tt>"""
    caption_set = DFXPReader().read(dfxp)
    print WebVTTWriter(video_width=640, video_height=360).write(caption_set)

The code above should output:

::

    WEBVTT

    00:01.000 --> 00:03.000 align:left position:50%,start line:50% size:50%
    I'm in the fourth quadrant!

Note that px values were converted to percentages. This can only be done if
a reference such as video_width or height are sent as parameters based on which
we can calculate the relative values. If the WebVTTWriter is initialized without
them and the input file contains px values, when the `.write` method is called,
it will raise `RelativizationError`.

* DFXP to DFXP

::

    from pycaption import DFXPReader, DFXPWriter
    dfxp = u"""<?xml version="1.0" encoding="utf-8"?>
    <tt xml:lang="en-us"
        xmlns="http://www.w3.org/ns/ttml"
        xmlns:tts='http://www.w3.org/ns/ttml#styling'
        >
    <head>
        <layout>
            <region xml:id="invalidRegion" tts:textAlign='left' tts:origin='360px 180px' tts:extent='420px 240px'/>
        </layout>
    </head>
    <body>
        <div>
            <p region="invalidRegion" begin='00:00:01.000' end='00:00:03.000'>
            I'm a long caption and I'm cropped by the right side of the screen.
            </p>
        </div>
    </body>
    </tt>"""
    caption_set = DFXPReader().read(dfxp)

This input is syntactically valid but presents two problems:

#. Positioning relies on absolute values (px). In systems that ingest one video
   and an associated caption file and outputs several formats for different
   platforms, this is a problem. A caption shifted 960px to the left in a 1920x1080
   video, for example, disappears in a 640x360 one.
#. Assuming a 640x360 resolution, the positioning specified above results in an
   overflowing cue box which in turn results in cropped content when the caption
   text is long enough.

Here are some examples of Writer initialization:

::

    >>> print DFXPWriter().write(caption_set)
    RelativizationError: At least one of video width or height must be given as a reference

    >>> print DFXPWriter(relativize=False).write(caption_set)
    ValueError: Units must be relativized before extent can be calculated based on origin.

    >>> print DFXPWriter(relativize=False, fit_to_screen=False).write(caption_set)
    <?xml version="1.0" encoding="utf-8"?>
    <tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
     <head>
      <styling>
       <style tts:color="white" tts:fontFamily="monospace" tts:fontSize="1c" xml:id="default"/>
      </styling>
      <layout>
       <region tts:displayAlign="after" tts:extent="420px 240px" tts:origin="360px 180px" tts:textAlign="left" xml:id="r0"/>
      </layout>
     </head>
     <body>
      <div region="r0" xml:lang="en-US">
       <p begin="00:00:01.000" end="00:00:03.000" region="r0" style="default">
        I'm a long caption and I'm cropped by the right side of the screen.
       </p>
      </div>
     </body>
    </tt>

    >>> print DFXPWriter(video_width=640, video_height=360, fit_to_screen=False).write(caption_set)
    <?xml version="1.0" encoding="utf-8"?>
    <tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
     <head>
      <styling>
       <style tts:color="white" tts:fontFamily="monospace" tts:fontSize="1c" xml:id="default"/>
      </styling>
      <layout>
       <region tts:displayAlign="after" tts:extent="420px 240px" tts:origin="360px 180px" tts:textAlign="left" xml:id="r0"/>
       <region tts:displayAlign="after" tts:extent="65.63% 66.67%" tts:origin="56.25% 50%" tts:textAlign="left" xml:id="r1"/>
      </layout>
     </head>
     <body>
      <div region="r0" xml:lang="en-US">
       <p begin="00:00:01.000" end="00:00:03.000" region="r1" style="default">
        I'm a long caption and I'm cropped by the right side of the screen.
       </p>
      </div>
     </body>
    </tt>

In the last example the values are relativized but ``origin + extent > 100%``, which
still results in the caption being cropped.

::


    >>> print DFXPWriter(video_width=640, video_height=360).write(caption_set)
    <?xml version="1.0" encoding="utf-8"?>
    <tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
     <head>
      <styling>
       <style tts:color="white" tts:fontFamily="monospace" tts:fontSize="1c" xml:id="default"/>
      </styling>
      <layout>
       <region tts:displayAlign="after" tts:extent="420px 240px" tts:origin="360px 180px" tts:textAlign="left" xml:id="r0"/>
       <region tts:displayAlign="after" tts:extent="43.75% 50%" tts:origin="56.25% 50%" tts:textAlign="left" xml:id="r1"/>
      </layout>
     </head>
     <body>
      <div region="r0" xml:lang="en-US">
       <p begin="00:00:01.000" end="00:00:03.000" region="r1" style="default">
        I'm a long caption and I'm cropped by the right side of the screen.
       </p>
      </div>
     </body>
    </tt>

Now the positioning is corrected and the caption is guaranteed to be within the
visible region of the screen.

**NOTE**: The region ``r0`` is still defined using absolute values. This is a bug that
should be fixed in the next release. In any case it is harmless because it is
overwritten by the relative values in ``r1``.
