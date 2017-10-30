# -*- coding: utf-8 -*-
from __future__ import unicode_literals

SAMPLE_DFXP = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="p" tts:color="#ffeedd" tts:fontFamily="Arial"
          tts:fontSize="10pt" tts:textAlign="center"/>
  </styling>
  <layout>
  <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"></region>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US" region="bottom">
   <p begin="00:00:09.209" end="00:00:12.312" region="bottom" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" region="bottom" style="p">
    MAN:<br/>
    When we think<br/>
    \u266a ...say bow, wow, \u266a
   </p>
   <p begin="00:00:17.000" end="00:00:18.752" region="bottom" style="p">
    <span tts:textalign="right">we have this vision of Einstein</span>
   </p>
   <p begin="00:00:18.752" end="00:00:20.887" region="bottom" style="p">
   <br/>
    as an old, wrinkly man<br/>
    with white hair.
   </p>
   <p begin="00:00:20.887" end="00:00:26.760" region="bottom" style="p">
    MAN 2:<br/>
    E equals m c-squared is<br/>
    not about an old Einstein.
   </p>
   <p begin="00:00:26.760" end="00:00:32.200" region="bottom" style="p">
    MAN 2:<br/>
    It's all about an eternal Einstein.
   </p>
   <p begin="00:00:32.200" end="00:00:36.200" region="bottom" style="p">
    &lt;LAUGHING &amp; WHOOPS!&gt;
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_WITH_INLINE_STYLE = """
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="p" tts:color="#ffeedd" tts:fontFamily="Arial"
          tts:fontSize="10pt" tts:textAlign="center"/>
  </styling>
  <layout>
  <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"></region>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US" region="bottom">
   <p begin="00:00:09.209" end="00:00:12.312" region="bottom" style="p">
    This is <span tts:fontstyle="italic">italic</span>, <span tts:fontweight="bold">bold
    </span>, <span tts:textdecoration="overline underline">
    underline</span>, <span tts:fontstyle="italic" tts:fontweight="bold" tts:textdecoration="underline">
    everything together in one tag</span>, and <span tts:textdecoration="underline">
    <span tts:fontweight="bold"><span tts:fontstyle="italic">nested</span></span></span>.
   </p>
  </div>
 </body>
</tt>
"""

SAMPLE_DFXP_WITH_DEFINED_STYLE = """
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="p" tts:color="#ffeedd" tts:fontFamily="Arial"
          tts:fontSize="10pt" tts:textAlign="center"/>
   <style xml:id="s1" tts:fontstyle="italic"/>
   <style xml:id="s2" tts:fontweight="bold" />
   <style xml:id="s3" tts:textdecoration="underline" />
  </styling>
  <layout>
  <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"></region>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US" region="bottom">
   <p begin="00:00:09.209" end="00:00:12.312" region="bottom" style="p">
    This is <span style="s1">italic</span>, <span style="s2">bold</span>, <span style="s3">
    underline</span>, <span style="s1 s2 s3">everything together in one tag</span>, and <span style="s3">
    <span style="s2"><span style="s1">nested</span></span></span>.
   </p>
  </div>
 </body>
</tt>
"""

SAMPLE_DFXP_WITH_INHERITED_STYLE = """
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="p" tts:color="#ffeedd" tts:fontFamily="Arial"
          tts:fontSize="10pt" tts:textAlign="center"/>
   <style xml:id="s1" tts:fontstyle="italic"/>
   <style xml:id="s2" tts:fontweight="bold" />
   <style xml:id="s3" tts:textdecoration="underline" />
   <style xml:id="inherit_s3" style="s3" />
   <style xml:id="inherit_s3_underline" style="s1" tts:textdecoration="underline" />
   <style xml:id="inherit_s3_bold" style="inherit_s3_underline" tts:fontweight="bold" />
   <style xml:id="inherit_s2" style="s2" />
   <style xml:id="inherit_s1" style="s1" />
  </styling>
  <layout>
  <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"></region>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US" region="bottom">
   <p begin="00:00:09.209" end="00:00:12.312" region="bottom" style="p">
    This is <span style="inherit_s1">italic</span>, <span style="inherit_s2">bold</span>, <span style="inherit_s3">
    underline</span>, <span style="inherit_s3_bold">everything together in one tag</span>, and <span style="inherit_s3">
    <span style="inherit_s2"><span style="inherit_s1">nested</span></span></span>.
   </p>
  </div>
 </body>
</tt>
"""

