import pytest


# Real-world bytes reproducing the "phantom BREAK" bug: two independent,
# simultaneously-timed paint-on captions ("Always by her side" / "And
# Trini!"). Row 13 is written from column 4, a same-row PAC then lands at
# column 24 — two columns shy of where that text ended, so it continues the
# line — and finally a skipped row jump (13 -> 15) forces the second cue.
@pytest.fixture(scope="session")
def sample_scc_row_jump_with_pending_reposition():
    return """\
Scenarist_SCC V1.0

00:00:21:11 9420 942f 94ae 9420 13f2 91ae 9137 20c1 ecf7 6179 7320 6279 2068 e5f2 2073 e964 e520 9137 137c 9723 9120 94f4 9723 c16e 6420 54f2 e96e e9a1

00:00:25:00 942c 942c 942f 942f
"""


# Real-world-equivalent bytes reproducing the phantom BREAK bug in its most
# direct form: a single paint-on PAC jumps both row (13 -> 15, a skipped
# row) and column (28 -> 8, far beyond a tab offset) in one step, with no
# intervening column-only PAC and no pending unconsumed repositioning to
# key off of. The row skip alone is already enough to force a new cue; the
# column jump is incidental.
@pytest.fixture(scope="session")
def sample_scc_paint_on_row_and_column_jump_in_one_pac():
    return """\
Scenarist_SCC V1.0

00:00:20:00 9429 9429 13fe 13fe c1c2 94f4 94f4 43c4 942c 942c
"""


# Same row-skip PAC pattern as
# sample_scc_paint_on_row_and_column_jump_in_one_pac, but in pop-on mode
# (9420 instead of 9429). A skipped row forces a new cue regardless of
# buffer mode, so this must also split into two cues, not stay joined by
# BREAK nodes.
@pytest.fixture(scope="session")
def sample_scc_pop_on_row_and_column_jump_in_one_pac():
    return """\
Scenarist_SCC V1.0

00:00:20:00 9420 9420 13fe 13fe c1c2 94f4 94f4 43c4 942c 942c 942f 942f
"""


# Same row-skip PAC pattern again, but in roll-up mode (9425/RU2 instead of
# 9429). Same as pop-on: the skipped row alone forces a new cue, so this
# also splits into two cues rather than staying joined by BREAK nodes.
@pytest.fixture(scope="session")
def sample_scc_roll_up_row_and_column_jump_in_one_pac():
    return """\
Scenarist_SCC V1.0

00:00:20:00 9425 9425 13fe 13fe c1c2 94f4 94f4 43c4 942c 942c
"""


# Real-world-equivalent bytes: a single paint-on PAC jumps to the very next
# row (5 -> 6, not a skip) but combined with a large column jump (0 -> 20,
# far beyond a tab offset), with no intervening column-only PAC and no
# pending unconsumed repositioning to key off of. Unlike a simple text wrap
# onto the next line (which stays at roughly the same column), this pattern
# indicates a second, independently-positioned region drawn one row below
# the first — the same "two side-by-side captions in paint-on mode" bug
# class this branch fixes for skipped rows, but for a row+1 jump instead.
@pytest.fixture(scope="session")
def sample_scc_paint_on_row_plus_one_large_column_jump():
    return """\
Scenarist_SCC V1.0

00:00:20:00 9429 9429 1540 1540 c1c2 157a 157a 43c4 942c 942c
"""


# Same row+1-plus-large-column-jump PAC pattern as
# sample_scc_paint_on_row_plus_one_large_column_jump, but in pop-on mode
# (9420 instead of 9429). column_jump_forces_reposition is only passed as
# True for paint-on buffers, so pop-on's large column shift between the
# wrapped lines is treated as legitimate same-cue formatting rather than an
# independent region — this must stay a single caption joined by a BREAK
# node, even though the column jump is identical to the paint-on case.
@pytest.fixture(scope="session")
def sample_scc_pop_on_row_plus_one_large_column_jump():
    return """\
Scenarist_SCC V1.0

00:00:20:00 9420 9420 1540 1540 c1c2 157a 157a 43c4 942c 942c 942f 942f
"""


# Same row+1-plus-large-column-jump PAC pattern again, but in roll-up mode
# (9425/RU2 instead of 9429). Like pop-on, roll-up is exempt from the
# column-jump check, so this must also stay a single caption joined by a
# BREAK node rather than being split like the paint-on case.
@pytest.fixture(scope="session")
def sample_scc_roll_up_row_plus_one_large_column_jump():
    return """\
Scenarist_SCC V1.0

00:00:20:00 9425 9425 1540 1540 c1c2 157a 157a 43c4 942c 942c
"""


# Real-world bytes: a single pop-on cue whose text skips a row (row 1 -> 3)
# with no preceding same-row PAC and no large-enough column jump to be
# mistaken for an independent region. This must split into two independently-
# positioned cues with no BREAK node joining them, since a skipped row is
# not an intentional blank line to preserve in the rendered cue.
@pytest.fixture(scope="session")
def sample_scc_row_skip_does_not_preserve_blank_line():
    return """\
Scenarist_SCC V1.0

00:00:20:00 9420 9420 9152 9152 9723 9723 c1c2 92d0 92d0 43c4 942c 942c 942f 942f
"""


@pytest.fixture(scope="session")
def sample_scc_created_dfxp_with_wrongly_closing_spans():
    return """\
Scenarist_SCC V1.0

00:01:28;09 9420 94ae 9420 9452 8080 e3e3 e3e3 e3e3 9470 8080 e3a1 e3a1 942f

00:01:31;10 9420 942f 94ae

00:01:31;18 9420 9454 6262 6262 9458 8080 91ae e3e3 e3e3 9470 8080 6262 6161 942f

00:01:35;18 9420 942f 94ae

00:01:40;25 942c

00:01:51;18 9420 9452 8080 6161 94da 8080 91ae 6262 9470 8080 e3e3 942f

00:01:55;22 9420 6162 e364 94f4 8080 6162 e364 942f

00:01:59;14 9420 942f 94ae
"""


@pytest.fixture(scope="session")
def scc_that_generates_webvtt_with_proper_newlines():
    return """\
Scenarist_SCC V1.0

00:21:29;23    9420 9452 6161 94f4 97a2 6262 942c 942f
"""


@pytest.fixture(scope="session")
def sample_scc_produces_captions_with_start_and_end_time_the_same():
    return """\
Scenarist_SCC V1.0

00:01:31;18 9420 9454 6162 9758 97a1 91ae 6261 9170 97a1 e362

00:01:35;18 9420 942f 94ae

00:01:40;25 942c
"""


