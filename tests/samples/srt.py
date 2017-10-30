# -*- coding: utf-8 -*-

SAMPLE_SRT = u"""1
00:00:09,209 --> 00:00:12,312
( clock ticking )

2
00:00:14,848 --> 00:00:17,000
MAN:
When we think
\u266a ...say bow, wow, \u266a

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
00:00:32,200 --> 00:00:36,200
<LAUGHING & WHOOPS!>
"""

SAMPLE_SRT_ASCII = u"""1
00:00:09,209 --> 00:00:12,312
( clock ticking )

2
00:00:14,848 --> 00:00:17,000
MAN:
When we think
of "E equals m c-squared",

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
00:00:32,200 --> 00:00:34,400
<LAUGHING & WHOOPS!>

8
00:00:34,400 --> 00:00:38,400
some more text
"""

SAMPLE_SRT_WITH_LAYOUT = SAMPLE_SRT_ASCII

SAMPLE_SRT_IGNORE_LAYOUT = u"""1
00:00:09,209 --> 00:00:12,312
( clock ticking )

2
00:00:14,848 --> 00:00:17,000
MAN: 
When we think 
of "E equals m c-squared",

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
00:00:32,200 --> 00:00:34,400
<LAUGHING & WHOOPS!>

8
00:00:34,400 --> 00:00:38,400
some more text
"""

SAMPLE_SRT_NUMERIC = u"""35
00:00:32,290 --> 00:00:32,890
TO  FIND  HIM.            IF

36
00:00:32,990 --> 00:00:33,590
YOU  HAVE  ANY  INFORMATION

37
00:00:33,690 --> 00:00:34,290
THAT  CAN  HELP,  CALL  THE

38
00:00:34,390 --> 00:00:35,020
STOPPERS  LINE.          THAT

39
00:00:35,120 --> 00:00:35,760
NUMBER  IS  662-429-84-77.

40
00:00:35,860 --> 00:00:36,360
STD  OUT

41
00:00:36,460 --> 00:02:11,500
3
"""


SAMPLE_SRT_EMPTY = u"""
"""

SAMPLE_SRT_BLANK_LINES = u"""35
00:00:32,290 --> 00:00:32,890


36
00:00:32,990 --> 00:00:33,590
YOU  HAVE  ANY  INFORMATION

"""

SAMPLE_SRT_TRAILING_BLANKS = u"""35
00:00:32,290 --> 00:00:32,890
HELP  I  SAY


36
00:00:32,990 --> 00:00:33,590
YOU  HAVE  ANY  INFORMATION



"""
