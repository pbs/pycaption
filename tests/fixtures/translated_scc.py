import pytest


@pytest.fixture(scope="session")
def sample_translated_scc_success():
    return """Scenarist_SCC V1.0

00:00:09:05 [Erase Non-displayed Memory] [Erase Non-displayed Memory] [Resume Caption Loading] [Resume Caption Loading] [row 15, column 00, with plain white text.] [row 15, column 00, with plain white text.] [( ] [cl] [oc] [k ] [ti] [ck] [in] [g ] [)] [Erase Displayed Memory] [Erase Displayed Memory] [End Of Caption] [End Of Caption]

00:00:12:08 [Erase Displayed Memory] [Erase Displayed Memory]

00:00:13:18 [Erase Non-displayed Memory] [Erase Non-displayed Memory] [Resume Caption Loading] [Resume Caption Loading] [row 13, column 00, with plain white text.] [row 13, column 00, with plain white text.] [MA] [N:] [row 14, column 00, with plain white text.] [row 14, column 00, with plain white text.] [Wh] [en] [ w] [e ] [th] [in] [k] [row 15, column 00, with plain white text.] [row 15, column 00, with plain white text.] [of] [ "] [E ] [eq] [ua] [ls] [ m] [ c] [-s] [qu] [ar] [ed] [",] [Erase Displayed Memory] [Erase Displayed Memory] [End Of Caption] [End Of Caption]

00:00:16:03 [Erase Non-displayed Memory] [Erase Non-displayed Memory] [Resume Caption Loading] [Resume Caption Loading] [row 15, column 00, with plain white text.] [row 15, column 00, with plain white text.] [we] [ h] [av] [e ] [th] [is] [ v] [is] [io] [n ] [of] [ E] [in] [st] [ei] [n] [Erase Displayed Memory] [Erase Displayed Memory] [End Of Caption] [End Of Caption]

00:00:17:20 [Erase Non-displayed Memory] [Erase Non-displayed Memory] [Resume Caption Loading] [Resume Caption Loading] [row 14, column 00, with plain white text.] [row 14, column 00, with plain white text.] [as] [ a] [n ] [ol] [d,] [ w] [ri] [nk] [ly] [ m] [an] [row 15, column 00, with plain white text.] [row 15, column 00, with plain white text.] [wi] [th] [ w] [hi] [te] [ h] [ai] [r.] [Erase Displayed Memory] [Erase Displayed Memory] [End Of Caption] [End Of Caption]

00:00:19:13 [Erase Non-displayed Memory] [Erase Non-displayed Memory] [Resume Caption Loading] [Resume Caption Loading] [row 13, column 00, with plain white text.] [row 13, column 00, with plain white text.] [MA] [N ] [2:] [row 14, column 00, with plain white text.] [row 14, column 00, with plain white text.] [E ] [eq] [ua] [ls] [ m] [ c] [-s] [qu] [ar] [ed] [ i] [s] [row 15, column 00, with plain white text.] [row 15, column 00, with plain white text.] [no] [t ] [ab] [ou] [t ] [an] [ o] [ld] [ E] [in] [st] [ei] [n.] [Erase Displayed Memory] [Erase Displayed Memory] [End Of Caption] [End Of Caption]

00:00:25:16 [Erase Non-displayed Memory] [Erase Non-displayed Memory] [Resume Caption Loading] [Resume Caption Loading] [row 13, column 00, with plain white text.] [row 13, column 00, with plain white text.] [MA] [N ] [2:] [row 14, column 00, with plain white text.] [row 14, column 00, with plain white text.] [It] ['s] [ a] [ll] [ a] [bo] [ut] [ a] [n ] [et] [er] [na] [l] [row 15, column 00, with plain white text.] [row 15, column 00, with plain white text.] [Ei] [ns] [te] [in] [.] [Erase Displayed Memory] [Erase Displayed Memory] [End Of Caption] [End Of Caption]

00:00:31:15 [Erase Non-displayed Memory] [Erase Non-displayed Memory] [Resume Caption Loading] [Resume Caption Loading] [row 15, column 00, with plain white text.] [row 15, column 00, with plain white text.] [<L] [AU] [GH] [IN] [G ] [& ] [WH] [OO] [PS] [!>] [Erase Displayed Memory] [Erase Displayed Memory] [End Of Caption] [End Of Caption]

00:00:36:04 [Erase Displayed Memory] [Erase Displayed Memory]

"""


