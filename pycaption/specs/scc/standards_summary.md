# SCC Technical Standards Reference

**Source Documents:**
- ANSI/CTA-608-E S-2019 (CEA-608): Line 21 Data Services  
- ANSI/CTA-708-E R-2018 (CEA-708): Digital Television (DTV) Closed Captioning

**Purpose:** Complete technical specification for SCC format compliance checking.

---

# Part 1: CEA-608 Line 21 Data Services

## 1.1 Signal Characteristics

### Line 21 Waveform Specification

2.1 Normative References
CEA-542-B, Cable Television Channel Identification Plan, July 2003

ECMA 262, Script language specification (June, 1997)

FIPS PUB 6-4, Counties and Equivalent Entities of the United States, Its Possessions, and Associated
Areas, 8/31/90

IEC 61880-2: (2002-09) Video System (525/60) Video and Accompanied Data Using the Vertical Blanking
Interval -- Part 2 525 Progressive Scan System

IEC 61880: (1998-01), Video System (525/60) Video and Accompanied Data Using the Vertical Blanking
Interval -- Analogue Interface

ANSI/IEEE 511:1979, Standard on Video Signal Transmission Measurement of Linear Waveform
Distortion

IETF RFC 791, Internet Protocol: DARPA Internet Program—Protocol Specification

IETF RFC 1071, Computing the Internet Checksum

IETF RFC 1738, Uniform Resource Locators (URL), (December, 1984)

ISO-8859-1: 1987, Information processing—8-bit single-byte coded graphic character sets – Part 1: Latin
alphabet No. 1

ISO-8601: 1988, Data elements and interchange formats - Information interchange - Representation of
dates and times

2.2 Informative References

ATSC A/53E, ATSC Digital Television Standard, With Amendment 1, April 18, 2006

ATSC A/65C, Program and System Information Protocol for Terrestrial Broadcast and Cable, With
Amendment No. 1, May 9, 2006

CEA-708-C, Digital Television (DTV) Closed Captioning, July, 2006

CEA-766-C, U.S. Region Rating Table (RRT) and Content Advisory Descriptor for Transport of Content
Advisory Information using ATSC Program and System Information Protocol (PSIP), July, 2006

Federal Communications Commission, R&O FCC 98-35,
http://www.fcc.gov/Bureaus/Cable/Orders/1998/fcc98035.html

Federal Communications Commission, R&O FCC 98-36,
http://www.fcc.gov/Bureaus/Engineering_Technology/Orders/1998/fcc98036.html

CRTC letter decision, Public Notice CRTC 1996-36, Respecting Children: A Canadian Approach to
Helping Families Deal with Television Violence,
(English) http://www.crtc.gc.ca/archive/ENG/Notices/1996/PB96-36.HTM
(French) http://www.crtc.gc.ca/archive/FRN/Notices/1996/PB96-36.HTM

                                                      2
                                                                                            CEA-608-E



CRTC letter decision, Public Notice CRTC 1997-80, Classification System for Violence in Television
Programming
(English) http://www.crtc.gc.ca/archive/ENG/Notices/1997/PB97-80.HTM
(French) http://www.crtc.gc.ca/archive/FRN/Notices/1997/PB97-80.HTM

SMPTE 12-1999, Television, Audio and Film—Time and Control Code

SMPTE 170-2004, Composite Analog Video Signal – NTSC for Studio Applications

SMPTE 331-2004, Television – Element and Metadata Definitions for the SDTI-CP

SMPTE EG-43-2004, System Implementation of CEA-708-B and CEA-608-B Closed Captioning
2.3 Regulatory References
47 C.F.R. 15.119, Closed Caption Decoder Requirement for Television Receivers

47 C.F.R. 15.120, Program Technology Blocking Requirements for Television Receivers
2.4 Antecedent References
EIA-702, Copy Generation Management System (Analog) (1997)

EIA-744-A, Transport of Content Advisory Information using Extended Data Service (XDS) (1998)

EIA-745, Transport of Cable Channel Mapping System Information using Extended Data Service (XDS),
1997

EIA-746-A, Transport of Internet Uniform Resource Locator (URL) Information Using Text-2 (T-2) Service
(1998)

EIA-752, Transport of Transmission Signal Identifier (TSID) Using Extended Data Service (XDS) (1998)

EIA-806, Transport of ATSC PSIP Information to Affiliate Broadcast Stations Using Extended Data
Service (XDS) (2000)

        NOTE—The topic discussed in EIA-806 has been removed from CEA-608-E.
2.5 Reference Acquisition
ANSI/CEA/EIA Standards:
• Global Engineering Documents, World Headquarters, 15 Inverness Way East, Englewood, CO USA
    80112-5776; Phone 800.854.7179; Fax 303.397.2740; Internet http://global.ihs.com ; Email
    global@ihs.com

SMPTE Standards:
• Society of Motion Picture & Television Engineers, 595 W. Hartsdale Ave., White Plains, NY 10607-
  1824 USA Phone: 914.761.1100 Fax: 914.761.3115; Email: eng@smpte.org; Internet
  http://www.smpte.org

ATSC Standards:
• Advanced Television Systems Committee (ATSC), 1750 K Street N.W., Suite 1200, Washington, DC
   20006; Phone 202.828.3130; Fax 202.828.3131; Internet http://www.atsc.org/standards.html

ECMA Standards:
• European Computer Manufacturers Association (ECMA), 114 Rue du Rhône, CH1204 Geneva,
  Switzerland; Internet http://www.ecma-international.org/publications/index.html

FCC
• FCC Regulations, U.S. Government Printing Office, Washington, D.C. 20401; Internet
   http://www.access.gpo.gov/cgi-bin/cfrassemble.cgi?title=199847
                                                   3
CEA-608-E



FIPS Standards:
• National Institute of Standards and Technology and Information Technology, U.S. Government
   Printing Office, Washington, D.C. 2040; http://www.itl.nist.gov/fipspubs/

IETF Standards:
• Internet Engineering Task Force (IETF), c/o Corporation for National Research Initiatives, 1895
   Preston White Drive, Suite 100, Reston, VA 20191-5434 USA; Phone 703-620-8990; Fax 703-758-
   5913; Email ietf-info@ietf.org ; Internet http://www.ietf.org/rfc/rfc0791.txt?number=791 and
   http://www.ietf.org/rfc/rfc1071.txt?number=1071

IEC and ISO Standards:
• Global Engineering Documents, World Headquarters, 15 Inverness Way East, Englewood, CO USA
   80112-5776; Phone 800-854-7179; Fax 303-397-2740; Internet http://global.ihs.com ; Email
   global@ihs.com
• ISO Central Secretariat, 1, rue de Varembe, Case postale 56, CH-1211 Genève 20, Switzerland;
   Phone + 41 22 749 01 11; Fax + 41 22 733 34 30; Internet http://www.iso.ch ; Email central@iso.ch




                                                  4
                                                                                                       CEA-608-E




3 Definitions
3.1 Definitions
With respect to definition of terms, abbreviations and units, the practice of the Institute of Electrical and
Electronics Engineers (IEEE) as outlined in the Institute’s published standards shall be used. Where an
abbreviation is not covered by IEEE practice or CEA-608-E practice differs from IEEE practice, then the
abbreviation in question is described in Section 3.2.1 or 3.2.2.
3.2 Terms Employed
3.2.1 Acronyms 1
AC            Article Clear
AE            Article End
ANE           Article Name End
ANS           Article Name Start
AOF           Reserved (formerly Alarm Off)
AON           Reserved (formerly Alarm On)
ANSI          American National Standards Institute
ASB           Analog Source Bit
ASCII         American Standard Code for Information Interchange
APS           Analog Protection System
ANSI          American National Standards Institute
ATSC          Advanced Television Systems Committee
BS            Backspace
CEA           Consumer Electronics Association
CGMS          Copy Generation Management System
CR            Carriage Return
CRTC          Canadian Radio-television and Telecommunications Commission
DER           Delete to End of Row
DVR           Digital Video Recorder
ECMA          European Computer Manufacturers Association
EDM           Erase Displayed Memory
EIA           Electronic Industries Alliance
ENM           Erase Non-Displayed Memory
EOC           End of Caption
FCC           Federal Communications Commission
FIPS          Federal Information Processing Standard
FON           Flash On
IEC           International Electrotechnical Commission
IEEE          Institute of Electrical and Electronics Engineers
IETF          Internet Engineering Task Force
IRE           Institute of Radio Engineers
ISO           International Organization for Standardization
NRZ           Non-Return-to-Zero
NTSC          National Television Standards Committee
PAC           Preamble Address Code
PSP           Pseudo Sync Pulse
RCD           Redistribution Control Descriptor
RCL           Resume Caption Loading
RDC           Resume Direct Captioning
RTD           Resume Text Display
RU2           Roll Up Captions 2 Rows
RU3           Roll Up Captions 3 Rows
RU4           Roll Up Captions 4 Rows
SMPTE         Society of Motion Picture and Television Engineers

1
  While some commands are included in Section 3.2.1, a complete list of commands may be found in 47 C.F.R.
§15.119.
                                                         5
CEA-608-E


TC1              TeleCaption I
TC2              TeleCaption II
TO1              Tab Offset 1 Column
TO2              Tab Offset 2 Columns
TO3              Tab Offset 3 Columns
TR               Text Restart
TSID             Transmission Signal Identifier
URL              Uniform Resource Locator
UTC              Coordinated Universal Time 2
XDS              eXtended Data Service
3.2.2 Glossary (Informative)
Base Row: The bottom row of a roll-up display. The cursor always remains on the base row. Rows of text
roll upward into the contiguous rows immediately above the base row.

Box: The area surrounding the active character display. In Text Mode, the box is the entire screen area
defined for display, whether or not displayable characters appear. In Caption Mode, the box is dynamically
redefined by each caption and each element of displayable characters within a caption. The box (or boxes,
in the case of a multiple-element caption) includes all the cells of the displayed characters, the non-
transparent spaces between them, and one cell at the beginning and end of each row within a caption
element in those decoders which use a solid space to improve legibility.

Character: A single group of 7 data bits plus a parity symbol.

Captioning: Textual representation of program dialogue that may include other program descriptions.

Caption File: A computer file that defines the captions used by a captioning encoder.

Captioning Diskette: A computer diskette with a caption file written on it. This file has captioning data
used by an encoder to insert captions.

Captioning Sync: The timing relationship between the picture and the appearance of captions on that
picture. See Section E.2.

Caption Master Tape: The earliest videotape generation of a production on which captions have been
recorded.

Cell: The discrete screen area in which each displayable character or space may appear. A cell is one row
high and one column wide.

Channel Grazing: When a viewer changes channels frequently to search for a desired show.

Channel Surfing: When a viewer changes channels frequently to search for a desired show.

Column: One of 32 vertical divisions of the screen, each of equal width, extending approximately across
the full width of the Safe Caption Area (see also). Two additional columns, one at the left of the screen and
one at the right, may be defined for the appearance of a box in those decoders which use a solid space to
improve legibility, but no displayable characters may appear in those additional columns. For reference,


## 1.2 Caption Character Sets

### 1.2.1 Standard ASCII-Based Characters (0x20-0x7F)

```

                                                         58
                                                                                                   CEA-608-E


Annex A Character Set Differences (Informative)
Table lists all characters between 0x20 and 0x7E in both the ISO8859-1 and CEA-608-E character sets.
The final column includes a bullet ("•") for character codes which differ in their interpretations in the two
sets.

         Character code      ISO-8859-1 character         CEA-608-E character          Different
         20                  [space]                      [space]
         21                  !                            !
         22                  "                            "
         23                  #                            #
         24                  $                            $
         25                  %                            %
         26                  &                            &
         27                  '                            '
         28                  (                            (
         29                  )                            )
         2A                  *                            Á                            •
         2B                  +                            +
         2C                  ,                            ,
         2D                  -                            -
         2E                  .                            .
         2F                  /                            /
         30                  0                            0
         31                  1                            1
         32                  2                            2
         33                  3                            3
         34                  4                            4
         35                  5                            5
         36                  6                            6
         37                  7                            7
         38                  8                            8
         39                  9                            9
         3A                  :                            :
         3B                  ;                            ;
         3C                  <                            <
         3D                  =                            =
         3E                  >                            >
         3F                  ?                            ?
         40                  @                            @
         41                  A                            A
         42                  B                            B
         43                  C                            C
         44                  D                            D
         45                  E                            E
         46                  F                            F
         47                  G                            G
         48                  H                            H
         49                  I                            I
         4A                  J                            J
         4B                  K                            K
         4C                  L                            L
         4D                  M                            M
         4E                  N                            N

                    Table 45 ISO 8859-1 and CEA-608-E Character Set Differences




                                                     59
CEA-608-E


       Character code    ISO-8859-1 character        CEA-608-E character   Different
       4F                O                           O
       50                P                           P
       51                Q                           Q
       52                R                           R
       53                S                           S
       54                T                           T
       55                U                           U
       56                V                           V
       57                W                           W
       58                X                           X
       59                Y                           Y
       5A                Z                           Z
       5B                [                           [
       5C                \                           É                     •
       5D                ]                           ]
       5E                '                           Í                     •
       5F                _                           Ó                     •
       60                `                           Ú                     •
       61                a                           a
       62                b                           b
       63                c                           c
       64                d                           d
       65                e                           e
       66                f                           f
       67                g                           g
       68                h                           h
       69                i                           i
       6A                j                           j
       6B                k                           k
       6C                l                           l
       6D                m                           m
       6E                n                           n
       6F                o                           o
       70                p                           p
       71                q                           q
       72                r                           r
       73                s                           s
       74                t                           t
       75                u                           u
       76                v                           v
       77                w                           w
       78                x                           x
       79                y                           y
       7A                z                           z
       7B                {                           Ç                     •
       7C                |                           ÷                     •
       7D                }                           Ñ                     •
       7E                ~                           Ñ                     •
            Table 45 ISO 8859-1 and CEA-608-E Character Set Differences (Continued)



```

### 1.2.2 Special Characters

```
   1      XX     XX     Caption Data-1       1       --      --    One Frame Delay   Input Analysis
   2      OO     OO     Nulls                2       --      --    Two Frame Delay   Output Response
   3      OO     OO     Nulls                3       XX     XX     Caption Data-1
   4      OO     OO     Nulls                4       01     03     XDS "Start"                   XDS "Type"
   5      OO     OO     Nulls                5       53     74     XDS Char.                     XDS Char.
   6      OO     OO     Nulls                6       61     72     XDS Char.                     XDS Char.
   7      OO     OO     Nulls                7       20     54     XDS Char.                     XDS Char.
   8      XX     XX     Caption Data-2       8       72     65     XDS Char.                     XDS Char.
   9      XX     XX     Caption Data-3       9       14     26     "Caption Ch-1"        "RU3"
                                                                                     *
  10     XX      XX     Caption Data-4      10      XX      XX     Caption Data-2
  11     XX      XX     Caption Data-5      11      XX      XX     Caption Data-3
  12     XX      XX     Caption Data-6      12      XX      XX     Caption Data-4
  13     XX      XX     Caption Data-7      13      XX      XX     Caption Data-5
  14     XX      XX     Caption Data-8      14      XX      XX     Caption Data-6
  15     OO      OO     Nulls               15      XX      XX     Caption Data-7
  16     OO      OO     Nulls               16      XX      XX     Caption Data-8
  17     XX      XX     Caption Data-9      17      02      03     XDS "Continue"        XDS "Type"
  18     XX      XX     Caption Data-10     18      14      26     "Caption Ch-1"        "RU3"
                                                                                     *
  19     XX      XX     Caption Data-11     19      XX      XX     Caption Data-9
  20     XX      XX     Caption Data-12     20      XX      XX     Caption Data-10
  21     XX      XX     Caption Data-13     21      XX      XX     Caption Data-11
  22     XX      XX     Caption Data-14     22      XX      XX     Caption Data-12
  23     OO      OO     Nulls               23      XX      XX     Caption Data-13
  24     XX      XX     Caption Data-15     24      XX      XX     Caption Data-14
  25     XX      XX     Caption Data-16     25      14      26     "Caption Ch-1"        "RU3"
                                                                                     *
  26     XX      XX     Caption Data-17     26      XX      XX     Caption Data-15
  27     XX      XX     Caption Data-18     27      XX      XX     Caption Data-16
  28     XX      XX     Caption Data-19     28      XX      XX     Caption Data-17
  29     OO      OO     Nulls               29      XX      XX     Caption Data-18
  30     OO      OO     Nulls               30      XX      XX     Caption Data-19
  31     OO      OO     Nulls               31      02      03     XDS "Continue"        XDS "Type"
  32     OO      OO     Nulls               32      6B      00     XDS char.                     XDS char.
  33     OO      OO     Nulls               33      0F      1D     XDS "End"                      Checksum
  34     OO      OO     Nulls               34      14      26     "Caption Ch-1"        "RU3"
                                                                                     *
  35     XX      XX     Caption Data-20     35      OO      OO     Nulls
  36     XX      XX     Caption Data-21     36      OO      OO     Nulls
                                            37      XX      XX     Caption Data-20
                                            38      XX      XX     Caption Data-21

* This assumes that the mode prior to the XDS transmission was "Capt 1", "RU3"
                       Table 13 Example—Hexadecimal Character Sequence
8.6.5 Multiple Interleave
XDS packets may be interleaved within one another; however, it is strongly recommended that no more
than one level of interleaving be used. This is because most decoders do not support more than two
incoming data buffers.
8.6.6 Packet Length
Each complete packet shall have no more than 32 Informational characters.
8.6.7 Packet Suspension
A packet may be suspended or interrupted by another packet type.

A packet may be suspended or interrupted by resuming a caption or Text transmission.
8.6.8 Packet Termination
A packet may be aborted or terminated by beginning another packet of the same class and type.



                                                   35
CEA-608-E

9 XDSPackets
9.1 Introduction
XDS mode is a third data service on field 2 intended to supply program related and other information to
the viewer.

As an adjunct to program identification, XDS provides the transport mechanism to identify advisories
about mature program content, intended to help consumers make appropriate viewing choices.

When fully implemented, the XDS data can be displayed on a decoder-equipped television to inform the
viewer of such information as current program title, length of show, type of show, time in show, (or time
left) and several other pieces of program-related information. This information may be particularly
valuable during commercials so viewers who change channels rapidly can identify XDS encoded
programs without the aid of a guide.

During specially prepared promos, the Impulse Capture function can be used to program decoder-
equipped VCRs and Digital Video Recorders (DVR) automatically. Future program and weather alert
information may also be displayed.

Program ID’s transmitted during commercials can be used to capture viewers who do not know what
program is scheduled for that channel.

This section defines and identifies kinds of packets to be used for the XDS of line 21, field 2.

The encoder operation for XDS is described in Section 9.6.

Unused bits are designated by “-” in format charts and should be set to logical 0. Reserved bits (for future
use) are designated by “Re” in format charts and shall be set to 0 until assigned.

Unless otherwise stated, channel numbers in packet data fields are referenced to CEA-542-B.

Information provided by one packet should not be added into any other packets, except as explicitly
provided in Section 9.5.1.10 or 9.5.1.11. This avoids sending redundant or conflicting data (e.g., A movie
rating should not be included as part of a program name packet.).
9.2 General Use
Each packet can have different refresh or repetition rates. General recommendations and guidelines for
packet repetition rates are given in Annex E.7.3.

While many packets are currently defined with fewer than 32 Informational characters, functions may be
added at a future point that could extend the definition and length of each packet. Such extensions shall
be added after the existing Informational characters (up to a maximum of 32) and can be ignored by
products designed prior to definition.

A receiver should continue to receive and verify packets that may be longer than initially defined.

There is no provision (or need) to "erase" or delete data sent previously. Updated or new information
simply replaces or supersedes old information. Changes in certain packets can clear several packets.

A packet is first begun by sending a Start/Type character pair. This pair would then be followed by
Informational/Informational character pairs until all the informational characters in the packet have been
sent, or until the packet is interrupted by captioning, Text, or another packet.

To resume sending a previously started packet, the Continue/Type character pair should be sent.

When resuming a packet, the Type code used with the Continue code shall be identical to the Type code
used with the Start code.



                                                     36
                                                                                                CEA-608-E

To end a packet, the End/Checksum pair shall be used. There is only one code for end, it is used to end
all packets and therefore always pertains to the currently active packet.

While some packets have a variable length, the formatting of the XDS packets requires that there always
be an even number of informational characters. If the contents of the information require an odd number
of characters, a standard null character (0x00) shall be added after the last character to achieve an even
number.
9.3 XDS Packet Control Codes
Six classes of packets are defined: Current, Future, Channel Information, Miscellaneous, Public Service,
and Reserved. In addition, a Private Data class has been included.

Each packet within the class may exist independently.