SAMPLE_DFXP_WITHOUT_REGION_AND_STYLE = """
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
 </head>
 <body>
  <div xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" region="bottom" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" region="bottom" style="p">
    MAN:<br/>
    When we think<br/>
    of "E equals m c-squared",
   </p>
   <p begin="00:00:17.000" end="00:00:18.752" region="bottom" style="p">
    <span tts:textalign="right">we have this vision of Einstein</span>
   </p>
   <p begin="00:00:18.752" end="00:00:20.887" region="bottom" style="p">
    as an old, wrinkly man<br/>
    with white hair.
   </p>
   <p begin="00:00:20.887" end="00:00:26.760" region="bottom" style="p">
    MAN 2:<br/>
    E equals m c-squared is<br/>
    not about an old Einstein.
   </p>
   <p begin="00:00:26.760" end="00:00:32.200" region="bottom" style="p">
    MAN 2:<br/>
    It's all about an eternal Einstein.
   </p>
   <p begin="00:00:32.200" end="00:00:34.400" region="bottom" style="p">
    &lt;LAUGHING &amp; WHOOPS!&gt;
   </p>
   <p begin="00:00:34.400" end="00:00:38.400" region="bottom" style="p">some more text</p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_WITH_POSITIONING = """<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en-us"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts='http://www.w3.org/ns/ttml#styling'
    >
<head>
    <styling>
        <style xml:id="padded" tts:backgroundColor="yellow" tts:padding="10%"/>
    </styling>
    <layout>
        <region xml:id="regionOne" tts:textAlign='middle' tts:origin='96px 54px' tts:extent='70% 25%' style="padded"/>
        <region xml:id="regionTwo" tts:backgroundColor="blue" tts:textAlign='right' tts:origin='25% 25%' tts:extent='50% 10%'/>
        <region xml:id="regionThree" tts:backgroundColor="green" tts:textAlign='left' tts:origin='50% 50%' tts:extent='25% 25%'/>
        <region xml:id="regionFour" tts:backgroundColor="red" tts:textAlign='right' tts:origin='25% 75%' tts:extent='25% 25%'/>
    </layout>
</head>
<body>
    <div>
        <p region="regionOne" tts:backgroundColor="black" begin='00:00:01.000' end='00:00:03.000'>
        You might not remember us. We are a typical transparent region with centered text that has an outline.
        </p>
        <p region="regionTwo" begin='00:00:03.500' end='00:00:05.000'>
        had <span tts:textDecoration="underline">personality.</span>
        </p>
        <p region="regionThree" begin='00:00:05.500' end='00:00:07.000'>
        Hello there, children! Have you seen any visitors?
        </p>
        <p region="regionFour" begin='00:00:07.500' end='00:00:09.000'>
        This is<br/>
        the last cue
        </p>
    </div>
</body>
</tt>"""

SAMPLE_DFXP_WITH_LAYOUT = SAMPLE_DFXP_WITH_POSITIONING

SAMPLE_DFXP_IGNORE_LAYOUT = """<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling/>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:01.000" end="00:00:03.000" region="bottom">
    You might not remember us. We are a typical transparent region with centered text that has an outline.
   </p>
   <p begin="00:00:03.500" end="00:00:05.000" region="bottom">
    had personality.
   </p>
   <p begin="00:00:05.500" end="00:00:07.000" region="bottom">
    Hello there, children! Have you seen any visitors?
   </p>
   <p begin="00:00:07.500" end="00:00:09.000" region="bottom">
    This is<br/>
    the last cue
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_WITH_RELATIVIZED_POSITIONING = """<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling/>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" tts:extent="70% 25%" tts:origin="15% 15%" tts:padding="10% 10% 10% 10%" xml:id="r0"/>
   <region tts:displayAlign="after" tts:extent="50% 10%" tts:origin="25% 25%" tts:textAlign="right" xml:id="r1"/>
   <region tts:displayAlign="after" tts:extent="25% 25%" tts:origin="50% 50%" tts:textAlign="left" xml:id="r2"/>
   <region tts:displayAlign="after" tts:extent="25% 25%" tts:origin="25% 75%" tts:textAlign="right" xml:id="r3"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:01.000" end="00:00:03.000" region="r0">
    You might not remember us. We are a typical transparent region with centered text that has an outline.
   </p>
   <p begin="00:00:03.500" end="00:00:05.000" region="r1">
    had <span region="r1">personality.</span>
   </p>
   <p begin="00:00:05.500" end="00:00:07.000" region="r2">
    Hello there, children! Have you seen any visitors?
   </p>
   <p begin="00:00:07.500" end="00:00:09.000" region="r3">
    This is<br/>
    the last cue
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_EMPTY = """
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="p" tts:color="#ffeedd" tts:fontfamily="Arial"
          tts:fontsize="10pt" tts:textAlign="center"/>
  </styling>
  <layout>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US">
  </div>
 </body>
</tt>
"""


SAMPLE_DFXP_SYNTAX_ERROR = """
<?xml version="1.0" encoding="UTF-16"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml">
<body>
  <div>
    <p begin="0:00:02.07" end="0:00:05.07">>>THE GENERAL ASSEMBLY'S 2014</p>
    <p begin="0:00:05.07" end="0:00:06.21">SESSION GOT OFF TO A LATE START,</p>
  </div>
 </body>
