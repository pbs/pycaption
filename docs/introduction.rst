Introduction
============

``pycaption`` is a caption reading/writing module. Use a Reader to parse
captions into a ``CaptionSet``, then use a Writer to output them in any
supported format.

Supported formats:

- **WebVTT** — W3C standard for HTML5 ``<track>`` (styling, positioning, regions)
- **SRT** — SubRip, widely supported by media players
- **DFXP/TTML** — W3C Timed Text Markup Language (XML-based, broadcast)
- **SAMI** — Microsoft Synchronized Accessible Media Interchange
- **SCC** — Scenarist Closed Captions (CEA-608, broadcast/cable)


Quick Start
-----------

Convert any format to any other format using the ``CaptionConverter``:

::

    from pycaption import CaptionConverter, SRTReader
    from pycaption import SAMIWriter, DFXPWriter, SCCWriter, WebVTTWriter

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
    print(converter.write(SCCWriter()))
    print(converter.write(WebVTTWriter()))

WebVTT output from the example above:

::

    WEBVTT

    00:00:09.209 --> 00:00:12.312
    This is an example SRT file,
    which, while extremely short,
    is still a valid SRT file.

Or use Readers and Writers directly:

::

    from pycaption import WebVTTReader, SCCWriter, DFXPWriter, SAMIWriter

    vtt_caps = '''WEBVTT

    STYLE
    ::cue(.yellow) { color: yellow }

    00:00:01.000 --> 00:00:05.000 align:center line:80%
    <b>Hello</b> <c.yellow>world</c>
    '''

    caption_set = WebVTTReader().read(vtt_caps)
    print(SCCWriter().write(caption_set))
    print(DFXPWriter().write(caption_set))
    print(SAMIWriter().write(caption_set))

DFXP output from the example above:

::

    <?xml version="1.0" encoding="utf-8"?>
    <tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
     <head>
      <styling>
       <style tts:color="yellow" xml:id="yellow"/>
      </styling>
      <layout>
       <region tts:displayAlign="after" tts:textAlign="start" xml:id="bottom"/>
       <region tts:extent="90% 15%" tts:origin="0% 80%" tts:textAlign="center" xml:id="r0"/>
      </layout>
     </head>
     <body>
      <div region="bottom" xml:lang="en-US">
       <p begin="00:00:01.000" end="00:00:05.000" region="r0">
        <span tts:fontWeight="bold">Hello</span>  <span tts:color="yellow">world</span>
       </p>
      </div>
     </body>
    </tt>


Format Detection
----------------

Auto-detect the input format:

::

    from pycaption import detect_format, SAMIWriter

    caps = '''1
    00:00:01,500 --> 00:00:12,345
    Small caption'''

    reader = detect_format(caps)
    if reader:
        print(SAMIWriter().write(reader().read(caps)))

Or check specific formats:

::

    from pycaption import SRTReader, DFXPReader, SCCReader, WebVTTReader, SAMIWriter

    caps = '''1
    00:00:01,500 --> 00:00:12,345
    Small caption'''

    if SRTReader().detect(caps):
        print(SAMIWriter().write(SRTReader().read(caps)))
    elif DFXPReader().detect(caps):
        print(SAMIWriter().write(DFXPReader().read(caps)))
    elif SCCReader().detect(caps):
        print(SAMIWriter().write(SCCReader().read(caps)))
    elif WebVTTReader().detect(caps):
        print(SAMIWriter().write(WebVTTReader().read(caps)))


Conversion Examples
-------------------

WebVTT to SCC
~~~~~~~~~~~~~

VTT positioning maps to CEA-608 row/column codes:

::

    from pycaption import WebVTTReader, SCCWriter

    vtt_caps = '''WEBVTT

    00:00:01.000 --> 00:00:04.000 align:center line:80%
    Hello world

    00:00:05.000 --> 00:00:08.000 line:20%
    Top positioned caption

    00:00:09.000 --> 00:00:12.000
    MAN: This is a test.
    '''

    caption_set = WebVTTReader().read(vtt_caps)
    print(SCCWriter().write(caption_set))

Output:

::

    Scenarist_SCC V1.0

    00:00:00:11	94ae 94ae 9420 9420 13f4 13f4 97a2 97a2 c8e5 ecec ef20 f7ef f2ec 6480 942c 942c 942f 942f

    00:00:03:29	942c 942c

    00:00:04:08	94ae 94ae 9420 9420 9240 9240 54ef 7020 70ef 73e9 f4e9 ef6e e564 20e3 6170 f4e9 ef6e 942c 942c 942f 942f

    00:00:07:29	942c 942c

    00:00:08:09	94ae 94ae 9420 9420 94e0 94e0 cdc1 ceba 2054 68e9 7320 e973 2061 20f4 e573 f4ae 942c 942c 942f 942f

    00:00:11:29	942c 942c

``line:80%`` maps to row 13 (near bottom), ``line:20%`` to row 4 (near top).
Timestamps shift slightly earlier to account for decoder buffer fill time.


SCC to WebVTT
~~~~~~~~~~~~~

