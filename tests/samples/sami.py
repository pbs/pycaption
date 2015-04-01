# -*- coding: utf-8 -*-

SAMPLE_SAMI_UNICODE = u"""
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


SAMPLE_SAMI_UTF8 = """
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
    ♪ ...say bow, wow, ♪
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
    of "E equals m c-squared",
</P></SYNC>
<SYNC start="17000"><P class="ENCC">



  <SPAN Style="text-align:right;">we have this vision of Einstein</SPAN>
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
<SYNC start="26760"><P class="ENCC">
    MAN 2:<br/>
    It's all about an eternal Einstein.
</P></SYNC>
<SYNC start="32200"><P class="ENCC">
    &lt;LAUGHING &amp; WHOOPS!&gt;
</P></SYNC>
<SYNC start="34400">
<P class="ENCC"><br/>some more text
</P>
</SYNC>
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
