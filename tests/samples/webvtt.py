# -*- coding: utf-8 -*-

SAMPLE_WEBVTT = u"""WEBVTT

00:09.209 --> 00:12.312
( clock ticking )

00:14.848 --> 00:17.000
MAN:
When we think
♪ ...say bow, wow, ♪

00:17.000 --> 00:18.752
we have this vision of Einstein

00:18.752 --> 00:20.887
as an old, wrinkly man
with white hair.

00:20.887 --> 00:26.760
MAN 2:
E equals m c-squared is
not about an old Einstein.

00:26.760 --> 00:32.200
MAN 2:
It's all about an eternal Einstein.

00:32.200 --> 00:36.200
<LAUGHING & WHOOPS!>
"""

SAMPLE_WEBVTT_FROM_DFXP = u"""WEBVTT

00:09.209 --> 00:12.312
( clock ticking )

00:14.848 --> 00:17.000
MAN:
When we think
♪ ...say bow, wow, ♪

00:17.000 --> 00:18.752 align:right
we have this vision of Einstein

00:18.752 --> 00:20.887
&nbsp;
as an old, wrinkly man
with white hair.

00:20.887 --> 00:26.760
MAN 2:
E equals m c-squared is
not about an old Einstein.

00:26.760 --> 00:32.200
MAN 2:
It's all about an eternal Einstein.

00:32.200 --> 00:36.200
&lt;LAUGHING &amp; WHOOPS!>
"""

SAMPLE_WEBVTT_FROM_SAMI = SAMPLE_WEBVTT_FROM_DFXP

SAMPLE_WEBVTT_FROM_SAMI_WITH_STYLE = u"""WEBVTT

00:09.209 --> 00:12.312
I <b>do</b> <i>not</i> want to go <u>home</u>.
I don't like it <i><u><b>there</b></u></i>.
"""

SAMPLE_WEBVTT_FROM_SAMI_WITH_ID_STYLE = u"""WEBVTT

00:09.209 --> 00:12.312
<i>This is in italics.</i>

00:14.848 --> 00:17.000
<u>This is underlined.</u>

00:17.000 --> 00:18.752
<b>This is bold.</b>

00:20.887 --> 00:26.760
<b><i><u>This is everything together.</u></i></b>
"""

SAMPLE_WEBVTT_FROM_DFXP_WITH_STYLE = u"""WEBVTT

00:09.209 --> 00:12.312
This is <i>italic</i>, <b>bold</b>, <u>underline</u>, <i><u><b>everything together in one tag</b></u></i>, and <u><b><i>nested</i></b></u>.
"""

SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING = u"""WEBVTT

00:01.000 --> 00:03.000 position:25%,start line:25% size:50%
You might not remember us. We are a typical transparent region with centered text that has an outline.

00:03.500 --> 00:05.000 align:right position:25%,start line:25% size:50%
had personality.

00:05.500 --> 00:07.000 align:left position:50%,start line:50% size:25%
Hello there, children! Have you seen any visitors?

00:07.500 --> 00:09.000 align:right position:25%,start line:75% size:25%
This is
the last cue
"""

SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING_AND_STYLE = u"""WEBVTT

00:01.000 --> 00:03.000 position:50% line:25% size:50%
You might not remember us. We are a typical transparent region with centered text that has an outline.

00:03.500 --> 00:05.000 align:right position:50% line:25% size:50%
had <u>personality.</u>

00:05.500 --> 00:07.000 align:left position:62.5% line:50% size:25%
Hello there, children! Have you seen any visitors?

00:07.500 --> 00:09.000 align:right position:37.5% line:75% size:25%
This is
the last cue
"""

SAMPLE_WEBVTT_WITH_LAYOUT = SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING_AND_STYLE