@pytest.fixture(scope="session")
def sample_scc_pop_on():
    return """Scenarist_SCC V1.0

00:00:09:05 94ae 94ae 9420 9420 9470 9470 a820 e3ec efe3 6b20 f4e9 e36b e96e 6720 2980 942c 942c 942f 942f

00:00:12:08 942c 942c

00:00:13:18 94ae 94ae 9420 9420 1370 1370 cdc1 ceba 94d0 94d0 5768 e56e 20f7 e520 f468 e96e 6b80 9470 9470 efe6 20a2 4520 e5f1 7561 ec73 206d 20e3 ad73 f175 61f2 e564 a22c 942c 942c 942f 942f

00:00:16:03 94ae 94ae 9420 9420 9470 9470 f7e5 2068 6176 e520 f468 e973 2076 e973 e9ef 6e20 efe6 2045 e96e 73f4 e5e9 6e80 942c 942c 942f 942f

00:00:17:20 94ae 94ae 9420 9420 94d0 94d0 6173 2061 6e20 efec 642c 20f7 f2e9 6e6b ec79 206d 616e 9470 9470 f7e9 f468 20f7 68e9 f4e5 2068 61e9 f2ae 942c 942c 942f 942f

00:00:19:13 94ae 94ae 9420 9420 1370 1370 cdc1 ce20 32ba 94d0 94d0 4520 e5f1 7561 ec73 206d 20e3 ad73 f175 61f2 e564 20e9 7380 9470 9470 6eef f420 6162 ef75 f420 616e 20ef ec64 2045 e96e 73f4 e5e9 6eae 942c 942c 942f 942f

00:00:25:16 94ae 94ae 9420 9420 1370 1370 cdc1 ce20 32ba 94d0 94d0 49f4 a773 2061 ecec 2061 62ef 75f4 2061 6e20 e5f4 e5f2 6e61 ec80 9470 9470 45e9 6e73 f4e5 e96e ae80 942c 942c 942f 942f

00:00:31:15 94ae 94ae 9420 9420 9470 9470 bc4c c1d5 c7c8 49ce c720 2620 57c8 4f4f d0d3 a13e 942c 942c 942f 942f

00:00:36:04 942c 942c

"""


# 6 captions
#   2 Pop-On captions.
#       The first has 3 random positions, and thus 3 captions
#       The second should be interpreted as 1 caption with 2 line breaks
#   2 Roll-Up captions - same comment
#   2 Paint-on captions - same comment
@pytest.fixture(scope="session")
def sample_scc_multiple_positioning():
    return """Scenarist_SCC V1.0

00:00:00:16 94ae 94ae 9420 9420 1370 1370 6162 6162 91d6 91d6 e364 e364 92fd 92fd e5e6 e5e6 942c 942c 942f 942f

00:00:02:16 94ae 94ae 9420 9420 16f2 16f2 6768 6768 9752 9752 e9ea e9ea 97f2 97f2 6bec 6bec 942c 942c 942f 942f

00:00:09:21 9425 9425 94ad 94ad 94f2 94f2 6d6e 6d6e 97d6 97d6 ef70 ef70 92dc 92dc f1f2 f1f2

00:00:11:21 9425 9425 94ad 94ad 15f2 15f2 73f4 73f4 1652 1652 7576 7576 16f2 f7f8 f7f8

00:00:20:02 9429 9429 9452 9452 97A2 97A2 797A 797A 917c 917c B031 B031 16d6 16d6 32B3 32B3

00:00:22:02 9429 9429 1352 1352 97A2 97A2 34B5 34B5 13f2 13f2 B637 B637 9452 9452 38B9 38B9

00:00:36:04 942c 942c

"""


# UNUSED SAMPLE
@pytest.fixture(scope="session")
def sample_scc_with_italics_bkup():
    return """\
Scenarist_SCC V1.0

00:00:00:01 9420 10d0 97a2 91ae 6162 6162 6162 6162 942c 8080 8080 942f
"""


@pytest.fixture(scope="session")
def sample_scc_with_italics():
    return """\

00:00:00:01 9420 10d0 97a2 91ae 6162 6162 6162 6162 942c 8080 8080 942f
"""


@pytest.fixture(scope="session")
def sample_scc_empty():
    return """Scenarist_SCC V1.0
"""


@pytest.fixture(scope="session")
def sample_scc_roll_up_ru2():
    return """\
Scenarist_SCC V1.0
00:00:00;22    9425 9425 94ad 94ad 9470 9470 3e3e 3e20 c849 ae80

00:00:02;23    9425 9425 94ad 94ad 9470 9470 49a7 cd20 cb45 d649 ce20 43d5 cece 49ce c720 c1ce c420 c154

00:00:04;17    9425 9425 94ad 94ad 9470 9470 49ce d645 d354 4f52 a7d3 20c2 c1ce cb20 5745 20c2 454c 4945 d645 2049 ce80

00:00:06;04    9425 9425 94ad 94ad 9470 9470 c845 4cd0 49ce c720 54c8 4520 4c4f 43c1 4c20 ce45 49c7 c8c2 4f52 c84f 4fc4 d380

00:00:09;21    9425 9425 94ad 94ad 9470 9470 c1ce c420 49cd d052 4fd6 49ce c720 54c8 4520 4c49 d645 d320 4f46 20c1 4c4c

00:00:11;07    9425 9425 94ad 94ad 9470 9470 5745 20d3 4552 d645 ae80

00:00:12;07    9425 9425 94ad 94ad 9470 9470 91b0 9131 9132 9132

00:00:12;15    9425 94ad 94ad 9470 9470 91b0 9131 9132 9132

00:00:13;07    9425 9425 94ad 94ad 9470 9470 c1c2 c3c4 c580 91bf

00:00:13;15    9425 9425 94ad 94ad 9470 9470 9137 

00:00:13;20    9425 9425 94ad 94ad 9470 9470 9137 9137

00:00:13;25    9425 9425 94ad 94ad 9470 9470 9137 9137 9137

00:00:13;29    9425 9425 94ad 94ad 9470 9470 9137 9137 9137 9137

00:00:14;07    9425 9425 94ad 94ad 9470 9470 9220 9220 92a1 92a2 92a7

00:00:17;01    9426 9426 94ad 94ad 9470 9470 57c8 4552 4520 d94f d5a7 5245 20d3 54c1 cec4 49ce c720 ce4f 572c

00:00:18;19    9426 9426 94ad 94ad 9470 9470 4c4f 4fcb 49ce c720 4fd5 5420 54c8 4552 452c 2054 c8c1 54a7 d320 c14c 4c

00:00:20;06    9426 9426 94ad 94ad 9470 9470 54c8 4520 4352 4f57 c4ae

00:00:21;24    9426 9426 94ad 94ad 9470 9470 3e3e 2049 5420 57c1 d320 c74f 4fc4 2054 4f20 c245 2049 ce20 54c8 45

00:00:34;27    94a7 94ad 9470 c16e 6420 f2e5 73f4 eff2 e520 49ef f761 a773 20ec 616e 642c 20f7 61f4 e5f2

00:00:36;12    94a7 94ad 9470 c16e 6420 f7e9 ec64 ece9 e6e5 ae80

00:00:44;08    94a7 94ad 9470 3e3e 20c2 e96b e520 49ef f761 2c20 79ef 75f2 2073 ef75 f2e3 e520 e6ef f280
"""