</tt>
"""

DFXP_FROM_SAMI_WITH_POSITIONING = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="p" tts:color="#ffeedd" tts:fontFamily="Arial"
          tts:fontSize="10pt" tts:textAlign="center"/>
  </styling>
  <layout>
   <region tts:padding="2pt 1pt 2pt 1pt" tts:textalign="center" xml:id="r0"></region>
   <region tts:padding="2pt 1pt 2pt 1pt" tts:textalign="right" xml:id="r1"></region>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US" region="r0">
   <p begin="00:00:09.209" end="00:00:12.312" region="r0" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" region="r0" style="p">
    MAN:<br/>
    When we think<br/>
    \u266a ...say bow, wow, \u266a
   </p>
   <p begin="00:00:17.000" end="00:00:18.752" region="r1" style="p">
    we have this vision of Einstein
   </p>
   <p begin="00:00:18.752" end="00:00:20.887" region="r0" style="p">
   <br/>
    as an old, wrinkly man<br/>
    with white hair.
   </p>
   <p begin="00:00:20.887" end="00:00:26.760" region="r0" style="p">
    MAN 2:<br/>
    E equals m c-squared is<br/>
    not about an old Einstein.
   </p>
   <p begin="00:00:26.760" end="00:00:32.200" region="r0" style="p">
    MAN 2:<br/>
    It's all about an eternal Einstein.
   </p>
   <p begin="00:00:32.200" end="00:00:36.200" region="r0" style="p">
    &lt;LAUGHING &amp; WHOOPS!&gt;
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_LONG_CUE = """<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:backgroundColor="black" tts:color="white" tts:fontFamily="monospace" tts:fontSize="8%" xml:id="basic"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:origin="25% 25%" tts:textAlign="center" xml:id="r0"/>
  </layout>
 </head>
 <body>
  <div>
   <p begin="00:00:01.000" end="00:00:02.000" region="bottom" style="basic">
    NARRATOR:
   </p>
   <p begin="00:00:02.000" end="00:00:03.000" region="r0" style="basic">
    They built the largest, most incredible, wildest, craziest,
   </p>
   <p begin="00:00:03.000" end="00:00:04.000" region="bottom" style="basic">
    most complex machine in history.
   </p>
  </div>
 </body>
</tt>
"""

SAMPLE_DFXP_LONG_CUE_FIT_TO_SCREEN = """<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="white" tts:fontFamily="monospace" tts:fontSize="8%" xml:id="basic"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" tts:extent="75% 75%" tts:origin="25% 25%" tts:textAlign="center" xml:id="r0"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:01.000" end="00:00:02.000" region="bottom" style="basic">
    NARRATOR:
   </p>
   <p begin="00:00:02.000" end="00:00:03.000" region="r0" style="basic">
    They built the largest, most incredible, wildest, craziest,
   </p>
   <p begin="00:00:03.000" end="00:00:04.000" region="bottom" style="basic">
    most complex machine in history.
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_FROM_SAMI_WITH_MARGINS = """<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffffff" tts:fontFamily="Tahoma" tts:fontSize="24pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:padding="0% 29pt 0% 29pt" tts:textAlign="center" xml:id="r0"/>
  </layout>
 </head>
 <body>
  <div region="r0" xml:lang="en-US">
   <p begin="00:00:00.133" end="00:00:04.133" region="r0" style="p">
    &gt;&gt; COMING UP NEXT, IT IS<br/>
    APPLAUSE AMERICA.
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_FROM_SAMI_WITH_LANG_MARGINS = """<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffffff" tts:fontFamily="Tahoma" tts:fontSize="24pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:padding="20px 20px 20px 20px" tts:textAlign="center" xml:id="r0"/>
  </layout>
 </head>
 <body>
  <div region="r0" xml:lang="en-US">
   <p begin="00:00:00.133" end="00:00:04.133" region="r0" style="p">
    &gt;&gt; COMING UP NEXT, IT IS<br/>
    APPLAUSE AMERICA.
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_FROM_SAMI_WITH_SPAN = """<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffffff" tts:fontFamily="Tahoma" tts:fontSize="24pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:padding="20px 20px 20px 20px" tts:textAlign="center" xml:id="r0"/>
  </layout>
 </head>
 <body>
  <div region="r0" xml:lang="en-US">
   <p begin="00:00:00.133" end="00:00:04.133" region="r0" style="p">
    <span tts:fontSize="36pt">we have this vision of Einstein</span>
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_FROM_SAMI_WITH_BAD_SPAN_ALIGN = """<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffffff" tts:fontFamily="Tahoma" tts:fontSize="24pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:padding="20px 20px 20px 20px" tts:textAlign="center" xml:id="r0"/>
   <region tts:padding="20px 20px 20px 20px" tts:textAlign="right" xml:id="r1"/>
  </layout>
 </head>
 <body>
  <div region="r0" xml:lang="en-US">
   <p begin="00:00:00.133" end="00:00:04.133" region="r1" style="p">
    Some say we have this vision of Einstein as an old, wrinkly man
   </p>
  </div>
 </body>