::

    from pycaption import SCCReader, WebVTTWriter

    scc_caps = '''Scenarist_SCC V1.0


    00:00:09:05\t94ae 94ae 9420 9420 9470 9470 a820 e3ec efe3 6b20 f4e9 e36b e96e 6720 2980 942c 942c 942f 942f

    00:00:12:08\t942c 942c

    00:00:14:24\t94ae 94ae 9420 9420 9470 9470 cdc1 ceba 942c 942c 942f 942f
    '''

    caption_set = SCCReader().read(scc_caps)
    print(WebVTTWriter().write(caption_set))

Output:

::

    WEBVTT

    00:00:09.743 --> 00:00:12.278 align:left position:10% line:89% size:80%
    ( clock ticking )

    00:00:15.148 --> 00:00:19.148 align:left position:10% line:89% size:80%
    MAN:

CEA-608 row 15 maps to ``line:89%``, and column 0 maps to ``position:10%``.
The SCC pop-on timing is converted to absolute start/end timestamps.


SAMI to DFXP
~~~~~~~~~~~~~

Multi-language SAMI with inline styles:

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

    print(DFXPWriter().write(SAMIReader().read(sami)))

Output:

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

If no language is detected, set a default via environment variable.
Without it, pycaption uses ``'und'`` (undetermined, per ISO 639-2).

::

   PYCAPTION_DEFAULT_LANG = "en-US"


Positioning
-----------

Caption formats support varying levels of positioning. PyCaption preserves
positioning when possible, applying adjustments to ensure captions display
correctly across formats.

.. py:class:: BaseWriter(relativize=True, video_width=None, video_height=None, fit_to_screen=True)

    :param relativize: If True (default), converts absolute positioning
            values (e.g. px) to percentages. Required for WebVTT output
            (which does not support absolute units).
    :param video_width: Reference video width for px-to-percentage conversion.
    :param video_height: Reference video height for px-to-percentage conversion.
    :param fit_to_screen: If True (default), clamps extent so regions stay
            within the visible area (origin + extent <= 90% horizontal,
            <= 95% vertical).

DFXP to WebVTT (with relativization)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    from pycaption import DFXPReader, WebVTTWriter

    dfxp = u"""<?xml version="1.0" encoding="utf-8"?>
    <tt xml:lang="en-us"
        xmlns="http://www.w3.org/ns/ttml"
        xmlns:tts='http://www.w3.org/ns/ttml#styling'>
    <head>
        <layout>
            <region xml:id="fourthQuadrant" tts:textAlign='left'
                    tts:origin='320px 180px' tts:extent='320px 180px'/>
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
    print(WebVTTWriter(video_width=640, video_height=360).write(caption_set))

Output:

::

    WEBVTT

    00:00:01.000 --> 00:00:03.000 align:left position:50%,start line:50% size:50%
    I'm in the fourth quadrant!

Pixel values are converted to percentages using the given video dimensions.
Without ``video_width``/``video_height``, pixel-based input raises
``RelativizationError``.


DFXP to DFXP (fit-to-screen)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    from pycaption import DFXPReader, DFXPWriter

    dfxp = u"""<?xml version="1.0" encoding="utf-8"?>
    <tt xml:lang="en-us"
        xmlns="http://www.w3.org/ns/ttml"
        xmlns:tts='http://www.w3.org/ns/ttml#styling'>
    <head>
        <layout>
            <region xml:id="invalidRegion" tts:textAlign='left'
                    tts:origin='360px 180px' tts:extent='420px 240px'/>
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

This input is syntactically valid but has two problems:

#. Absolute pixel positioning doesn't scale across resolutions.
#. At 640x360, origin + extent overflows the screen, cropping long text.

Writer behavior with different settings:

::

    >>> DFXPWriter().write(caption_set)
    # raises RelativizationError (px values need video dimensions)

    >>> DFXPWriter(relativize=False, fit_to_screen=False).write(caption_set)
    # passes through px values unchanged (may overflow)

    >>> DFXPWriter(video_width=640, video_height=360, fit_to_screen=False).write(caption_set)
    # relativizes but does NOT clamp (origin 56.25% + extent 65.63% > 90%)

    >>> DFXPWriter(video_width=640, video_height=360).write(caption_set)
    # relativizes AND clamps — output below:

Output with ``fit_to_screen=True`` (default):

::

    <?xml version="1.0" encoding="utf-8"?>
    <tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
     <head>
      <styling>
       <style tts:color="white" tts:fontFamily="monospace" tts:fontSize="1c" xml:id="default"/>
      </styling>
      <layout>
       <region tts:displayAlign="after" tts:extent="420px 240px" tts:origin="360px 180px" tts:textAlign="left" xml:id="r0"/>
       <region tts:displayAlign="after" tts:extent="33.75% 45%" tts:origin="56.25% 50%" tts:textAlign="left" xml:id="r1"/>
      </layout>
     </head>
     <body>
      <div region="r0" xml:lang="en-us">
       <p begin="00:00:01.000" end="00:00:03.000" region="r1" style="default">
        I'm a long caption and I'm cropped by the right side of the screen.
       </p>
      </div>
     </body>
    </tt>

The caption uses region ``r1`` (clamped: 56.25% + 33.75% = 90%) instead of
the overflowing original. The output is guaranteed to stay within the visible
region.