@pytest.fixture(scope="session")
def sample_translated_scc_no_brackets():
    return """Scenarist_SCC V1.0

00:00:09:05 Erase Non-displayed Memory Erase Non-displayed Memory Resume Caption Loading Resume Caption Loading row 15, column 00, with plain white text. row 15, column 00, with plain white text. (  cl oc k  ti ck in g  ) Erase Displayed Memory Erase Displayed Memory End Of Caption End Of Caption

00:00:12:08 Erase Displayed Memory Erase Displayed Memory

00:00:13:18 Erase Non-displayed Memory Erase Non-displayed Memory Resume Caption Loading Resume Caption Loading row 13, column 00, with plain white text. row 13, column 00, with plain white text. MA N: row 14, column 00, with plain white text. row 14, column 00, with plain white text. Wh en  w e  th in k row 15, column 00, with plain white text. row 15, column 00, with plain white text. of  " E  eq ua ls  m  c -s qu ar ed ", Erase Displayed Memory Erase Displayed Memory End Of Caption End Of Caption

00:00:16:03 Erase Non-displayed Memory Erase Non-displayed Memory Resume Caption Loading Resume Caption Loading row 15, column 00, with plain white text. row 15, column 00, with plain white text. we  h av e  th is  v is io n  of  E in st ei n Erase Displayed Memory Erase Displayed Memory End Of Caption End Of Caption

00:00:17:20 Erase Non-displayed Memory Erase Non-displayed Memory Resume Caption Loading Resume Caption Loading row 14, column 00, with plain white text. row 14, column 00, with plain white text. as  a n  ol d,  w ri nk ly  m an row 15, column 00, with plain white text. row 15, column 00, with plain white text. wi th  w hi te  h ai r. Erase Displayed Memory Erase Displayed Memory End Of Caption End Of Caption

00:00:19:13 Erase Non-displayed Memory Erase Non-displayed Memory Resume Caption Loading Resume Caption Loading row 13, column 00, with plain white text. row 13, column 00, with plain white text. MA N  2: row 14, column 00, with plain white text. row 14, column 00, with plain white text. E  eq ua ls  m  c -s qu ar ed  i s row 15, column 00, with plain white text. row 15, column 00, with plain white text. no t  ab ou t  an  o ld  E in st ei n. Erase Displayed Memory Erase Displayed Memory End Of Caption End Of Caption

00:00:25:16 Erase Non-displayed Memory Erase Non-displayed Memory Resume Caption Loading Resume Caption Loading row 13, column 00, with plain white text. row 13, column 00, with plain white text. MA N  2: row 14, column 00, with plain white text. row 14, column 00, with plain white text. It 's  a ll  a bo ut  a n  et er na l row 15, column 00, with plain white text. row 15, column 00, with plain white text. Ei ns te in . Erase Displayed Memory Erase Displayed Memory End Of Caption End Of Caption

00:00:31:15 Erase Non-displayed Memory Erase Non-displayed Memory Resume Caption Loading Resume Caption Loading row 15, column 00, with plain white text. row 15, column 00, with plain white text. <L AU GH IN G  &  WH OO PS !> Erase Displayed Memory Erase Displayed Memory End Of Caption End Of Caption

00:00:36:04 Erase Displayed Memory Erase Displayed Memory

"""


@pytest.fixture(scope="session")
def sample_translated_scc_commands_not_found():
    return """Scenarist_SCC V1.0

00:04:36;06 942x 942x 942x 942x [row 01, column 12, with plain white text.] [MA] [Ä] 525x c8cx ba8x
"""