</tt>"""

DFXP_STYLE_REGION_ALIGN_CONFLICT = """<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffffff" tts:fontFamily="Arial" tts:fontSize="10pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:textAlign="left" xml:id="r0"/>
  </layout>
 </head>
 <body>
  <div region="r0" xml:lang="en-US">
   <p begin="00:00:04.537" end="00:00:07.841" region="r0" style="p">
    IT'S WORD GIRL♫
   </p>
   <p begin="00:00:08.537" end="00:00:10.841" region="r0" style="p">
    ♫WORD UP,<br/>
    IT'S WORD GIRL♫
   </p>
  </div>
 </body>
</tt>
"""

SAMPLE_DFXP_INVALID_BUT_SUPPORTED_POSITIONING_INPUT = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="p" tts:color="#ffeedd" tts:fontFamily="Arial"
          tts:fontSize="10pt" tts:textAlign="center"/>
  </styling>
  <layout>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US">
   <p tts:origin="17.5% 10%" tts:extent="62.5% 5.33%" begin="0:00:02.777" end="0:00:05.700">
   Hello there!
   </p>
   <p tts:origin="20% 15.67%" tts:extent="30% 7.67%" begin="0:00:05.700" end="0:00:06.210">
   How are you?<span tts:origin="1px 2px">>>Fine, thx<<</span>
   </p>
   <p tts:extent="60% 22%" begin="0:00:07.900" end="0:00:08.900" tts:textAlign="right" tts:displayAlign="before">
   Just fine?
   </p>
   <p tts:origin="11% 11%" begin="0:00:09.900" end="0:00:10.800">
    <span weirdAttribute="1" tts:textAlign="right">>>>Lol, yes!</span>
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_INVALID_BUT_SUPPORTED_POSITIONING_OUTPUT = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" tts:extent="62.5% 5.33%" tts:origin="17.5% 10%" tts:textAlign="center" xml:id="r0"/>
   <region tts:displayAlign="after" tts:extent="30% 7.67%" tts:origin="20% 15.67%" tts:textAlign="center" xml:id="r1"/>
   <region tts:displayAlign="after" tts:extent="30% 7.67%" tts:origin="1px 2px" tts:textAlign="center" xml:id="r2"/>
   <region tts:displayAlign="before" tts:extent="60% 22%" tts:textAlign="right" xml:id="r3"/>
   <region tts:displayAlign="after" tts:origin="11% 11%" tts:textAlign="center" xml:id="r4"/>
   <region tts:displayAlign="after" tts:origin="11% 11%" tts:textAlign="right" xml:id="r5"/>
  </layout>
 </head>
 <body>
  <div region="bottom" tts:displayAlign="after" tts:textAlign="center" xml:lang="en-US">
   <p begin="00:00:02.777" end="00:00:05.700" region="r0" style="p" tts:displayAlign="after" tts:extent="62.5% 5.33%" tts:origin="17.5% 10%" tts:textAlign="center">
    Hello there!
   </p>
   <p begin="00:00:05.700" end="00:00:06.210" region="r1" style="p" tts:displayAlign="after" tts:extent="30% 7.67%" tts:origin="20% 15.67%" tts:textAlign="center">
    How are you?<span region="r2" tts:origin="1px 2px" tts:textAlign="center" tts:extent="30% 7.67%" tts:displayAlign="after">&gt;&gt;Fine, thx&lt;&lt;</span>
   </p>
   <p begin="00:00:07.900" end="00:00:08.900" region="r3" style="p" tts:displayAlign="before" tts:extent="60% 22%" tts:textAlign="right">
    Just fine?
   </p>
   <p begin="00:00:09.900" end="00:00:10.800" region="r4" style="p" tts:displayAlign="after" tts:origin="11% 11%" tts:textAlign="center">
    <span tts:textAlign="right" region="r5" tts:origin="11% 11%" tts:textAlign="right" tts:displayAlign="after">&gt;&gt;&gt;Lol, yes!</span>
   </p>
  </div>
 </body>
</tt>"""


