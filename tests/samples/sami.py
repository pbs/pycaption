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

SAMPLE_SAMI_WITH_STYLE_TAGS = """
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

SAMPLE_SAMI_WITH_CSS_INLINE_STYLE = """
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

SAMPLE_SAMI_WITH_CSS_ID_STYLE = """
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

SAMPLE_SAMI_EMPTY = """
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


SAMPLE_SAMI_SYNTAX_ERROR = """
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

SAMPLE_SAMI_DOUBLE_BR = """
<SAMI><HEAD><TITLE>NOVA3213</TITLE>
</HEAD><BODY>
<SYNC start="14848"><P class="ENCC">
    MAN:<br/><br/>
    When we think<br/>
    of "E equals m c-squared",
</BODY></SAMI>
"""

SAMPLE_SAMI_PARTIAL_MARGINS = """
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

SAMPLE_SAMI_PARTIAL_MARGINS_RELATIVIZED = """<sami>
 <head>
  <style type="text/css">
   <!--
    p {
     background-color: #000;
     color: #ffffff;
     font-family: Tahoma;
     font-size: 24pt;
     font-weight: bold;
     margin-bottom: 0%;
     margin-left: 6.04%;
     margin-right: 6.04%;
     margin-top: 0%;
     text-align: center;
    }

    .subttl {
     lang: en-US;
     margin-bottom: 0%;
     margin-left: 6.04%;
     margin-right: 6.04%;
     margin-top: 0%;
     name: "Subtitles";
     samitype: CC;
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

SAMPLE_SAMI_LANG_MARGIN = """
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

SAMPLE_SAMI_WITH_SPAN = """
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

SAMPLE_SAMI_WITH_BAD_SPAN_ALIGN = """
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

SAMPLE_SAMI_WITH_BAD_DIV_ALIGN = """
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

SAMPLE_SAMI_WITH_P_ALIGN = """
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

SAMPLE_SAMI_WITH_P_AND_SPAN_ALIGN = """
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

SAMPLE_SAMI_WITH_MULTIPLE_SPAN_ALIGNS = """
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

SAMPLE_SAMI_NO_LANG = """
<SAMI>
<Head><STYLE TYPE="text/css"></Style></Head>
<BODY>
<Sync Start=0><P Class=ENCC></p></sync>
<Sync Start=1301><P Class=ENCC>>> FUNDING FOR OVERHEARD</p></sync>
</Body>
</SAMI>
"""

SAMPLE_SAMI_WITH_LANG = """
<sami>
<head>
<style type="text/css"><!--.en-US {lang: en-US;}--></style>
</head>
<body>
<sync start="1301"><p class="en-US">&gt;&gt; FUNDING FOR OVERHEARD</p></sync>
</body>
</sami>
"""