Table 14 lists the use of the assigned control codes.

                          Control Code             Function               Class
                             0x01                    Start               Current
                             0x02                  Continue              Current
                             0x03                    Start                Future
                             0x04                  Continue               Future
                             0x05                    Start               Channel
                             0x06                  Continue              Channel
                             0x07                    Start            Miscellaneous
                             0x08                  Continue           Miscellaneous
                             0x09                    Start            Public Service
                             0x0A                  Continue           Public Service
                             0x0B                    Start              Reserved
                             0x0C                  Continue             Reserved
                             0x0D                    Start             Private Data
                             0x0E                  Continue            Private Data
                             0x0F                    End                   ALL

                                  Table 14 Control Code Assignments
9.4 Class Definitions
The Current class is used to describe a program currently being transmitted.

The Future class is used to describe a program to be transmitted later.

The Channel Information class is used to describe non-program specific information about the
transmitting channel.

The Miscellaneous class is used to describe other information.

The Public Service class is used to transmit data or messages of a public service nature such as the
National Weather Service Warnings and messages.

The Reserved Class is reserved for future definition.

The Private Data Class is for use in any closed system for whatever that system wishes. It shall not be
defined by this standard now or in the future.

For each Class, there shall be two groups of similar packet types. Bit 6 is used as an indicator of these
two groups. When bit 6 of the Type character is set to 0 the packet shall only describe information relating
to the channel that carries the signal. This is known as an In-Band packet. When bit 6 of the Type
character is set to 1, the packet shall only contain information for another channel. This is known as an
Out-of-Band packet.

                                                    37
CEA-608-E

9.5 Type Definitions
9.5.1 Current Class
       9.5.1.1 Type=0x01 Program Identification Number
(Scheduled Start Time). This packet contains four characters that define the program start time and date
relative to UTC. This is binary data so b6 shall be set high (b6=1). The format of the characters is
identified in Table 15.

                          Character      b6     b5        b4        b3        b2        b1        b0

                          Minute         1      m5        m4        m3        m2        m1        m0

                          Hour           1      D         h4        h3        h2        h1        h0

                          Date           1      L         d4        d3        d2        d1        d0

                          Month          1      Z         T         m3        m2        m1        m0

                                       Table 15 Time/Date Coding

The minute field has a valid range of 0 to 59, the hour field from 0 to 23, the date field from 1 to 31, the
month field from 1 to 12. The "T" bit is used to indicate a program that is routinely tape delayed (for
Mountain and Pacific Time zones). The D, L, and Z bits are ignored by the decoder when processing this
packet. (The same format utilizes these bits for time setting, and the D, L and Z bits are defined in Section
9.5.4.1.) The T bit is used to determine if an offset is necessary because of local station tape delays. A
separate packet of the Channel Information Class shall indicate the amount of tape delay used for a given
time zone. When all characters of this packet contain all Ones, it indicates the end of the current program.

A change in received Current Class Program Identification Number is interpreted by XDS receivers as the
start of a new current program. All previously received current program information shall normally be
discarded in this case.
      9.5.1.2 Type=0x02 Length/Time-in-Show
This packet is composed of 2, 4 or 6 binary informational characters, so, with the exception of the Null
character, b6 shall be set high (b6=1). It is used to indicate the scheduled length of the program as well
as the elapsed time for the program. The first two informational characters are used to indicate the
program’s length in hours and minutes. The second two informational characters show the current time
elapsed by the program in hours and minutes. The final two informational characters extend the elapsed
time count with seconds.

The informational characters are encoded as indicated in Table 16.

           Character                                 b6        b5        b4        b3        b2        b1   b0

           Length - (m)                              1         m5        m4        m3        m2        m1   m0
           Length - (h)                              1         h5        h4        h3        h2        h1   h0

           Elapsed time - (m)                        1         m5        m4        m3        m2        m1   m0
           Elapsed time - (h)                        1         h5        h4        h3        h2        h1   h0

           Elapsed time - (s)                        1         s5        s4        s3        s2        s1   s0
           Null                                      0          0        0         0         0         0    0

                                      Table 16 Show Length Coding

The minute and second fields have a valid range of 0 to 59, and the hour fields from 0 to 23. The sixth
character is a standard null.




                                                         38
                                                                                                CEA-608-E

      9.5.1.3 Type=0x03 Program Name (Title)
This packet contains a variable number, 2 to 32, of Informational characters that define the program title.
Each character is in the range of 0x20 to 0x7F. The variable size of this packet allows for efficient
transmission of titles of any length up to 32 characters. A change in received Current Class Program

```

### 1.2.3 Extended Character Sets

```

                                                    39
CEA-608-E

The list of keywords is broken down into two groups. The first group consists of the codes 0x20 to 0x26
and is called the "BASIC" group. The second group contains the codes 0x27 to 0x7F and is called the
"DETAIL" group.

The Basic group is used to define the program at the highest level. All programs that use this packet shall
specify one or more of these codes to define the general category of the program. Programs which may
fit more than one Basic category are free to specify several of these keywords. The keyword "OTHER" is
used when the program doesn't really fit into the other Basic categories. These keywords shall always be
specified before any of the keywords from the Detail group.

The Detail group is used to add more specific information if appropriate. These keywords are all optional
and shall follow the Basic keywords. Programs that may fit more than one Detail are free to specify
several of these keywords. Only keywords which actually apply should be specified. If the program can
not be accurately described with any of these keywords, then none of them should be sent. In this case,
the keywords from the Basic group are all that are needed.
                                                   3
      9.5.1.5 Type=0x05 Content Advisory
This packet includes two characters that contain information about the program’s MPA, U.S. TV Parental
Guidelines, Canadian English Language, and Canadian French Language ratings. These four systems
are mutually exclusive, so if one is included, then the others shall not be. This is binary data so b6 shall
be set high (b6=1). Table 18 indicates the contents of the characters.

                           Character        b6     b5       b4     b3       b2    b1        b0
                           Character 1      1      D/a2     a1     a0       r2    r1        r0
                           Character 2      1      (F)V     S      L/a3     g2    g1        g0
                                       Table 18 Content Advisory XDS Packet

Bits a3, a2, a1, and a0 define which rating system is in use. If (a1, a0) = (1, 1) then a2 and a3 are used to
further define this rating system. Only one rating system can be in use at any given time based on Table
19.

             a3     a2     a1     a0     System        Name
             -      -      0      0      0             MPA
             L      D      0      1      1             U.S. TV Parental Guidelines
             -      -      1      0      2             MPA 4
             0      0      1      1      3             Canadian English Language Rating
             0      1      1      1      4             Canadian French Language Rating
             1      0      1      1      5             Reserved for non-U.S. & non-Canadian system
             1      1      1      1      6             Reserved for non-U.S. & non-Canadian system
                             Table 19 Content Advisory Systems a0-a3 Bit Usage

Where MPA (system 0 or system 2) is used, then bits g0-g2 shall be set to zero. In all other cases, bits r0-
r2 shall be set to zero.

Bits b5-b4 within the second character shall not be used with the Canadian English and Canadian French
rating systems. In these cases, these bits shall be reserved for future use and, pending future assignment
shall be set to “0”.


3
  In CEA-608-E the term “program rating” has been replaced by “content advisory”. CEA-608-E describes not only the
MPA rating system and the U.S. TV Parental Guideline System, but two rating systems for use in Canada. An official
translation, as supplied by the Canadian Government, of the French portion of the normative standard may be found
in Annex K. Annex K also contains a translation of the English language Canadian System into French. In DTV,
content advisory data is carried via methods described in ATSC A/65C and CEA-766-B.
4
    This system (2) has been provided for backward compatibility with existing equipment.

                                                           40
                                                                                                 CEA-608-E

The three bits r0-r2 shall be used to encode the MPA picture rating, if used. See Table 20.

                                         r2    R1   r0       Rating
                                         0     0    0        N/A
                                         0     0    1        “G”
                                         0     1    0        “PG”
                                         0     1    1        “PG-13”
                                         1     0    0        “R”
                                         1     0    1        “NC-17”
                                         1     1    0        “X”
                                         1     1    1        Not Rated
                                         Table 20 MPA Rating System

A distinction is made between N/A and Not Rated. When all zeros are specified (N/A) it means that
motion picture ratings are not applicable to this program. When all ones are used (Not Rated) it indicates
a motion picture that did not receive a rating for a variety of possible reasons.
9.5.1.5.1 U.S. TV Parental Guideline Rating System
If bits a0 – a1 indicate the U.S. TV Parental Guideline system is in use, then bits D, L, S, (F)V and g0 - g2
in the second character shall be as shown in Table 21.

                        g2     g1    g0       Age Rating     FV    V     S   L    D
                        0      0     0        None*
                        0      0     1        “TV-Y”
                        0      1     0        “TV-Y7”        X
                        0      1     1        “TV-G”
                        1      0     0        “TV-PG”              X     X   X    X
                        1      0     1        “TV-14”              X     X   X    X

                        1      1     0        “TV-MA”              X     X   X
                        1      1     1        None*

                         *No blocking is intended per the content advisory criteria.
                            Table 21 U.S. TV Parental Guideline Rating System

Bits (F) V, S, L, and D may be included in some combinations with bits g0-g2. Only combinations
indicated by an X in Table 21 are allowed.

                NOTE—When the guideline category is TV-Y7, then the V bit shall be the FV bit.

                FV - Fantasy Violence
                V - Violence
                S - Sexual Situations
                L - Adult Language
                D - Sexually Suggestive Dialog

Definition of symbols for the U.S. TV Parental Guideline rating system (informative):

TV-Y All Children. This program is designed to be appropriate for all children. Whether animated or live-
   action, the themes and elements in this program are specifically designed for a very young audience,
   including children from ages 2-6. This program is not expected to frighten younger children.
TV-Y7 Directed to Older Children. This program is designed for children age 7 and above. It may be
   more appropriate for children who have acquired the developmental skills needed to distinguish
   between make-believe and reality. Themes and elements in this program may include mild fantasy
   violence or comedic violence, or may frighten children under the age of 7. Therefore, parents may

                                                        41
CEA-608-E

    wish to consider the suitability of this program for their very young children. Note: For those programs
    where fantasy violence may be more intense or more combative than other programs in this category,
    such programs will be designated TV-Y7-FV.

The following categories apply to programs designed for the entire audience:

TV-G General Audience. Most parents would find this program suitable for all ages. Although this rating
   does not signify a program designed specifically for children, most parents may let younger children
   watch this program unattended. It contains little or no violence, no strong language and little or no
   sexual dialogue or situations.
TV-PG Parental Guidance Suggested. This program contains material that parents may find unsuitable
   for younger children. Many parents may want to watch it with their younger children. The theme itself
   may call for parental guidance and/or the program contains one or more of the following: moderate
   violence (V), some sexual situations (S), infrequent coarse language (L), or some suggestive
   dialogue (D).
TV-14 Parents Strongly Cautioned. This program contains some material that many parents would find
   unsuitable for children under 14 years of age. Parents are strongly urged to exercise greater care in
   monitoring this program and are cautioned against letting children under the age of 14 watch
   unattended. This program contains one or more of the following: intense violence (V), intense sexual
   situations (S), strong coarse language (L), or intensely suggestive dialogue (D).
TV-MA Mature Audience Only. This program is specifically designed to be viewed by adults and
   therefore may be unsuitable for children under 17. This program contains one or more of the
   following: graphic violence (V), explicit sexual activity (S), or crude indecent language (L).

(This is the end of this informative section).
9.5.1.5.2 Canadian English Language Rating System
If bits a0 – a3 indicate the Canadian English Language rating system is in use, then bits g0 - g2 in the
second character shall be as shown in Table 22.

               g2     g1     g0    Rating      Description
               0      0      0     E           Exempt
               0      0      1     C           Children
               0      1      0     C8+         Children eight years and older
               0      1      1     G           General programming, suitable for all audiences
               1      0      0     PG          Parental Guidance
               1      0      1     14+         Viewers 14 years and older
               1      1      0     18+         Adult Programming
               1      1      1
                           Table 22 Canadian English Language Rating System

A Canadian English Language rating level of (g2, g1, g0) = (1, 1, 1) shall be treated as an invalid content
advisory packet.

Definition of symbols for the Canadian English Language rating system (informative) 5 :

E      Exempt - Exempt programming includes: news, sports, documentaries and other information
programming; talk shows, music videos, and variety programming.

C        Programming intended for children under age 8 - Violence Guidelines: Careful attention is paid to
themes, which could threaten children's sense of security and well-being. There will be no realistic scenes
of violence. Depictions of aggressive behaviour will be infrequent and limited to portrayals that are clearly
imaginary, comedic or unrealistic in nature.


5
 A translation of this informative material into French may be found in the Section Labeled Official Translations in
Annex K. These translations are approved by the Government of Canada.

                                                         42
                                                                                                 CEA-608-E

Other Content Guidelines: There will be no offensive language, nudity or sexual content.

C8+       Programming generally considered acceptable for children 8 years and over to watch on their
own - Violence Guidelines: Violence will not be portrayed as the preferred, acceptable, or only way to
resolve conflict; or encourage children to imitate dangerous acts which they may see on television. Any
realistic depictions of violence will be infrequent, discreet, of low intensity and will show the
consequences of the acts.

Other Content Guidelines: There will be no profanity, nudity or sexual content.

G       General Audience - Violence Guidelines: Will contain very little violence, either physical or verbal
or emotional. Will be sensitive to themes which could frighten a younger child, will not depict realistic
scenes of violence which minimize or gloss over the effects of violent acts.

Other Content Guidelines: There may be some inoffensive slang, no profanity and no nudity.

PG      Parental Guidance - Programming intended for a general audience but which may not be suitable
for younger children. Parents may consider some content inappropriate for unsupervised viewing by
children aged 8-13. Violence Guidelines: Depictions of conflict and/or aggression will be limited and
moderate; may include physical, fantasy, or supernatural violence.

Other Content Guidelines: May contain infrequent mild profanity, or mildly suggestive language. Could
also contain brief scenes of nudity.

14+      Programming contains themes or content which may not be suitable for viewers under the age of
14 - Parents are strongly cautioned to exercise discretion in permitting viewing by pre-teens and early
teens. Violence Guidelines: May contain intense scenes of violence. Could deal with mature themes and
societal issues in a realistic fashion.

Other Content Guidelines: May contain scenes of nudity and/or sexual activity. There could be frequent
use of profanity.

18+     Adult - Violence Guidelines: May contain violence integral to the development of the plot,
character or theme, intended for adult audiences.

Other Content Guidelines: may contain graphic language and explicit portrayals of nudity and/or sex.

(This is the end of this informative section.)
9.5.1.5.3 Système de classification français du Canada
(Canadian French Language Rating System):
If bits a0 – a3 indicate the Canadian French Language rating system is in use, then bits g0 - g2 in the
second character shall be as shown in Table 23.

    g2     g1     g0    Rating        Description
    0      0      0     E             Exemptées
    0      0      1     G             Général
    0      1      0     8 ans +       Général- Déconseillé aux jeunes enfants
    0      1      1     13 ans +      Cette émission peut ne pas convenir aux enfants de moins de 13
                                      ans
    1      0      0     16 ans +      Cette émission ne convient pas aux moins de 16 ans
    1      0      1     18 ans +      Cette émission est réservée aux adultes
    1      1      0
    1      1      1
                          Table 23 Canadian French Language Rating System



                                                     43
CEA-608-E

Canadian French Language rating levels (g2, g1, g0) = (1, 1, 0) and (1, 1, 1) shall be treated as invalid
content advisory packets.

Definition of symbols for the Canadian French Language rating system (informative) 6 :

E                 Exemptées - Émissions exemptées de classement

G                Général - Cette émission convient à un public de tous âges. Elle ne contient aucune
violence ou la violence qu’elle contient est minime, ou bien traitée sur le mode de l’humour, de la
caricature, ou de manière irréaliste.

8 ans+            Général-Déconseillé aux jeunes enfants - Cette émission convient à un public large mais
elle contient une violence légère ou occasionnelle qui pourrait troubler de jeunes enfants. L’écoute en
compagnie d’un adulte est donc recommandée pour les jeunes enfants (âgés de moins de 8 ans) qui ne
font pas la différence entre le réel et l’imaginaire.

13 ans+        Cette émission peut ne pas convenir aux enfants de moins de 13 ans - Elle contient soit
quelques scènes de violence, soit une ou des scènes d’une violence assez marquée pour les affecter.
L’écoute en compagnie d’un adulte est donc fortement recommandée pour les enfants de moins de 13
ans.

16 ans+         Cette émission ne convient pas aux moins de 16 ans - Elle contient de fréquentes scènes
de violence ou des scènes d’une violence intense.

18 ans+         Cette émission est réservée aux adultes - Elle contient une violence soutenue ou des
scènes d’une violence extrême.

(This is the end of this informative section)
9.5.1.5.4 General Content Advisory Requirements
All program content analysis is the function of parties involved in program production or distribution. No
precise criteria for establishing content ratings or advisories are given or implied. The characters are
provided for the convenience of consumers in the implementation of a parental viewing control system.

The data within this packet shall be cleared or updated upon a change of the information contained in the
Current Class Program Identification Number and/or Program Name packets.

The data within this packet shall not change during the course of a program, which shall be construed to
include program segments, commercials, promotions, station identifications et al.
      9.5.1.6 Type=0x06 Audio Services
This packet contains two characters that define the contents of the main and second audio programs.
This is binary data so b6 shall be set high (b6=1). The format is indicated in Table 24.

                               Character        b6    b5    b4   b3    b2    b1    b0

                               Main             1     L2    L1   L0    T2    T1    T0

                               SAP              1     L2    L1   L0    T2    T1    T0

                                            Table 24 Audio Services

Each of these two characters contains two fields: language and type. The language fields of both
characters are encoded using the same format, as indicated in Table 25.



6
 A translation of this informative material into English may be found in the Section Labeled Official Translations in
Annex K. These translations are approved by the Government of Canada.

                                                           44
                                                                                               CEA-608-E

                                      L2     L1    L0      Language
                                      0      0     0       Unknown
                                      0      0     1       English
                                      0      1     0       Spanish
                                      0      1     1       French
                                      1      0     0       German
                                      1      0     1       Italian
                                      1      1     0       Other
                                      1      1     1       None
                                            Table 25 Language

The type fields of each character are encoded using the different formats indicated in Table 26.

      Main Audio Program                            Second Audio Program
      T2    T1     T0    Type                       T2   T1    T0    Type
      0     0      0     Unknown                    0    0     0     Unknown
      0     0      1     Mono                       0    0     1     Mono
      0     1      0     Simulated Stereo           0    1     0     Video Descriptions
      0     1      1     True Stereo                0    1     1     Non-program Audio
      1     0      0     Stereo Surround            1    0     0     Special Effects
      1     0      1     Data Service               1    0     1     Data Service
      1     1      0     Other                      1    1     0     Other
      1     1      1     None                       1    1     1     None
                                           Table 26 Audio Types
      9.5.1.7 Type=0x07 Caption Services
This packet contains a variable number, 2 to 8 characters that define the available forms of caption
encoded data. One character is needed to specify each available service. This is binary data so bit 6 shall
be set high (b6=1). Each of the characters shall follow the same format, as indicated in Table 27. The
language bits shall be as defined in Table 25 (the same format for the audio services packet).
The F, C, and T bits shall be as shall be as defined in Table 28.

                          Character          b6    b5     b4   b3   b2   b1   b0
                          Service Code       1     L2     L1   L0   F    C    T

                                       Table 27 Caption Services

The language bits are encoded using the same format as for the audio services packet. See Table 25.

                            F    C     T     Caption Service
                            0    0     0     field one, channel C1, captioning
                            0    0     1     field one, channel C1, Text
                            0    1     0     field one, channel C2, captioning
                            0    1     1     field one, channel C2, Text
                            1    0     0     field two, channel C1, captioning
                            1    0     1     field two, channel C1, Text
                            1    1     0     field two, channel C2, captioning
                            1    1     1     field two, channel C2, Text
                                     Table 28 Caption Service Types
      9.5.1.8 Type=0x08 Copy and Redistribution Control Packet
This packet contains binary data so b6 shall be set high (b6=1). For copy generation management system
(CGMS-A), APS, ASB and RCD syntax, see Table 29.



                                                     45
CEA-608-E

                      b6      b5            b4                 b3          b2          b1       b0
       Byte 1          1       -         CGMS-A           CGMS-A           APS        APS       ASB


       Byte 2          1      Re           Re                  Re          Re          Re       RCD
Re = Reserved bit for possible future use.
                            Table 29 Copy and Redistribution Control Packet

In Table 29, bits b5-b1, of the second byte, are reserved for future use. All reserved bits shall be zero until
assigned. ASB shall be defined as the Analog Source Bit. CEA-608-E does not define the use or meaning
of the ASB.