SAMPLE_DFXP_MULTIPLE_REGIONS_INPUT = """
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="p" tts:color="#ffeedd" tts:fontfamily="Arial"
          tts:fontsize="10pt" tts:textAlign="center"/>
    <style xml:id="referential_style2" tts:extent="3em 4em"/>
    <style xml:id="referential_style1" tts:padding="3px 4px 5px" style="referential_style2"/>
  </styling>
  <layout>
   <region tts:textAlign="center" xml:id="pixel_region">
    <style tts:origin="40px 50px" tts:extent="30px 40px"/>
   </region>
   <region tts:origin="10% 30%" tts:extent="50% 50%" xml:id="percent_region"/>
   <region tts:padding="2c" xml:id="padding_region" />
   <region xml:id="referential_region" style="referential_style1"/>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US">
   <p region="pixel_region" begin="0:00:02.700" end="0:00:05.700">
   Hello there!
   </p>
   <p region="percent_region" begin="0:00:05.700" end="0:00:06.210">
   How are you?
   </p>
   <p region="padding_region" begin="0:00:07.700" end="0:00:09.210">
   >> I'm fine, thank you << replied someone.
   <span region="percent_region">
    >>And now we're going to have fun<<
    </span>
   </p>
   <p region="referential_region" begin="0:00:10.707" end="0:00:11.210">
   What do you have in mind?
   </p>
   <p begin="0:00:12.900" end="0:00:13.900" tts:textAlign="start"
        tts:displayAlign="after">
   To write random words here!
   </p>
  </div>
 </body>
</tt>
"""

SAMPLE_DFXP_MULTIPLE_REGIONS_OUTPUT = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" tts:extent="30px 40px" tts:origin="40px 50px" tts:textAlign="center" xml:id="r0"/>
   <region tts:displayAlign="after" tts:extent="50% 50%" tts:origin="10% 30%" tts:textAlign="center" xml:id="r1"/>
   <region tts:displayAlign="after" tts:padding="2c 2c 2c 2c" tts:textAlign="center" xml:id="r2"/>
   <region tts:displayAlign="after" tts:extent="3em 4em" tts:padding="3px 4px 5px 4px" tts:textAlign="center" xml:id="r3"/>
   <region tts:displayAlign="after" tts:textAlign="start" xml:id="r4"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:02.700" end="00:00:05.700" region="r0" style="p">
    Hello there!
   </p>
   <p begin="00:00:05.700" end="00:00:06.210" region="r1" style="p">
    How are you?
   </p>
   <p begin="00:00:07.700" end="00:00:09.210" region="r2" style="p">
    &gt;&gt; I'm fine, thank you &lt;&lt; replied someone.<span region="r1">&gt;&gt;And now we're going to have fun&lt;&lt;</span>
   </p>
   <p begin="00:00:10.707" end="00:00:11.210" region="r3" style="p">
    What do you have in mind?
   </p>
   <p begin="00:00:12.900" end="00:00:13.900" region="r4" style="p" tts:textAlign="start">
    To write random words here!
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_TO_RENDER_WITH_ONLY_DEFAULT_POSITIONING_INPUT = u"""\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" tts:textAlign="center" xml:id="p" tts:origin="10% 20%" tts:extent="10% 30%"/>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" tts:textAlign="left" xml:id="p2"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" tts:extent="30px 40px" tts:origin="40px 50px" tts:textAlign="center" xml:id="r0"/>
   <region tts:displayAlign="after" tts:extent="50% 50%" tts:origin="10% 30%" tts:textAlign="center" xml:id="r1"/>
   <region tts:displayAlign="after" tts:padding="2c 2c 2c 2c" tts:textAlign="center" xml:id="r2"/>
   <region tts:displayAlign="after" tts:extent="3em 4em" tts:padding="3px 4px 5px 4px" tts:textAlign="center" xml:id="r3"/>
   <region tts:displayAlign="after" tts:textAlign="start" xml:id="r4"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:02.700" end="00:00:05.700" region="r0" style="p">
    Hello there!
   </p>
   <p begin="00:00:05.700" end="00:00:06.210" region="r1" style="p2">
    How are you?
   </p>
  </div>
 </body>
</tt>"""

##
# When converting from DFXP to DFXP, notice the extra region "r0" is added, to
# support the spam that sets the "tts:textAlign" attribute.
# This attribute is meaningless on the <span> tag, and should affect only <p>
# tags. It's a feature that should affect only only those players that don't
# conform to the specs.

