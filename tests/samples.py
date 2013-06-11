# -*- coding: utf-8 -*-
SAMPLE_SAMI = """
<SAMI><HEAD><TITLE>NOVA3213</TITLE><STYLE TYPE="text/css">
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
    color: #ffeedd; }

.ENCC {Name: English; lang: en-US; SAMI_Type: CC;}

--></STYLE></HEAD><BODY>
<SYNC start="9209"><P class="ENCC">
       ( clock ticking )
</P></SYNC>
<SYNC start="12312"><P class="ENCC">&nbsp;</P></SYNC>
<SYNC start="14848"><P class="ENCC">
              MAN:<br/>
         When we think<br/>
    of E equals m c-squared,
</P></SYNC>
<SYNC start="17350"><P class="ENCC">
we have this vision of Einstein
</P></SYNC>
<SYNC start="18752"><P class="ENCC">
     as an old, wrinkly man<br/>
        with white hair.
</P></SYNC>
<SYNC start="20887"><P class="ENCC">
             MAN 2:<br/>
    E equals m c-squared is<br/>
   not about an old Einstein.
</P></SYNC>
<SYNC start="30764"><P class="ENCC">
             MAN 2:<br/>
    It's all about...
</P></SYNC>
<SYNC start="40152"><P class="ENCC">
    &lt;LAUGHING AND WHOOPS!&gt;
</P></SYNC>
</BODY></SAMI>
"""


SAMPLE_SRT = """1
00:00:09,209 --> 00:00:12,312
( clock ticking )

2
00:00:14,848 --> 00:00:17,000
MAN:
When we think
of E equals m c-squared,

3
00:00:17,000 --> 00:00:18,752
we have this vision of Einstein

4
00:00:18,752 --> 00:00:20,887
as an old, wrinkly man
with white hair.

5
00:00:20,887 --> 00:00:26,760
MAN 2:
E equals m c-squared is
not about an old Einstein.

6
00:00:26,760 --> 00:00:32,200
MAN 2:
It's all about an eternal Einstein.

7
00:00:32,200 --> 00:00:39,439
<LAUGHING AND WHOOPS!>
"""


SAMPLE_DFXP = """
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style id="p" tts:color="#ffffff" tts:fontfamily="Arial"
          tts:fontsize="10pt" tts:textAlign="center"/>
  </styling>
 </head>
 <body>
  <div xml:lang="en-US">
   <p begin="00:00:02.268" end="00:00:05.000" style="p">
    ♫Every day, when you're<br/>
    walking down the street♫
   </p>
   <p begin="00:00:05.000" end="00:00:09.909" style="p">
    ♫Everybody that you meet<br/>
    has an original point of view♫
   </p>
   <p begin="00:00:09.909" end="00:00:11.578" style="p">
    (laughing)
   </p>
   <p begin="00:00:11.578" end="00:00:13.780" style="p">
    ♫And I say, hey♫<br/>
    Hey!
   </p>
  </div>
 </body>
</tt>
"""