The CGMS-A bits have the meanings indicated in Table 30.

                                   b4 b3         CGMS-A Meaning
                                   0,0           Copying is permitted without restriction


                                   0,1           No more copies (one generation copy has been
                                                 made)*
                                   1,0           One generation of copies may be made


                                   1,1           No copying is permitted
                                   * This definition differs from IEC-61880 and IEC 61880-2.

                                       Table 30 CGMS-A Bit Meanings

        NOTE—Conditions for applying the CGMS-A and APS bits in source devices may be bound by
        private agreements or government directives. Also, required behavior of sink devices detecting
        the CGMS-A and APS bits may be bound by private agreements or government directives.
        Implementers are cautioned to read and understand all applicable agreements and directives.

        NOTE—Where the CGMS-A bits are set to 0,1 or 1,1, a source device may use APS to apply
        anti-copying protection to its APS-capable outputs, assuming that the device applying the anti-
        copying protection signal is under an appropriate license from an anti-taping protection
        technology provider. If the CGMS-A bits in Table 30 are set to either 0,0 or 1,0 (i.e., CGMS-A
        states that permit copying), APS data should not trigger the application of APS. Notwithstanding,
        all APS bits should be preserved in signals in the CEA-608-E format, so that APS may be
        triggered where downstream devices receive such signals with CGMS-A bits set to 1,0 and
        remark as 0,1 the CGMS-A bits on recordings of the content of those signals.

        NOTE—There may be conditions where APS bits are used independently of CGMS-A bits.

The Analog Protection System (APS) bits have the meanings in Table 31.

                                   b2 b1         Meaning
                                   0,0           No APS
                                   0,1           PSP On; Split Burst Off
                                   1,0           PSP On; 2 line Split Burst On
                                   1,1           PSP On; 4 line Split Burst On
                                           Table 31 APS Bit Meanings




                                                          46
                                                                                                      CEA-608-E

        NOTE—Pseudo Sync Pulse (PSP) may cause degraded recordings, as does either method of
        Split Burst. PSP may also prevent recording.

The Redistribution Control Descriptor (RCD) bit (b0) in Byte 2 of Table 29, when set to ‘1’, shall mean
technological control of consumer redistribution has been signaled by the presence of the ATSC A/65C
rc_descriptor. Application of the RCD bit in a source device and behavior of receiving devices are out of
scope of CEA-608-E. CEA-608-E imposes no requirement on a receiving device to do more than pass the
RCD bit through, unaltered.

        NOTE—Conditions for applying the RCD bit in source devices may be bound by private
        agreements or government regulations, for example 47 C.F.R. Parts 73 and 76. Also, sink device
        behavior when detecting the RCD bit may be bound by private agreements or government
        regulations. Implementers are cautioned to read and understand all applicable agreements and
        regulations.

The recommended transmission rate for this packet is high priority.
     9.5.1.9 Type=0x09 Reserved
The Current Class Type 0x09 is reserved as it was used in prior editions of CEA-608-E.
      9.5.1.10 Type=0x0C Composite Packet-1
This packet is designed to provide an efficient means of transmitting the information from several packets
as a single group. The first four fields are always a fixed length. If information is not available, null
characters shall be used within each field. The total length of the packet shall be an even number equal to
32 or less. The last field is the title field, which can be a variable length of up to 22 characters. A change
in the received Current Class Composite Packet-1 Program Title field is interpreted by XDS receivers as
the start of a new current program. All previously received current program information shall normally be
discarded in this case.

When program titles longer than 22 characters are needed, the packet should terminate after the
Time-in-show field and the separate Program Title field should be used for the long name. Table 32
shows the contents of each field within the packet.

                                        Field Contents           Length
                                        Program Type             5
                                        Content Advisory         17
                                        Length                   2
                                        Time-in-show             2
                                        Title                    0-22


                              Table 32 Field Contents—Composite Packet-1

The informational characters of each field are encoded just as they would for each of their respective
separate packets.
      9.5.1.11 Type=0x0D Composite Packet-2
This packet is designed to provide an efficient means of transmitting the information from several packets
as a single group. The first five fields are always a fixed length. If information is not available, null
characters shall be used within each field. The total length of the packet shall be an even number equal to
32 or less. The last field is the Network Name field, which can be a variable length of up to 18 characters.

When network names longer than 18 characters are needed, the packet should terminate after the Native
Channel field. The following table shows the contents of each field within the packet. See Table 33.



7
 Only the first byte of the Content Advisory Packet Type=0x05 is carried in Composite Packet-1 as per Section
9.6.2.5.

                                                        47
CEA-608-E

                                   Field Contents                Length
                                   Program Start Time (ID#)      4
                                   Audio Services                2
                                   Caption Services              2
                                   Call Letters*                 4
                                   Native Channel*               2
                                   Network Name*                 0-18
                             Table 33 Field Contents—Composite Packet-2

The informational characters of each field are encoded just as they would for each of their respective
separate packets. Information for the fields marked with asterisk (*) comes from the Channel Information
Class.

A change in received Current Class Program Identification Number is interpreted by XDS receivers as the
start of a new current program. All previously received current program information shall normally be
discarded in this case.
      9.5.1.12 Type=0x10 to 0x17 Program Description Row 1 to Row 8
These packets form a sequence of up to eight packets that each can contain a variable number (0 to 32)
of displayable characters used to provide a detailed description of the program. Each character is a
closed caption character in the range of 0x20 to 0x7F.

This description is free form and contains any information that the provider wishes to include. Some
examples: episode title, date of release, cast of characters, brief story synopsis, etc.

Each packet is used in numerical sequence. If a packet contains no informational characters, a blank line
shall be displayed. The first four rows should contain the most important information as some receivers
may not be capable of displaying all eight rows.
9.5.2 Future Programming
This class contains the same information and formats as the Current Class. Information about future
programs is sent by any sequence of separate packets transmitted with the Future Class identifier codes.



9.5.3 Channel Information Class
      9.5.3.1 Type=0x01 Network Name (Affiliation)
This packet contains a variable number, 2 to 32, of characters that define the network name associated
with the local channel. Each character is a closed caption character in the range of 0x20 to 0x7F. Each
network should use a short, unique, and consistent name so that receivers could access internal
information, like a logo, about the network.
      9.5.3.2 Type=0x02 Call Letters (Station ID) and Native Channel
This packet contains four or six characters. The first four shall define the call letters of the local
broadcasting station. If it is a three letter call sign the fourth character shall be blank (0x20). Each
character is a closed caption character in the range of 0x20 to 0x7F. A four-letter (or fewer) abbreviation
of the network name may also be substituted for the four character call letters.

When six characters are used, the last two are displayable numeric characters that are used to indicate
the channel number that is assigned by the FCC to the station for local over-the-air broadcasting. In a
CATV system, the native channel number is frequently different than the CATV channel number which
carries the station. The valid range for these channels is 2-69. Single digit numbers may either be
preceded by a zero or a standard null.

While five- or six- letter names or abbreviations are technically permitted (instead of four characters and
two numerals), they should be avoided as some TV receivers may only use the first four letters.



                                                     48
                                                                                                 CEA-608-E

      9.5.3.3 Type=0x03 Tape Delay
This packet contains two characters that define the number of hours and minutes that the local station
routinely tape delays network programs. This is binary data so b6 shall be set high (b6=1). These
characters shall be formatted the same as minute and hour characters of the Program Identification
Number packet, as shown in Table 34.

                            Character             b6   b5 b4 b3 b2 b1 b0
                            Minute                1    m5 m4 m3 m2 m1 m0

```

## 1.3 Control Codes

### 1.3.1 Preamble Address Codes (PACs)


PACs (Preamble Address Codes) are two-byte commands that:
1. Set the row (1-15) for caption display
2. Set the column indent (0, 4, 8, 12, 16, 20, 24, 28)  
3. Optionally set text attributes (color, italics, underline)

**Format:** Two bytes, both with bit 7 clear (0) and bit 6 set (parity)
- First byte: determines row
- Second byte: determines indent and attributes

```

Autres directives à l’égard du contenu : Les émissions peuvent présenter un contenu comportant de
l’argot, mais aucune représentation de scène de nudité ou de sexe ne sera faite.

PG       Surveillance parentale - Bien qu’elles soient destinées à un auditoire général, ces émissions
peuvent ne pas convenir aux jeunes enfants. Les parents doivent savoir que le contenu de ces émissions
pourrait comporter des éléments que certains pourraient considérer comme impropres pour que des
enfants de 8 à 13 ans les regardent sans surveillance. Lignes directrices sur la violence : Toute
représentation de conflits et (ou) d’agressions doit être limitée et modérée; il pourrait s’agir de violence
physique légère ou humoristique, ou de violence surnaturelle.

Autres directives à l’égard du contenu : Ces émissions peuvent présenter un contenu quelque peu
grossier, un langage suggestif, ou encore de brèves scènes de nudité.

14+     Émissions comportant des thèmes ou des éléments de contenu qui pourraient ne pas convenir
aux téléspectateurs de moins de 14 ans - On incite fortement les parents à faire preuve de circonspection
en permettant à des préadolescents et à des enfants au début de l’adolescence de regarder ces
émissions. Lignes directrices sur la violence : Ces émissions pourraient contenir des scènes intenses de
violence et présenter de façon réaliste des thèmes adultes et des problèmes de société.

Autres directives à l’égard du contenu : Les émissions pourraient présenter des scènes de nudité ou de
sexe, et utiliser un langage grossier.

18+    Adultes - Lignes directrices sur la violence : Ces émissions peuvent faire certaines
représentations de la violence faisant partie intégrante de l’évolution de l’intrigue, des personnages et des
thèmes, et s’adressent aux adultes.

Autres directives à l’égard du contenu : Ces émissions peuvent comporter un langage grossier et une
représentation explicite de nudité et (ou) de sexe.

                                           French to English
Canadian French Language Rating System

E               Exempt - Exempt programming

G                General - Programming intended for audience of all ages. Contains no violence, or the
violence it contains is minimal or is depicted appropriately with humour or caricature or in an unrealistic
manner.

8 ans+           8+ General - Not recommended for young children - Programming intended for a broad
audience but contains light or occasional violence that could disturb young children. Viewing with an adult
is therefore recommended for young children (under the age of 8) who cannot differentiate between real
and imaginary portrayals.

13 ans+         Programming may not be suitable for children under the age of 13 - Contains either a few
violent scenes or one or more sufficiently violent scenes to affect them. Viewing with an adult is therefore
strongly recommended for children under 13.

16 ans+           Programming is not suitable for children under the age of 16 - Contains frequent scenes
of violence or intense violence.




                                                     120
                                                                                           CEA-608-E


18 ans+        Programming restricted to adults - Contains constant violence or scenes of extreme
violence.

The following are contracted forms of the English and French Language rating systems. The standards
shall be used where applicable.
K.1 Primary Language

                        CONTRACTIONS FOR ENGLISH RATINGS
Title          Cdn. English Ratings
Symbol         Contracted Description
E              Exempt
C              Children
C8+            8+
G              General
PG             PG
14+            14+
18+            18+
                           CONTRACTIONS FOR FRENCH RATINGS
Title         Codes fr. du Canada
Symbol        Contracted Description
E              Exemptées
G              Pour tous
8 ans +        8+
13 ans +       13+
16 ans +       16+
18 ans +       18+

                     OFFICIAL TRANSLATION OF CONTRACTED FORMS
                                         English to French
Titre :        Codes ang. du Canada
Titre          Symbole
E              Exemptées
C              Enfants
C8+            8+
G              Général
PG             Surv. parentale
14+            14+
18+            18+
                                         French to English
Title:         Cdn. French Ratings
Title          Symbol
E              Exempt
G              For all
8 ans+         8+
13 ans+        13+
16 ans+        16+
18 ans+        18+




                                                 121
CEA-608-E



Annex L Content Advisories (Informative)
L.1 Scope
This annex is intended to provide guidance for XDS decoder manufacturers utilizing the Program Rating
(Content Advisory) packet. This packet has a current class type code 0x05, and is described in detail in
Section 9.5.1.1.

This annex also provides guidance for manufacturers of Digital Television Receivers and contains
recommended practices for use with CEA-766-B and ATSC A/53E and A/65C.

For excerpts from relevant U.S. Federal Communications Commission regulations, see Annex F2
(Informative). For information concerning relevant Canadian government decisions, see Annex K
(Informative).
L.2 Receiver Indication
Once a program is blocked, the receiver should indicate to the viewer that Content Advisory blocking has
occurred via an appropriate on screen display message The receiver may use additional XDS or PSIP
data to display other information, such as program length, title, etc., if available.
L.3 Blocking
The default state of a receiver (i.e. as provided to the consumer) should not block unrated programs
However, it is permissible to include features that allow the user to reprogram the receiver to block
programs that are not rated.

                •   For U.S., see FCC Rules Section 15.120(e)(2).
                •   For Canada, see Public Notice CRTC 1996-36, section 1, paragraph 3.

In the U.S., programs with a rating of “None” are not intended to be blocked per the content advisory
criteria (see Table 22). Certain types of programming may either carry the content advisory of "None" or
not contain a content advisory packet. Examples of this type of programming include:

                •   Emergency Bulletins (such as EAS messages, weather warnings and others)
                •   Locally originated programming
                •   News
                •   Political
                •   Public Service Announcements
                •   Religious
                •   Sports
                •   Weather

Programs which are not intended to be blocked in Canada are rated with an "Exempt" rating code.
Exempt programming includes: News, sports, documentaries and other information programming such as
talk shows, music videos, and variety programming (see Public Notice CRTC 1997-80, Appendix A).

If provisions are included to allow the consumer to block on a rating of “None” or when no rating packets
are present, receiver manufacturers should appropriately educate consumers on the use of this feature
(e.g. in the instruction book).
L.4 Cessation

        NOTE—Section L.4.1 is considered part of Section L.4 when an analog set is in use, and Section
        L.4.2 is considered part of Section L.4 when a digital set is in use.

If the user has enabled program blocking and the receiver allows the user to program the default blocking
state (i.e. to block or unblock), then the TV should immediately revert to the default blocking state under
the following conditions If the receiver does not allow the user to program the default blocking state, then
the TV should immediately unblock under the following conditions:


                                                    122
                                                                                                  CEA-608-E


a) If the channel is changed.
b) If the input source is changed.

Channel blocking should always cease when a content advisory packet is received which contains an
acceptable rating and/or advisory level.
L.4.1 Analog Cessation
When an analog set is in use, the following is a continuation of the list in Section L.4:

c) If no content advisory is received for 5 seconds.
d) If a new Current Class ID or Title packet is received.
e) If the XDS Content Advisory packet’s a0 and a1 bits indicate the MPA rating system is in use and an
   MPAA rating of “N/A” is received.
f) If the XDS Content Advisory packet’s a0 and a1 bits indicate the TV Parental Guideline rating system is
   in use and a TV Parental Guideline rating of “None” is received.
g) If there is no valid line 21 data on field 2 for 45 frames.
h) If the XDS Content Advisory packet's a0, a1, a2, a3 bits indicate the Canadian English language rating
   system is in use and a Canadian English Language rating of "Exempt" is received.
i) If the XDS Content Advisory packet's a0, a1, a2, a3 bits indicate the Canadian French language rating
   system is in use and a Canadian French Language rating of "Exempt" is received.
j) If a Content Advisory packet is received with the a0, a1, a2, a3 bits indicating systems 5 and 6 (non US
   and non-Canadian rating system) is in use (until these rating systems are further defined).
L.4.2 Digital Cessation
When a digital set is in use, the following is a continuation of the list in Section L.4:

k) If the content advisory descriptor indicates that the MPA rating system is in use and an MPA rating of
   "N/A" is received
l) If the content advisory descriptor indicates that the TV Parental Guideline rating system is in use and a
   TV Parental Guideline rating of "None" is received
m) If the content advisory descriptor indicates that the Canadian English Language rating system is in use
   and a Canadian English Language rating packet of "Exempt" is received
n) If the content advisory descriptor indicates that the Canadian French Language rating system is in use
   and a Canadian French Language rating packet of "Exempt" is received
o) If there is no valid content advisory descriptor information for 1.2 seconds.
L.5 Selection Advisory
When the categories D, L, S, V, and FV are chosen for blocking, without an age based rating, a receiver
should display an advisory that some program sources will not be blocked.
L.6 Rating Information
The remote control may include a button, which displays the rating icon, and/or the descriptive language,
but neither should be displayed except upon action of the viewer unless the set is in the blocked mode.
Note that the categories D, L, S, & V should be displayed only in alphabetical order, especially when each
is denoted by a single letter.

For the Canadian systems, as a minimum requirement, the rating information as viewed on-screen should
be available in its primary language That is, the English language rating system should be available in
English and the French language rating system should be available in French. Manufacturers are free to
implement translations, however, if they wish to do so they should adhere to the translations provided in
Annex K.
L.7 XDS Data
NTSC Broadcasters should include XDS packets with the title, start time, and stop time/duration for
display when the receiver is in blocking mode. This parallels a recommendation for DTV Broadcasters.




                                                       123
CEA-608-E


L.8 Auxiliary Input
If a receiver has the ability to decode line 21 XDS information for the Auxiliary Inputs, then it should block
the inputs based on the MPA, U.S. TV Parental Guideline, Canadian English Language or Canadian
French Language rating level selected by the viewer. If the receiver does not have the ability to decode
the Auxiliary Input’s line 21 XDS information, then it should block or otherwise disable the Auxiliary Inputs
if the viewer has enabled Content Advisory blocking Once again, this appears to be the only valid solution
for allowing Content Advisory information to be a useful feature.

In a similar fashion, DTV sets with an Auxiliary Input should block the inputs based on the MPA, U.S. TV
Parental Guideline, Canadian English Language or Canadian French Language rating level selected by
the viewer. If the receiver does not have the ability to decode the Auxiliary Input’s content advisory
descriptor information, then it should block or otherwise disable the Auxiliary Inputs if the viewer has
enabled Content Advisory blocking.
L.9 Invalid Ratings
An invalid rating should be ignored by the receiver and treated as if no rating packet or content advisory
descriptor was received.

For the TV Parental Guidelines, an invalid rating is defined as any combination of Age Rating and
Content Flag which does not appear in Table 22 for NTSC receivers or Table 1 of CEA-766-B for DTV

```

### 1.3.2 Mid-Row Codes


Mid-row codes change text attributes in the middle of a row without moving the cursor.
They insert a space and then apply the attribute to following characters.

```
Prog Desc 7          6/36        L17                      36        L11                      36

Prog Desc 8          6/36        L18                      36        L12                      36

Channel Info Class

Network Name         6/36        H6                       36        H2                       36

Call Ltr/Chan        8/10        H7                       10        H2                       10

Tape Delay           6           L19        6             6         L13            6         6

                         Table 57 Alternating Algorithm Lookup Table (Continued)




                                                    116
                                                                                                CEA-608-E



Packet Description      Linear      Linear Algorithm                   Alternating Algorithm
                        Min/max     Priority    Pkt Len      Pkt Len   Priority       Pkt Len   Pkt Len
                                                Set 1        Set 2                    Set 1     Set 2
Misc Class

Time of Day             10          L20         10           10        L16              10      10

Impulse Capt            10          H8                                 H2

Suppl Date Loc          6/36        L21                      6         L14                      6

Time Zone/DST           6           L22                      6         L15                      6

OOB Channel #           6           L23                      6         L4                       6
Public Serv Class

NWS Code                16          H9                       16        H2                       16

NWS Message             6/36        H10                      36        H2                       36

Undefined XDS           4/36        Not Repetitive                     Not Repetitive
Data Set Char Counts

XDS Char Count                                  376          948                        376     948

High Rep Char Cnt                               60           150                        60      150

Med Rep Char Cnt                                120          356                        120     356

Low Rep Char Cnt                                196          442                        196     442
Data Set Group Counts

High Rep Group Cnt                              2            7                          2       2

Med Rep Group Cnt                               4            12                         4       9

Low Rep Group Cnt                               8            21                         8       16
Algorithm Char Counts

Total Char/Pass                                 3556         48868                      2116    16938

High Rep Char/Pass                              2400         40950                      960     10800

Med Rep Char/Pass                               960          7476                       960     5696

Low rep Char/Pass                               196          442                        196     442

                            Table 58 Alternating Algorithm Lookup Table (Continued)




                                                       117
       CEA-608-E




Packet Description        Linear      Linear Algorithm                      Alternating Algorithm


                          Min/max     Priority     Pkt Len       Pkt Len    Priority        Pkt Len    Pkt Len

                                                   Set 1         Set 2                      Set 1      Set 2

Avg Rep Rate 100% BW,s

High                                               1.5           3.0                        2.2        3.9

Medium                                             7.4           38.3                       4.4        17.6

Low                                                59.3          814.5                      35.3       282.3

Avg Rep Rate 70% BW,s

High                                               2.1           4.3                        3.1        5.6

Medium                                             10.6          55.4                       6.3        25.2

Low                                                84.7          1163.5                     50.4       403.3

Avg Rep Rate 30% BW,s

High                                               4.9           9.9                        7.3        13.1

Medium                                             24.7          129.3                      14.7       58.8

Low                                                197.6         2714.9                     117.6      941.0

Worst Case Rep Rate 30% BW,s

High                                               5.0           7.8                        8.3        17.7

Medium                                             23.7          130.1                      15.0       60.2

Low                                                197.6         2714.9                     117.6      941.0

Assumptions for data set 2: Composite 1 is not transmitted because program type, length, and title