# UNUSED SAMPLE
SAMPLE_DFXP_TO_DFXP_OUTPUT = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" tts:textAlign="right" xml:id="r0"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" region="bottom" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" region="bottom" style="p">
    MAN:<br/>
    When we think<br/>
    of "E equals m c-squared",
   </p>
   <p begin="00:00:17.000" end="00:00:18.752" region="bottom" style="p">
    <span tts:textAlign="right" region="r0">we have this vision of Einstein</span>
   </p>
   <p begin="00:00:18.752" end="00:00:20.887" region="bottom" style="p">
    <br/>
    as an old, wrinkly man<br/>
    with white hair.
   </p>
   <p begin="00:00:20.887" end="00:00:26.760" region="bottom" style="p">
    MAN 2:<br/>
    E equals m c-squared is<br/>
    not about an old Einstein.
   </p>
   <p begin="00:00:26.760" end="00:00:32.200" region="bottom" style="p">
    MAN 2:<br/>
    It's all about an eternal Einstein.
   </p>
   <p begin="00:00:32.200" end="00:00:34.400" region="bottom" style="p">
    &lt;LAUGHING &amp; WHOOPS!&gt;
   </p>
   <p begin="00:00:34.400" end="00:00:38.400" region="bottom" style="p">
    some more text
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_OUTPUT = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" tts:textAlign="right" xml:id="r0"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" region="bottom" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" region="bottom" style="p">
    MAN:<br/>
    When we think<br/>
    \u266a ...say bow, wow, \u266a
   </p>
   <p begin="00:00:17.000" end="00:00:18.752" region="bottom" style="p">
    <span tts:textAlign="right" region="r0">we have this vision of Einstein</span>
   </p>
   <p begin="00:00:18.752" end="00:00:20.887" region="bottom" style="p">
    <br/>
    as an old, wrinkly man<br/>
    with white hair.
   </p>
   <p begin="00:00:20.887" end="00:00:26.760" region="bottom" style="p">
    MAN 2:<br/>
    E equals m c-squared is<br/>
    not about an old Einstein.
   </p>
   <p begin="00:00:26.760" end="00:00:32.200" region="bottom" style="p">
    MAN 2:<br/>
    It's all about an eternal Einstein.
   </p>
   <p begin="00:00:32.200" end="00:00:36.200" region="bottom" style="p">
    &lt;LAUGHING &amp; WHOOPS!&gt;
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_STYLE_TAG_WITH_NO_XML_ID_INPUT = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" xml:id="p"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" xml:id="r0">
    <style tts:textAlign="start"/>
   </region>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" region="r0" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" region="bottom" style="p">
    MAN:<br/>
    When we think<br/>
    of "E equals m c-squared",
   </p>
  </div>
 </body>
</tt>
"""

SAMPLE_DFXP_STYLE_TAG_WITH_NO_XML_ID_OUTPUT = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" xml:id="p"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" tts:textAlign="start" xml:id="r0"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" region="r0" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" region="bottom" style="p">
    MAN:<br/>
    When we think<br/>
    of "E equals m c-squared",
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_FROM_SCC_OUTPUT = """<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="white" tts:fontFamily="monospace" tts:fontSize="1c" xml:id="default"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="before" tts:origin="0% 80%" tts:textAlign="center" xml:id="r0"/>
   <region tts:displayAlign="before" tts:origin="37.5% 0%" tts:textAlign="center" xml:id="r1"/>
   <region tts:displayAlign="before" tts:origin="75% 20%" tts:textAlign="center" xml:id="r2"/>
   <region tts:displayAlign="before" tts:origin="12.5% 46.67%" tts:textAlign="center" xml:id="r3"/>
   <region tts:displayAlign="before" tts:origin="12.5% 93.33%" tts:textAlign="center" xml:id="r4"/>
   <region tts:displayAlign="before" tts:origin="37.5% 53.33%" tts:textAlign="center" xml:id="r5"/>
   <region tts:displayAlign="before" tts:origin="75% 13.33%" tts:textAlign="center" xml:id="r6"/>
   <region tts:displayAlign="before" tts:origin="12.5% 33.33%" tts:textAlign="center" xml:id="r7"/>
   <region tts:displayAlign="before" tts:origin="12.5% 86.67%" tts:textAlign="center" xml:id="r8"/>
   <region tts:displayAlign="before" tts:origin="75% 6.67%" tts:textAlign="center" xml:id="r9"/>
   <region tts:displayAlign="before" tts:origin="37.5% 40%" tts:textAlign="center" xml:id="r10"/>
   <region tts:displayAlign="before" tts:origin="12.5% 73.33%" tts:textAlign="center" xml:id="r11"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:01.167" end="00:00:03.103" region="r0" style="default">
    abab
   </p>
   <p begin="00:00:01.167" end="00:00:03.103" region="r1" style="default">
    cdcd
   </p>
   <p begin="00:00:01.167" end="00:00:03.103" region="r2" style="default">
    efef
   </p>
   <p begin="00:00:03.169" end="00:00:09.743" region="r3" style="default">
    ghgh<br/>
    ijij<br/>
    klkl
   </p>
   <p begin="00:00:09.743" end="00:00:11.745" region="r4" style="default">
    mnmn
   </p>
   <p begin="00:00:09.743" end="00:00:11.745" region="r5" style="default">
    opop
   </p>
   <p begin="00:00:09.743" end="00:00:11.745" region="r6" style="default">
    qrqr
   </p>
   <p begin="00:00:11.745" end="00:00:20.100" region="r7" style="default">
    stst<br/>
    uvuv<br/>
    wxwx
   </p>
   <p begin="00:00:20.100" end="00:00:22.100" region="r8" style="default">
    yzyz
   </p>
   <p begin="00:00:20.100" end="00:00:22.100" region="r9" style="default">
    0101
   </p>
   <p begin="00:00:20.100" end="00:00:22.100" region="r10" style="default">
    2323
   </p>
   <p begin="00:00:22.100" end="00:00:36.202" region="r11" style="default">
    4545<br/>
    6767<br/>
    8989
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_WITH_PROPERLY_CLOSING_SPANS_OUTPUT = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="white" tts:fontFamily="monospace" tts:fontSize="1c" xml:id="default"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="before" tts:extent="87.5% 13.33%" tts:origin="12.5% 86.67%" tts:textAlign="center" xml:id="r0"/>
   <region tts:displayAlign="before" tts:extent="75% 13.33%" tts:origin="25% 86.67%" tts:textAlign="center" xml:id="r1"/>
   <region tts:displayAlign="before" tts:extent="50% 13.33%" tts:origin="50% 86.67%" tts:textAlign="center" xml:id="r2"/>
   <region tts:displayAlign="before" tts:extent="37.5% 13.33%" tts:origin="62.5% 86.67%" tts:textAlign="center" xml:id="r3"/>
   <region tts:displayAlign="before" tts:extent="75% 6.67%" tts:origin="25% 93.33%" tts:textAlign="center" xml:id="r4"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:01:31.400" end="00:01:35.666" region="r0" style="default">
    cccccc<br/>
    c!c!
   </p>
   <p begin="00:01:35.666" end="00:01:40.866" region="r1" style="default">
    bbbb
   </p>
   <p begin="00:01:35.666" end="00:01:40.866" region="r2" style="default">
    <span tts:fontStyle="italic" region="r2">cccc<br/>
    bbaa</span>
   </p>
   <p begin="00:01:55.800" end="00:01:59.533" region="r0" style="default">
    aa
   </p>
   <p begin="00:01:55.800" end="00:01:59.533" region="r3" style="default">
    <span tts:fontStyle="italic" region="r3">bb<br/>
    cc</span>
   </p>
   <p begin="00:01:59.533" end="00:01:59.533" region="r3" style="default">
    abcd
   </p>
   <p begin="00:01:59.533" end="00:01:59.533" region="r4" style="default">
    abcd
   </p>
   <p begin="00:01:59.533" end="00:01:59.700" region="r4" style="default">
    dddd
   </p>
  </div>
 </body>
