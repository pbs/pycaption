import pytest


@pytest.fixture(scope="session")
def sample_sami():
    return """
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


@pytest.fixture(scope="session")
def sample_sami_with_style_tags():
    return """
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


@pytest.fixture(scope="session")
def sample_sami_with_css_inline_style():
    return """
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


@pytest.fixture(scope="session")
def sample_sami_with_css_id_style():
    return """
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


@pytest.fixture(scope="session")
def sample_sami_empty():
    return """
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


@pytest.fixture(scope="session")
def sample_sami_syntax_error():
    return """
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


@pytest.fixture(scope="session")
def sample_sami_double_br():
    return """
<SAMI><HEAD><TITLE>NOVA3213</TITLE>
</HEAD><BODY>
<SYNC start="14848"><P class="ENCC">
    MAN:<br/><br/>
    When we think<br/>
    of "E equals m c-squared",
</BODY></SAMI>
"""


@pytest.fixture(scope="session")
def sample_sami_partial_margins():
    return """
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


@pytest.fixture(scope="session")
def sample_sami_partial_margins_relativized():
    return """<sami>
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


@pytest.fixture(scope="session")
def sample_sami_lang_margin():
    return """
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


@pytest.fixture(scope="session")
def sample_sami_with_span():
    return """
<SAMI>
<HEAD>
    <STYLE TYPE="Text/css">
    <!--
        P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
        .ENCC {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
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


@pytest.fixture(scope="session")
def sample_sami_with_bad_span_align():
    return """
<SAMI>
<HEAD>
    <STYLE TYPE="Text/css">
    <!--
        P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
        .ENCC {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
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


@pytest.fixture(scope="session")
def sample_sami_with_bad_div_align():
    return """
<SAMI>
<HEAD>
    <STYLE TYPE="Text/css">
    <!--
        P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
        .ENCC {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
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


@pytest.fixture(scope="session")
def sample_sami_with_p_align():
    return """
<SAMI>
<HEAD>
    <STYLE TYPE="Text/css">
    <!--
        P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
        .ENCC {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
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


@pytest.fixture(scope="session")
def sample_sami_with_p_and_span_align():
    return """
<SAMI>
<HEAD>
    <STYLE TYPE="Text/css">
    <!--
        P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
        .ENCC {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
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


@pytest.fixture(scope="session")
def sample_sami_with_multiple_span_aligns():
    return """
<SAMI>
<HEAD>
    <STYLE TYPE="Text/css">
    <!--
        P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
        .ENCC {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
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


@pytest.fixture(scope="session")
def sample_sami_no_lang():
    return """
<SAMI>
<Head><STYLE TYPE="text/css"></Style></Head>
<BODY>
<Sync Start=0><P Class=ENCC></p></sync>
<Sync Start=1301><P Class=ENCC>>> FUNDING FOR OVERHEARD</p></sync>
</Body>
</SAMI>
"""


@pytest.fixture(scope="session")
def sample_sami_with_lang():
    return """
<sami>
<head>
<style type="text/css"><!--.en-US {lang: en-US;}--></style>
</head>
<body>
<sync start="1301"><p class="en-US">&gt;&gt; FUNDING FOR OVERHEARD</p></sync>
</body>
</sami>
"""


@pytest.fixture(scope="session")
def sample_sami_with_multi_lang():
    return """
<sami>
<head>
<style type="text/css"><!--.en-US {lang: en-US;} .de-DE {lang: de-DE;}--></style>
</head>
<body>
<sync start="14848">
    <p class="en-US">Butterfly.</p>
    <p class="de-DE">Schmetterling.</p>
</sync>
</body>
</sami>
"""


@pytest.fixture(scope="session")
def sample_sami_with_multiple_p():
    return """
<SAMI>
<HEAD>
    <STYLE TYPE="Text/css">
    <!--
        P {font-size: 24pt; text-align: center; font-family: Tahoma; font-weight: bold; color: #FFFFFF; background-color: #000000;}
        .ENCC {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
    -->
    </STYLE>
</HEAD>
<BODY>
    <SYNC start="133">
        <P class="ENCC" Style="text-align:right;">
            1st paragraph.
        </P>
        <P class="ENCC" Style="text-align:left;">
           2nd paragraph.
        </P>
    </SYNC>
    <SYNC start="1337">
        <P class="ENCC" Style="text-align:right;">
            3rd paragraph.
        </P>
    </SYNC>
</BODY>
</SAMI>
"""


@pytest.fixture(scope="session")
def sample_sami_empty_cue_output():
    return """
<sami>
 <head>
  <style type="text/css">
   <!--
    .en-US {
     lang: en-US;
    }
   -->
  </style>
 </head>
 <body>
  <sync start="1209">
   <p class="en-US">
    abc
   </p>
  </sync>
 </body>
</sami>
"""


@pytest.fixture(scope="session")
def sample_sami_with_invalid_inline_style():
    return """
<SAMI><HEAD>
    <STYLE TYPE="text/css">
    <!--
        .ENCC {Name: 'Subtitles'; Lang: en-US; SAMIType: CC; margin-top: 20px; margin-right: 20px; margin-bottom: 20px; margin-left: 20px;}
    -->
    </STYLE></HEAD>
<BODY>
    <SYNC start="133">
        <P class="ENCC" Style="text-align:right:font-style:italic">
            Some say we have this vision of Einstein as an old, wrinkly man
        </P>
    </SYNC>
</BODY></SAMI>
"""


@pytest.fixture(scope="session")
def sample_sami_including_hexadecimal_charref():
    return """
<SAMI><HEAD><STYLE TYPE="text/css">
<!--
.ENCC {Name: English; lang: en-US; SAMI_Type: CC;}
--></STYLE></HEAD><BODY>
<SYNC start="101"><P class="ENCC">&#x3E; &#x3E;</P></SYNC>
</BODY></SAMI>
"""


@pytest.fixture(scope="session")
def sample_sami_including_decimal_charref():
    return """
<SAMI><HEAD><STYLE TYPE="text/css">
<!--
.ENCC {Name: English; lang: en-US; SAMI_Type: CC;}
--></STYLE></HEAD><BODY>
<SYNC start="101"><P class="ENCC">&#62; &#62;</P></SYNC>
</BODY></SAMI>
"""


@pytest.fixture(scope="session")
def sample_sami_including_html5_entityref():
    return """
<SAMI><HEAD><STYLE TYPE="text/css">
<!--
.ENCC {Name: English; lang: en-US; SAMI_Type: CC;}
--></STYLE></HEAD><BODY>
<SYNC start="1301"><P class="ENCC">&starf;_&starf;</P></SYNC>
</BODY></SAMI>
"""


@pytest.fixture(scope="session")
def sample_sami_with_unclosed_tag():
    return """
<SAMI><HEAD><STYLE TYPE="text/css">
<!--
.ENCC {Name: English; lang: en-US; SAMI_Type: CC;}
--></STYLE></HEAD><BODY>
<SYNC start="1101"><P class="ENCC">.</P></SYNC>
</BODY>
"""


@pytest.fixture(scope="session")
def sample_sami_with_inline_lang():
    return """
<SAMI><HEAD></HEAD><BODY>
<SYNC start="1201"><P lang="en-US">Inlined.</P></SYNC>
</BODY></SAMI>
"""


# we do not seem to support nested spans, update this if fixed.
@pytest.fixture(scope="session")
def sample_sami_from_dfxp_with_nested_spans():
    return """<sami>
 <head>
  <style type="text/css">
   <!--
    .s1 {
     font-style: italic;
    }
    .s2 {
     font-weight: bold;
    }
    .s3 {
     text-decoration: underline;
    }
    .en-US {
     lang: en-US;
    }
   -->
  </style>
 </head>
 <body>
  <sync start="3209">
   <p class="en-US">
    That is  <span class="s3" style="classes:['s3'];class:s3;"></span> <span class="s2" style="classes:['s2'];class:s2;"></span> <span class="s1" style="classes:['s1'];class:s1;">nested</span> .
   </p>
  </sync>
 </body>
</sami>"""


@pytest.fixture(scope="session")
def sample_sami_with_separate_multi_lang():
    return """<sami>
 <head>
  <style type="text/css">
   <!--
    .en-UK {
     lang: en-UK;
    }
    .en-US {
     lang: en-US;
    }
   -->
  </style>
 </head>
 <body>
  <sync start="1209">
   <p class="en-UK">
    British text.
   </p>
  </sync>
  <sync start="3209">
   <p class="en-US">
    English text.
   </p>
  </sync>
  <sync start="7209">
   <p class="en-UK">
    OTHER British text.
   </p>
  </sync>
 </body>
</sami>
"""


@pytest.fixture(scope="session")
def sample_sami_missing_start():
    return """
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
    <SYNC><P class="ENCC">
           ( clock ticking )
    </P></SYNC>
    </BODY></SAMI>
    """