```

### 1.3.3 Miscellaneous Control Codes


These are mode-setting and cursor control commands.

**Key Commands:**
- **RCL (Resume Caption Loading)**: 0x1420 - Selects pop-on style  
- **BS (Backspace)**: 0x1421 - Moves cursor left one column
- **AOF (Reserved)**: 0x1422
- **AON (Reserved)**: 0x1423  
- **DER (Delete to End of Row)**: 0x1424 - Deletes from cursor to end of row
- **RU2 (Roll-Up 2 rows)**: 0x1425 - Selects 2-row roll-up
- **RU3 (Roll-Up 3 rows)**: 0x1426 - Selects 3-row roll-up  
- **RU4 (Roll-Up 4 rows)**: 0x1427 - Selects 4-row roll-up
- **FON (Flash On)**: 0x1428 - Not well supported
- **RDC (Resume Direct Captioning)**: 0x1429 - Selects paint-on style
- **TR (Text Restart)**: 0x142A - For text mode
- **RTD (Resume Text Display)**: 0x142B - For text mode  
- **EDM (Erase Displayed Memory)**: 0x142C - Erases displayed caption
- **CR (Carriage Return)**: 0x142D - Used in roll-up mode
- **ENM (Erase Non-Displayed Memory)**: 0x142E - Erases buffer
- **EOC (End Of Caption)**: 0x142F - Display caption (pop-on)

**Tab Offsets:**
- **TO1**: 0x1721 - Tab forward 1 column  
- **TO2**: 0x1722 - Tab forward 2 columns
- **TO3**: 0x1723 - Tab forward 3 columns

```

Low                                                84.7          1163.5                     50.4       403.3

Avg Rep Rate 30% BW,s

High                                               4.9           9.9                        7.3        13.1

Medium                                             24.7          129.3                      14.7       58.8

Low                                                197.6         2714.9                     117.6      941.0

Worst Case Rep Rate 30% BW,s

High                                               5.0           7.8                        8.3        17.7

Medium                                             23.7          130.1                      15.0       60.2

Low                                                197.6         2714.9                     117.6      941.0

Assumptions for data set 2: Composite 1 is not transmitted because program type, length, and title

Overflow the fields and it is more efficient to transmit them separately. Composite 2 is not transmitted

Because caption services, network name and native channel overflow their respective fields.

                            Table 59 Alternating Algorithm Lookup Table (Continued)




                                                           118
                                                                                                       CEA-608-E




Annex K Canadian CRTC Letter Decisions and Official Translations (Informative)
Following is the text of a communication received from Industry Canada concerning the French
translations and the official contracted forms appearing in EIA-744-A: 11

Dear Mr. Hanover;

This is to inform you that Industry Canada supports fully the Draft
EIA744, its French translations and the official contracted forms for the
V-chip descriptors (as per attached).

George Zurakowski
Manager, Broadcasting Regulations and Standards
Industry Canada
613-990-4950 (Voice) 613-991-0652 (Fax)
zurakowg@spectrum.ic.gc.ca (Internet address)

This annex is informative as supplied by the Canadian Government. For further information, see the letter
decisions:

                    •   Public Notice CRTC 1996-36, Respecting Children: A Canadian Approach to Helping
                        Families Deal with Television Violence
                    •   Public Notice CRTC 1997-80, Classification System for Violence in Television
                        Programming

                                        OFFICIAL TRANSLATIONS
                                              English to French
Système de classification anglais du Canada

E        Émissions exemptées de classification - Sont exemptes, notamment les émissions suivantes : les
émissions de nouvelles, les émissions de sports, les documentaires et les autres émissions d’information;
les tribunes téléphoniques, les émissions de musique vidéo et les émissions de variétés.

C       Émissions à l’intention des enfants de moins de 8 ans - Lignes directrices sur la violence : Il faut
porter une attention particulière aux thèmes qui pourraient troubler la tranquilité d’esprit et menacer le
bien-être des enfants. Les émissions ne doivent pas présenter de scènes réalistes de la violence. Les
représentations de comportements agressifs doivent être peu fréquentes et limitées à des images de
nature manifestement imaginaires, humoristiques et irréalistes.

Autres directives à l’égard du contenu : Le contenu des émissions ne doit en aucun cas comporter de
jurons, de nudité ou de sexe.

C8+      Émissions que les enfants de huit ans et plus peuvent généralement regarder seuls - Lignes
directrices sur la violence: Il s’agit d’émissions qui ne représentent pas la violence comme moyen
privilégié, acceptable ou comme seul moyen de résoudre les conflits, ou qui n’encouragent pas les
enfants à imiter les actes dangereux qu’ils peuvent voir à la télévision. Toutes réprésentations réallistes
de violence seront peu fréquentes, discrètes, de basse intensité et montreront les conséquences des
actes.

Autres directives à l’égard du contenu : Le contenu de ces émissions peut présenter un langage grossier,
de la nudité ou du sexe.


11
     EIA-774-A was an antecedent document to CEA-608-E and its information is fully contained in CEA-608-E.


                                                        119
CEA-608-E


G       Général - Lignes directrices sur la violence : Les émissions comporteront très peu de scènes de
violence physique, verbale ou affective. Elles porteront une attention particulière aux thèmes qui
pourraient effrayer un jeune enfant et ne comporteront aucune scène réaliste de violence qui minimise ou
estompe les effets des actes violents.

```

## 1.4 Caption Modes and Styles

### 1.4.1 Pop-On Captions (Pop-Up)


**Description:** Captions are built in non-displayed memory, then displayed all at once with EOC command.

**Characteristics:**
- Most common style for pre-produced content
- Allows editing before display
- Typically 1-3 rows per caption
- No scrolling effect

**Protocol:**
1. RCL - Select pop-on mode
2. ENM - Clear non-displayed memory (optional)  
3. PAC - Position cursor and set attributes
4. [characters] - Write caption text
5. EOC - Display the caption (swaps displayed and non-displayed memory)

**Timing:** Caption appears instantly when EOC is received.

### 1.4.2 Roll-Up Captions


**Description:** Text scrolls up from bottom of screen, typically used for live content.

**Characteristics:**
- 2, 3, or 4 rows visible (set by RU2, RU3, or RU4)
- Base row (bottom row) typically row 14 or 15
- New text appears at base row, old text scrolls up
- Top row scrolls off screen

**Protocol:**
1. RU2/RU3/RU4 - Select roll-up mode and depth
2. PAC - Set base row and indent
3. [characters] - Write text
4. CR - Carriage return causes roll-up

**Base Row:** The bottom row where new text appears. Set by row in PAC command.

### 1.4.3 Paint-On Captions


**Description:** Characters appear on screen as soon as they are received.

**Characteristics:**
- No buffering - instant display
- Used for special effects or corrections
- Can selectively erase with DER

**Protocol:**
1. RDC - Select paint-on mode  
2. PAC - Set position
3. [characters] - Appear immediately as received

## 1.5 Field 1 vs Field 2


Line 21 data is transmitted in two fields per video frame:

**Field 1:**
- Channel CC1 (primary caption service)
- Channel CC2 (secondary language or caption service)  
- Text Channel T1
- Text Channel T2

**Field 2:**
- Channel CC3 (additional caption service)
- Channel CC4 (additional caption service)
- Text Channel T3  
- Text Channel T4
- XDS (eXtended Data Services) packets

**Data Format:** Each field transmits 2 bytes per video frame.

**Channel Selection:**  
Channels are selected by control code preambles. Decoders filter for their selected channel.

## 1.6 Text Attributes and Colors


### 1.6.1 Foreground Colors  

Captions support the following text colors:
- White
- Green
- Blue
- Cyan
- Red  
- Yellow
- Magenta
- Black (when italics enabled)

### 1.6.2 Background Colors

- Black (default)
- White
- Green  
- Blue
- Cyan
- Red
- Yellow
- Magenta

### 1.6.3 Text Styles

- **Italics**: Slanted text
- **Underline**: Underlined text  
- **Flash**: Blinking text (rarely supported)

### 1.6.4 Attribute Setting

Attributes can be set by:
1. **PAC codes**: Set attributes when positioning cursor
2. **Mid-row codes**: Change attributes mid-row (inserts space)
3. **Background Attribute codes**: Set background color/transparency

### 1.6.5 Background Transparency

- Opaque
- Semi-transparent  
- Transparent

## 1.7 Caption Positioning


### 1.7.1 Screen Layout

- **Rows**: 15 total (rows 1-15)
- **Columns**: 32 total (columns 1-32)
- **Safe Area**: Recommended rows 2-14, columns 3-30

### 1.7.2 PAC Indents

PACs provide coarse positioning at these column indents:
- Indent 0: Column 1
- Indent 4: Column 5  
- Indent 8: Column 9
- Indent 12: Column 13
- Indent 16: Column 17
- Indent 20: Column 21  
- Indent 24: Column 25
- Indent 28: Column 29

### 1.7.3 Tab Offsets

Tab Offset commands (TO1, TO2, TO3) provide fine positioning by moving cursor 1-3 columns right.

Combined PAC + Tab Offset allows positioning at any of 32 columns.

## 1.8 Data Encoding Details


### 1.8.1 Byte Format

Each transmitted byte:
- Bit 7: Always 0 (per NRZ encoding)
- Bit 6: Odd parity bit (set so byte has odd number of 1 bits)  
- Bits 5-0: Data payload

### 1.8.2 Control Code Transmission

- All control codes are **2 bytes**
- Must be transmitted **twice** in consecutive fields for reliability
- Decoders accept command on first instance but wait for second as confirmation

### 1.8.3 Timing

- Data rate: 2 bytes per video frame (1 byte per field)  
- Frame rates: 29.97 fps (NTSC)
- Effective data rate: ~60 bytes/second

### 1.8.4 Special Codes

- **0x80 0x80**: No data / padding
- **0x00 0x00**: Null (reserved, not used in captioning)

## 1.9 XDS (eXtended Data Services)


XDS packets provide metadata about programs, transmitted in Field 2 when not used for captions.

### 1.9.1 XDS Packet Structure

1. **Start byte**: 0x01-0x0F (packet class)
2. **Type byte**: Packet type within class  
3. **Data bytes**: Variable length data
4. **Checksum**: Error detection
5. **End byte**: 0x0F (marks packet end)

### 1.9.2 XDS Packet Classes

- **Current/Future (0x01-0x02)**: Program info, ratings, title
- **Channel (0x03-0x04)**: Network name, call letters
- **Miscellaneous (0x05-0x06)**: Time of day, timers  
- **Public Service (0x07-0x08)**: Emergency alerts

### 1.9.3 Common XDS Packets

- Program name/title
- Content advisory / ratings (V-chip)
- Program length and time-in-show  
- Network identification
- Time of day



---

# Part 2: CEA-708 Digital Television Closed Captioning

## 2.1 Overview


CEA-708 is the digital television standard for closed captions, designed for DTV (ATSC) broadcasts.

**Key Differences from CEA-608:**
- Much higher data rate
- More styling options
- Support for multiple languages simultaneously  
- Unicode character support
- Advanced window positioning and transparency
- Carried in MPEG-2 user data or ATSC DTVCC stream

**Relationship to CEA-608:**  
- CEA-708 streams often include CEA-608 compatibility service
- Allows backwards compatibility with older decoders

## 2.2 CEA-708 Service Architecture


- Up to 6 independent caption services
- Each service can have 8 windows
- Windows can be positioned anywhere on screen  
- Supports rich text attributes

### Services:
- **Service 1-6**: Independent caption streams
- Typically Service 1 = primary language
- Services 2-6 for secondary languages or enhanced services

### CEA-708 Technical Introduction

```
6 DTVCC Service Layer ............................................................................................................................ 23
   6.1 Services ........................................................................................................................................... 23
   6.2 Service Blocks ................................................................................................................................ 24
     6.2.1 Standard Service Block Header .............................................................................................. 24
     6.2.2 Extended Service Block Header .............................................................................................. 25


                                                                                i
                                                                                                                                           CEA-708-E

      6.2.3 Null Service Block Header ....................................................................................................... 25
      6.2.4 Service Block Data ................................................................................................................... 25
      6.2.5 Service Blocks within Caption Channel Packets .................................................................. 25
    6.3 Transport Constraints on Encapsulating Caption Data ............................................................. 26

7 DTVCC Coding Layer - Caption Data Services (Services 1 - 63) ....................................................... 27
   7.1 Code Space Organization .............................................................................................................. 27
     7.1.1 Extending the Code Space ...................................................................................................... 29
     7.1.2 Unused Codes ........................................................................................................................... 30
     7.1.3 Numerical Organization of Codes ........................................................................................... 30
     7.1.4 Code Set C0 - Miscellaneous Control Codes ......................................................................... 30
     7.1.5 C1 Code Set - Captioning Command Control Codes ............................................................ 32
     7.1.6 G0 Code Set - ASCII Printable Characters ............................................................................. 33
     7.1.7 G1 Code Set - ISO 8859-1 Latin-1 Character Set ................................................................... 34
     7.1.8 G2 Code Set - Extended Miscellaneous Characters ............................................................. 35
     7.1.9 G3 Code Set - Future Expansion ............................................................................................. 36
     7.1.10 C2 Code Set - Extended Control Code Set 1 ........................................................................ 37
     7.1.11 C3 Code Set - Extended Control Code Set 2 ........................................................................ 38

8 DTVCC Interpretation Layer .................................................................................................................. 42
   8.1 DTVCC Caption Components ........................................................................................................ 42
   8.2 Screen Coordinates ........................................................................................................................ 42
   8.3 User Options ................................................................................................................................... 44
   8.4 Caption Windows............................................................................................................................ 44
     8.4.1 Window Identifier ...................................................................................................................... 45
     8.4.2 Window Priority......................................................................................................................... 45
     8.4.3 Anchor Points ........................................................................................................................... 45
     8.4.4 Anchor ID ................................................................................................................................... 45
     8.4.5 Anchor Location ....................................................................................................................... 46
     8.4.6 Window Size .............................................................................................................................. 46
     8.4.7 Window Row and Column Locking ......................................................................................... 47
     8.4.8 Word Wrapping ......................................................................................................................... 48
     8.4.9 Window Text Painting .............................................................................................................. 49
     8.4.10 Window Display ...................................................................................................................... 51
     8.4.11 Window Colors and Borders ................................................................................................. 51
     8.4.12 Predefined Window and Pen Styles ...................................................................................... 52
   8.5 Caption Pen ..................................................................................................................................... 52
     8.5.1 Pen Size ..................................................................................................................................... 52
     8.5.2 Pen Spacing .............................................................................................................................. 53
     8.5.3 Font Styles................................................................................................................................. 53
     8.5.4 Character Offsetting ................................................................................................................. 54
     8.5.5 Pen Styles .................................................................................................................................. 54
     8.5.6 Foreground Color and Opacity................................................................................................ 54
     8.5.7 Background Color and Opacity ............................................................................................... 54
     8.5.8 Character Edges ....................................................................................................................... 54
     8.5.9 Caption Text Function Tags .................................................................................................... 56
     8.5.10 Pen Attributes ......................................................................................................................... 57
   8.6 Caption Text .................................................................................................................................... 57
   8.7 Caption Positioning ........................................................................................................................ 58
     8.7.1 Location within Internal Buffer ................................................................................................ 58
     8.7.2 Location (0,0)............................................................................................................................. 58
     8.7.3 Caption Row Lengths ............................................................................................................... 58
   8.8 Color Representation ..................................................................................................................... 58
   8.9 Service Synchronization ................................................................................................................ 58
     8.9.1 Delay Command ........................................................................................................................ 59
     8.9.2 DelayCancel Command ............................................................................................................ 59


                                                                             ii
                                                                                                                                          CEA-708-E

      8.9.3 Reset Command........................................................................................................................ 59
      8.9.4 Reset and DelayCancel Command Recognition.................................................................... 60
      8.9.5 Service Reset Conditions ........................................................................................................ 61
    8.10 DTVCC Command Set .................................................................................................................. 61
      8.10.1 Window Commands ............................................................................................................... 62
      8.10.2 Pen Commands ....................................................................................................................... 63
      8.10.3 Synchronization Commands ................................................................................................. 63
      8.10.4 Caption Text ............................................................................................................................ 63
      8.10.5 Command Descriptions ......................................................................................................... 63
    8.11 Proper Order of Data .................................................................................................................... 84
      8.11.1 Simple Roll-up Style Captions............................................................................................... 84
      8.11.2 Simple Paint-on Style Captions............................................................................................. 84
      8.11.3 Simple Pop-on Style Captions............................................................................................... 85

9 DTVCC Decoder Manufacturer Requirements and Recommendations ........................................... 85
   9.1 DTVCC Section 6.1 - Services ....................................................................................................... 85
   9.2 DTVCC Section 6.2 - Service Blocks ............................................................................................ 85
     9.2.1 Caption Service Directory and DTVCC Services ................................................................... 85
     9.2.2 Decoding 16 Services ............................................................................................................... 86
     9.2.3 Selecting CEA-608 Services Regardless of Presence of Caption Service Directory ........ 86
     9.2.4 Ignoring Reserved Field in caption_service_descriptor() .................................................... 86
     9.2.5 Automatic Switching from 708 to 608 ..................................................................................... 86
   9.3 DTVCC Section 7.1 - Code Space Organization .......................................................................... 86
   9.4 DTVCC Section 8.2 - Screen Coordinates .................................................................................... 87
   9.5 DTVCC Section 8.4 - Caption Windows ........................................................................................ 89
   9.6 DTVCC Section 8.4.2 - Window Priority........................................................................................ 89
   9.7 DTVCC Section 8.4.6 - Window Size ............................................................................................. 89
   9.8 DTVCC Section 8.4.8 - Word Wrapping ........................................................................................ 89
   9.9 DTVCC Section 8.4.9 - Window Text Painting ............................................................................. 89
     9.9.1 Justification ............................................................................................................................... 89
     9.9.2 Print Direction ........................................................................................................................... 90
     9.9.3 Scroll Direction ......................................................................................................................... 90
     9.9.4 Scroll Rate ................................................................................................................................. 90
     9.9.5 Smooth Scrolling ...................................................................................................................... 90
     9.9.6 Display Effects .......................................................................................................................... 90
   9.10 DTVCC Section 8.4.11 - Window Colors and Borders .............................................................. 91
   9.11 DTVCC Section 8.4.12 - Predefined Window and Pen Styles ................................................... 91
   9.12 DTVCC Section 8.5.1 - Pen Size .................................................................................................. 91
   9.13 DTVCC Section 8.5.3 - Font Styles.............................................................................................. 91
   9.14 DTVCC Section 8.5.4 - Character Offsetting .............................................................................. 91
   9.15 DTVCC Section 8.5.5 - Pen Styles ............................................................................................... 91
   9.16 DTVCC Section 8.5.6 - Foreground Color and Opacity............................................................. 91
   9.17 DTVCC Section 8.5.7 - Background Color and Opacity ............................................................ 91
   9.18 DTVCC Section 8.5.8 - Character Edges .................................................................................... 91
   9.19 DTVCC Section 8.8 - Color Representation ............................................................................... 91
   9.20 Character Rendition Considerations .......................................................................................... 92
   9.21 DTVCC Section 8.9 - Service Synchronization .......................................................................... 93
   9.22 DTV to NTSC (CEA-608) Transcoders ........................................................................................ 93
   9.23 Receivers Without Displays and Set-top Box (STB) Options .................................................. 94
   9.24 Use of CEA-608 datastream by DTV Receivers ......................................................................... 94

10 DTVCC Authoring and Encoding for Transmission (Informative) .................................................. 94
  10.1 Caption Authoring and Encoding ............................................................................................... 95
  10.2 Monitoring Captions ..................................................................................................................... 96

Annex A Possible Decoder Implementations (Informative).................................................................. 97


                                                                            iii
                                                                                                                                           CEA-708-E

Annex B Transmission ............................................................................................................................. 98
  B.1 Interpretation of Transmission Syntax ........................................................................................ 98

Annex C Caption Channel Packet Transmission Examples in MPEG-2 Video (Informative) ............ 99
  C.1 PICTURE 1: picture_structure = 11, top_field_first = 1, repeat_first_field = 1 ......................... 99
  C.2 PICTURE 2: picture_structure = 11, top_field_first = 0, repeat_first_field = 0 ......................... 99
  C.3 PICTURE 3: picture_structure = 11, top_field_first = 0, repeat_first_field = 1 ....................... 100

Annex D Transmission Order and Display Process Examples in MPEG-2 Video (Informative) ..... 101

Annex E DTVCC in the ATSC Transport with MPEG-2 Video (Informative) ...................................... 102
  E.1 General .......................................................................................................................................... 102
  E.2 MPEG-2 Picture User Data .......................................................................................................... 103
   E.2.1 Latency .................................................................................................................................... 103
  E.3 Caption Service Metadata and PSIP ........................................................................................... 103
  E.4 Caption Service Encoding ........................................................................................................... 103

Annex F (Deleted) ................................................................................................................................... 104

Annex G Closed Caption Data Structure .............................................................................................. 105




                                                                     Figures