</tt>"""


SAMPLE_DFXP_FOR_LEGACY_WRITER_INPUT = """
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="p" tts:color="#ffeedd" tts:fontfamily="Arial"
          tts:fontsize="10pt" tts:textAlign="center"/>
  </styling>
  <layout>
   <region xml:id="r0" tts:origin="20% 30%" tts:extent="30% 30%"/>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" region="r0" style="p">
    MAN:<br/>
    When we think<br/>
    of "E equals m c-squared",
   </p>
   <p begin="00:00:17.000" end="00:00:18.752" style="p">
    <span tts:textAlign="right">we have this vision of Einstein</span>
   </p>
   <p begin="00:00:18.752" end="00:00:20.887" style="p">
    as an old, wrinkly man<br/>
    with white hair.
   </p>
   <p begin="00:00:20.887" end="00:00:26.760" tts:origin="10% 10%" style="p">
    MAN 2:<br/>
    E equals m c-squared is<br/>
    not about an old Einstein.
   </p>
   <p begin="00:00:26.760" end="00:00:32.200" tts:testAlign="left" style="p">
    MAN 2:<br/>
    It's all about an eternal Einstein.
   </p>
   <p begin="00:00:32.200" end="00:00:34.400" style="p">
    &lt;LAUGHING &amp; WHOOPS!&gt;
   </p>
   <p begin="00:00:34.400" end="00:00:38.400" style="p">some more text</p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_FOR_LEGACY_WRITER_OUTPUT = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" region="bottom" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" region="bottom" style="p">
    MAN:<br/>
    When we think<br/>
    of "E equals m c-squared",
   </p>
   <p begin="00:00:17.000" end="00:00:18.752" region="bottom" style="p">
    <span tts:textAlign="right">we have this vision of Einstein</span>
   </p>
   <p begin="00:00:18.752" end="00:00:20.887" region="bottom" style="p">
    as an old, wrinkly man<br/>
    with white hair.
   </p>
   <p begin="00:00:20.887" end="00:00:26.760" region="bottom" style="p">
    MAN 2:<br/>
    E equals m c-squared is<br/>
    not about an old Einstein.
   </p>
   <p begin="00:00:26.760" end="00:00:32.200" region="bottom" style="p">
    MAN 2:<br/>
    It's all about an eternal Einstein.
   </p>
   <p begin="00:00:32.200" end="00:00:34.400" region="bottom" style="p">
    &lt;LAUGHING &amp; WHOOPS!&gt;
   </p>
   <p begin="00:00:34.400" end="00:00:38.400" region="bottom" style="p">
    some more text
   </p>
  </div>
 </body>