@pytest.fixture(scope="session")
def sample_scc_roll_up_ru3():
    return """\
Scenarist_SCC V1.0
00:00:00;22    9425 9425 94ad 94ad 9470 9470 3e3e 3e20 c849 ae80

00:00:02;23    9425 9425 94ad 94ad 9470 9470 49a7 cd20 cb45 d649 ce20 43d5 cece 49ce c720 c1ce c420 c154

00:00:04;17    9425 9425 94ad 94ad 9470 9470 49ce d645 d354 4f52 a7d3 20c2 c1ce cb20 5745 20c2 454c 4945 d645 2049 ce80

00:00:06;04    9425 9425 94ad 94ad 9470 9470 c845 4cd0 49ce c720 54c8 4520 4c4f 43c1 4c20 ce45 49c7 c8c2 4f52 c84f 4fc4 d380

00:00:09;21    9425 9425 94ad 94ad 9470 9470 c1ce c420 49cd d052 4fd6 49ce c720 54c8 4520 4c49 d645 d320 4f46 20c1 4c4c

00:00:11;07    9425 9425 94ad 94ad 9470 9470 5745 20d3 4552 d645 ae80

00:00:12;07    9425 9425 94ad 94ad 9470 9470 91b0 9131 9132 9132

00:00:13;07    9425 9425 94ad 94ad 9470 9470 c1c2 c3c4 c580 91bf

00:00:14;07    9425 9425 94ad 94ad 9470 9470 9220 9220 92a1 92a2 92a7

00:00:17;01    9426 9426 94ad 94ad 9470 9470 57c8 4552 4520 d94f d5a7 5245 20d3 54c1 cec4 49ce c720 ce4f 572c

00:00:18;19    9426 9426 94ad 94ad 9470 9470 4c4f 4fcb 49ce c720 4fd5 5420 54c8 4552 452c 2054 c8c1 54a7 d320 c14c 4c

00:00:20;06    9426 9426 94ad 94ad 9470 9470 54c8 4520 4352 4f57 c4ae

00:00:21;24    9426 9426 94ad 94ad 9470 9470 3e3e 2049 5420 57c1 d320 c74f 4fc4 2054 4f20 c245 2049 ce20 54c8 45

00:00:34;27    94a7 94ad 9470 c16e 6420 f2e5 73f4 eff2 e520 49ef f761 a773 20ec 616e 642c 20f7 61f4 e5f2

00:00:36;12    94a7 94ad 9470 c16e 6420 f7e9 ec64 ece9 e6e5 ae80

00:00:44;08    94a7 94ad 9470 3e3e 20c2 e96b e520 49ef f761 2c20 79ef 75f2 2073 ef75 f2e3 e520 e6ef f280
"""


@pytest.fixture(scope="session")
def sample_no_positioning_at_all_scc():
    return """\
Scenarist_SCC V1.0

00:23:28;01    9420 94ae 5245 c1c2 942f

00:24:29;21    942c

00:53:28;01    9420 94ae 4552 aeae 942f

00:54:29;21    942c
"""


# UNUSED SAMPLE
@pytest.fixture(scope="session")
def sample_scc_not_explicitly_switching_italics_off():
    return """\
Scenarist_SCC V1.0

00:01:28;09    9420 942f 94ae 9420 9452 97a2 b031 6161 9470 9723 b031 6262

00:01:31;10    9420 942f 94ae

00:01:31;18    9420 9454 b032 e3e3 9458 97a1 91ae b032 6464 9470 97a1 b032 e5e5

00:01:35;18    9420 942f 94ae

00:01:40;25    942c

00:01:51;18    9420 9452 97a1 b0b3 6161 94da 97a2 91ae b0b3 6262 9470 97a1 b0b3 e3e3

00:01:55;22    9420 942f b034 6161 94f4 9723 b034 6262

00:01:59;14    9420 942f 94ae 9420 94f4 b034 3180 e3e3

00:02:02;01    9420 942f 94ae 9420 94d0 b0b5 6161 94f2 97a2 b0b5 6262

00:02:04;05    9420 942f 94ae

00:09:53;06    942c 9420 13f4 9723 b0b6 e3e3 9454 97a2 b0b6 6464 9470 97a2 b0b6 e5e5

00:09:56;09    9420 942f 94ae 9420 94f2 b037 6161

00:09:58;18    9420 942f 94ae 9420 9454 b038 6262 9454 97a2 91ae b038 e3e3 94f2 97a1 94f2 97a1 91ae b038 6162 6464

00:09:59;28    9420 942f 94ae 9420 9452 97a2 e5e5 94f4 b0b9 6161

00:10:02;22    9420 942f 94ae 9420 9452 97a1 31b0 e5e5 9470 97a2 31b0 6262

00:10:04;10    9420 942f 94ae

00:52:03;02    9420 9470 97a2 3131 e3e3

00:52:18;20    9420 91d0 9723 3132 6464 9158 97a1 91ae 3132 e5e5 91da 97a2 9120 3132 6161 91f2 9723 3132 6262

00:52:22;22    9420 942c 942f 9420 9152 97a2 31b3 e3e3

00:52:25;04    9420 942c 942f 9420 91d0 97a2 3134 6464 91f2 e5e5

00:52:26;28    9420 942c 942f

00:52:27;18    9420 9152 9152 9152 91ae 31b5 6161 9154 97a1 9120 31b5 6262 9170 9723 31b5 e3e3

00:52:31;22    9420 942c 942f

00:52:34;14    942c

00:53:03;15    9420 94f4 97a1 94f4 97a1 91ae 31b6 6464
"""


@pytest.fixture(scope="session")
def sample_scc_no_explicit_end_to_last_caption():
    return """\
Scenarist_SCC V1.0

00:00:00;00    73e9 e329 942f

00:00:06;01    942c

00:24:55;14    9420 94ae 9470 97a2 a875 7062 e561 f420 f2ef e36b 206d 7573 e9e3 2980 942f
"""


@pytest.fixture(scope="session")
def sample_scc_flashing_cue():
    return """\
Scenarist_SCC V1.0

00:00:00;20 9420 9420 942c 942c 942f 942f 9420 9420 9152 9152 4fd5 5220 cec1 5449 4fce c14c 20d0 c152 cbd3 91f2 91f2 c245 4c4f cec7 2054 4f20 c14c 4c20 4f46 20d5 d3ae

00:00:02;02 9420 9420 942c 942c 942f 942f 9420 9420 91d0 91d0 54c8 45d9 20c1 5245 20d0 4cc1 4345 d320 4f46 20c4 49d3 434f d645 52d9 2c80 9170 9170 54c8 45d9 20c1 5245 20d0 4cc1 4345 d320 4f46 2049 ced3 d049 52c1 5449 4fce 2c80

00:00:04;29 9420 9420 942c 942c 942f 942f

00:00:06;08 9420 9420 9154 9154 54c8 45d9 20c1 5245 91f2 91f2 c1cd 4552 4943 c1a7 d320 c245 d354 2049 c445 c1ae

00:00:09;24 9420 9420 942c 942c 942f 942f

00:00:10;06 9420 9420 9152 9152 cdc1 4a4f 5220 46d5 cec4 49ce c720 d052 4fd6 49c4 45c4 20c2 d980

00:00:13;19 9420 9420 942c 942c 942f 942f 9420 9420 9154 9154 54c8 4520 45d6 454c d9ce 9170 9170 c1ce c420 57c1 4c54 4552 20c8 c1c1 d32c 204a 52ae 2046 d5ce c4ae

00:00:15;11 9420 9420 942c 942c 942f 942f

00:00:16;08 9420 9420 9152 9152 c1c4 c449 5449 4fce c14c 2046 d5ce c449 cec7 91f2 91f2 57c1 d320 d052 4fd6 49c4 45c4 20c2 d9ba

00:00:19;19 9420 94ae 9152 9723 c1c4 c449 5449 4fce c14c 2046 d5ce c449 cec7 91f4 57c1 d320 d052 4fd6 49c4 45c4 20c2 d9ba 942c

00:00:20;13 942f 942c

00:00:21;19 9420 94ae 9152 9723 54c8 4520 d0c1 52cb 2046 4fd5 cec4 c154 494f ce80 942c

00:00:22;07 942f 942c

00:00:22;14 9420 94ae 9152 97a2 49ce 20d3 d5d0 d04f 5254 204f 4620 c120 434c 45c1 ce80 91f2 c1ce c420 c845 c14c 54c8 d920 45ce d649 524f cecd 45ce 543b 942c

00:00:23;15 942f 942c

00:00:25;09 9420 94ae 9152 97a1 54c8 4520 c152 54c8 d552 20d6 49ce 49ce c720 c4c1 d649 d380 91f4 97a2 464f d5ce c4c1 5449 4fce d32c 942c

00:00:26;06 942f 942c

00:00:27;15 9420 94ae 91d0 9723 c445 c449 43c1 5445 c420 544f 20d3 5452 45ce c754 c845 ce49 cec7 91f4 c1cd 4552 4943 c1a7 d320 46d5 54d5 5245 942c

00:00:28;14 942f 942c
"""