Figure 1 DTV Closed-Captioning Protocol Model .................................................................................... 8
Figure 2 cc_data() State Table ................................................................................................................. 12
Figure 3 Example of CEA-608 Captioning Field Buffers ....................................................................... 13
Figure 4 Caption Channel Packet ............................................................................................................ 21
Figure 5 CCP State Table ......................................................................................................................... 23
Figure 6 Service Block.............................................................................................................................. 24
Figure 7 Service Block Header ................................................................................................................ 24
Figure 8 Extended Service Block Header ............................................................................................... 25
Figure 9 Null Service Block Header ........................................................................................................ 25
Figure 10 Service Blocks in a Caption Channel Packets (Example) ................................................... 26
Figure 11 Example of Window and Grid Location ................................................................................. 43
Figure 12 DTV 16:9 Screen and DTVCC Window Positioning Grid ...................................................... 44
Figure 13 Anchor ID Location .................................................................................................................. 45
Figure 14 Implied Caption Text Expansion Based on Anchor Points ................................................. 46
Figure 15 Examples of Caption Window Shrinking when User Selects Small Character Size ......... 47
Figure 16 Examples of Caption Window Growing when Going to Larger Font .................................. 48
Figure 17 Examples of Various Justifications, Print Directions and Scroll Directions ..................... 50
Figure 18 Character Background Color Examples ................................................................................ 54
Figure 19 Edge Type Examples ............................................................................................................... 56
Figure 20 Reset & DelayCancel Command Detector(s) and Service Input Buffers .......................... 60
Figure 21 Reset & DelayCancel Command Detector(s) Detail.............................................................. 61
Figure 22 Minimum Grid Location Super Cell Example ....................................................................... 88
Figure 23 Caption Authoring and Encoding into Caption Channel Packets ...................................... 95
Figure 24 Relationship Between Caption Data and Frames ................................................................. 96
Figure 25 DTVCC Transport Stream Decoder for an MPEG-2 Transport ........................................... 97
Figure 26 DTVCC Caption Data in the DTV Bitstream ......................................................................... 102
Figure 27 Structure of cc_data() ............................................................................................................ 105




                                                                            iv
                                                                                                                                  CEA-708-E

                                                                Tables
Table 1 DTVCC Protocol Stack .............................................................................................................. 6
Table 2 cc_data() Syntax ...................................................................................................................... 10
Table 3 Closed-Caption Type (cc_type) Coding ................................................................................ 11
Table 4 DTVCC Example #1 - MPEG-2 Video Transport Channel—cc_data() parameters ............ 16
Table 5 DTVCC Example #2 - MPEG-2 Video Transport Channel—cc_data() parameters ............ 17
Table 6 Aligned cc_data() structure and CCP Example .................................................................... 17
Table 7 Unaligned Caption Channel Packet Example ....................................................................... 18
Table 8 cc_data() Structure Example Showing Unusual Sequences of cc_ valid ......................... 18
Table 9 DTVCC Caption Channel Packet Syntax ............................................................................... 22
Table 10 Service Block Syntax ............................................................................................................ 24
Table 11 DTVCC Code Space Organization ....................................................................................... 28
Table 12 DTVCC Code Set Mapping ................................................................................................... 29
Table 13 C0 Code Set ........................................................................................................................... 30
Table 14 C1 Code Set ........................................................................................................................... 32
Table 15 G0 Code Set ........................................................................................................................... 33
Table 16 G1 Code Set ........................................................................................................................... 34
Table 17 G2 Code Set ........................................................................................................................... 35
Table 18 G3 Code Set ........................................................................................................................... 36
Table 19 C2 Code Set ........................................................................................................................... 37
Table 20 Extended Codes and Bytes to Skip—C2 Code Set ............................................................ 38
Table 21 C3 Code Set ........................................................................................................................... 38
Table 22 Extended Codes & Bytes to Skip—C3 Code Set ................................................................ 39
Table 23 Extended Codes and Bytes to Skip 0x90-0x9F .................................................................. 41
Table 24 Cursor Movement After Drawing Characters ..................................................................... 50
Table 25 Safe Title Area and Recommended Character Dimensions ............................................. 53
Table 26 Predefined Window Style IDs............................................................................................... 68
Table 27 Predefined Pen Style IDs ...................................................................................................... 69
Table 28 G2 Character Substitution Table ......................................................................................... 87
Table 29 Screen Coordinate Resolutions & Limits ........................................................................... 87
Table 30 Minimum Color List Table .................................................................................................... 91
Table 31 Alternative Minimum Color List Table ................................................................................ 92
Table 32 Caption Channel Packet Transmission Example A ........................................................... 99
Table 33 DTVCC Caption Channel Packet Transmission Example B ............................................. 99
Table 34 DTVCC Caption Channel Transmission Example C ........................................................ 100




                                                                      v
                                        CEA-708-E




(This page intentionally left blank.)




                 vi
                                                                                           CEA-708-E

                                         FOREWORD
This standard defines a method for coding text with associated parameters to control its display. This
document specifies the standard for Closed Captioning in Digital Television (DTV) technology.
Predecessors of this document were developed under the auspices of the Consumer Electronics
Association (CEA) Technology & Standards R4.3 Television Data Systems Subcommittee in parallel with
the U.S. Advanced Television Systems Committee’s (ATSC) definition, design, and development of the
audio, video and ancillary data processing standard for Advanced Television. The DTV standard
developed by the cable industry in SCTE for caption carriage is documented in SCTE 21 [6].

CEA-708-E supersedes CEA-708-D.




                                                  vii
                                        CEA-708-E




(This page intentionally left blank.)




                 viii
                                                                                               CEA-708-E

                Digital Television (DTV) Closed Captioning
1 Scope
This standard defines DTV Closed Captioning (DTVCC) and provides specifications and guidelines for
caption service providers, distributors of television signals, decoder and encoder manufacturers, DTV
receiver manufacturers, and DTV signal processing equipment manufacturers. CEA-708-E may also be
useful in other systems. This standard includes the following:

    a)   a description of the transport method of DTVCC data in the DTV signal
    b)   a specification for processing DTVCC information
    c)   a list of minimum implementation recommendations for DTVCC receiver manufacturers
    d)   a set of recommended practices for DTV encoder and decoder manufacturers

The use of the term DTV throughout is intended to include, and apply to, High Definition Television
(HDTV) and Standard Definition Television (SDTV).
1.1 Overview
DTVCC is a migration of the closed-captioning concepts and capabilities developed in the 1970’s for
National Television Systems Committee II (NTSC) television video signals to the digital television
environment defined by the ATV (Advanced Television) Grand Alliance and standardized by ATSC. This
new television environment provides for larger screens and higher screen resolutions, as well as higher
data rates for transmission of closed-captioning data.

NTSC Closed Captioning (CC) consists of an analog waveform inserted on line 21, field 1 and possibly
field 2, of the NTSC Vertical Blanking Interval (VBI). That waveform provides a transport channel which
can deliver 2 bytes of data on every field of video. This translates to a nominal 60 or 120 bytes per
second (Bps), or a nominal 480 or 960 bits per second (bps).

In contrast, DTV Closed Captioning is transported as a logical data channel in the DTV digital bitstream.

```



---

# Part 3: SCC File Format

## 3.1 SCC File Structure


SCC (Scenarist Closed Caption) is a file format for storing CEA-608 caption data.

### 3.1.1 File Header

```
Scenarist_SCC V1.0
```

This header **must** be the first line of every SCC file.

### 3.1.2 Timecode Format

Each caption data line begins with a timecode in format:

```
HH:MM:SS:FF
```

Where:
- **HH**: Hours (00-23)
- **MM**: Minutes (00-59)  
- **SS**: Seconds (00-59)
- **FF**: Frames (00-29 for 30fps, 00-23 for 24fps)

**Frame Rates:**
- NTSC: 29.97 fps (non-drop-frame)
- NTSC Drop-Frame: 29.97 fps with frame drop compensation
- Film: 23.976 fps  
- PAL: 25 fps (less common)

**Drop-Frame Notation:**  
Use semicolon before frames for drop-frame: `HH:MM:SS;FF`

### 3.1.3 Caption Data Format

After timecode, hex-encoded byte pairs separated by spaces:

```
00:00:03:29 9420 9420 94ad 94ad 9470 9470 4c4f 5245 4d20 4950 5355 4d
```

**Format Rules:**
1. Timecode followed by TAB or space
2. Hex byte pairs (4 characters each)  
3. Byte pairs separated by spaces
4. Control codes typically sent twice
5. One or more lines of data per timecode

### 3.1.4 Example SCC File

```
Scenarist_SCC V1.0

00:00:00:00 9420 9420 94ad 94ad 9470 9470 54c5 5354 2043 4150 5449 4f4e

00:00:03:00 942c 942c

00:00:05:15 9420 9420 9452 9452 5365 636f 6e64 2063 6170 7469 6f6e

00:00:08:00 942c 942c
```

**Explanation:**
- Line 1: File header
- Line 2: (blank line optional)  
- Line 3: At 00:00:00:00, send control codes and "TEST CAPTION" text
- Line 4: At 00:00:03:00, erase displayed memory (942c = EDM)
- Line 5: At 00:00:05:15, send new caption
- Line 6: At 00:00:08:00, erase displayed memory

### 3.1.5 Hex Encoding

Each byte pair represents one caption byte:
- **0x94, 0x20**: RCL command (Resume Caption Loading)
- **0x94, 0x2C**: EDM command (Erase Displayed Memory)  
- **0x94, 0x2F**: EOC command (End Of Caption)
- **0x91, 0x4E**: PAC for Row 1, indent 0
- **0x41**: ASCII 'A'
- **0x20**: Space

**Control Code Doubling:**  
Control codes are typically sent twice in SCC files for reliability:
```
9420 9420
```
This represents the same command (RCL) sent twice.

## 3.2 SCC Encoding Rules


### 3.2.1 Mandatory Elements

1. **Header**: Must be first line: `Scenarist_SCC V1.0`
2. **Timecodes**: Must be monotonically increasing
3. **Hex Pairs**: All data as 4-character hex pairs (e.g., 9420)  

### 3.2.2 Control Code Handling

- Control codes should be sent twice consecutively
- Some decoders require doubling, others accept single
- Best practice: always double control codes

### 3.2.3 Pop-On Caption Sequence

Typical pop-on caption in SCC:
```
00:00:01:00 9420 9420 94ad 94ad 9470 9470 [text bytes...] 942f 942f
```

**Breakdown:**
1. `9420 9420` - RCL (select pop-on mode) doubled  
2. `94ad 94ad` - CR (carriage return) doubled
3. `9470 9470` - PAC (row 1, indent 0) doubled
4. [text bytes] - Caption text
5. `942f 942f` - EOC (display caption) doubled

### 3.2.4 Erase Commands

To clear screen:
```  
00:00:05:00 942c 942c
```
`942c` = EDM (Erase Displayed Memory)

### 3.2.5 Roll-Up Caption Sequence

```
00:00:00:00 9425 9425 9470 9470 [text...] 94ad 94ad
```

**Breakdown:**
1. `9425 9425` - RU2 (2-row roll-up mode)
2. `9470 9470` - PAC (set base row)
3. [text bytes]  
4. `94ad 94ad` - CR (carriage return - triggers roll)

## 3.3 Common SCC Hex Commands Reference


### Mode Commands
| Hex Code | Command | Description |
|----------|---------|-------------|
| 9420 | RCL | Resume Caption Loading (pop-on mode) |
| 9425 | RU2 | Roll-Up 2 rows |  
| 9426 | RU3 | Roll-Up 3 rows |
| 9429 | RDC | Resume Direct Captioning (paint-on mode) |

### Display Commands
| Hex Code | Command | Description |
|----------|---------|-------------|
| 942c | EDM | Erase Displayed Memory |
| 942e | ENM | Erase Non-Displayed Memory |  
| 942f | EOC | End Of Caption (display pop-on) |

### Cursor Commands
| Hex Code | Command | Description |
|----------|---------|-------------|
| 9421 | BS | Backspace |
| 94ad | CR | Carriage Return |  

### Tab Offsets  
| Hex Code | Command | Description |
|----------|---------|-------------|
| 9721 | TO1 | Tab Offset 1 column |
| 9722 | TO2 | Tab Offset 2 columns |
| 9723 | TO3 | Tab Offset 3 columns |

### PAC Commands (Row Positioning)
| Hex Code | Row | Indent |
|----------|-----|--------|
| 9140 | 1 | 0 |  
| 9141 | 1 | 4 |
| 9142 | 1 | 8 |
| 9143 | 1 | 12 |
| 91d0 | 2 | 0 |
| 9240 | 3 | 0 |  
| 9340 | 4 | 0 |
| 9470 | 11 | 0 |
| 1040 | 12 | 0 |
| 1340 | 13 | 0 |
| 1640 | 14 | 0 |
| 9670 | 15 | 0 |

*(Full PAC table in Section 1.3.1)*



---

# Part 4: Compliance Requirements

## 4.1 SCC File Format Compliance


### 4.1.1 Mandatory Requirements

A compliant SCC file **MUST**:
1. Start with header: `Scenarist_SCC V1.0`
2. Use timecode format: `HH:MM:SS:FF` or `HH:MM:SS;FF` (drop-frame)
3. Encode all caption data as hex byte pairs (4 hex chars per pair)
4. Use spaces or tabs to separate hex pairs  
5. Have monotonically increasing timecodes

### 4.1.2 Caption Data Compliance  

Caption data **MUST**:
1. Use valid CEA-608 control codes
2. Use valid character codes (0x20-0x7F for basic, special codes for extended)
3. Not exceed 32 characters per row
4. Not exceed 15 rows total  
5. Respect safe caption area (rows 2-14, columns 3-30 recommended)

### 4.1.3 Control Code Compliance

Implementations **SHOULD**:
1. Double all control codes (send twice) for reliability
2. Properly pair control code bytes (two bytes per command)
3. Use proper command sequences for each caption mode  

### 4.1.4 Timing Compliance

Implementations **MUST**:
1. Handle drop-frame vs non-drop-frame correctly
2. Not send captions faster than decoder can process (~30 chars/second max)
3. Provide adequate display time for readability (minimum 1.5 seconds)

## 4.2 CEA-608 Decoder Compliance


A compliant CEA-608 decoder **MUST**:

### 4.2.1 Memory Requirements
- Support minimum 4 rows of caption memory
- Handle both displayed and non-displayed memory for pop-on
- Support roll-up modes with 2, 3, and 4 row depths

### 4.2.2 Character Support  
- Display all standard characters (0x20-0x7F)
- Display all special characters
- Support at least basic extended character sets (Spanish, French)

### 4.2.3 Command Support
- Implement all mandatory control codes (RCL, RU2-4, RDC, EDM, ENM, EOC, CR)
- Implement PAC positioning for all 15 rows
- Support tab offsets (TO1-TO3)  
- Implement backspace (BS)
- Implement delete to end of row (DER)

### 4.2.4 Attribute Support
- Support all foreground colors (white, green, blue, cyan, red, yellow, magenta)
- Support background colors
- Support italics and underline  
- Support mid-row attribute changes

### 4.2.5 Mode Support
- Pop-on captions (mandatory)
- Roll-up captions in 2, 3, and 4 row modes
- Paint-on captions  
- Text mode (optional for captions)

## 4.3 SCC Writer Compliance


A compliant SCC writer **MUST**:

### 4.3.1 File Format
1. Output valid SCC header
2. Use proper timecode format with correct frame rate
3. Encode bytes as uppercase or lowercase hex (uppercase preferred)  
4. Separate hex pairs with single space
5. Use proper line endings (CRLF or LF acceptable)

### 4.3.2 Data Encoding
1. Double all control codes  
2. Use valid CEA-608 command sequences
3. Properly encode extended characters
4. Handle special characters correctly

### 4.3.3 Timing
1. Output monotonically increasing timecodes  
2. Calculate proper frame numbers for frame rate
3. Handle drop-frame compensation if required

### 4.3.4 Caption Modes
1. Generate proper command sequences for pop-on mode
2. Generate proper command sequences for roll-up modes
3. Generate proper PAC commands for positioning  
4. Use appropriate erase commands

## 4.4 Common Compliance Issues


### 4.4.1 Invalid Control Codes
- Using invalid byte combinations
- Not doubling control codes
- Mixing Field 1 and Field 2 commands incorrectly  

### 4.4.2 Positioning Errors
- Positioning beyond row 15 or column 32
- Not using PACs before text
- Improper base row for roll-up

### 4.4.3 Character Encoding Errors  
- Using invalid character codes
- Improper extended character sequences
- Missing parity bits (in raw transmission, N/A for SCC files)

### 4.4.4 Timing Errors
- Non-monotonic timecodes
- Incorrect frame count for frame rate  
- Drop-frame notation errors

### 4.4.5 Mode Switching Errors
- Switching modes without proper erase commands
- Roll-up depth conflicts with base row
- Not using proper style command before caption data



---

# Part 5: Quick Reference Tables

## 5.1 Complete Control Code Table

```



                                                     113
CEA-608-E


Data Set Group counts - The linear algorithm has no grouping, in effect having one group per packet. The
alternating algorithm groups several packets together.

    High rep group count - Number of groups in the high repetition rate category.
    Med rep group count - Number of groups in the medium repetition rate category.
    Low rep group count - Number of groups in the low repetition rate category.

Algorithm Char counts -

Total Chars/pass - The number of characters transmitted each time the algorithm is executed.
High rep chars/pass - The number of high repetition rate packet characters transmitted each time the
algorithm is executed.
Med rep chars/pass - The number of medium repetition rate packet characters transmitted each time the
algorithm is executed.
Low rep chars/pass - The number of low repetition rate packet characters transmitted each time the
algorithm is executed.

Avg Rep Rate 100% BW, s

High - The average number of seconds between each occurrence of a given high repetition rate packet if
all field 2 bandwidth is dedicated to XDS.
Med - The average number of seconds between each occurrence of a given medium repetition rate packet
if all field 2 bandwidth is dedicated to XDS.
Low - The average number of seconds between each occurrence of a given low repetition rate packet if all
field 2 bandwidth is dedicated to XDS.

Avg Rep Rate 70% or 30% BW, s

High, Med, Low - The average number of seconds between each occurrence of a given high, medium or
low repetition rate packet if 70% or 40% of field 2 bandwidth is dedicated to XDS.

Worst case Rep Rate 30% BW, s

High, Med, Low - The longest time, in seconds, between two of a given high, medium or low repetition rate
packet over the one complete pass of the algorithm, assuming 30% of field 2 bandwidth is dedicated to
XDS.




                                                  114
                                                                                             CEA-608-E




Packet Description   Linear      Linear Algorithm                   Alternating Algorithm


                     Min/max     Priority   Pkt Len       Pkt Len   Priority       Pkt Len   Pkt Len

                                            Set 1         Set 2                    Set 1     Set 2

Current Class

Program ID           8           M1                       8         M1                       8

Length/TIS           6/10        H1                       8         H1                       8

Prog Name            6/36        H2                       36        H1                       36

Prog Type            6/36        M2                       36        M1                       36

Prog Rating          6           M3                       6         M1                       6

Audio Services       6           M4                       6         M1                       6

Caption Services     6/12        M5                       12        M1                       12

Aspect Ratio         6/8         H3                       8         H2                       8

Composite 1          16/36       H4         30                      H1             30

Composite 2          18/36       H5         30                      H2             30

Prog Desc 1          6/36        M6         30            36        M2             30        36

Prog Desc 2          6/36        M7         30            36        M3             30        36

Prog Desc 3          6/36        M8         30            36        M4             30        36

Prog Desc 4          6/36        M9         30            36        M5             30        36

Prog Desc 5          6/36        M10                      36        M6                       36

Prog Desc 6          6/36        M11                      36        M7                       36

Prog Desc 7          6/36        M12                      36        M8                       36

Prog Desc 8          6/36        M13                      36        M9                       36

                         Table 56 Alternating Algorithm Lookup Table (Continued)




                                                    115
     CEA-608-E




Packet Description   Linear      Linear Algorithm                   Alternating Algorithm


                     Min/max     Priority   Pkt Len       Pkt Len   Priority       Pkt Len   Pkt Len

                                            Set 1         Set 2                    Set 1     Set 2

Future Class

Program ID           8           L2                       8         L1                       8

Length/TIS           6/10        L3                       8         L1                       8

Prog Name            6/36        L4                       36        L1                       36

Prog Type            6/36        L5                       36        L2                       36

Prog Rating          6           L6                       6         L2                       6

Audio Services       6           L7                       6         L2                       6

Caption Services     6/12        L8                       12        L3                       12

Aspect Ratio         6/8         L9                       8         L2                       8

Composite 1          16/36       L10        30                      L3             30

Composite 2          18/36       L1         30                      L1             30

Prog Desc 1          6/36        L11        30            36        L5             30        36

Prog Desc 2          6/36        L12        30            36        L6             30        36

Prog Desc 3          6/36        L13        30            36        L7             30        36

Prog Desc 4          6/36        L14        30            36        L8             30        36

Prog Desc 5          6/36        L15                      36        L9                       36

Prog Desc 6          6/36        L16                      36        L10                      36

Prog Desc 7          6/36        L17                      36        L11                      36

Prog Desc 8          6/36        L18                      36        L12                      36

Channel Info Class

