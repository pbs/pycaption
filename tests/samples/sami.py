# -*- coding: utf-8 -*-

SAMPLE_SAMI = u"""
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
    \u266a ...say bow, wow, \u266a
</P></SYNC>
<SYNC start="17000"><P class="ENCC">
  <SPAN Style="text-align:right;">we have this vision of Einstein</SPAN>
</P></SYNC>
<SYNC start="18752"><P class="ENCC">
    <br/>
    as an old, wrinkly man<br/>
    with white hair.
</P></SYNC>
<SYNC start="20887"><P class="ENCC">
    MAN 2:<br/>
    E equals m c-squared is<br/>
    not about an old Einstein.
</P></SYNC>
<SYNC start="26760"><P class="ENCC">
    MAN 2:<br/>
    It's all about an eternal Einstein.
</P></SYNC>
<SYNC start="32200"><P class="ENCC">
    &lt;LAUGHING &amp; WHOOPS!&gt;
</P></SYNC>
</BODY></SAMI>
"""

SAMPLE_SAMI_WITH_STYLE_TAGS = u"""
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
    I <b>do</b> <i>not</i> want to go <u>home</u>.<br />
    I don't like it <i><u><b>there</b></u></i>.
</P></SYNC>
<SYNC start="12312"><P class="ENCC">&nbsp;</P></SYNC>
</BODY></SAMI>
"""

SAMPLE_SAMI_WITH_CSS_INLINE_STYLE = u"""
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
    I <span style="font-weight: bold">do</span> <span style="font-style: italic">not</span> want to go <span style="text-decoration: underline">home</span>.<br />
    I don't like it <span style="font-weight:bold;font-style:italic;text-decoration:underline">there</span>.
</P></SYNC>
<SYNC start="12312"><P class="ENCC">&nbsp;</P></SYNC>
</BODY></SAMI>
"""

SAMPLE_SAMI_WITH_CSS_ID_STYLE = u"""
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

#StyleItalic { font-style: italic; }
#StyleBold { font-weight: bold; }
#StyleUnderline { text-decoration: underline; }
#StyleItalicBoldUnderline { font-style: italic; font-weight: bold; text-decoration: underline; }

.ENCC {Name: English; lang: en-US; SAMI_Type: CC;}

--></STYLE></HEAD><BODY>
<SYNC start="9209"><P class="ENCC" id="StyleItalic">
    This is in italics.
</P></SYNC>
<SYNC start="12312"><P class="ENCC">&nbsp;</P></SYNC>
<SYNC start="14848"><P class="ENCC" id="StyleUnderline">
    This is underlined.
</P></SYNC>
<SYNC start="17000"><P class="ENCC" id="StyleBold">
    This is bold.
</P></SYNC>
<SYNC start="18752"><P class="ENCC">&nbsp;</P></SYNC>
<SYNC start="20887"><P class="ENCC" id="StyleItalicBoldUnderline">
    This is everything together.
</P></SYNC>
<SYNC start="26760"><P class="ENCC">&nbsp;</P></SYNC>
</BODY></SAMI>
"""

SAMPLE_SAMI_EMPTY = u"""
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
</BODY></SAMI>
"""


SAMPLE_SAMI_SYNTAX_ERROR = u"""
<SAMI>
<Head>
<title>ir2014_111</title>
  <STYLE TYPE="text/css">
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

    #Small {Name:SmallTxt; font-family:Arial;font-weight:normal;font-size:10pt;color:#ffffff;}
    #Big {Name:BigTxt; font-family:Arial;font-weight:bold;font-size:12pt;color:#ffffff;}

    .ENCC {Name:English; lang: en-US; SAMI_Type: CC;}

    -->

  </Style>

</Head>

<BODY>

<Sync Start=0><P Class=ENCC>
<Sync Start=5905><P Class=ENCC>>>> PRESENTATION OF "IDAHO<br>REPORTS" ON IDAHO PUBLIC
<Sync Start=7073><P Class=ENCC>TELEVISION IS MADE POSSIBLE<br>THROUGH THE GENEROUS SUPPORT OF

</Body>
</SAMI>
"""

SAMPLE_SAMI_DOUBLE_BR = u"""
<SAMI><HEAD><TITLE>NOVA3213</TITLE>
</HEAD><BODY>
<SYNC start="14848"><P class="ENCC">
    MAN:<br/><br/>
    When we think<br/>
    of "E equals m c-squared",
</BODY></SAMI>
"""

SAMPLE_SAMI_PARTIAL_MARGINS = u"""
<SAMI>
<HEAD>
   <STYLE TYPE="Text/css">
   <!--
      P {margin-left: 29pt; margin-right: 29pt; font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
      .SUBTTL {Name: 'Subtitles'; Lang: en-US; SAMIType: CC;}
   -->
   </STYLE>
</HEAD>
<BODY>
   <SYNC START=133>
      <P CLASS=SUBTTL>>> COMING UP NEXT, IT IS<br>APPLAUSE AMERICA.
</BODY>
</SAMI>
"""

SAMPLE_SAMI_PARTIAL_MARGINS_RELATIVIZED = u"""\
<sami>
 <head>
  <style type="text/css">
   <!--
    .subttl {
     lang: en-US;
     name: "Subtitles";
     margin-left: 6.04%;
     margin-bottom: 0%;
     margin-top: 0%;
     margin-right: 6.04%;
     samitype: CC;
    }

    p {
     font-size: 24pt;
     font-family: Tahoma;
     color: #ffffff;
     margin-right: 6.04%;
     margin-bottom: 0%;
     margin-top: 0%;
     margin-left: 6.04%;
     font-weight: bold;
     background-color: #000;
     text-align: center;
    }
   -->
  </style>
 </head>
 <body>
  <sync start="133">
   <p class="subttl" p_style="class:subttl;">
    &gt;&gt; COMING UP NEXT, IT IS<br/>
    APPLAUSE AMERICA.
   </p>
  </sync>
 </body>
</sami>"""