@pytest.fixture(scope="session")
def sample_scc_eoc_first_command():
    return """\
Scenarist_SCC V1.0

00:00:00;24    942f

00:00:02;00    73e9 e329 942f

00:00:06;01    942c

00:24:55;14    9420 94ae 9470 97a2 a875 7062 e561 f420 f2ef e36b 206d 7573 e9e3 2980 942f

00:25:00;00    942c
"""


@pytest.fixture(scope="session")
def sample_scc_with_extended_characters():
    return """\
Scenarist_SCC V1.0

00:04:36;06	9420 942c 942f 9420 91d6 cdc1 13b0 5254 c8c1 ba80 942f
00:22:32:18	9420 942c 942f 9420 9454 97a1 4ad5 ce49 4f52 ba20 a180 92a7 d975 6da1 9470 9723 d961 206d e520 73e9

00:22:34:28	942c e56e f4ef 206d 75e3 68ef 206d e5ea eff2 ae80 9420 942c 942f 9420 94f2 9723 4ad5 ce49 4f52 ba20 4f79 e52c 20c1 ec6d 612c
"""


@pytest.fixture(scope="session")
def sample_scc_with_ampersand_character():
    return """\
Scenarist_SCC V1.0

00:04:36;06	 9420 9420 9152 9152 cdc1 4a4f 5220 46d5 cec4 49ce c720 d052 4fd6 49c4 45c4 20c2 d980 2026 942f
"""


@pytest.fixture(scope="session")
def sample_scc_multiple_formats():
    return """\
Scenarist_SCC V1.0

00:00:00;00	942c 1c2c

00:00:00;08	9429 9152 97a2 a843 ece9 e56e f4a7 7320 d6ef e9e3 e529 91f2 97a2 52e5 6de5 6d62 e5f2 20f4 6861 f420 64e5 67f2 e5e5 9252 97a2 79ef 7520 67ef f420 e96e 20f4 61f8 61f4 e9ef 6ebf 9420 9152 97a2 a8c4 616e 6e79 2980 91f2 97a2 4fe6 20e3 ef75 f273 e520 79ef 7520 64ef 6ea7 f480 9252 97a2 62e5 e361 7573 e520 79ef 7520 64e9 646e a7f4 a180

00:00:02;15	9420 942c 942f 9420 91d0 9723 d9ef 75f2 20ea ef62 20e9 736e a7f4 2064 efe9 6e67 2068 61f2 6480 9170 9723 f7ef f26b aeae ae80

00:00:04;15	9420 942c 942f 9420 91d0 97a2 aeae aee9 f4a7 7320 6d61 6be9 6e67 20f4 68e5 6d20 64ef 2068 61f2 6480 9170 97a2 f7ef f26b aeae ae80

00:00:06;03	9420 942c 942f 9420 91d0 97a2 aeae ae61 6e64 2067 e5f4 f4e9 6e67 2070 61e9 6420 e6ef f220 e9f4 ae80

00:00:08;04	9420 942c 942f 9420 91d0 97a1 a8d6 4f29 9170 97a1 d36e 6170 2061 6e64 2073 eff2 f420 79ef 75f2 20e5 f870 e56e 73e5 7320 f4ef 92d0 97a1 7361 76e5 20ef 76e5 f220 a434 2cb6 b0b0 2061 f420 f461 f820 f4e9 6de5 ae80

00:00:09;18	9420 942c 942f 9420 9152 51d5 4943 cbc2 4f4f cbd3 ae20 c2c1 43cb 49ce c720 d94f d5ae

00:00:13;04	9420 942c 942f

"""


@pytest.fixture(scope="session")
def sample_scc_duplicate_tab_offset():
    return """\
Scenarist_SCC V1.0

00:00:29:04 9420 1370 97a1 1370 97a1 91ae 5b52 6164 e9ef 20f2 e570 eff2 f4e5 f25d 94d0 97a1 94d0 97a1 91ae 5468 e520 49ad 31b0 20d3 616e f461 20cd ef6e e9e3 6120 46f2 e5e5 f761 7980 9470 97a1 9470 97a1 91ae f7e5 73f4 62ef 756e 6420 e973 20ea 616d 6de5 642c 9420 942c 942f 9420 94d0 97a2 94d0 97a2 91ae 6475 e520 f4ef 2061 20f4 68f2 e5e5 ade3 61f2 2061 e3e3 e964 e56e f480 9470 97a2 9470 97a2 91ae 62ec efe3 6be9 6e67 20ec 616e e573 2031 2061 6e64 2032 942f
"""


@pytest.fixture(scope="session")
def sample_scc_duplicate_special_characters():
    return """\
Scenarist_SCC V1.0

00:23:28;01 9420 9420 91b0 91b0 9131 9131 9132 9132 91b3 91b3 9134 9134 91b5 91b5 91b6 91b6 9137 9137 9138 9138 91b9 91b9 91ba 91ba 913b 913b 91bc 91bc 913d 913d 913e 913e 91bf 91bf 942f

00:33:28;01 9420 91b0 9131 9132 91b3 9134 91b5 91b6 9137 9138 91b9 91ba 913b 91bc 913d 913e 91bf 942f

00:53:28;01 9420 91b0 9131 c1c1 9132 91b3 9134 91b5 91b6 9137 9138 91b9 91ba 913b 91bc c1c1 913d 913e 91bf 942f

"""


@pytest.fixture(scope="session")
def sample_scc_tab_offset():
    return """\
Scenarist_SCC V1.0

00:00:00;00	9420 9420

00:00:00;03	942f 9420 9454 9723 cec1 5252 c154 4f52 ba80 9470 97a1 5468 e520 f7ef f2ec 6420 efe6 20f7 eff2 6b20 e973 20e3 6861 6e67 e96e 67ae

00:00:02;01	9420 942c 942f

00:00:02;08	9420 9470 9723 c2d9 524f ce20 c1d5 c7d5 d354 45ba 2054 68e5 20e6 75f4 75f2 e580

00:00:05;24	9420 942c 942f 9420 94d0 97a1 e973 2067 efe9 6e67 20f4 ef20 62e5 2076 e5f2 7920 64e9 e6e6 e5f2 e56e f480 94f4 97a1 f468 616e 20f4 68e5 2070 6173 f4ae 9420 942c 942f 9420 9452 9723 cec1 5252 c154 4f52 ba20 52ef 62ef f4e9 e373 9470 97a2 616e 6420 61f2 f4e9 e6e9 e3e9 61ec 20e9 6ef4 e5ec ece9 67e5 6ee3 e580

00:00:09;10	9420 942c 942f 9420 94f4 61f2 e520 ef6e 20f4 68e5 20f2 e973 e5ae

00:00:12;00	9420 942c 942f 9420 9454 97a2 cbc1 49ad 46d5 204c 4545 ba80 94f2 97a1 57e5 a7f2 e520 6275 e9ec 64e9 6e67 2073 7973 f4e5 6d73

00:00:13;06	9420 942c 942f 9420 94d0 9723 f468 61f4 20e3 616e 2064 e9f2 e5e3 f4ec 7920 f2e5 70ec 61e3 e580 94f2 97a1 6875 6d61 6e20 eaef 6273 2061 6e64 20f4 6173 6b73 ae80

00:00:15;26	9420 942c 942f """