Network Name         6/36        H6                       36        H2                       36

Call Ltr/Chan        8/10        H7                       10        H2                       10

Tape Delay           6           L19        6             6         L13            6         6

                         Table 57 Alternating Algorithm Lookup Table (Continued)




                                                    116
                                                                                                CEA-608-E



Packet Description      Linear      Linear Algorithm                   Alternating Algorithm
                        Min/max     Priority    Pkt Len      Pkt Len   Priority       Pkt Len   Pkt Len
                                                Set 1        Set 2                    Set 1     Set 2
Misc Class

Time of Day             10          L20         10           10        L16              10      10

Impulse Capt            10          H8                                 H2

Suppl Date Loc          6/36        L21                      6         L14                      6

Time Zone/DST           6           L22                      6         L15                      6

OOB Channel #           6           L23                      6         L4                       6
Public Serv Class

NWS Code                16          H9                       16        H2                       16

NWS Message             6/36        H10                      36        H2                       36

Undefined XDS           4/36        Not Repetitive                     Not Repetitive
Data Set Char Counts

XDS Char Count                                  376          948                        376     948

High Rep Char Cnt                               60           150                        60      150

Med Rep Char Cnt                                120          356                        120     356

Low Rep Char Cnt                                196          442                        196     442
Data Set Group Counts

High Rep Group Cnt                              2            7                          2       2

Med Rep Group Cnt                               4            12                         4       9

Low Rep Group Cnt                               8            21                         8       16
Algorithm Char Counts

Total Char/Pass                                 3556         48868                      2116    16938

High Rep Char/Pass                              2400         40950                      960     10800

Med Rep Char/Pass                               960          7476                       960     5696

Low rep Char/Pass                               196          442                        196     442

                            Table 58 Alternating Algorithm Lookup Table (Continued)




                                                       117
       CEA-608-E




Packet Description        Linear      Linear Algorithm                      Alternating Algorithm


                          Min/max     Priority     Pkt Len       Pkt Len    Priority        Pkt Len    Pkt Len

                                                   Set 1         Set 2                      Set 1      Set 2

Avg Rep Rate 100% BW,s

High                                               1.5           3.0                        2.2        3.9

Medium                                             7.4           38.3                       4.4        17.6

Low                                                59.3          814.5                      35.3       282.3

Avg Rep Rate 70% BW,s

High                                               2.1           4.3                        3.1        5.6

Medium                                             10.6          55.4                       6.3        25.2

Low                                                84.7          1163.5                     50.4       403.3

Avg Rep Rate 30% BW,s

High                                               4.9           9.9                        7.3        13.1

Medium                                             24.7          129.3                      14.7       58.8

Low                                                197.6         2714.9                     117.6      941.0

Worst Case Rep Rate 30% BW,s

High                                               5.0           7.8                        8.3        17.7

Medium                                             23.7          130.1                      15.0       60.2

Low                                                197.6         2714.9                     117.6      941.0

Assumptions for data set 2: Composite 1 is not transmitted because program type, length, and title

Overflow the fields and it is more efficient to transmit them separately. Composite 2 is not transmitted

Because caption services, network name and native channel overflow their respective fields.

                            Table 59 Alternating Algorithm Lookup Table (Continued)




                                                           118
                                                                                                       CEA-608-E




Annex K Canadian CRTC Letter Decisions and Official Translations (Informative)
Following is the text of a communication received from Industry Canada concerning the French
translations and the official contracted forms appearing in EIA-744-A: 11

Dear Mr. Hanover;

This is to inform you that Industry Canada supports fully the Draft
EIA744, its French translations and the official contracted forms for the
V-chip descriptors (as per attached).

George Zurakowski
Manager, Broadcasting Regulations and Standards
Industry Canada
613-990-4950 (Voice) 613-991-0652 (Fax)
zurakowg@spectrum.ic.gc.ca (Internet address)

This annex is informative as supplied by the Canadian Government. For further information, see the letter
decisions:

                    •   Public Notice CRTC 1996-36, Respecting Children: A Canadian Approach to Helping
                        Families Deal with Television Violence
                    •   Public Notice CRTC 1997-80, Classification System for Violence in Television
                        Programming

                                        OFFICIAL TRANSLATIONS
                                              English to French
Système de classification anglais du Canada

E        Émissions exemptées de classification - Sont exemptes, notamment les émissions suivantes : les
émissions de nouvelles, les émissions de sports, les documentaires et les autres émissions d’information;
les tribunes téléphoniques, les émissions de musique vidéo et les émissions de variétés.

C       Émissions à l’intention des enfants de moins de 8 ans - Lignes directrices sur la violence : Il faut
porter une attention particulière aux thèmes qui pourraient troubler la tranquilité d’esprit et menacer le
bien-être des enfants. Les émissions ne doivent pas présenter de scènes réalistes de la violence. Les
représentations de comportements agressifs doivent être peu fréquentes et limitées à des images de
nature manifestement imaginaires, humoristiques et irréalistes.

Autres directives à l’égard du contenu : Le contenu des émissions ne doit en aucun cas comporter de
jurons, de nudité ou de sexe.

C8+      Émissions que les enfants de huit ans et plus peuvent généralement regarder seuls - Lignes
directrices sur la violence: Il s’agit d’émissions qui ne représentent pas la violence comme moyen
privilégié, acceptable ou comme seul moyen de résoudre les conflits, ou qui n’encouragent pas les
enfants à imiter les actes dangereux qu’ils peuvent voir à la télévision. Toutes réprésentations réallistes
de violence seront peu fréquentes, discrètes, de basse intensité et montreront les conséquences des
actes.

Autres directives à l’égard du contenu : Le contenu de ces émissions peut présenter un langage grossier,
de la nudité ou du sexe.


11
     EIA-774-A was an antecedent document to CEA-608-E and its information is fully contained in CEA-608-E.


                                                        119
CEA-608-E


G       Général - Lignes directrices sur la violence : Les émissions comporteront très peu de scènes de
violence physique, verbale ou affective. Elles porteront une attention particulière aux thèmes qui
pourraient effrayer un jeune enfant et ne comporteront aucune scène réaliste de violence qui minimise ou
estompe les effets des actes violents.

Autres directives à l’égard du contenu : Les émissions peuvent présenter un contenu comportant de
l’argot, mais aucune représentation de scène de nudité ou de sexe ne sera faite.

PG       Surveillance parentale - Bien qu’elles soient destinées à un auditoire général, ces émissions
peuvent ne pas convenir aux jeunes enfants. Les parents doivent savoir que le contenu de ces émissions
pourrait comporter des éléments que certains pourraient considérer comme impropres pour que des
enfants de 8 à 13 ans les regardent sans surveillance. Lignes directrices sur la violence : Toute
représentation de conflits et (ou) d’agressions doit être limitée et modérée; il pourrait s’agir de violence
physique légère ou humoristique, ou de violence surnaturelle.

Autres directives à l’égard du contenu : Ces émissions peuvent présenter un contenu quelque peu
grossier, un langage suggestif, ou encore de brèves scènes de nudité.

14+     Émissions comportant des thèmes ou des éléments de contenu qui pourraient ne pas convenir
aux téléspectateurs de moins de 14 ans - On incite fortement les parents à faire preuve de circonspection
en permettant à des préadolescents et à des enfants au début de l’adolescence de regarder ces
émissions. Lignes directrices sur la violence : Ces émissions pourraient contenir des scènes intenses de
violence et présenter de façon réaliste des thèmes adultes et des problèmes de société.

Autres directives à l’égard du contenu : Les émissions pourraient présenter des scènes de nudité ou de
sexe, et utiliser un langage grossier.

18+    Adultes - Lignes directrices sur la violence : Ces émissions peuvent faire certaines
représentations de la violence faisant partie intégrante de l’évolution de l’intrigue, des personnages et des
thèmes, et s’adressent aux adultes.

Autres directives à l’égard du contenu : Ces émissions peuvent comporter un langage grossier et une
représentation explicite de nudité et (ou) de sexe.

                                           French to English
Canadian French Language Rating System

E               Exempt - Exempt programming

G                General - Programming intended for audience of all ages. Contains no violence, or the
violence it contains is minimal or is depicted appropriately with humour or caricature or in an unrealistic
manner.

8 ans+           8+ General - Not recommended for young children - Programming intended for a broad
audience but contains light or occasional violence that could disturb young children. Viewing with an adult
is therefore recommended for young children (under the age of 8) who cannot differentiate between real
and imaginary portrayals.

13 ans+         Programming may not be suitable for children under the age of 13 - Contains either a few
violent scenes or one or more sufficiently violent scenes to affect them. Viewing with an adult is therefore
strongly recommended for children under 13.

16 ans+           Programming is not suitable for children under the age of 16 - Contains frequent scenes
of violence or intense violence.




                                                     120
                                                                                           CEA-608-E


18 ans+        Programming restricted to adults - Contains constant violence or scenes of extreme
violence.

The following are contracted forms of the English and French Language rating systems. The standards
shall be used where applicable.
K.1 Primary Language

                        CONTRACTIONS FOR ENGLISH RATINGS
Title          Cdn. English Ratings
Symbol         Contracted Description
E              Exempt
C              Children
C8+            8+
G              General
PG             PG
14+            14+
18+            18+
                           CONTRACTIONS FOR FRENCH RATINGS
Title         Codes fr. du Canada
Symbol        Contracted Description
E              Exemptées
G              Pour tous
8 ans +        8+
13 ans +       13+
16 ans +       16+
18 ans +       18+

                     OFFICIAL TRANSLATION OF CONTRACTED FORMS
                                         English to French
Titre :        Codes ang. du Canada
Titre          Symbole
E              Exemptées
C              Enfants
C8+            8+
G              Général
PG             Surv. parentale
14+            14+
18+            18+
                                         French to English
Title:         Cdn. French Ratings
Title          Symbol
E              Exempt
G              For all
8 ans+         8+
13 ans+        13+
16 ans+        16+
18 ans+        18+




                                                 121
CEA-608-E



Annex L Content Advisories (Informative)
L.1 Scope
This annex is intended to provide guidance for XDS decoder manufacturers utilizing the Program Rating
(Content Advisory) packet. This packet has a current class type code 0x05, and is described in detail in
Section 9.5.1.1.

This annex also provides guidance for manufacturers of Digital Television Receivers and contains
recommended practices for use with CEA-766-B and ATSC A/53E and A/65C.

For excerpts from relevant U.S. Federal Communications Commission regulations, see Annex F2
(Informative). For information concerning relevant Canadian government decisions, see Annex K
(Informative).
L.2 Receiver Indication
Once a program is blocked, the receiver should indicate to the viewer that Content Advisory blocking has
occurred via an appropriate on screen display message The receiver may use additional XDS or PSIP
data to display other information, such as program length, title, etc., if available.
L.3 Blocking
The default state of a receiver (i.e. as provided to the consumer) should not block unrated programs
However, it is permissible to include features that allow the user to reprogram the receiver to block
programs that are not rated.

                •   For U.S., see FCC Rules Section 15.120(e)(2).
                •   For Canada, see Public Notice CRTC 1996-36, section 1, paragraph 3.

In the U.S., programs with a rating of “None” are not intended to be blocked per the content advisory
criteria (see Table 22). Certain types of programming may either carry the content advisory of "None" or
not contain a content advisory packet. Examples of this type of programming include:

                •   Emergency Bulletins (such as EAS messages, weather warnings and others)
                •   Locally originated programming
                •   News
                •   Political
                •   Public Service Announcements
                •   Religious
                •   Sports
                •   Weather

Programs which are not intended to be blocked in Canada are rated with an "Exempt" rating code.
Exempt programming includes: News, sports, documentaries and other information programming such as
talk shows, music videos, and variety programming (see Public Notice CRTC 1997-80, Appendix A).

If provisions are included to allow the consumer to block on a rating of “None” or when no rating packets
are present, receiver manufacturers should appropriately educate consumers on the use of this feature
(e.g. in the instruction book).
L.4 Cessation

        NOTE—Section L.4.1 is considered part of Section L.4 when an analog set is in use, and Section
        L.4.2 is considered part of Section L.4 when a digital set is in use.

If the user has enabled program blocking and the receiver allows the user to program the default blocking
state (i.e. to block or unblock), then the TV should immediately revert to the default blocking state under
the following conditions If the receiver does not allow the user to program the default blocking state, then
the TV should immediately unblock under the following conditions:


                                                    122
                                                                                                  CEA-608-E


a) If the channel is changed.
b) If the input source is changed.

Channel blocking should always cease when a content advisory packet is received which contains an
acceptable rating and/or advisory level.
L.4.1 Analog Cessation
When an analog set is in use, the following is a continuation of the list in Section L.4:

c) If no content advisory is received for 5 seconds.
d) If a new Current Class ID or Title packet is received.
e) If the XDS Content Advisory packet’s a0 and a1 bits indicate the MPA rating system is in use and an
   MPAA rating of “N/A” is received.
f) If the XDS Content Advisory packet’s a0 and a1 bits indicate the TV Parental Guideline rating system is
   in use and a TV Parental Guideline rating of “None” is received.
g) If there is no valid line 21 data on field 2 for 45 frames.
h) If the XDS Content Advisory packet's a0, a1, a2, a3 bits indicate the Canadian English language rating
   system is in use and a Canadian English Language rating of "Exempt" is received.
i) If the XDS Content Advisory packet's a0, a1, a2, a3 bits indicate the Canadian French language rating
   system is in use and a Canadian French Language rating of "Exempt" is received.
j) If a Content Advisory packet is received with the a0, a1, a2, a3 bits indicating systems 5 and 6 (non US
   and non-Canadian rating system) is in use (until these rating systems are further defined).
L.4.2 Digital Cessation
When a digital set is in use, the following is a continuation of the list in Section L.4:

k) If the content advisory descriptor indicates that the MPA rating system is in use and an MPA rating of
   "N/A" is received
l) If the content advisory descriptor indicates that the TV Parental Guideline rating system is in use and a
   TV Parental Guideline rating of "None" is received
m) If the content advisory descriptor indicates that the Canadian English Language rating system is in use
   and a Canadian English Language rating packet of "Exempt" is received
n) If the content advisory descriptor indicates that the Canadian French Language rating system is in use
   and a Canadian French Language rating packet of "Exempt" is received
o) If there is no valid content advisory descriptor information for 1.2 seconds.
L.5 Selection Advisory
When the categories D, L, S, V, and FV are chosen for blocking, without an age based rating, a receiver
should display an advisory that some program sources will not be blocked.
L.6 Rating Information
The remote control may include a button, which displays the rating icon, and/or the descriptive language,
but neither should be displayed except upon action of the viewer unless the set is in the blocked mode.
Note that the categories D, L, S, & V should be displayed only in alphabetical order, especially when each
is denoted by a single letter.

For the Canadian systems, as a minimum requirement, the rating information as viewed on-screen should
be available in its primary language That is, the English language rating system should be available in
English and the French language rating system should be available in French. Manufacturers are free to
implement translations, however, if they wish to do so they should adhere to the translations provided in
Annex K.
L.7 XDS Data
NTSC Broadcasters should include XDS packets with the title, start time, and stop time/duration for
display when the receiver is in blocking mode. This parallels a recommendation for DTV Broadcasters.




                                                       123
CEA-608-E


L.8 Auxiliary Input
If a receiver has the ability to decode line 21 XDS information for the Auxiliary Inputs, then it should block
the inputs based on the MPA, U.S. TV Parental Guideline, Canadian English Language or Canadian
French Language rating level selected by the viewer. If the receiver does not have the ability to decode
the Auxiliary Input’s line 21 XDS information, then it should block or otherwise disable the Auxiliary Inputs
if the viewer has enabled Content Advisory blocking Once again, this appears to be the only valid solution
for allowing Content Advisory information to be a useful feature.

In a similar fashion, DTV sets with an Auxiliary Input should block the inputs based on the MPA, U.S. TV
Parental Guideline, Canadian English Language or Canadian French Language rating level selected by
the viewer. If the receiver does not have the ability to decode the Auxiliary Input’s content advisory
descriptor information, then it should block or otherwise disable the Auxiliary Inputs if the viewer has
enabled Content Advisory blocking.
L.9 Invalid Ratings
An invalid rating should be ignored by the receiver and treated as if no rating packet or content advisory
descriptor was received.

For the TV Parental Guidelines, an invalid rating is defined as any combination of Age Rating and
Content Flag which does not appear in Table 22 for NTSC receivers or Table 1 of CEA-766-B for DTV
receivers.

For the Canadian English Language ratings, a rating level of (g2,g1,g0) = (1,1,1) is invalid For the
Canadian French Language ratings, the rating levels (g2,g1,g0) = (1,1,0) and (1,1,1) are invalid.
L.10 Multiple Rating Systems
CEA-608-E precludes the simultaneous use of multiple rating systems. All six systems described in
Section 9.5.1.1 are mutually exclusive.

In a similar fashion, a given program transmitted within digital TV, targeted for distribution in a single
region, should only use a single rating system within the content advisory descriptor (per CEA-766-B).
L.11 Blocking Hierarchy (Television Parental Guidelines)
Table 60 indicates the only valid combinations of age and content based ratings with a “3” in the
appropriate boxes For example, TV-PG-S,V is a valid rating, as is TV-PG However, TV-PG-FV is not a
valid rating.

                          Age Rating       FV       D       L        S       V
                          “TV-Y”
                          “TV-Y7”          X
                          “TV-G”
                          “TV-PG”                   X       X        X       X
                          “TV-14”                   X       X        X       X
                          “TV-MA”                           X        X       X
                                      Table 60 Blocking Example A

The following examples apply to both analog and digital TV In the following tables and in reference to the
corresponding examples, a “B” indicates a rating, which is blocked, and a “U” indicates a rating, which is
unblocked. In these examples, the user should always have the capability to override the automatic
blocking on a cell by cell basis.

If a viewer chooses to block any program with a Violence (V) flag without regard to an age based rating,
all entries in that column are automatically blocked as shown by the shaded cells in Table 60. Note that
the same result will occur if the TV-PG-V rating combination is chosen based on the automatic blocking
feature.



                                                     124
                                                                                                      CEA-608-E


                           Age Rating        FV       D        L       S        V
                           “TV-Y”
                           “TV-Y7”           U
                           “TV-G”
                           “TV-PG”                    U        U       U        B
                           “TV-14”                    U        U       U        B
                           “TV-MA”                             U       U        B
                                        Table 61 Blocking Example B

It should be noted that the rating TV-MA-D is not a valid age based and content based rating

```

## 5.2 Complete PAC Table

```

Autres directives à l’égard du contenu : Les émissions peuvent présenter un contenu comportant de
l’argot, mais aucune représentation de scène de nudité ou de sexe ne sera faite.

PG       Surveillance parentale - Bien qu’elles soient destinées à un auditoire général, ces émissions
peuvent ne pas convenir aux jeunes enfants. Les parents doivent savoir que le contenu de ces émissions
pourrait comporter des éléments que certains pourraient considérer comme impropres pour que des
enfants de 8 à 13 ans les regardent sans surveillance. Lignes directrices sur la violence : Toute
représentation de conflits et (ou) d’agressions doit être limitée et modérée; il pourrait s’agir de violence
physique légère ou humoristique, ou de violence surnaturelle.

Autres directives à l’égard du contenu : Ces émissions peuvent présenter un contenu quelque peu
grossier, un langage suggestif, ou encore de brèves scènes de nudité.

14+     Émissions comportant des thèmes ou des éléments de contenu qui pourraient ne pas convenir
aux téléspectateurs de moins de 14 ans - On incite fortement les parents à faire preuve de circonspection
en permettant à des préadolescents et à des enfants au début de l’adolescence de regarder ces
émissions. Lignes directrices sur la violence : Ces émissions pourraient contenir des scènes intenses de
violence et présenter de façon réaliste des thèmes adultes et des problèmes de société.

Autres directives à l’égard du contenu : Les émissions pourraient présenter des scènes de nudité ou de
sexe, et utiliser un langage grossier.

18+    Adultes - Lignes directrices sur la violence : Ces émissions peuvent faire certaines
représentations de la violence faisant partie intégrante de l’évolution de l’intrigue, des personnages et des
thèmes, et s’adressent aux adultes.

Autres directives à l’égard du contenu : Ces émissions peuvent comporter un langage grossier et une
représentation explicite de nudité et (ou) de sexe.

                                           French to English
Canadian French Language Rating System

E               Exempt - Exempt programming

G                General - Programming intended for audience of all ages. Contains no violence, or the
violence it contains is minimal or is depicted appropriately with humour or caricature or in an unrealistic
manner.

8 ans+           8+ General - Not recommended for young children - Programming intended for a broad
audience but contains light or occasional violence that could disturb young children. Viewing with an adult
is therefore recommended for young children (under the age of 8) who cannot differentiate between real
and imaginary portrayals.

13 ans+         Programming may not be suitable for children under the age of 13 - Contains either a few
violent scenes or one or more sufficiently violent scenes to affect them. Viewing with an adult is therefore
strongly recommended for children under 13.

16 ans+           Programming is not suitable for children under the age of 16 - Contains frequent scenes
of violence or intense violence.




                                                     120
                                                                                           CEA-608-E