@pytest.fixture(scope="session")
def sample_translated_scc_custom_brackets():
    return """Scenarist_SCC V1.0

00:00:09:05 {Erase Non-displayed Memory} {Erase Non-displayed Memory} {Resume Caption Loading} {Resume Caption Loading} {row 15, column 00, with plain white text.} {row 15, column 00, with plain white text.} {( } {cl} {oc} {k } {ti} {ck} {in} {g } {)} {Erase Displayed Memory} {Erase Displayed Memory} {End Of Caption} {End Of Caption}

00:00:12:08 {Erase Displayed Memory} {Erase Displayed Memory}

00:00:13:18 {Erase Non-displayed Memory} {Erase Non-displayed Memory} {Resume Caption Loading} {Resume Caption Loading} {row 13, column 00, with plain white text.} {row 13, column 00, with plain white text.} {MA} {N:} {row 14, column 00, with plain white text.} {row 14, column 00, with plain white text.} {Wh} {en} { w} {e } {th} {in} {k} {row 15, column 00, with plain white text.} {row 15, column 00, with plain white text.} {of} { "} {E } {eq} {ua} {ls} { m} { c} {-s} {qu} {ar} {ed} {",} {Erase Displayed Memory} {Erase Displayed Memory} {End Of Caption} {End Of Caption}

00:00:16:03 {Erase Non-displayed Memory} {Erase Non-displayed Memory} {Resume Caption Loading} {Resume Caption Loading} {row 15, column 00, with plain white text.} {row 15, column 00, with plain white text.} {we} { h} {av} {e } {th} {is} { v} {is} {io} {n } {of} { E} {in} {st} {ei} {n} {Erase Displayed Memory} {Erase Displayed Memory} {End Of Caption} {End Of Caption}

00:00:17:20 {Erase Non-displayed Memory} {Erase Non-displayed Memory} {Resume Caption Loading} {Resume Caption Loading} {row 14, column 00, with plain white text.} {row 14, column 00, with plain white text.} {as} { a} {n } {ol} {d,} { w} {ri} {nk} {ly} { m} {an} {row 15, column 00, with plain white text.} {row 15, column 00, with plain white text.} {wi} {th} { w} {hi} {te} { h} {ai} {r.} {Erase Displayed Memory} {Erase Displayed Memory} {End Of Caption} {End Of Caption}

00:00:19:13 {Erase Non-displayed Memory} {Erase Non-displayed Memory} {Resume Caption Loading} {Resume Caption Loading} {row 13, column 00, with plain white text.} {row 13, column 00, with plain white text.} {MA} {N } {2:} {row 14, column 00, with plain white text.} {row 14, column 00, with plain white text.} {E } {eq} {ua} {ls} { m} { c} {-s} {qu} {ar} {ed} { i} {s} {row 15, column 00, with plain white text.} {row 15, column 00, with plain white text.} {no} {t } {ab} {ou} {t } {an} { o} {ld} { E} {in} {st} {ei} {n.} {Erase Displayed Memory} {Erase Displayed Memory} {End Of Caption} {End Of Caption}

00:00:25:16 {Erase Non-displayed Memory} {Erase Non-displayed Memory} {Resume Caption Loading} {Resume Caption Loading} {row 13, column 00, with plain white text.} {row 13, column 00, with plain white text.} {MA} {N } {2:} {row 14, column 00, with plain white text.} {row 14, column 00, with plain white text.} {It} {'s} { a} {ll} { a} {bo} {ut} { a} {n } {et} {er} {na} {l} {row 15, column 00, with plain white text.} {row 15, column 00, with plain white text.} {Ei} {ns} {te} {in} {.} {Erase Displayed Memory} {Erase Displayed Memory} {End Of Caption} {End Of Caption}

00:00:31:15 {Erase Non-displayed Memory} {Erase Non-displayed Memory} {Resume Caption Loading} {Resume Caption Loading} {row 15, column 00, with plain white text.} {row 15, column 00, with plain white text.} {<L} {AU} {GH} {IN} {G } {& } {WH} {OO} {PS} {!>} {Erase Displayed Memory} {Erase Displayed Memory} {End Of Caption} {End Of Caption}

00:00:36:04 {Erase Displayed Memory} {Erase Displayed Memory}

"""


@pytest.fixture(scope="session")
def sample_translated_scc_special_and_extended_characters():
    return """Scenarist_SCC V1.0

00:00:16;29 [ ] [®] [°] [½] [¿] [™] [¢] [£] 

00:04:36;06 [♪] [à] [ ] [è] [â] [ê] [î] [ô] [û]

00:08:00;00 [É] [Ó] [Ú] [Ü] [ü] [‘] [¡] [*] [’] [—] [©]

00:12:00;23 [℠] [•] [“] [”] [À] [Â] [Ç] [È] [Ê] [Ë] [ë] [Î] [Ï] 

00:16:24;11 [ï] [Ô] [Ù] [ù] [Û] [«] [»] [Ã] [ã] [Í] [Ì] [ì] [Ò]

00:20:19;12 [ò] [Õ] [õ] [{] [}] [\\] [^] [_] [¦] [~] [Ä] [ä] [Ö]

00:24:39;28 [ö] [ß] [¥] [¤] [|] [Å] [å] [Ø] [ø] [┌] [┐] [└] [┘]
"""
