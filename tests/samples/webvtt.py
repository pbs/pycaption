# -*- coding: utf-8 -*-

SAMPLE_WEBVTT = """WEBVTT

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

SAMPLE_WEBVTT_OUTPUT = """WEBVTT

00:09.209 --> 00:12.312
( clock ticking )

00:14.848 --> 00:17.000
MAN:
When we think
♪ ...say bow, wow, ♪

00:17.000 --> 00:18.752
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

SAMPLE_WEBVTT_FROM_DFXP = """WEBVTT

00:09.209 --> 00:12.312 align:middle
( clock ticking )

00:14.848 --> 00:17.000 align:middle
MAN:
When we think
♪ ...say bow, wow, ♪

00:17.000 --> 00:18.752 align:right
we have this vision of Einstein

00:18.752 --> 00:20.887 align:middle
&nbsp;
as an old, wrinkly man
with white hair.

00:20.887 --> 00:26.760 align:middle
MAN 2:
E equals m c-squared is
not about an old Einstein.

00:26.760 --> 00:32.200 align:middle
MAN 2:
It's all about an eternal Einstein.

00:32.200 --> 00:36.200 align:middle
&lt;LAUGHING &amp; WHOOPS!>
"""

SAMPLE_WEBVTT_FROM_SAMI = SAMPLE_WEBVTT_FROM_DFXP

SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING = """WEBVTT

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

SAMPLE_WEBVTT_FROM_SRT = """WEBVTT

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

SAMPLE_WEBVTT_2 = """WEBVTT

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

SAMPLE_WEBVTT_EMPTY = """WEBVTT
"""

SAMPLE_WEBVTT_DOUBLE_BR = """WEBVTT

00:14.848 --> 00:18.848
MAN:
&nbsp;
When we think
of "E equals m c-squared",
"""
