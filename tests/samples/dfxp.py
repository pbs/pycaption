# -*- coding: utf-8 -*-

SAMPLE_DFXP_UNICODE = u"""\
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

SAMPLE_DFXP_UTF8 = """
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
  <div xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" style="p">
    MAN:<br/>
    When we think<br/>
    ♪ ...say bow, wow, ♪
   </p>
   <p begin="00:00:17.000" end="00:00:18.752" style="p">
    <span tts:textAlign="right">we have this vision of Einstein</span>
   </p>
   <p begin="00:00:18.752" end="00:00:20.887" style="p">
   <br/>
    as an old, wrinkly man<br/>
    with white hair.
   </p>
   <p begin="00:00:20.887" end="00:00:26.760" style="p">
    MAN 2:<br/>
    E equals m c-squared is<br/>
    not about an old Einstein.
   </p>
   <p begin="00:00:26.760" end="00:00:32.200" style="p">
    MAN 2:<br/>
    It's all about an eternal Einstein.
   </p>
   <p begin="00:00:32.200" end="00:00:36.200" style="p">
    &lt;LAUGHING &amp; WHOOPS!&gt;
   </p>
  </div>
 </body>
</tt>"""

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


SAMPLE_DFXP = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="p" tts:color="#ffeedd" tts:fontfamily="Arial"
          tts:fontsize="10pt" tts:textAlign="center"/>
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
    of "E equals m c-squared",
   </p>
   <p begin="00:00:17.000" end="00:00:18.752" region="bottom" style="p">
    <span tts:textAlign="right">we have this vision of Einstein</span>
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
   <style xml:id="p" tts:color="#ffeedd" tts:fontfamily="Arial"
          tts:fontsize="10pt" tts:textAlign="center"/>
  </styling>
  <layout>
   <region tts:padding="2pt 1pt 2pt 1pt" tts:textalign="center" xml:id="r0"></region>
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
    of "E equals m c-squared",
   </p>
   <p begin="00:00:17.000" end="00:00:18.752" region="r0" style="p">
    <span tts:textAlign="right">we have this vision of Einstein</span>
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
   <p begin="00:00:32.200" end="00:00:34.400" region="r0" style="p">
    &lt;LAUGHING &amp; WHOOPS!&gt;
   </p>
   <p begin="00:00:34.400" end="00:00:38.400" region="r0" style="p">
    some more text
   </p>
  </div>
 </body>
</tt>"""

DFXP_FROM_SAMI_WITH_POSITIONING_UTF8 = """
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
    ♪ ...say bow, wow, ♪
   </p>
   <p begin="00:00:17.000" end="00:00:18.752" region="r0" style="p">
    <span tts:textAlign="right">we have this vision of Einstein</span>
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

DFXP_FROM_SAMI_WITH_POSITIONING_UNICODE = u"""\
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
   <p begin="00:00:17.000" end="00:00:18.752" region="r0" style="p">
    <span tts:textalign="right">we have this vision of Einstein</span>
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