</tt>"""

DFXP_WITH_CONCURRENT_CAPTIONS = u"""\
<tt xml:lang="en-us"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts='http://www.w3.org/ns/ttml#styling'
    >
<head>
    <layout>
        <region xml:id="r0" tts:textAlign="center" tts:displayAlign="after" tts:origin="5% 5%" tts:extent="90% 90%"/>
        <region xml:id="r1" tts:textAlign="center" tts:displayAlign="after" tts:origin="5% 15%" tts:extent="90% 80%"/>
    </layout>
</head>
<body>
    <div>
        <p region="r0" begin='00:00:01.000' end='00:00:03.000'>
        When we think
        </p>
        <p region="r1" begin='00:00:01.000' end='00:00:03.000'>
        of "E equals m c-squared",
        </p>
        <p region="r0" begin='00:00:03.000' end='00:00:04.000'>
        we have this vision of Einstein
        </p>
        <p region="r0" begin='00:00:04.000' end='00:00:05.000'>
        as an old, wrinkly man
        </p>
        <p region="r1" begin='00:00:04.000' end='00:00:05.000'>
        with white hair.
        </p>
    </div>
</body>
</tt>"""

# 'style_name' is the template parameter to use in str.format
DFXP_WITH_TEMPLATED_STYLE = """\
<tt xml:lang="en-us"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts='http://www.w3.org/ns/ttml#styling'
    >
<head>
    <layout>
        <region xml:id="r0" tts:textAlign="center" tts:displayAlign="after" tts:origin="5% 5%" tts:extent="90% 90%"/>
    </layout>
    <styling>
        <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" tts:textAlign="center" xml:id="{style_name}"/>
    </styling>
</head>
<body>
    <div>
        <p region="r0" begin="00:00:01.000" end="00:00:03.000" style="{style_name}">
        When we think
        </p>
    </div>
</body>
</tt>
"""

DFXP_WITH_ESCAPED_APOSTROPHE = u"""\
<tt xml:lang="en-us"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts='http://www.w3.org/ns/ttml#styling'
    >
<head>
    <layout>
        <region xml:id="r0" tts:textAlign="center" tts:displayAlign="after" tts:origin="5% 5%" tts:extent="90% 90%"/>
    </layout>
</head>
<body>
    <div>
        <p region="r0" begin='00:00:01.000' end='00:00:03.000'>
        << &quot;Andy&apos;s Caf&eacute; & Restaurant&quot; this way
        </p>
    </div>
</body>
</tt>"""

DFXP_WITH_ALTERNATIVE_TIMING_FORMATS = u"""\
<tt xml:lang="en-us"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts='http://www.w3.org/ns/ttml#styling'
    >
<head>
    <layout>
        <region xml:id="r0" tts:textAlign="center" tts:displayAlign="after" tts:origin="5% 5%" tts:extent="90% 90%"/>
    </layout>
</head>
<body>
    <div>
        <p region="r0" begin='00:00:01.9' end='00:00:03.05'>
            foo
        </p>
        <p region="r0" begin='4s' end='5.2s'>
            bar
        </p>
    </div>
</body>
</tt>"""


SAMPLE_DFXP_EMPTY_PARAGRAPH = """
<?xml version="1.0" encoding="UTF-16"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml">
<body>
  <div>
    <p begin="0:00:02.07" end="0:00:05.07"></p>
    <p begin="0:00:05.07" end="0:00:06.21">SESSION GOT OFF TO A LATE START,</p>
  </div>
 </body>
</tt>
"""

SAMPLE_DFXP_EMPTY_PARAGRAPH_WITH_NEWLINE = """
<?xml version="1.0" encoding="UTF-16"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml">
<body>
  <div>
    <p begin="0:00:02.07" end="0:00:05.07">
    </p>
    <p begin="0:00:05.07" end="0:00:06.21">SESSION GOT OFF TO A LATE START,</p>
  </div>
 </body>
</tt>
"""

SAMPLE_DFXP_EMPTY_PARAGRAPH_WITH_MULTIPLE_NEWLINES = """
<?xml version="1.0" encoding="UTF-16"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml">
<body>
  <div>
    <p begin="0:00:02.07" end="0:00:05.07">
    


    </p>
    <p begin="0:00:05.07" end="0:00:06.21">SESSION GOT OFF TO A LATE START,</p>
  </div>
 </body>
</tt>
"""