@pytest.fixture(scope="session")
def sample_scc_with_unknown_commands():
    return """\
Scenarist_SCC V1.0

00:04:36;06 942x 942x 942x 942x 91d6 cdc1 13b0 525x c8cx ba8x
"""


@pytest.fixture(scope="session")
def sample_scc_special_and_extended_characters():
    return """\
Scenarist_SCC V1.0

00:00:16;29 2080 91b0 9131 9132 91b3 9134 91b5 91b6 

00:04:36;06 9137 9138 91b9 91ba 913b 91bc 913d 913e 91bf

00:08:00;00 92a1 92a2 9223 92a4 9225 9226 92a7 92a8 9229 922a 92ab

00:12:00;23 922c 92ad 92ae 922f 92b0 9231 9232 92b3 9234 92b5 92b6 9237 9238 

00:16:24;11 92b9 92ba 923b 92bc 923d 923e 92bf 1320 13a1 13a2 1323 13a4 1325

00:20:19;12 1326 13a7 13a8 1329 132a 13ab 132c 13ad 13ae 132f 13b0 1331 1332

00:24:39;28 13b3 1334 13b5 13b6 1337 1338 13b9 13ba 133b 13bc 133d 133e 13bf
"""


@pytest.fixture(scope="session")
def sample_scc_with_line_too_long():
    return """\
Scenarist_SCC V1.0

00:00:00;03	942c

00:00:01;15	9420 91f4 cb45 4c4c d920 4ac1 cd45 d3ba 20c8 eff7 9254 f468 e520 7368 eff7 2073 f461 f2f4 e564 942c 8080 8080 942f

00:00:02;20	9420 91e0 9723 f761 7320 4361 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 ec20 c4e5 6ee9 73ef 6e2c 2061 20e6 f2e9 e56e 6480 9240 9723 efe6 20ef 75f2 732c 20f7 6173 2064 efe9 6e67 206d 7920 43c4 73ae 942c 8080 8080 942f

00:00:06;25	9420 94e0 c16e 6420 68e5 2073 61e9 642c 2049 20e3 616e 2064 ef20 6120 54d6 2073 68ef f7ae 942c 8080 8080 942f

00:00:08;28	9420 9452 4920 ea75 73f4 20f7 616e f4e5 6420 ef6e e520 7368 eff7 2c80 94f2 ea75 73f4 20f4 ef20 6861 76e5 2061 7320 6120 ece9 f4f4 ece5 942c 8080 8080 942f
"""


# "HI" at row 14, column 4, then a PAC and Tab Offset putting the next line at
# column 31, the last one, with 32 characters after it. The text alone fits a
# row; starting 27 columns right of the cue's origin, it runs past the end.
@pytest.fixture(scope="session")
def sample_scc_with_line_indented_past_the_last_column():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9452 c849 94fe 9723 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 d5d6 5758 d9da c1c2 43c4 4546

00:00:03:00\t942c 942f

"""


@pytest.fixture(scope="function")
def sample_scc_mid_row_before_text_pop():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9420 91d0 9120 c1c2 20c1 c280 942f
    
"""


@pytest.fixture(scope="function")
def sample_scc_mid_row_before_text_roll():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9425 91d0 9120 c1c2 20c1 c280

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_before_text_paint():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9429 91d0 9120 c1c2 20c1 c280

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_following_text_no_text_before_italics_off_pop():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9420 91ce 91ab 91ae c1c2 9120 c1c2 942f

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_following_text_no_text_before_italics_off_roll():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9425 91ce 91ab 91ae c1c2 9120 c1c2 

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_following_text_no_text_before_italics_off_paint():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9429 91ce 91ab 91ae c1c2 9120 c1c2 

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_following_text_no_text_before_italics_on_pop():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9420 91d0 c1c2 91ae c1c2 942f

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_following_text_no_text_before_italics_on_roll():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9425 91d0 c1c2 91ae c1c2 

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_following_text_no_text_before_italics_on_paint():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9429 91d0 c1c2 91ae c1c2 

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_with_space_before_pop():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9420 91d0 c180 c220 91ae c1c2 942f

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_with_space_before_roll():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9425 91d0 c180 c220 91ae c1c2

"""


@pytest.fixture(scope="session")
def sample_scc_mid_row_with_space_before_paint():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9429 91d0 c180 c220 91ae c1c2

"""


@pytest.fixture(scope="session")
def sample_scc_with_spaces_at_eol_pop():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9420 91d0 c180 c220 91e0 c1c2 2020 2080 92c2 c1c2 2080 942f

"""


@pytest.fixture(scope="session")
def sample_scc_with_spaces_at_eol_roll():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9425 91d0 c180 c220 91e0 c1c2 2020 2080 92c2 c1c2 2080

"""


@pytest.fixture(scope="session")
def sample_scc_with_spaces_at_eol_paint():
    return """\
Scenarist_SCC V1.0

00:00:01:24	9429 91d0 c180 c220 91e0 c1c2 2020 2080 92c2 c1c2 2080

"""


@pytest.fixture(scope="session")
def sample_scc_paint_on_edm():
    return """\
Scenarist_SCC V1.0

00:00:00;00	9429 4920 f468 e96e 6b80

00:00:01;00	942c

00:00:02;00	9429 c8e5 ecec ef80

00:00:04;00	942c

"""


@pytest.fixture(scope="session")
def sample_scc_doubled_mid_row_before_punctuation():
    return """\
Scenarist_SCC V1.0

00:26:48;29\t9420 9420 94d0 94d0 97a1 97a1 3e3e 2057 e5a7 ecec 2062 e520 6261 e36b 206e e5f8 f420 f7e5 e56b 20f7 e9f4 6880 9470 9470 616e eff4 68e5 f220 e570 e973 ef64 e520 efe6 91ae 91ae 4361 6e61 6461 2046 e9ec e573 9120 9120 ae80 942c 942c 8080 8080 942f 942f

"""


# The caption at 00:05:50.800 of examples/2000370803_Original_en.txt: 'A ' is
# written at column 11, then a PAC lands at column 12 — right at the cursor —
# before the mid-row italic command and 'yaaruin?'. One line of text, so one
# origin and one cue.
@pytest.fixture(scope="session")
def sample_scc_mid_row_code_at_the_cursor():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 94f4 9723 c180 9476 91ae 7961 61f2 75e9 6ebf

00:00:03:00\t9420 942f

00:00:05:00\t942c

"""


@pytest.fixture(scope="session")
def sample_scc_frame_30():
    return """\
Scenarist_SCC V1.0

00:00:09:30 94ae 94ae 9420 9420 9470 9470 c865 ecec ef80 942c 942c 942f 942f

"""


@pytest.fixture(scope="session")
def sample_scc_frame_29():
    return """\
Scenarist_SCC V1.0

00:00:09:29 94ae 94ae 9420 9420 9470 9470 c865 ecec ef80 942c 942c 942f 942f