SAMPLE_WEBVTT_IGNORE_LAYOUT = u"""WEBVTT

00:01.000 --> 00:03.000
You might not remember us. We are a typical transparent region with centered text that has an outline.

00:03.500 --> 00:05.000
had personality.

00:05.500 --> 00:07.000
Hello there, children! Have you seen any visitors?

00:07.500 --> 00:09.000
This is
the last cue
"""


SAMPLE_WEBVTT_FROM_SRT = u"""WEBVTT

00:09.209 --> 00:12.312
( clock ticking )

00:14.848 --> 00:17.000
MAN:
When we think
♪ ...say bow, wow, ♪

00:17.000 --> 00:18.752
we have this vision of Einstein

00:18.752 --> 00:20.887
as an old, wrinkly man
with white hair.

00:20.887 --> 00:26.760
MAN 2:
E equals m c-squared is
not about an old Einstein.

00:26.760 --> 00:32.200
MAN 2:
It's all about an eternal Einstein.

00:32.200 --> 00:36.200
&lt;LAUGHING &amp; WHOOPS!>
"""

# This is not equal to the input because we accept unescaped illegal characters
# when reading (because many players do so) but escape them when writing
# in order to conform to the specification.
SAMPLE_WEBVTT_FROM_WEBVTT = SAMPLE_WEBVTT_FROM_SRT

SAMPLE_WEBVTT_2 = u"""WEBVTT

1
00:00:00.000 --> 00:00:43.000
- HELLO WORLD!

2
00:00:59.000 --> 00:01:30.000
- LOOKING GOOOOD.

3
00:01:40.000 --> 00:02:00.000
- HA HA HA!

4
00:02:05.105 --> 00:03:07.007
- HI. WELCOME TO SESAME STREET.

5
00:04:07.007 --> 00:05:38.441
ON TONIGHT'S SHOW...

6
00:05:58.441 --> 00:06:40.543
- I'M NOT GOING TO WATCH THIS.

7
00:07:10.543 --> 00:07:51.711
HEY. WATCH THIS.
"""

SAMPLE_WEBVTT_EMPTY = u"""WEBVTT
"""

SAMPLE_WEBVTT_EMPTY_CUE = u"""WEBVTT

1
00:00:00.000 --> 00:00:43.000


2
00:00:59.000 --> 00:01:30.000
- HELLO WORLD!
"""

SAMPLE_WEBVTT_FROM_EMPTY_CUE = u"""WEBVTT

00:59.000 --> 01:30.000
- HELLO WORLD!
"""

SAMPLE_WEBVTT_DOUBLE_BR = u"""WEBVTT

00:14.848 --> 00:18.848
MAN:
&nbsp;
When we think
of "E equals m c-squared",
"""

SAMPLE_WEBVTT_OUTPUT_LONG_CUE = u"""WEBVTT

00:01.000 --> 00:02.000
NARRATOR:

00:02.000 --> 00:03.000 position:62.5% line:25% size:75%
They built the largest, most incredible, wildest, craziest,

00:03.000 --> 00:04.000
most complex machine in history.
"""

WEBVTT_FROM_DFXP_WITH_CONFLICTING_ALIGN = u"""WEBVTT

00:04.537 --> 00:07.841
IT'S WORD GIRL♫

00:08.537 --> 00:10.841
♫WORD UP,
IT'S WORD GIRL♫
"""

SAMPLE_WEBVTT_WITH_CUE_SETTINGS = u"""\
WEBVTT

00:01.000 --> 00:06.000 align:middle position:37%,start line:74%
37% 74% - NARRATOR:

00:01.000 --> 00:06.000 this is invalid, but will also be kept
They built the largest,
"""

SAMPLE_WEBVTT_FROM_SCC_PROPERLY_WRITES_NEWLINES_OUTPUT = u"""\
WEBVTT

21:30.033 --> 21:34.033 position:56.25% line:86.67% size:87.5%
aa
bb
"""

SAMPLE_WEBVTT_LAST_CUE_ZERO_START = u"""WEBVTT

00:00.000 --> 00:12.312
( clock ticking )"""
