py-caption
==========

`py-caption` is a caption reading/writing module. Use one of the given Readers to read content into an intermediary format known as CCG (Closed Caption Generic), and then use one of the Writers to output the CCG into captions of your desired format.

Turn a caption into multiple caption outputs:

    srt_caps = '''1
    00:00:09,209 --> 00:00:12,312
    This is an example SRT file,
    which, while extremely short,
    is still a valid SRT file.
    '''
    
    converter = CaptionConverter()
    converter.read(srt_caps)
    converter.write(SAMIWriter())
    converter.write(DFXPWriter())
    converter.write(TranscriptWriter())
    
Not sure what format the caption is in? Detect it:

    if SRTReader().detect(caps):
        sami = SAMIWriter().write(SRTReader().read(caps))
    elif DFXPReader().detect(caps):
        sami = SAMIWriter().write(DFXPReader().read(caps))
    elif SCCReader().detect(caps):
        sami = SAMIWriter().write(SCCReader().read(caps))

Supported Formats
-----------------

Read:
 - SCC
 - SRT
 - SAMI
 - DFXP

Write:
 - Transcript
 - SRT
 - SAMI
 - DFXP

See the [examples folder][1] for example captions that currently can be read correctly.

Python Usage
------------ 

Example: Convert from SAMI to DFXP

    from pycaption.sami import SAMIReader
    from pycaption.dfxp import DFXPWriter
    
    sami = '''<SAMI><HEAD><TITLE>NOVA3213</TITLE><STYLE TYPE="text/css">
    <!--
    P {	margin-left:  1pt;
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

    <?xml version="1.0" encoding="utf-8"?>
    <tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml">
     <head>
      <styling xmlns:tts="http://www.w3.org/ns/ttml#styling">
       <style id="p" tts:color="#fff" tts:fontfamily="Arial" tts:fontsize="10pt" tts:textAlign="center"/>
      </styling>
     </head>
     <body id="p">
      <div xml:lang="fr-cc">
       <p begin="00:00:09.209" end="00:00:14.848">
        FRENCH LINE 1!
       </p>
       <p begin="00:00:14.848" end="00:00:18.848">
        FRENCH LINE 2?
       </p>
      </div>
      <div xml:lang="en-US">
       <p begin="00:00:09.209" end="00:00:12.312">
        ( clock ticking )
       </p>
       <p begin="00:00:14.848" end="00:00:18.848">
        MAN:<br/>
        <span tts:textAlign="center" tts:fontsize="10">When <span tts:fontStyle="italic">we</span> think</span><br/>
        of E equals m c-squared,
       </p>
      </div>
     </body>
    </tt>


Scalability
-----------

Different readers and writers are easy to add if you would like to:
 - Read/Write a previously unsupported format
 - Read/Write a supported format in a different way (more styling?)
 
Simply follow the format of a current Reader or Writer, and edit to your heart's desire.


Transcript Usage
----------------

The transcript writer uses natural sentence boundary detection algorithms to create the transcript.

To use the transcript writer, the appropriate Punkt tokenizer info must be downloaded.

From python, run this code:

    import nltk
    nltk.download()


PyCaps Format:
------------------

The different Readers will return the captions in Closed Caption Generic (CCG) format.
The Writers will be expecting captions in CCG format as well.

CCG format:

    {
        "captions": {
            lang: list of captions
        }
        "styles":{
            style: styling
        }
    }

Example CCG json:

    {
        "captions": {
            "en": [
                [
                    9209000,
                    12312000,
                    [
                        {"type": "text", "content": "Line 1"},
                        {"type": "break"},
                        {"type": "style", "start": True, "content": {"italics": True}},
                        {"type": "text", "content": "Line 2"},
                        {"type": "style", "start": False, "content": {"italics": True}}
                    ],
                    {
                        "class": "encc",
                        "text-align": "right"
                    }
                ],
                [
                    14556000,
                    18993000,
                    [
                        {"type": "text", "content": "Line 3, all by itself"}
                    ],
                    {
                        "class": "encc",
                        "italics": True
                    }
                ]
            ]
        }
        "styles": {
                ".encc": {
                    "lang": "en-US",
                    "style": {
                        "lang": "en-US"
                    }
                },
                "p": {
                    "lang": "None",
                    "style": {
                        "color": "#fff",
                        "font-size": "10pt",
                        "font-family": "Arial",
                        "text-align": "center"
                    }
                }
        }
    }


SAMI Reader / Writer :: [spec][2]
--------------------

Supported Styling:
 - text-align
 - italics
 - font-size
 - font-family
 - color
 
If the SAMI file is not valid XML (e.g. unclosed tags), will still attempt to read it.


DFXP Reader / Writer :: [spec][3]
--------------------

Supported Styling:
 - text-align
 - italics
 - font-size
 - font-family
 - color


SRT Reader / Writer :: [spec][4]
-------------------

Supported Styling:
 - None
 

SCC Reader :: [spec][5]
----------

Supported Styling:
 - italics


Transcript Writer
-----------------
Supported Styling:
 - None


License
-------

This module is Copyright 2012 PBS.org and is available under the [Apache License, Version 2.0][6].

[1]: https://github.com/pbs/pycaption/blob/master/examples/
[2]: http://msdn.microsoft.com/en-us/library/ms971327.aspx
[3]: http://www.w3.org/TR/ttaf1-dfxp/
[4]: http://matroska.org/technical/specs/subtitles/srt.html
[5]: http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/SCC_FORMAT.HTML
[6]: http://www.apache.org/licenses/LICENSE-2.0