00:00:12:00 942c 942c

"""


# A PAC plus a Tab Offset puts the origin at column 6, 'A ' takes the cursor
# to column 8, and the next PAC lands exactly on it, so this is still the same
# line. Measured off the origin at 6 instead, that PAC looked like a Tab Offset
# two columns along and dragged the origin with it.
@pytest.fixture(scope="session")
def sample_scc_same_row_pac_near_the_origin_after_text():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 94f2 97a2 c120 94f4 91ae 79e5 7380

00:00:03:00\t942c 942f

"""


# 'Quyana, ' is written from column 0, so the cursor ends at column 8 and the
# PAC that follows lands exactly on it: the same line, continuing.
@pytest.fixture(scope="session")
def sample_scc_same_row_pac_at_the_cursor():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 94e0 5175 7961 6e61 2c20 94f4 c1f4 7361 f1ae

00:00:03:00\t942c 942f

"""


# The shape at 00:14:25.566 of examples/2000370803_Original_en.txt: line 1
# starts at column 15, a same-row PAC plus Tab Offset lands on the cursor at
# column 26 before the italic run, then a row+1 PAC plus Tab Offset starts
# line 2. One cue of two lines, at the line 1 origin.
@pytest.fixture(scope="session")
def sample_scc_same_row_pac_at_the_cursor_then_next_row():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 91d6 9723 57e5 20e3 61ec ec20 68e9 6d80 91dc 97a2 91ae 79e5 e9ec 917a 97a1 e96e 2054 ece9 6e67 e9f4 ae80

00:00:03:00\t942c 942f

"""


# The same PAC twice on one line, with text in between so it is not filtered
# as a doubled command. Measured off the cursor at column 6 the second one
# looks like a jump six columns back, but it names the column the line already
# starts at, so there is nowhere new for it to go.
@pytest.fixture(scope="session")
def sample_scc_pac_restating_the_position_after_text():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 94e0 5175 7961 6e61 94e0 20c1 f473 61f1 ae80

00:00:03:00\t942c 942f

"""


# 'Ah' is written from column 0, so the cursor ends at column 2 and the PAC
# that follows points at column 4: columns 2 and 3 are blank screen columns in
# the middle of the line, and have to survive as spaces.
@pytest.fixture(scope="session")
def sample_scc_same_row_pac_ahead_of_the_cursor():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 94e0 c168 94f2 f468 e5f2 e520 79ef 7520 61f2 e5ae

00:00:03:00\t942c 942f

"""


# Thirty characters are written from column 0, then a PAC points at column 28
# and 'WXYZ' follows it with nothing in between to move it on. Those four
# characters take columns 28 to 31, so they land on top of the last two
# already written: the line is 32 columns wide, not 34.
@pytest.fixture(scope="session")
def sample_scc_same_row_pac_behind_the_cursor():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 94e0 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 d5d6 5758 d9da 6162 e364 94fe 5758 d9da

00:00:03:00\t942c 942f

"""


# A row+1 PAC opens a second line and a Tab Offset follows it, so the offset
# indents that line rather than repositioning the caption. The same-row PAC at
# column 4 then lands exactly on the cursor the offset moved: one cue, two
# lines, the second indented by the offset's two columns and nothing more.
@pytest.fixture(scope="session")
def sample_scc_tab_offset_after_line_break():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 c1c2 94e0 97a2 43c4 94f2 4546

00:00:03:00\t942c 942f

"""


# A row+1 PAC opens a second line, then a PAC three rows up repositions before
# any text arrives on it. The line that was never written cannot still owe a
# break, so the repositioning stands: two separately positioned cues.
@pytest.fixture(scope="session")
def sample_scc_line_break_then_repositioning():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 c1c2 94e0 92da 43c4

00:00:03:00\t942c 942f

"""


# The shape at 00:00:45;26 of examples/2000370803_Original_en.txt: an italic
# run is still open when a row+2 PAC repositions, so the italics have to be
# closed off. The closing node belongs to the text it closes, not to the
# position the PAC has already moved to.
@pytest.fixture(scope="session")
def sample_scc_italics_still_open_at_repositioning():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 13f4 97a2 91ae 9137 20c1 c220 9137 94f4 97a1 91ae 9137 2043 c420 9137

00:00:03:00\t942c 942f

"""


# 'AB' is written, then a row+1 PAC wraps to the next line and an extended
# character arrives first on it. Extended characters carry an automatic
# backspace, but there is nothing to their left to erase when they open a row.
@pytest.fixture(scope="session")
def sample_scc_extended_char_first_on_a_wrapped_line():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 c1c2 94e0 9220 c243

00:00:03:00\t942c 942f

"""


# The same, except the PAC repositions rather than wrapping, so the character
# the automatic backspace would reach for belongs to a different cue.
@pytest.fixture(scope="session")
def sample_scc_extended_char_first_at_a_new_position():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 c1c2 92da 9220 c243

00:00:03:00\t942c 942f

"""


# The same PAC twice for error correction, then a Tab Offset. The duplicate is
# filtered out, but the offset still belongs to a PAC and still indents it:
# column 0 + 3, not column 0.
@pytest.fixture(scope="session")
def sample_scc_doubled_pac_with_tab_offset():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 9440 9723 c1c2

00:00:03:00\t942c 942f

"""


# The same shape, with line 2 filled out to the full 32 columns. Carrying the
# abandoned line's blank columns into it would make it 33 wide and fail
# validation, so this is the width check on the fix above.
@pytest.fixture(scope="session")
def sample_scc_blank_columns_abandoned_before_a_full_line():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 c1c2 9452 94e0 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 d5d6 5758 d9da 6162 e364 e520

00:00:03:00\t942c 942f

"""


# 'AB' is written from column 0 and a PAC points at column 4, then a Tab Offset
# carries it two further columns on to column 6. The offset arrives part-way
# through a line, so the four columns between the text and column 6 are blank
# screen columns rather than an indent for a line that has not started.
@pytest.fixture(scope="session")
def sample_scc_tab_offset_part_way_through_a_line():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 c1c2 9452 97a2 43c4

00:00:03:00\t942c 942f

"""


# Thirty characters are written from column 0 and a PAC points back at column
# 28, but a style-setting PAC stands between the text and the four characters
# that follow. The columns those four overwrite are screen columns, not nodes,
# so the style change in between cannot spare them: the line is 32 wide.
@pytest.fixture(scope="session")
def sample_scc_style_command_between_the_text_and_a_refill_pac():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 946e c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 d5d6 5758 d9da 6162 e364 94fe 5758 d9da

00:00:03:00\t942c 942f

"""


# 'ABCD' is written from column 2 and a PAC points back at column 4, then a
# mid-row code arrives instead of text. The mid-row code moves the line on, so
# the PAC turns out not to have been an overwrite after all and 'EF' follows the
# text rather than landing on top of it.
@pytest.fixture(scope="session")
def sample_scc_mid_row_code_after_a_pac_behind_the_cursor():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9470 97a2 c1c2 43c4 94f2 91ae 4546

00:00:03:00\t942c 942f

"""


# Ten characters are written from column 5, one of them an extended character
# whose automatic backspace erases the character before it. The PAC that follows
# points at column 16, which is one column past where the text really ended —
# so exactly one blank column survives, and only if the backspace was counted.
@pytest.fixture(scope="session")
def sample_scc_backspace_before_a_pac_ahead_of_the_cursor():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 94f2 97a1 c1c2 43c4 4546 c7c8 9220 92a1 92a2 94f8 5758

00:00:03:00\t942c 942f

"""