18 ans+        Programming restricted to adults - Contains constant violence or scenes of extreme
violence.

The following are contracted forms of the English and French Language rating systems. The standards
shall be used where applicable.
K.1 Primary Language

                        CONTRACTIONS FOR ENGLISH RATINGS
Title          Cdn. English Ratings
Symbol         Contracted Description
E              Exempt
C              Children
C8+            8+
G              General
PG             PG
14+            14+
18+            18+
                           CONTRACTIONS FOR FRENCH RATINGS
Title         Codes fr. du Canada
Symbol        Contracted Description
E              Exemptées
G              Pour tous
8 ans +        8+
13 ans +       13+
16 ans +       16+
18 ans +       18+

                     OFFICIAL TRANSLATION OF CONTRACTED FORMS
                                         English to French
Titre :        Codes ang. du Canada
Titre          Symbole
E              Exemptées
C              Enfants
C8+            8+
G              Général
PG             Surv. parentale
14+            14+
18+            18+
                                         French to English
Title:         Cdn. French Ratings
Title          Symbol
E              Exempt
G              For all
8 ans+         8+
13 ans+        13+
16 ans+        16+
18 ans+        18+




                                                 121
CEA-608-E



Annex L Content Advisories (Informative)
L.1 Scope
This annex is intended to provide guidance for XDS decoder manufacturers utilizing the Program Rating
(Content Advisory) packet. This packet has a current class type code 0x05, and is described in detail in
Section 9.5.1.1.

This annex also provides guidance for manufacturers of Digital Television Receivers and contains
recommended practices for use with CEA-766-B and ATSC A/53E and A/65C.

For excerpts from relevant U.S. Federal Communications Commission regulations, see Annex F2
(Informative). For information concerning relevant Canadian government decisions, see Annex K
(Informative).
L.2 Receiver Indication
Once a program is blocked, the receiver should indicate to the viewer that Content Advisory blocking has
occurred via an appropriate on screen display message The receiver may use additional XDS or PSIP
data to display other information, such as program length, title, etc., if available.
L.3 Blocking
The default state of a receiver (i.e. as provided to the consumer) should not block unrated programs
However, it is permissible to include features that allow the user to reprogram the receiver to block
programs that are not rated.

                •   For U.S., see FCC Rules Section 15.120(e)(2).
                •   For Canada, see Public Notice CRTC 1996-36, section 1, paragraph 3.

In the U.S., programs with a rating of “None” are not intended to be blocked per the content advisory
criteria (see Table 22). Certain types of programming may either carry the content advisory of "None" or
not contain a content advisory packet. Examples of this type of programming include:

                •   Emergency Bulletins (such as EAS messages, weather warnings and others)
                •   Locally originated programming
                •   News
                •   Political
                •   Public Service Announcements
                •   Religious
                •   Sports
                •   Weather

Programs which are not intended to be blocked in Canada are rated with an "Exempt" rating code.
Exempt programming includes: News, sports, documentaries and other information programming such as
talk shows, music videos, and variety programming (see Public Notice CRTC 1997-80, Appendix A).

If provisions are included to allow the consumer to block on a rating of “None” or when no rating packets
are present, receiver manufacturers should appropriately educate consumers on the use of this feature
(e.g. in the instruction book).
L.4 Cessation

        NOTE—Section L.4.1 is considered part of Section L.4 when an analog set is in use, and Section
        L.4.2 is considered part of Section L.4 when a digital set is in use.

If the user has enabled program blocking and the receiver allows the user to program the default blocking
state (i.e. to block or unblock), then the TV should immediately revert to the default blocking state under
the following conditions If the receiver does not allow the user to program the default blocking state, then
the TV should immediately unblock under the following conditions:


                                                    122
                                                                                                  CEA-608-E


a) If the channel is changed.
b) If the input source is changed.

Channel blocking should always cease when a content advisory packet is received which contains an
acceptable rating and/or advisory level.
L.4.1 Analog Cessation
When an analog set is in use, the following is a continuation of the list in Section L.4:

c) If no content advisory is received for 5 seconds.
d) If a new Current Class ID or Title packet is received.
e) If the XDS Content Advisory packet’s a0 and a1 bits indicate the MPA rating system is in use and an
   MPAA rating of “N/A” is received.
f) If the XDS Content Advisory packet’s a0 and a1 bits indicate the TV Parental Guideline rating system is
   in use and a TV Parental Guideline rating of “None” is received.
g) If there is no valid line 21 data on field 2 for 45 frames.
h) If the XDS Content Advisory packet's a0, a1, a2, a3 bits indicate the Canadian English language rating
   system is in use and a Canadian English Language rating of "Exempt" is received.
i) If the XDS Content Advisory packet's a0, a1, a2, a3 bits indicate the Canadian French language rating
   system is in use and a Canadian French Language rating of "Exempt" is received.
j) If a Content Advisory packet is received with the a0, a1, a2, a3 bits indicating systems 5 and 6 (non US
   and non-Canadian rating system) is in use (until these rating systems are further defined).
L.4.2 Digital Cessation
When a digital set is in use, the following is a continuation of the list in Section L.4:

k) If the content advisory descriptor indicates that the MPA rating system is in use and an MPA rating of
   "N/A" is received
l) If the content advisory descriptor indicates that the TV Parental Guideline rating system is in use and a
   TV Parental Guideline rating of "None" is received
m) If the content advisory descriptor indicates that the Canadian English Language rating system is in use
   and a Canadian English Language rating packet of "Exempt" is received
n) If the content advisory descriptor indicates that the Canadian French Language rating system is in use
   and a Canadian French Language rating packet of "Exempt" is received
o) If there is no valid content advisory descriptor information for 1.2 seconds.
L.5 Selection Advisory
When the categories D, L, S, V, and FV are chosen for blocking, without an age based rating, a receiver
should display an advisory that some program sources will not be blocked.
L.6 Rating Information
The remote control may include a button, which displays the rating icon, and/or the descriptive language,
but neither should be displayed except upon action of the viewer unless the set is in the blocked mode.
Note that the categories D, L, S, & V should be displayed only in alphabetical order, especially when each
is denoted by a single letter.

For the Canadian systems, as a minimum requirement, the rating information as viewed on-screen should
be available in its primary language That is, the English language rating system should be available in
English and the French language rating system should be available in French. Manufacturers are free to
implement translations, however, if they wish to do so they should adhere to the translations provided in
Annex K.
L.7 XDS Data
NTSC Broadcasters should include XDS packets with the title, start time, and stop time/duration for
display when the receiver is in blocking mode. This parallels a recommendation for DTV Broadcasters.




                                                       123
CEA-608-E


L.8 Auxiliary Input
If a receiver has the ability to decode line 21 XDS information for the Auxiliary Inputs, then it should block
the inputs based on the MPA, U.S. TV Parental Guideline, Canadian English Language or Canadian
French Language rating level selected by the viewer. If the receiver does not have the ability to decode
the Auxiliary Input’s line 21 XDS information, then it should block or otherwise disable the Auxiliary Inputs
if the viewer has enabled Content Advisory blocking Once again, this appears to be the only valid solution
for allowing Content Advisory information to be a useful feature.

In a similar fashion, DTV sets with an Auxiliary Input should block the inputs based on the MPA, U.S. TV
Parental Guideline, Canadian English Language or Canadian French Language rating level selected by
the viewer. If the receiver does not have the ability to decode the Auxiliary Input’s content advisory
descriptor information, then it should block or otherwise disable the Auxiliary Inputs if the viewer has
enabled Content Advisory blocking.
L.9 Invalid Ratings
An invalid rating should be ignored by the receiver and treated as if no rating packet or content advisory
descriptor was received.

For the TV Parental Guidelines, an invalid rating is defined as any combination of Age Rating and
Content Flag which does not appear in Table 22 for NTSC receivers or Table 1 of CEA-766-B for DTV
receivers.

For the Canadian English Language ratings, a rating level of (g2,g1,g0) = (1,1,1) is invalid For the
Canadian French Language ratings, the rating levels (g2,g1,g0) = (1,1,0) and (1,1,1) are invalid.
L.10 Multiple Rating Systems
CEA-608-E precludes the simultaneous use of multiple rating systems. All six systems described in
Section 9.5.1.1 are mutually exclusive.

In a similar fashion, a given program transmitted within digital TV, targeted for distribution in a single
region, should only use a single rating system within the content advisory descriptor (per CEA-766-B).
L.11 Blocking Hierarchy (Television Parental Guidelines)
Table 60 indicates the only valid combinations of age and content based ratings with a “3” in the
appropriate boxes For example, TV-PG-S,V is a valid rating, as is TV-PG However, TV-PG-FV is not a
valid rating.

                          Age Rating       FV       D       L        S       V
                          “TV-Y”
                          “TV-Y7”          X
                          “TV-G”
                          “TV-PG”                   X       X        X       X
                          “TV-14”                   X       X        X       X
                          “TV-MA”                           X        X       X
                                      Table 60 Blocking Example A

The following examples apply to both analog and digital TV In the following tables and in reference to the
corresponding examples, a “B” indicates a rating, which is blocked, and a “U” indicates a rating, which is
unblocked. In these examples, the user should always have the capability to override the automatic
blocking on a cell by cell basis.

If a viewer chooses to block any program with a Violence (V) flag without regard to an age based rating,
all entries in that column are automatically blocked as shown by the shaded cells in Table 60. Note that
the same result will occur if the TV-PG-V rating combination is chosen based on the automatic blocking
feature.



                                                     124
                                                                                                      CEA-608-E


                           Age Rating        FV       D        L       S        V
                           “TV-Y”
                           “TV-Y7”           U
                           “TV-G”
                           “TV-PG”                    U        U       U        B
                           “TV-14”                    U        U       U        B
                           “TV-MA”                             U       U        B
                                        Table 61 Blocking Example B

It should be noted that the rating TV-MA-D is not a valid age based and content based rating
combination. Thus choosing to block TV-PG-D will automatically block TV-14-D, but will cause no
blocking of a program with a rating of TV-MA This is shown by the shaded cells in Table 62. In this
instance, the same result can be achieved by choosing to block on the Dialog (D) flag without regard to
any age-based rating.

                           Age Rating        FV       D        L       S        V
                           “TV-Y”
                           “TV-Y7”           U
                           “TV-G”
                           “TV-PG”                    B        U       U        U
                           “TV-14”                    B        U       U        U
                           “TV-MA”                             U       U        U

                                        Table 62 Blocking Example C

If the rating TV-14 is chosen to be blocked without regards to any content based ratings, it not only
automatically blocks all cells below it in the table, but all cells to the right This is shown in Table 63.

                           Age Rating        FV       D        L       S        V
                           “TV-Y”
                           “TV-Y7”           U
                           “TV-G”
                           “TV-PG”                    U        U       U        U
                           “TV-14”                    B        B       B        B
                           “TV-MA”                             B       B        B
                                        Table 63 Blocking Example D

Note that the ratings TV-Y and TV-Y7 are independent of other age-based ratings and blocking them will
not automatically cause cells in the rest of the grid to be blocked. This is shown in Table 64, where the
user has selected to block on the rating TV-Y7 Note that this same result can also be achieved by
blocking on the age and content based rating combination of TV-Y7-FV.




                                                       125
CEA-608-E


                          Age Rating      FV       D       L       S        V
                          “TV-Y”
                          “TV-Y7”         B
                          “TV-G”
                          “TV-PG”                  U       U       U        U
                          “TV-14”                  U       U       U        U
                          “TV-MA”                          U       U        U
                                      Table 64 Blocking Example E
L.12 Blocking Hierarchy (MPA Guidelines)
Although “Not Rated” is the last table entry in the MPA ratings (Table 20 or Figure 1, dimension (7) of
CEA-766-B) it should not be automatically blocked when another rating is set to be blocked.
L.13 Blocking Hierarchy (Canadian English and French Language rating systems)
Hierarchical based blocking is used for the Canadian English and French Language services The
"Exempt" rating level, which is the first entry in both tables, should not be blocked.
L.14 On Screen Display
There should be a display presented to the user which allows review of the blocking settings.
L.15 Terms and Codes
When used in OSDs and/or instruction books, the terms for the Content Advisory codes should be as
stated in CEA-608-E or CEA-766-B.

      U.S. TV Parental Guideline example:
         Short phrase:        “TV-PG”, “TV-MA”, “TV-14-L”, “TV-MA-S,V”
         Long phrase:         “TV-PG Parental Guidance Suggested”
                              “TV-MA Mature Audience Only”
                              “TV-14-L Strong Coarse Language”
                              “TV-MA-S Explicit Sexual Activity”

      Canadian English Language example:
         Short phrase:      “C”, “PG”, “14+”, “18+”
         Long phrase:       “C Children”
                            “PG Parental Guidance”
                            “14+ Viewers 14 Years and Older”
                            “18+ Adult Programming”

      Canadian French Language example:
         Short phrase:     “G”, “8 ans +”, “16 ans +”
         Long phrase:      “G Général”
                           “8 ans + Général - Déconseillé aux jeunes enfants”
                           “16 ans + Cette émission ne convient pas aux moins de 16 ans”




                                                    126
                                                                                                 CEA-608-E



Annex M Recommended Practice for Expansion of XDS to Include Cable Channel Mapping System
Information (Informative)
The three packets addressed in Annex M, 0x41-0x43, are described in Sections 9.5.4.5.2 through
9.5.4.5.3.
M.1 Encoder Recommendations
The Channel Mapping information consists of a table of available channels on the cable system,
specifying the actual channel they are broadcast on, the channel which the user selects, and an optional
field containing the channel’s identification letters. Every channel that is broadcast on the cable system
shall be listed in the table, whether it is re-mapped or not. The channel mapping information is carried to
the receiver by three XDS packets, Channel Map Pointer (0x41), Channel Map Header (0x42), and the
Channel Map (0x43).

The channel mapping information should be broadcast on the lowest non-scrambled universally tunable

```

## 5.3 Complete Character Set Tables

### 5.3.1 Standard Characters (0x20-0x7F)

```
        CGMS-A

                                      M7      Current Description 6                Future Aspect Ratio

                                      M8      Current Description 7        L3      Future Composite 1

                                      M9      Current Description 8                Future Caption Services

                                      M10     Undefined XDS                L4      Out of Band Channel

                                              Channel Map Pointer          L5      Future Description 1

                                      M15     Channel Map Header           L6      Future Description 2

                                              Channel Map                  L7      Future Description 3

                                                                           L8      Future Description 4

                                                                           L9      Future Description 5

                                                                           L10     Future Description 6

                                                                           L11     Future Description 7

                                                                           L12     Future Description 8

                                                                           L13     Tape Delay

                                                                           L14     Supplemental Data Loc

                                                                           L15     Time Zone

                                                                           L16     Time of Day


                                                                           L17     NWS Message

                                Table 55 Alternating Algorithm Lookup Table



                                                      111
CEA-608-E




Sequence if all packets are transmitted:

H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L1
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L2
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L3
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L4
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L5
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L6
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L7
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L8
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L9
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L10
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L11
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L12
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L13
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L14
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L15
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 H2 M10 L16

Transmission sequence for Data Set 1:

H1 M2 H2 M3 H1 M4 H2 M5 L1 H1 M2 H2 M3 H1 M4 H2 M5 L3
H1 M2 H2 M3 H1 M4 H2 M5 L5 H1 M2 H2 M3 H1 M4 H2 M5 L6
H1 M2 H2 M3 H1 M4 H2 M5 L7 H1 M2 H2 M3 H1 M4 H2 M5 L8
H1 M2 H2 M3 H1 M4 H2 M5 L13 H1 M2 H2 M3 H1 M4 H2 M5 L16

Transmission sequence for Data Set 2:

H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L1
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L2
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L3
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L4
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L5
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L6
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L7
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L8
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L9
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L10
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L11
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L12
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L13
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L14
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L15
H1 M1 H2 M2 H1 M3 H2 M4 H1 M5 H2 M6 H1 M7 H2 M8 H1 M9 L16




                                                    112
                                                                                                   CEA-608-E



J.3 Linear VS Alternating Algorithm - Conclusions
e) The Linear algorithm treats every valid packet separately, while the Alternating algorithm groups several
     packets together.
f) The Linear Algorithm treats every priority group the same, while the Alternating algorithm treats
     high/medium and low groups differently.
g) The differences in 1 and 2 cause the Alternating algorithm to be more difficult to implement.
h) For a given fixed set of data, the Linear algorithm has a consistent repetition rate. The Alternating
     algorithm has occasional high priority packet pauses that are longer than the Linear rate when the
     number of medium packets in the data set is even.
i) The Alternating algorithm favors medium and low priority packets at the expense of high priority packets.
     (If enough packets are shifted from the high priority group to the medium priority group, the opposite
     phenomenon occurs.)
J.4 Linear VS Alternating Algorithm - Detailed Analysis
This analysis has 3 steps:

a) Define lookup tables.
b) Example transmission sequences.
c) Spreadsheet analysis of repetition rates using sample data sets.

The following spreadsheet is a performance comparison between the two algorithms using two sample
sets of data. Set 1 is an expected typical real-world set of packets. Set 2 is the worst case data set with all
packets used to their maximum length (except for duplicate fields in the composite packets).
J.5 Spreadsheet Heading Description
Packet description - The name of the packet as described in Section 9.

Pkt Len, Min/Max - Each packet has a minimum length of at least six characters due to overhead, and
possibly higher if the data field has a minimum length of more than one character. Each packet has an
absolute maximum length of 32 characters due to the structure of the system, and some may be smaller
due to the size of the data field.

Linear Algorithm - all columns under this heading refer to the Linear Algorithm.

Alternating Algorithm - all columns under this heading refer to the Alternating Algorithm.

Priority - each packet has a priority assigned in the lookup tables on previous pages. For example, “M1”
refers to the first medium priority packet in the respective Linear or Alternating algorithm table.

Pkt Len - This is the number of characters in the packet, including an overhead of 4 characters.

Set 1 - A likely real-world set of packets to be transmitted.

Set 2 - A worst case real-world set of packets to be transmitted.

Data Set Char Counts -

    XDS Char Count - A sum of the respective all packets in the Pkt Len column.
    High Rep Char Cnt - A sum of high repetition rate packets in the Pkt Len column
    Med Rep Char Cnt - A sum of medium repetition rate packets in the Pkt Len column
    Low Rep Char Cnt - A sum of low repetition rate packets in the Pkt Len column




                                                     113
CEA-608-E


Data Set Group counts - The linear algorithm has no grouping, in effect having one group per packet. The
alternating algorithm groups several packets together.

    High rep group count - Number of groups in the high repetition rate category.
    Med rep group count - Number of groups in the medium repetition rate category.
    Low rep group count - Number of groups in the low repetition rate category.

Algorithm Char counts -

Total Chars/pass - The number of characters transmitted each time the algorithm is executed.
High rep chars/pass - The number of high repetition rate packet characters transmitted each time the
algorithm is executed.
Med rep chars/pass - The number of medium repetition rate packet characters transmitted each time the
algorithm is executed.
Low rep chars/pass - The number of low repetition rate packet characters transmitted each time the
algorithm is executed.

Avg Rep Rate 100% BW, s

High - The average number of seconds between each occurrence of a given high repetition rate packet if
all field 2 bandwidth is dedicated to XDS.
Med - The average number of seconds between each occurrence of a given medium repetition rate packet
if all field 2 bandwidth is dedicated to XDS.
Low - The average number of seconds between each occurrence of a given low repetition rate packet if all
field 2 bandwidth is dedicated to XDS.

Avg Rep Rate 70% or 30% BW, s

High, Med, Low - The average number of seconds between each occurrence of a given high, medium or
low repetition rate packet if 70% or 40% of field 2 bandwidth is dedicated to XDS.

Worst case Rep Rate 30% BW, s

High, Med, Low - The longest time, in seconds, between two of a given high, medium or low repetition rate
packet over the one complete pass of the algorithm, assuming 30% of field 2 bandwidth is dedicated to
XDS.




                                                  114
                                                                                             CEA-608-E


```

### 5.3.2 Extended Characters

```

                                       Table 15 Time/Date Coding

The minute field has a valid range of 0 to 59, the hour field from 0 to 23, the date field from 1 to 31, the
month field from 1 to 12. The "T" bit is used to indicate a program that is routinely tape delayed (for
Mountain and Pacific Time zones). The D, L, and Z bits are ignored by the decoder when processing this
packet. (The same format utilizes these bits for time setting, and the D, L and Z bits are defined in Section
9.5.4.1.) The T bit is used to determine if an offset is necessary because of local station tape delays. A
separate packet of the Channel Information Class shall indicate the amount of tape delay used for a given
time zone. When all characters of this packet contain all Ones, it indicates the end of the current program.

A change in received Current Class Program Identification Number is interpreted by XDS receivers as the
start of a new current program. All previously received current program information shall normally be
discarded in this case.
      9.5.1.2 Type=0x02 Length/Time-in-Show
