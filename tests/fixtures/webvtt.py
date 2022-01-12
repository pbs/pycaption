import pytest


@pytest.fixture(scope="session")
def sample_webvtt():
    return """WEBVTT

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


@pytest.fixture(scope="session")
def sample_webvtt_from_dfxp():
    return """WEBVTT

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


@pytest.fixture(scope="session")
def sample_webvtt_from_sami(sample_webvtt_from_dfxp):
    return sample_webvtt_from_dfxp


@pytest.fixture(scope="session")
def sample_webvtt_from_sami_with_style():
    return """WEBVTT

00:09.209 --> 00:12.312
I <b>do</b> <i>not</i> want to go <u>home</u>.
I don't like it <i><u><b>there</b></u></i>.
"""


@pytest.fixture(scope="session")
def sample_webvtt_from_sami_with_id_style():
    return """WEBVTT

00:09.209 --> 00:12.312
<i>This is in italics.</i>

00:14.848 --> 00:17.000
<u>This is underlined.</u>

00:17.000 --> 00:18.752
<b>This is bold.</b>

00:20.887 --> 00:26.760
<b><i><u>This is everything together.</u></i></b>
"""


@pytest.fixture(scope="session")
def sample_webvtt_from_dfxp_with_style():
    return """WEBVTT

00:09.209 --> 00:12.312
This is <i>italic</i>, <b>bold</b>, <u>underline</u>, <i><u><b>everything together in one tag</b></u></i>, and <u><b><i>nested</i></b></u>.
"""


@pytest.fixture(scope="session")
def sample_webvtt_from_dfxp_with_positioning():
    return """WEBVTT

00:01.000 --> 00:03.000 position:25% line:25% size:50%
You might not remember us. We are a typical transparent region with centered text that has an outline.

00:03.500 --> 00:05.000 align:right position:25% line:25% size:50%
had personality.

00:05.500 --> 00:07.000 align:left position:50% line:50% size:25%
Hello there, children! Have you seen any visitors?

00:07.500 --> 00:09.000 align:right position:25% line:75% size:25%
This is
the last cue
"""


@pytest.fixture(scope="session")
def sample_webvtt_from_dfxp_with_positioning_and_style():
    return """WEBVTT

00:01.000 --> 00:03.000 position:25% line:25% size:50%
You might not remember us. We are a typical transparent region with centered text that has an outline.

00:03.500 --> 00:05.000 align:right position:25% line:25% size:50%
had <u>personality.</u>

00:05.500 --> 00:07.000 align:left position:50% line:50% size:25%
Hello there, children! Have you seen any visitors?

00:07.500 --> 00:09.000 align:right position:25% line:75% size:25%
This is
the last cue
"""


@pytest.fixture(scope="session")
def sample_webvtt_from_srt():
    return """WEBVTT

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
@pytest.fixture(scope="session")
def sample_webvtt_from_webvtt(sample_webvtt_from_srt):
    return sample_webvtt_from_srt


@pytest.fixture(scope="session")
def sample_webvtt_2():
    return """WEBVTT

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


@pytest.fixture(scope="session")
def sample_webvtt_empty():
    return """WEBVTT
"""


@pytest.fixture(scope="session")
def sample_webvtt_double_br():
    return """WEBVTT

00:14.848 --> 00:18.848
MAN:
&nbsp;
When we think
of "E equals m c-squared",
"""


@pytest.fixture(scope="session")
def sample_webvtt_output_long_cue():
    return """\
WEBVTT

00:01.000 --> 00:02.000
NARRATOR:

00:02.000 --> 00:03.000 position:25% line:25% size:65%
They built the largest, most incredible, wildest, craziest,

00:03.000 --> 00:04.000
most complex machine in history.
"""


@pytest.fixture(scope="session")
def webvtt_from_dfxp_with_conflicting_align():
    return """WEBVTT

00:04.537 --> 00:07.841
IT'S WORD GIRL♫

00:08.537 --> 00:10.841
♫WORD UP,
IT'S WORD GIRL♫
"""


@pytest.fixture(scope="session")
def sample_webvtt_with_cue_settings():
    return """\
WEBVTT

00:01.000 --> 00:06.000 align:middle position:37% line:74%
37% 74% - NARRATOR:

00:01.000 --> 00:06.000 this is invalid, but will also be kept
They built the largest,
"""


@pytest.fixture(scope="session")
def sample_webvtt_from_scc_properly_writes_newlines_output():
    return """\
WEBVTT

21:30.000 --> 21:34.000 align:left position:20% line:83% size:70%
aa
bb
"""


@pytest.fixture(scope="session")
def sample_webvtt_last_cue_zero_start():
    return """WEBVTT

00:00.000 --> 00:12.312
( clock ticking )"""


@pytest.fixture(scope="session")
def sample_webvtt_empty_cue():
    return """WEBVTT

1
00:00.000 --> 00:02.000

00:04.000 --> 00:05.000
Transcribed by Celestials
"""


@pytest.fixture(scope="session")
def sample_webvtt_multi_lang_en():
    return """WEBVTT

00:14.848 --> 00:18.848
Butterfly.
"""


@pytest.fixture(scope="session")
def sample_webvtt_multi_lang_de():
    return """WEBVTT

00:14.848 --> 00:18.848
Schmetterling.
"""


@pytest.fixture(scope="session")
def sample_webvtt_empty_cue_output():
    return """\
WEBVTT

00:01.209 --> 00:02.312 position:10% line:10% size:80%
abc
"""


@pytest.fixture(scope="session")
def sample_webvtt_timestamps():
    return """WEBVTT

01:01.001 --> 10:10.100
Test zero padded and two digit timestamps without hours

01:01:01.001 --> 10:10:10.100
Test zero padded and two digit timestamps without hours"""