# Eight columns of text from column 20, then the restated PAC followed by a Tab
# Offset, which resolves at column 22 — still behind the cursor at 28. An offset
# that far back is moving over the text, not nudging the PAC onto the cursor, so
# it must not cancel the overwrite: 'AB' survives and 'WXYZIJ' covers columns 22
# to 27. Appended instead, the row would run past column 32.
@pytest.fixture(scope="session")
def sample_scc_tab_offset_resolving_behind_the_cursor():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 947a c1c2 43c4 4546 c7c8 947a 97a2 5758 d9da 494a

00:00:03:00\t942c 942f

"""


# Twenty-four columns of text, then the origin PAC restated and twenty-four more.
# Treating that as a continuation appended them, making a 48-character line out
# of a row the decoder shows in 24 columns.
@pytest.fixture(scope="session")
def sample_scc_restated_origin_pac_refilling_a_long_line():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9470 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 d5d6 5758 9470 d9da c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 d5d6

00:00:03:00\t942c 942f

"""


# A roll-up row restates its own PAC mid-row, then the rest of the row arrives
# in pieces, as live-caption encoders send it. Taken as an overwrite, the nine
# columns that follow cover "HE'S YOUNG" and the caption loses its first words;
# appended, the row is 19 columns and fits.
@pytest.fixture(scope="session")
def sample_scc_roll_up_pac_restating_the_row_mid_row():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9425 9425 94ad 94ad 1340 1340 c845 a7d3 20d9 4fd5 cec7 13d0

00:00:01:10\t20c1 ce80

00:00:01:13\tc480

00:00:01:14\t2057 454c

00:00:01:17\t4c80

00:00:03:00\t942c 942c

"""


# Real-world bytes: a roll-up row restates its PAC in the middle of a word,
# between "TH" and "E". The row fits appended, so the word has to come out whole.
@pytest.fixture(scope="session")
def sample_scc_roll_up_pac_restating_the_row_mid_word():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9425 9425 94ad 94ad 1340 1340 57c8 45ce 20d9 4fd5 204c 4f4f cb80 20c1 5480 2054 c880 13d0 4580

00:00:03:00\t942c 942c

"""


# The row restating its PAC mid-row fits appended on its own, 23 columns, then
# rolls up into the caption of a second row. Joined to that row it is 34
# columns, which would make the restated PAC look like an overwrite of
# "HE'S YOUNG" if the rows were settled together instead of one by one.
@pytest.fixture(scope="session")
def sample_scc_roll_up_restated_row_rolled_into_a_long_line():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9425 9425 94ad 94ad 1340 1340 c845 a7d3 20d9 4fd5 cec7 13d0 20c1 cec4 2057 454c 4c2c 204f cb80

00:00:02:00\t94ad 94ad 1340 1340 c1c2 43c4 4546 c7c8 494a

00:00:03:00\t94ad 94ad

00:00:04:00\t942c 942c

"""


# A full 32-column row, then its PAC restated with a Tab Offset to column 1 and
# four more characters. Neither reading fits: appended the row is 36 columns,
# and covering from column 1 leaves the 27 columns past "WXYZ" on screen. The
# row has to be rejected, not cut down to "AWXYZ".
@pytest.fixture(scope="session")
def sample_scc_pac_pointing_back_over_a_full_row_with_less_text():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9470 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 d5d6 5758 d9da 6162 e364 e5e6 9470 97a1 5758 d9da

00:00:03:00\t942c 942f

"""


# A roll-up row sent again in full over itself, then a second row. Simulated,
# the first row is read again for the caption the second rolls into.
@pytest.fixture(scope="session")
def sample_scc_roll_up_row_refilled_then_rolled():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9425 9425 94ad 94ad 9470 9470 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 d5d6 5758 9470 9470 d9da c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 d5d6

00:00:02:00\t94ad 94ad 9470 9470 d9da

00:00:02:15\t94ad 94ad

00:00:03:00\t942c 942c

"""


# A pop-on caption right-justified by its PACs: 'SAM:' at row 3, column 26+2,
# then the line below at row 4, column 4+3, opening with an italics code. The
# cue's origin has to be the second line's column, or the box the writers draw
# from the first line's is too narrow for it and it wraps.
@pytest.fixture(scope="session")
def sample_scc_pop_on_line_starting_left_of_the_origin():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 92dc 97a2 d3c1 cdba 92f2 9723 91ae 5468 e520 ece9 6ee5 2062 e5ec eff7 20e9 f480

00:00:03:00\t942c 942f

"""


# "AB" at row 14, column 16, then a second line whose PAC and Tab Offset put it
# at column 5 before a PAC on the same row skips it on to column 8. The three
# columns skipped are blank screen columns of the second line, so it starts at
# column 5, not 8.
@pytest.fixture(scope="session")
def sample_scc_pop_on_line_starting_with_skipped_columns():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9458 c1c2 94f2 97a1 94f4 43c4

00:00:03:00\t942c 942f

"""


# "HELLO" at row 14, column 4, then a PAC to row 15, column 12 that a second
# PAC on the same row overrides with column 4 before any text arrives. "WORLD"
# lands at column 4, under "HELLO", so the second line is not indented.
@pytest.fixture(scope="session")
def sample_scc_pop_on_pac_overriding_the_line_start_before_text():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9452 c845 4c4c 4f80 9476 94f2 574f 524c c480

00:00:03:00\t942c 942f

"""


# A PAC to row 14 that no text follows, then a PAC to row 15, column 0 and a
# Tab Offset of 2. The row 14 PAC is the cue's origin, so "WORLD" is placed by
# indenting its line 2 columns, not by moving the origin down onto row 15.
@pytest.fixture(scope="session")
def sample_scc_pop_on_tab_offset_on_the_line_below_an_empty_row():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 94e0 97a2 574f 524c c480

00:00:03:00\t942c 942f

"""


# "HELLO" at row 14, column 0, then a PAC to row 15, column 12 that a second
# PAC on the same row overrides with column 4 before any text arrives. The
# second PAC is more than a tab offset from the first, but the line has no
# text yet, so "WORLD" still continues the cue, starting at column 4.
@pytest.fixture(scope="session")
def sample_scc_pop_on_pac_overriding_the_line_start_far_from_it():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 c845 4c4c 4f80 9476 94f2 574f 524c c480

00:00:03:00\t942c 942f

"""


# "HELLO" at row 14, column 16, then PACs to row 15 at columns 16, 24 and 8
# before "WORLD". The skip from 16 to 24 owes blank columns that the PAC back to
# 8 cancels, so "WORLD" starts the line at column 8 and nothing is left of it.
@pytest.fixture(scope="session")
def sample_scc_pop_on_pac_pulling_back_over_skipped_columns():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9458 c845 4c4c 4f80 94f8 94fc 94f4 574f 524c c480

00:00:03:00\t942c 942f

"""


# "HELLO" at row 14, column 0, then "AB" at row 15, column 12, then a PAC to
# row 15, column 0 and "CD". The PAC points back further than the second line
# reaches, so whatever it overwrites, it cannot reach into the line above.
@pytest.fixture(scope="session")
def sample_scc_pop_on_pac_pointing_back_past_the_start_of_the_line():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 c845 4c4c 4f80 9476 c1c2 94e0 43c4

00:00:03:00\t942c 942f

"""