This packet is composed of 2, 4 or 6 binary informational characters, so, with the exception of the Null
character, b6 shall be set high (b6=1). It is used to indicate the scheduled length of the program as well
as the elapsed time for the program. The first two informational characters are used to indicate the
program’s length in hours and minutes. The second two informational characters show the current time
elapsed by the program in hours and minutes. The final two informational characters extend the elapsed
time count with seconds.

The informational characters are encoded as indicated in Table 16.

           Character                                 b6        b5        b4        b3        b2        b1   b0

           Length - (m)                              1         m5        m4        m3        m2        m1   m0
           Length - (h)                              1         h5        h4        h3        h2        h1   h0

           Elapsed time - (m)                        1         m5        m4        m3        m2        m1   m0
           Elapsed time - (h)                        1         h5        h4        h3        h2        h1   h0

           Elapsed time - (s)                        1         s5        s4        s3        s2        s1   s0
           Null                                      0          0        0         0         0         0    0

                                      Table 16 Show Length Coding

The minute and second fields have a valid range of 0 to 59, and the hour fields from 0 to 23. The sixth
character is a standard null.




                                                         38
                                                                                                CEA-608-E

      9.5.1.3 Type=0x03 Program Name (Title)
This packet contains a variable number, 2 to 32, of Informational characters that define the program title.
Each character is in the range of 0x20 to 0x7F. The variable size of this packet allows for efficient
transmission of titles of any length up to 32 characters. A change in received Current Class Program
name is interpreted by XDS receivers as the start of a new current program. All previously received
current program information shall normally be discarded in this case.
     9.5.1.4 Type=0x04 Program Type
This packet contains a variable number, 2 to 32, of informational characters that define keywords
describing the type or category of program. These characters are coded to keywords as shown in Table
17.

HEX   Descriptive           HEX Code Descriptive                          HEX         Descriptive
Code  Keyword                           Keyword                           Code        Keyword
20    Education             40          Fantasy                           60          Music
21    Entertainment         41          Farm                              61          Mystery
22    Movie                 42          Fashion                           62          National
23    News                  43          Fiction                           63          Nature
24    Religious             44          Food                              64          Police
25    Sports                45          Football                          65          Politics
26    OTHER                 46          Foreign                           66          Premier
27    Action                47          Fund Raiser                       67          Prerecorded
28    Advertisement         48          Game/Quiz                         68          Product
29    Animated              49          Garden                            69          Professional
2A    Anthology             4A          Golf                              6A          Public
2B    Automobile            4B           Government                       6B          Racing
2C    Awards                4C          Health                            6C          Reading
2D    Baseball              4D          High School                       6D          Repair
2E    Basketball            4E          History                           6E          Repeat
2F    Bulletin              4F          Hobby                             6F          Review
30    Business              50          Hockey                            70          Romance
31    Classical             51          Home                              71          Science
32    College               52          Horror                            72          Series
33    Combat                53          Information                       73          Service
34    Comedy                54          Instruction                       74          Shopping
35    Commentary            55          International                     75          Soap Opera
36    Concert               56          Interview                         76          Special
37    Consumer              57          Language                          77          Suspense
38    Contemporary          58          Legal                             78          Talk
39    Crime                 59          Live                              79          Technical
3A    Dance                 5A          Local                             7A          Tennis
3B    Documentary           5B          Math                              7B          Travel
3C    Drama                 5C          Medical                           7C          Variety
3D    Elementary            5D          Meeting                           7D          Video
3E    Erotica               5E          Military                          7E          Weather
3F    Exercise              5F          Miniseries                        7F          Western
NOTE—ATSC A/65C Table 6.20 extends Table 17 for other uses.
                             Table 17 Hex Code and Descriptive Key Word

The service provider or program producer should specify all keywords which apply to the program and
should order them according to their opinion of their importance. A single character is used to represent
each entire keyword. This allows multiple keywords to be transmitted very efficiently.




                                                    39
CEA-608-E

The list of keywords is broken down into two groups. The first group consists of the codes 0x20 to 0x26
and is called the "BASIC" group. The second group contains the codes 0x27 to 0x7F and is called the
"DETAIL" group.

The Basic group is used to define the program at the highest level. All programs that use this packet shall
specify one or more of these codes to define the general category of the program. Programs which may
fit more than one Basic category are free to specify several of these keywords. The keyword "OTHER" is
used when the program doesn't really fit into the other Basic categories. These keywords shall always be
specified before any of the keywords from the Detail group.

The Detail group is used to add more specific information if appropriate. These keywords are all optional
and shall follow the Basic keywords. Programs that may fit more than one Detail are free to specify
several of these keywords. Only keywords which actually apply should be specified. If the program can
not be accurately described with any of these keywords, then none of them should be sent. In this case,
the keywords from the Basic group are all that are needed.
                                                   3
      9.5.1.5 Type=0x05 Content Advisory
This packet includes two characters that contain information about the program’s MPA, U.S. TV Parental
Guidelines, Canadian English Language, and Canadian French Language ratings. These four systems
are mutually exclusive, so if one is included, then the others shall not be. This is binary data so b6 shall
be set high (b6=1). Table 18 indicates the contents of the characters.

                           Character        b6     b5       b4     b3       b2    b1        b0
                           Character 1      1      D/a2     a1     a0       r2    r1        r0
                           Character 2      1      (F)V     S      L/a3     g2    g1        g0
                                       Table 18 Content Advisory XDS Packet

Bits a3, a2, a1, and a0 define which rating system is in use. If (a1, a0) = (1, 1) then a2 and a3 are used to
further define this rating system. Only one rating system can be in use at any given time based on Table
19.

             a3     a2     a1     a0     System        Name
             -      -      0      0      0             MPA
             L      D      0      1      1             U.S. TV Parental Guidelines
             -      -      1      0      2             MPA 4
             0      0      1      1      3             Canadian English Language Rating
             0      1      1      1      4             Canadian French Language Rating
             1      0      1      1      5             Reserved for non-U.S. & non-Canadian system
             1      1      1      1      6             Reserved for non-U.S. & non-Canadian system
                             Table 19 Content Advisory Systems a0-a3 Bit Usage

Where MPA (system 0 or system 2) is used, then bits g0-g2 shall be set to zero. In all other cases, bits r0-
r2 shall be set to zero.

Bits b5-b4 within the second character shall not be used with the Canadian English and Canadian French
rating systems. In these cases, these bits shall be reserved for future use and, pending future assignment
shall be set to “0”.


3
  In CEA-608-E the term “program rating” has been replaced by “content advisory”. CEA-608-E describes not only the
MPA rating system and the U.S. TV Parental Guideline System, but two rating systems for use in Canada. An official
translation, as supplied by the Canadian Government, of the French portion of the normative standard may be found
in Annex K. Annex K also contains a translation of the English language Canadian System into French. In DTV,
content advisory data is carried via methods described in ATSC A/65C and CEA-766-B.
4
    This system (2) has been provided for backward compatibility with existing equipment.

                                                           40
                                                                                                 CEA-608-E

The three bits r0-r2 shall be used to encode the MPA picture rating, if used. See Table 20.

                                         r2    R1   r0       Rating
                                         0     0    0        N/A
                                         0     0    1        “G”
                                         0     1    0        “PG”
                                         0     1    1        “PG-13”
                                         1     0    0        “R”
                                         1     0    1        “NC-17”
                                         1     1    0        “X”
                                         1     1    1        Not Rated
                                         Table 20 MPA Rating System

A distinction is made between N/A and Not Rated. When all zeros are specified (N/A) it means that
motion picture ratings are not applicable to this program. When all ones are used (Not Rated) it indicates
a motion picture that did not receive a rating for a variety of possible reasons.
9.5.1.5.1 U.S. TV Parental Guideline Rating System
If bits a0 – a1 indicate the U.S. TV Parental Guideline system is in use, then bits D, L, S, (F)V and g0 - g2
in the second character shall be as shown in Table 21.

                        g2     g1    g0       Age Rating     FV    V     S   L    D
                        0      0     0        None*
                        0      0     1        “TV-Y”
                        0      1     0        “TV-Y7”        X
                        0      1     1        “TV-G”
                        1      0     0        “TV-PG”              X     X   X    X
                        1      0     1        “TV-14”              X     X   X    X

                        1      1     0        “TV-MA”              X     X   X
                        1      1     1        None*

                         *No blocking is intended per the content advisory criteria.
                            Table 21 U.S. TV Parental Guideline Rating System

Bits (F) V, S, L, and D may be included in some combinations with bits g0-g2. Only combinations
indicated by an X in Table 21 are allowed.

                NOTE—When the guideline category is TV-Y7, then the V bit shall be the FV bit.

                FV - Fantasy Violence
                V - Violence
                S - Sexual Situations
                L - Adult Language
                D - Sexually Suggestive Dialog

Definition of symbols for the U.S. TV Parental Guideline rating system (informative):

TV-Y All Children. This program is designed to be appropriate for all children. Whether animated or live-
   action, the themes and elements in this program are specifically designed for a very young audience,
   including children from ages 2-6. This program is not expected to frighten younger children.
TV-Y7 Directed to Older Children. This program is designed for children age 7 and above. It may be
   more appropriate for children who have acquired the developmental skills needed to distinguish
   between make-believe and reality. Themes and elements in this program may include mild fantasy
   violence or comedic violence, or may frighten children under the age of 7. Therefore, parents may

                                                        41
CEA-608-E

    wish to consider the suitability of this program for their very young children. Note: For those programs
    where fantasy violence may be more intense or more combative than other programs in this category,
    such programs will be designated TV-Y7-FV.

The following categories apply to programs designed for the entire audience:

TV-G General Audience. Most parents would find this program suitable for all ages. Although this rating
   does not signify a program designed specifically for children, most parents may let younger children
   watch this program unattended. It contains little or no violence, no strong language and little or no
   sexual dialogue or situations.
TV-PG Parental Guidance Suggested. This program contains material that parents may find unsuitable
   for younger children. Many parents may want to watch it with their younger children. The theme itself
   may call for parental guidance and/or the program contains one or more of the following: moderate
   violence (V), some sexual situations (S), infrequent coarse language (L), or some suggestive
   dialogue (D).
TV-14 Parents Strongly Cautioned. This program contains some material that many parents would find
   unsuitable for children under 14 years of age. Parents are strongly urged to exercise greater care in
   monitoring this program and are cautioned against letting children under the age of 14 watch
   unattended. This program contains one or more of the following: intense violence (V), intense sexual
   situations (S), strong coarse language (L), or intensely suggestive dialogue (D).
TV-MA Mature Audience Only. This program is specifically designed to be viewed by adults and
   therefore may be unsuitable for children under 17. This program contains one or more of the
   following: graphic violence (V), explicit sexual activity (S), or crude indecent language (L).

(This is the end of this informative section).
9.5.1.5.2 Canadian English Language Rating System
If bits a0 – a3 indicate the Canadian English Language rating system is in use, then bits g0 - g2 in the
second character shall be as shown in Table 22.

               g2     g1     g0    Rating      Description
               0      0      0     E           Exempt
               0      0      1     C           Children
               0      1      0     C8+         Children eight years and older
               0      1      1     G           General programming, suitable for all audiences
               1      0      0     PG          Parental Guidance
               1      0      1     14+         Viewers 14 years and older
               1      1      0     18+         Adult Programming
               1      1      1
                           Table 22 Canadian English Language Rating System

A Canadian English Language rating level of (g2, g1, g0) = (1, 1, 1) shall be treated as an invalid content
advisory packet.

Definition of symbols for the Canadian English Language rating system (informative) 5 :

E      Exempt - Exempt programming includes: news, sports, documentaries and other information
programming; talk shows, music videos, and variety programming.

C        Programming intended for children under age 8 - Violence Guidelines: Careful attention is paid to
themes, which could threaten children's sense of security and well-being. There will be no realistic scenes
of violence. Depictions of aggressive behaviour will be infrequent and limited to portrayals that are clearly
imaginary, comedic or unrealistic in nature.


5
 A translation of this informative material into French may be found in the Section Labeled Official Translations in
Annex K. These translations are approved by the Government of Canada.

                                                         42
                                                                                                 CEA-608-E

Other Content Guidelines: There will be no offensive language, nudity or sexual content.

C8+       Programming generally considered acceptable for children 8 years and over to watch on their
own - Violence Guidelines: Violence will not be portrayed as the preferred, acceptable, or only way to
resolve conflict; or encourage children to imitate dangerous acts which they may see on television. Any
realistic depictions of violence will be infrequent, discreet, of low intensity and will show the
consequences of the acts.

Other Content Guidelines: There will be no profanity, nudity or sexual content.

G       General Audience - Violence Guidelines: Will contain very little violence, either physical or verbal
or emotional. Will be sensitive to themes which could frighten a younger child, will not depict realistic
scenes of violence which minimize or gloss over the effects of violent acts.

Other Content Guidelines: There may be some inoffensive slang, no profanity and no nudity.

PG      Parental Guidance - Programming intended for a general audience but which may not be suitable
for younger children. Parents may consider some content inappropriate for unsupervised viewing by
children aged 8-13. Violence Guidelines: Depictions of conflict and/or aggression will be limited and
moderate; may include physical, fantasy, or supernatural violence.

Other Content Guidelines: May contain infrequent mild profanity, or mildly suggestive language. Could
also contain brief scenes of nudity.

14+      Programming contains themes or content which may not be suitable for viewers under the age of
14 - Parents are strongly cautioned to exercise discretion in permitting viewing by pre-teens and early
teens. Violence Guidelines: May contain intense scenes of violence. Could deal with mature themes and
societal issues in a realistic fashion.

Other Content Guidelines: May contain scenes of nudity and/or sexual activity. There could be frequent
use of profanity.

18+     Adult - Violence Guidelines: May contain violence integral to the development of the plot,
character or theme, intended for adult audiences.

Other Content Guidelines: may contain graphic language and explicit portrayals of nudity and/or sex.

(This is the end of this informative section.)
9.5.1.5.3 Système de classification français du Canada
(Canadian French Language Rating System):
If bits a0 – a3 indicate the Canadian French Language rating system is in use, then bits g0 - g2 in the
second character shall be as shown in Table 23.

    g2     g1     g0    Rating        Description
    0      0      0     E             Exemptées
    0      0      1     G             Général
    0      1      0     8 ans +       Général- Déconseillé aux jeunes enfants
    0      1      1     13 ans +      Cette émission peut ne pas convenir aux enfants de moins de 13
                                      ans
    1      0      0     16 ans +      Cette émission ne convient pas aux moins de 16 ans
    1      0      1     18 ans +      Cette émission est réservée aux adultes
    1      1      0
    1      1      1
                          Table 23 Canadian French Language Rating System



                                                     43
CEA-608-E

Canadian French Language rating levels (g2, g1, g0) = (1, 1, 0) and (1, 1, 1) shall be treated as invalid
content advisory packets.

Definition of symbols for the Canadian French Language rating system (informative) 6 :

E                 Exemptées - Émissions exemptées de classement

G                Général - Cette émission convient à un public de tous âges. Elle ne contient aucune
violence ou la violence qu’elle contient est minime, ou bien traitée sur le mode de l’humour, de la
caricature, ou de manière irréaliste.

8 ans+            Général-Déconseillé aux jeunes enfants - Cette émission convient à un public large mais
elle contient une violence légère ou occasionnelle qui pourrait troubler de jeunes enfants. L’écoute en
compagnie d’un adulte est donc recommandée pour les jeunes enfants (âgés de moins de 8 ans) qui ne
font pas la différence entre le réel et l’imaginaire.

13 ans+        Cette émission peut ne pas convenir aux enfants de moins de 13 ans - Elle contient soit
quelques scènes de violence, soit une ou des scènes d’une violence assez marquée pour les affecter.
L’écoute en compagnie d’un adulte est donc fortement recommandée pour les enfants de moins de 13
ans.

16 ans+         Cette émission ne convient pas aux moins de 16 ans - Elle contient de fréquentes scènes
de violence ou des scènes d’une violence intense.

18 ans+         Cette émission est réservée aux adultes - Elle contient une violence soutenue ou des
scènes d’une violence extrême.

(This is the end of this informative section)
9.5.1.5.4 General Content Advisory Requirements
All program content analysis is the function of parties involved in program production or distribution. No
precise criteria for establishing content ratings or advisories are given or implied. The characters are
provided for the convenience of consumers in the implementation of a parental viewing control system.

The data within this packet shall be cleared or updated upon a change of the information contained in the
Current Class Program Identification Number and/or Program Name packets.

The data within this packet shall not change during the course of a program, which shall be construed to
include program segments, commercials, promotions, station identifications et al.
      9.5.1.6 Type=0x06 Audio Services
This packet contains two characters that define the contents of the main and second audio programs.
This is binary data so b6 shall be set high (b6=1). The format is indicated in Table 24.

                               Character        b6    b5    b4   b3    b2    b1    b0

                               Main             1     L2    L1   L0    T2    T1    T0

                               SAP              1     L2    L1   L0    T2    T1    T0

                                            Table 24 Audio Services

Each of these two characters contains two fields: language and type. The language fields of both
characters are encoded using the same format, as indicated in Table 25.



6
 A translation of this informative material into English may be found in the Section Labeled Official Translations in
Annex K. These translations are approved by the Government of Canada.

                                                           44
                                                                                               CEA-608-E

                                      L2     L1    L0      Language
                                      0      0     0       Unknown
                                      0      0     1       English
                                      0      1     0       Spanish
                                      0      1     1       French
                                      1      0     0       German
                                      1      0     1       Italian
                                      1      1     0       Other
                                      1      1     1       None
                                            Table 25 Language

The type fields of each character are encoded using the different formats indicated in Table 26.

      Main Audio Program                            Second Audio Program
      T2    T1     T0    Type                       T2   T1    T0    Type
      0     0      0     Unknown                    0    0     0     Unknown
      0     0      1     Mono                       0    0     1     Mono
      0     1      0     Simulated Stereo           0    1     0     Video Descriptions
      0     1      1     True Stereo                0    1     1     Non-program Audio
      1     0      0     Stereo Surround            1    0     0     Special Effects
      1     0      1     Data Service               1    0     1     Data Service
      1     1      0     Other                      1    1     0     Other
      1     1      1     None                       1    1     1     None
                                           Table 26 Audio Types
      9.5.1.7 Type=0x07 Caption Services
This packet contains a variable number, 2 to 8 characters that define the available forms of caption
encoded data. One character is needed to specify each available service. This is binary data so bit 6 shall
be set high (b6=1). Each of the characters shall follow the same format, as indicated in Table 27. The
language bits shall be as defined in Table 25 (the same format for the audio services packet).
The F, C, and T bits shall be as shall be as defined in Table 28.

                          Character          b6    b5     b4   b3   b2   b1   b0
                          Service Code       1     L2     L1   L0   F    C    T

                                       Table 27 Caption Services

The language bits are encoded using the same format as for the audio services packet. See Table 25.

                            F    C     T     Caption Service
                            0    0     0     field one, channel C1, captioning
                            0    0     1     field one, channel C1, Text
                            0    1     0     field one, channel C2, captioning
                            0    1     1     field one, channel C2, Text
                            1    0     0     field two, channel C1, captioning
                            1    0     1     field two, channel C1, Text
                            1    1     0     field two, channel C2, captioning
                            1    1     1     field two, channel C2, Text
                                     Table 28 Caption Service Types
      9.5.1.8 Type=0x08 Copy and Redistribution Control Packet
This packet contains binary data so b6 shall be set high (b6=1). For copy generation management system
(CGMS-A), APS, ASB and RCD syntax, see Table 29.



                                                     45
CEA-608-E

                      b6      b5            b4                 b3          b2          b1       b0
       Byte 1          1       -         CGMS-A           CGMS-A           APS        APS       ASB


       Byte 2          1      Re           Re                  Re          Re          Re       RCD
Re = Reserved bit for possible future use.
                            Table 29 Copy and Redistribution Control Packet

In Table 29, bits b5-b1, of the second byte, are reserved for future use. All reserved bits shall be zero until
assigned. ASB shall be defined as the Analog Source Bit. CEA-608-E does not define the use or meaning
of the ASB.

The CGMS-A bits have the meanings indicated in Table 30.

                                   b4 b3         CGMS-A Meaning
                                   0,0           Copying is permitted without restriction


                                   0,1           No more copies (one generation copy has been
                                                 made)*
                                   1,0           One generation of copies may be made


                                   1,1           No copying is permitted
                                   * This definition differs from IEC-61880 and IEC 61880-2.

                                       Table 30 CGMS-A Bit Meanings

        NOTE—Conditions for applying the CGMS-A and APS bits in source devices may be bound by
        private agreements or government directives. Also, required behavior of sink devices detecting
        the CGMS-A and APS bits may be bound by private agreements or government directives.
        Implementers are cautioned to read and understand all applicable agreements and directives.

        NOTE—Where the CGMS-A bits are set to 0,1 or 1,1, a source device may use APS to apply
        anti-copying protection to its APS-capable outputs, assuming that the device applying the anti-
        copying protection signal is under an appropriate license from an anti-taping protection
        technology provider. If the CGMS-A bits in Table 30 are set to either 0,0 or 1,0 (i.e., CGMS-A

```