SAMPLE_SAMI_LANG_MARGIN = u"""
<SAMI>
<HEAD>
   <STYLE TYPE="Text/css">
   <!--
      P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
      .SUBTTL {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
   -->
   </STYLE>
</HEAD>
<BODY>
   <SYNC START=133>
      <P CLASS=SUBTTL>>> COMING UP NEXT, IT IS<br>APPLAUSE AMERICA.
</BODY>
</SAMI>
"""

SAMPLE_SAMI_WITH_SPAN = u"""
<SAMI>
<HEAD>
    <STYLE TYPE="Text/css">
    <!--
        P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
        .SUBTTL {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
    -->
    </STYLE>
</HEAD>
<BODY>
    <SYNC start="133">
        <P class="ENCC">
            <SPAN Style="font-size:36pt;">we have this vision of Einstein</SPAN>
        </P>
    </SYNC>
</BODY>
</SAMI>
"""

SAMPLE_SAMI_WITH_BAD_SPAN_ALIGN = u"""
<SAMI>
<HEAD>
    <STYLE TYPE="Text/css">
    <!--
        P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
        .SUBTTL {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
    -->
    </STYLE>
</HEAD>
<BODY>
    <SYNC start="133">
        <P class="ENCC">
            Some say <SPAN Style="text-align:right;">we have this vision of Einstein</SPAN> as an old, wrinkly man
        </P>
    </SYNC>
</BODY>
</SAMI>
"""

SAMPLE_SAMI_WITH_BAD_DIV_ALIGN = u"""
<SAMI>
<HEAD>
    <STYLE TYPE="Text/css">
    <!--
        P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
        .SUBTTL {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
    -->
    </STYLE>
</HEAD>
<BODY>
    <SYNC start="133">
        <P class="ENCC">
            Some say <DIV Style="text-align:right;">we have this vision of Einstein</DIV> as an old, wrinkly man
        </P>
    </SYNC>
</BODY>
</SAMI>
"""

SAMPLE_SAMI_WITH_P_ALIGN = u"""
<SAMI>
<HEAD>
    <STYLE TYPE="Text/css">
    <!--
        P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
        .SUBTTL {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
    -->
    </STYLE>
</HEAD>
<BODY>
    <SYNC start="133">
        <P class="ENCC" Style="text-align:right;">
            Some say we have this vision of Einstein as an old, wrinkly man
        </P>
    </SYNC>
</BODY>
</SAMI>
"""

SAMPLE_SAMI_WITH_P_AND_SPAN_ALIGN = u"""
<SAMI>
<HEAD>
    <STYLE TYPE="Text/css">
    <!--
        P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
        .SUBTTL {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
    -->
    </STYLE>
</HEAD>
<BODY>
    <SYNC start="133">
        <P class="ENCC" Style="text-align:right;">
            <SPAN Style="text-align:left;">Some say we have this vision of Einstein as an old, wrinkly man</SPAN>
        </P>
    </SYNC>
</BODY>
</SAMI>
"""

SAMPLE_SAMI_WITH_MULTIPLE_SPAN_ALIGNS = u"""
<SAMI>
<HEAD>
    <STYLE TYPE="Text/css">
    <!--
        P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
        .SUBTTL {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
    -->
    </STYLE>
</HEAD>
<BODY>
    <SYNC start="133">
        <P class="ENCC">
            <SPAN Style="text-align:right">Some say </SPAN>
            <SPAN Style="text-align:left;">we have this vision of Einstein </SPAN>
            as an old, wrinkly man
        </P>
    </SYNC>
</BODY>
</SAMI>
"""

SAMPLE_SAMI_WITH_LAYOUT = SAMPLE_SAMI_WITH_MULTIPLE_SPAN_ALIGNS

SAMPLE_SAMI_IGNORE_LAYOUT = u"""<sami>
 <head>
  <style type="text/css">
   <!--
    .subttl {
     lang: en-US;
     name: "Subtitles";
     margin-left: 20px;
     margin-bottom: 20px;
     margin-top: 20px;
     margin-right: 20px;
     samitype: CC;
    }

    p {
     font-size: 24pt;
     font-weight: bold;
     color: #ffffff;
     font-family: Tahoma;
     background-color: #000;
     text-align: center;
    }
   -->
  </style>
 </head>
 <body>
  <sync start="133">
   <p class="en-US" p_style="class:encc;">
    Some say  we have this vision of Einstein  as an old, wrinkly man
   </p>
  </sync>
 </body>
</sami>"""

SAMPLE_SAMI_NO_LANG = u"""
<SAMI>
<Head><STYLE TYPE="text/css"></Style></Head>
<BODY>
<Sync Start=0><P Class=ENCC></p></sync>
<Sync Start=1301><P Class=ENCC>>> FUNDING FOR OVERHEARD</p></sync>
</Body>
</SAMI>
"""

SAMPLE_SAMI_WITH_LANG = u"""
<sami>
<head>
<style type="text/css"><!--.en-US {lang: en-US;}--></style>
</head>
<body>
<sync start="1301"><p class="en-US">&gt;&gt; FUNDING FOR OVERHEARD</p></sync>
</body>
</sami>
"""