# "ABCDEFGH" at row 15, column 0, then a PAC back to column 0 overwrites it
# with "WX", leaving the cursor at column 2. A PAC to column 4 is then within a
# tab offset of the cursor and continues the line.
@pytest.fixture(scope="session")
def sample_scc_pac_within_a_tab_offset_of_an_overwrite():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9470 c1c2 43c4 4546 c7c8 9470 5758 94f2 d9da

00:00:03:00\t942c 942f

"""


# Italic "ABCDE" at row 15, columns 1-5, then a mid-row code turning italics off
# takes column 6, leaving the cursor at 7. A PAC to column 4 is within a tab
# offset of it, so "XY" overwrites "DE" on the same line.
@pytest.fixture(scope="session")
def sample_scc_pac_within_a_tab_offset_of_a_mid_row_code():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9470 91ae c1c2 43c4 4580 9120 94f2 58d9

00:00:03:00\t942c 942f

"""


# A roll-up row carrying on in the next line of the file with no Carriage
# Return to roll it up first: 40 columns on the base row.
@pytest.fixture(scope="session")
def sample_scc_roll_up_next_line_without_a_carriage_return():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9425 9425 94ad 94ad 9470 9470 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:02:00\tc1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:03:00\t94ad 94ad

00:00:04:00\t942c 942c

"""


# "HI" at row 14, column 0, then a second line at row 15, column 8, whose text
# carries on in the next line of the file with no PAC: 30 characters, 8
# columns right of the cue's origin.
@pytest.fixture(scope="session")
def sample_scc_indented_line_on_the_same_row_without_a_pac():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 c849 9475 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:02:00\tc1c2 43c4 4546 c7c8 494a

00:00:03:00\t942c 942f

"""


# "HI" places a first caption on row 15. The next one writes its first part
# with no PAC, so it lands on that row by default, then a PAC naming the same
# row carries the text on along it: 40 columns.
@pytest.fixture(scope="session")
def sample_scc_text_before_its_pac_on_the_same_row():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 9470 c849 942f

00:00:02:00\t94ae 9420 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 9470 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 942f

00:00:03:00\t942c

"""


# A PAC on row 14 with no text before the one on row 15, so the caption opens
# with an empty line, then the row 15 text carries on in the next line of the
# file with no PAC: 40 columns on the second line.
@pytest.fixture(scope="session")
def sample_scc_caption_opening_with_a_blank_line_then_continuing_its_row():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 9470 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:02:00\tc1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:03:00\t942c 942f

"""


# A two-line cue on rows 1 and 2, then a cue on row 14 whose text carries on
# in the next line of the file with no PAC: 40 columns on the second cue.
@pytest.fixture(scope="session")
def sample_scc_two_cues_the_second_continuing_its_row():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9140 c849 91e0 c849 9440 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:02:00\tc1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:03:00\t942c 942f

"""


# "HI" on row 14, then the next line of the file moves to row 15 before
# sending 40 columns in one go: the row changed, so nothing continued it.
@pytest.fixture(scope="session")
def sample_scc_long_line_after_a_row_change():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 c849

00:00:02:00\t9470 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:03:00\t942c 942f

"""


# "HI" on row 15, then the next line of the file repositions to row 1 before
# sending 40 columns in one go: a cue of its own, not a continued row.
@pytest.fixture(scope="session")
def sample_scc_long_line_after_a_repositioning():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9470 c849

00:00:02:00\t9140 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:03:00\t942c 942f

"""


# A roll-up row "HI" rolled up by a Carriage Return on a line of its own, then
# 40 columns sent in one go: the Carriage Return started a row of its own.
@pytest.fixture(scope="session")
def sample_scc_roll_up_long_line_after_a_carriage_return():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9425 9425 94ad 94ad 9470 9470 c849

00:00:02:00\t94ad 94ad

00:00:03:00\tc1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:04:00\t942c 942c

"""


# "HI" left in pop-on memory, then the next line of the file switches to
# paint-on and sends 40 columns in one go with no PAC: a memory of its own,
# so nothing on its row was continued.
@pytest.fixture(scope="session")
def sample_scc_pop_on_text_then_paint_on_line_without_a_pac():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 94ae 9470 c849

00:00:02:00\t9429 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:03:00\t942c

"""


# A 40-column line sent in one go on row 14, then a row 15 line whose text
# carries on in the next line of the file with no PAC: two lines too long,
# only the second because of a continued row.
@pytest.fixture(scope="session")
def sample_scc_long_line_then_a_line_continuing_its_row():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9440 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:02:00\t9470 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:03:00\tc1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:04:00\t942c 942f

"""


# A roll-up row "ABCDE" carried on to "ABCDEFGHIJ" by the next line of the
# file with no PAC, then rolled up under three more rows.
@pytest.fixture(scope="session")
def sample_scc_roll_up_row_continued_without_a_pac_then_rolled():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9426 9426 94ad 94ad 9470 9470 c1c2 43c4 4580

00:00:02:00\t46c7 c849 4a80

00:00:03:00\t94ad 94ad

00:00:04:00\t9470 cb4c cdce 4f80

00:00:05:00\t94ad 94ad

00:00:06:00\t9470 d5d6 5758 d9da

00:00:07:00\t94ad 94ad

00:00:08:00\t9470 45ce c480

00:00:09:00\t94ad 94ad 942c

"""


# As above, the first row "ABCDEFGHIJ" sent in one go.
@pytest.fixture(scope="session")
def sample_scc_roll_up_row_sent_in_one_go_then_rolled():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9426 9426 94ad 94ad 9470 9470 c1c2 43c4 4546 c7c8 494a

00:00:03:00\t94ad 94ad

00:00:04:00\t9470 cb4c cdce 4f80

00:00:05:00\t94ad 94ad

00:00:06:00\t9470 d5d6 5758 d9da

00:00:07:00\t94ad 94ad

00:00:08:00\t9470 45ce c480

00:00:09:00\t94ad 94ad 942c

"""


# "ABC" carried on to "ABCDE" by the next line of the file, then a PAC
# restating the row's origin sends the row again in full, 40 columns: the
# overwrite drops "ABCDE", so nothing of the row is left to have continued.
@pytest.fixture(scope="session")
def sample_scc_pac_resending_a_continued_row_in_full_past_the_last_column():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9470 c1c2 4380

00:00:02:00\tc445

00:00:03:00\t9470 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:04:00\t942c 942f

"""


# As sample_scc_text_before_its_pac_on_the_same_row, the PAC naming row 14
# rather than the row 15 the text before it took: no row was carried on.
@pytest.fixture(scope="session")
def sample_scc_text_before_its_pac_on_another_row():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 9470 c849 942f

00:00:02:00\t94ae 9420 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 9440 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 942f

00:00:03:00\t942c

"""


# "ABCDE" sent again in full by a PAC restating the row's origin, 40 columns,
# then "XY" carried on by the next line of the file with no PAC: the resend
# continued nothing, but "XY" continued the row it left.
@pytest.fixture(scope="session")
def sample_scc_pac_resending_a_row_in_full_then_a_line_continuing_it():
    return """\
Scenarist_SCC V1.0

00:00:01:00\t9420 942f 94ae 9420 9470 c1c2 43c4 4580

00:00:02:00\t9470 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354 c1c2 43c4 4546 c7c8 494a cb4c cdce 4fd0 5152 d354

00:00:03:00\t58d9

00:00:04:00\t942c 942f

"""
