py-caption
==========

`py-caption` is a caption reading/writing module. Use one of the given Readers to read content into an intermediary format known as PCC (PBS Common Captions), and then use one of the Writers to output the PCC into captions of your desired format.

Turn a caption into multiple caption outputs:

    srt_caps = '''1
    00:00:09,209 --> 00:00:12,312
    This is an example SRT file,
    which, while extremely short,
    is still a valid SRT file.
    '''
    
    converter = CaptionConverter()
    converter.read(srt_caps, SRTReader())
    print converter.write(SAMIWriter())
    print converter.write(DFXPWriter())
    print converter.write(TranscriptWriter())
    
Not sure what format the caption is in? Detect it:

    caps = '''1
    00:00:01,500 --> 00:00:12,345
    Small caption'''

    if SRTReader().detect(caps):
        print SAMIWriter().write(SRTReader().read(caps))
    elif DFXPReader().detect(caps):
        print SAMIWriter().write(DFXPReader().read(caps))
    elif SCCReader().detect(caps):
        print SAMIWriter().write(SCCReader().read(caps))

Supported Formats
-----------------

Read:
 - SCC
 - SAMI
 - SRT
 - DFXP

Write:
 - DFXP
 - SAMI
 - SRT
 - Transcript

See the [examples folder][1] for example captions that currently can be read correctly.

Python Usage
------------ 

Example: Convert from SAMI to DFXP

    from pycaption import SAMIReader, DFXPWriter

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


Scalability
-----------

Different readers and writers are easy to add if you would like to:
 - Read/Write a previously unsupported format
 - Read/Write a supported format in a different way (more styling?)
 
Simply follow the format of a current Reader or Writer, and edit to your heart's desire.


PyCaps Format:
------------------

The different Readers will return the captions in PBS Common Captions (PCC) format.
The Writers will be expecting captions in PCC format as well.

PCC format:

    {
        "captions": {
            lang: list of captions
        }
        "styles":{
            style: styling
        }
    }

Example PCC json:

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
        },
        "styles": {
                "encc": {
                    "lang": "en-US"
                },
                "p": {
                    "color": "#fff",
                    "font-size": "10pt",
                    "font-family": "Arial",
                    "text-align": "center"
                }
        }
    }


SAMI Reader / Writer :: [spec][2]
--------------------

Microsoft Synchronized Accessible Media Interchange. Supports multiple languages.

Supported Styling:
 - text-align
 - italics
 - font-size
 - font-family
 - color

If the SAMI file is not valid XML (e.g. unclosed tags), will still attempt to read it.


DFXP Reader / Writer :: [spec][3]
--------------------

The W3 standard. Supports multiple languages.

Supported Styling:
 - text-align
 - italics
 - font-size
 - font-family
 - color


SRT Reader / Writer :: [spec][4]
-------------------

SubRip captions. If given multiple languages to write, will output all joined together by a 'MULTI-LANGUAGE SRT' line.

Supported Styling:
 - None

Assumes input language is english. To change:

    pycaps = SRTReader().read(srt_content, lang='fr')


SCC Reader :: [spec][5]
----------

Scenarist Closed Caption format. Assumes Channel 1 input.

Supported Styling:
 - italics

By default, the SCC Reader does not simulate roll-up captions. To enable roll-ups:

    pycaps = SCCReader().read(scc_content, simulate_roll_up=True)

Also, assumes input language is english. To change:

    pycaps = SCCReader().read(scc_content, lang='fr')

Now has the option of specifying an offset (measured in seconds) for the timestamp. For example, if the SCC file is 45 seconds ahead of the video:

    pycaps = SCCReader().read(scc_content, offset=45)

The SCC Reader handles both dropframe and non-dropframe captions, and will auto-detect which format the captions are in.


Transcript Writer
-----------------

Text stripped of styling, arranged in sentences.

Supported Styling:
 - None

The transcript writer uses natural sentence boundary detection algorithms to create the transcript.

To use the transcript writer, the appropriate Punkt tokenizer info must be downloaded. From python, run this code:

    import nltk
    nltk.download()
    

License
-------

This module is Copyright 2012 PBS.org and is available under the [Apache License, Version 2.0][6].

[1]: https://github.com/pbs/pycaption/tree/master/examples/
[2]: http://msdn.microsoft.com/en-us/library/ms971327.aspx
[3]: http://www.w3.org/TR/ttaf1-dfxp/
[4]: http://matroska.org/technical/specs/subtitles/srt.html
[5]: http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/SCC_FORMAT.HTML
[6]: http://www.apache.org/licenses/LICENSE-2.0