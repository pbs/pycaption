# pycaption - Project Understanding

## What Is pycaption?

pycaption is a **closed caption format converter** library used by PBS's media pipeline (Skylab).
It reads caption files in one format and writes them in another, supporting the major broadcast
and web caption formats. It is the caption ingestion engine behind PBS's video platform.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python (see `setup.py` for version bounds) |
| Framework | None (pure library) |
| Testing | pytest, pytest-lazy-fixture |
| Linting | flake8, pre-commit hooks |
| Packaging | setuptools (setup.py) |
| Dependencies | beautifulsoup4, lxml, cssutils |
| Optional | nltk (transcript features) |

---

## Project Structure

```
pycaption/
├── pycaption/                    # Main library
│   ├── __init__.py               # Public API (re-exports all readers/writers)
│   ├── base.py                   # BaseReader, BaseWriter, Caption, CaptionSet, CaptionNode
│   ├── geometry.py               # Layout/positioning primitives
│   ├── exceptions.py             # Custom exception classes
│   ├── utils.py                  # Shared utilities
│   ├── scc/                      # SCC (CEA-608) format
│   │   ├── __init__.py           # Package exports (SCCReader, SCCWriter)
│   │   ├── reader.py             # SCCReader class
│   │   ├── writer.py             # SCCWriter class
│   │   ├── constants.py          # Character maps, control codes, PAC tables
│   │   ├── specialized_collections.py  # TimingCorrectingCaptionList, CaptionCreator, PopOnCue
│   │   ├── state_machines.py     # Position tracking
│   │   └── translator.py         # SCC command translation/debugging
│   ├── dfxp/                     # DFXP/TTML format
│   │   ├── __init__.py           # Package exports (DFXPReader, DFXPWriter)
│   │   ├── reader.py             # DFXPReader, LayoutAwareDFXPParser, LayoutInfoScraper
│   │   ├── writer.py             # DFXPWriter, RegionCreator
│   │   ├── constants.py          # DFXP namespaces, default region, base markup
│   │   └── extras.py             # LegacyDFXPWriter, SinglePositioningDFXPWriter
│   ├── sami/                     # SAMI format
│   │   ├── __init__.py           # Package exports (SAMIReader, SAMIWriter)
│   │   ├── reader.py             # SAMIReader class
│   │   ├── writer.py             # SAMIWriter class
│   │   ├── parser.py             # SAMIParser (HTML normalization)
│   │   └── constants.py          # SAMI base markup, alignment map
│   ├── webvtt/                   # WebVTT format
│   │   ├── __init__.py           # Package exports (WebVTTReader, WebVTTWriter)
│   │   ├── reader.py             # WebVTTReader class
│   │   ├── writer.py             # WebVTTWriter class
│   │   └── constants.py          # Regex patterns, timing helpers
│   ├── srt.py                    # SRT format (reader + writer in single file)
│   ├── microdvd.py               # MicroDVD format (reader + writer)
│   └── transcript.py             # Plain text transcript (writer only, uses nltk)
├── tests/                        # Test suite (504 tests)
│   ├── conftest.py               # Fixture imports (re-exports from fixtures/)
│   ├── fixtures/                 # Pytest fixture modules (inline caption strings)
│   │   ├── scc.py, translated_scc.py, dfxp.py, webvtt.py, srt.py, sami.py, microdvd.py
│   ├── captions/                 # Raw caption files used as test data
│   ├── mixins.py                 # Shared test helpers (ReaderTestingMixIn)
│   ├── test_scc.py               # SCC reader tests
│   ├── test_scc_writer.py        # SCC writer tests
│   ├── test_scc_conversion.py    # SCC -> other format tests
│   ├── test_scc_translator.py    # SCC translator tests
│   ├── test_dfxp.py              # DFXP reader tests
│   ├── test_dfxp_conversion.py   # DFXP -> other format tests
│   ├── test_dfxp_extras.py       # Legacy DFXP writer tests
│   ├── test_webvtt.py            # WebVTT reader tests
│   ├── test_webvtt_conversion.py # WebVTT -> other format tests
│   ├── test_srt.py               # SRT reader tests
│   ├── test_srt_conversion.py    # SRT -> other format tests
│   ├── test_sami.py              # SAMI reader tests
│   ├── test_sami_conversion.py   # SAMI -> other format tests
│   ├── test_microdvd.py          # MicroDVD tests
│   ├── test_microdvd_conversion.py
│   ├── test_base.py              # Base class tests
│   ├── test_geometry.py          # Geometry tests
│   └── test_functions.py         # Utility function tests
├── ai_artifacts/                 # AI-generated specs and compliance reports
│   ├── specs/                    # Format specification summaries (SCC, DFXP, WebVTT, SAMI)
│   └── compliance_checks/        # Code-vs-spec compliance reports
├── pycaption/scripts/            # Local-only supporting documentation (not committed)
├── examples/                     # Sample caption files
├── docs/                         # Sphinx documentation (introduction.rst)
├── setup.py                      # Package config (version here)
├── .pre-commit-config.yaml       # Linting: end-of-file-fixer, trailing-whitespace, flake8
└── README.rst                    # Project readme
```

---

## Architecture

### Reader/Writer Pattern

Every caption format follows the same interface:

```python
# Reading
reader = SCCReader()
caption_set = reader.read(content_string)

# Writing
writer = WebVTTWriter()
output = writer.write(caption_set)
```

- **BaseReader** (`base.py`): Abstract base with `detect()` and `read()` methods
- **BaseWriter** (`base.py`): Abstract base with `write()` method, accepts
  `relativize`, `video_width`, `video_height`, `fit_to_screen` parameters
- **CaptionSet**: Container mapping language codes to lists of `Caption` objects;
  also stores styles (dict) and regions (dict)
- **Caption**: Single cue with `start`, `end` (microseconds), a list of `CaptionNode`s,
  optional `style` dict, `layout_info` (Layout object), and metadata attrs
  (`caption_mode`, `roll_up_rows`)
- **CaptionNode**: Text, style, or line break node with optional `layout_info`

### Supported Formats

| Format | Reader | Writer | Module | Spec |
|---|---|---|---|---|
| SCC (CEA-608) | SCCReader | SCCWriter | `pycaption/scc/` | Broadcast closed captions |
| DFXP/TTML | DFXPReader | DFXPWriter | `pycaption/dfxp/` | XML-based timed text (W3C) |
| WebVTT | WebVTTReader | WebVTTWriter | `pycaption/webvtt/` | Web video captions (W3C) |
| SRT | SRTReader | SRTWriter | `pycaption/srt.py` | SubRip subtitle format |
| SAMI | SAMIReader | SAMIWriter | `pycaption/sami/` | Microsoft Synchronized Accessible Media |
| MicroDVD | MicroDVDReader | MicroDVDWriter | `pycaption/microdvd.py` | Frame-based subtitles |
| Transcript | - | TranscriptWriter | `pycaption/transcript.py` | Plain text (nltk sentence splitting) |

### Format Module Architecture

Each multi-file format module follows the same split pattern:

```
format/
├── __init__.py      # Package exports
├── reader.py        # Reader class (parsing, detect)
├── writer.py        # Writer class (serialization)
└── constants.py     # Shared constants, maps, regex patterns
```

**SCC** also has: `specialized_collections.py` (data structures), `state_machines.py`
(position tracking), `translator.py` (debug translation).

**SAMI** also has: `parser.py` (SAMIParser — HTML normalization before DOM walking).

**DFXP** also has: `extras.py` (LegacyDFXPWriter for older output format).

### SCC Reader Internals (Most Complex)

The SCC reader is significantly more complex than other formats because SCC encodes
closed captions as hex control codes rather than plain text. Key concepts:

- **Three caption modes**: Pop-On (buffered, displayed on EOC command), Paint-On (displayed immediately),
  Roll-Up (scrolling display)
- **Buffer system**: `NotifyingDict` with keys "pop", "paint", "roll" — mode switches trigger
  `_flush_implicit_buffers` observer
- **Pop-On queue**: `deque` of `PopOnCue` namedtuples for managing pop-on caption lifecycle
  (EOC queues, EDM finalizes)
- **Timing**: `TimingCorrectingCaptionList` auto-corrects end times based on next caption's start
- **Positioning**: PAC (Preamble Address Codes) set row/column, tab offsets adjust column,
  tracked by `DefaultProvidingPositionTracker`
- **Control code doubling**: CEA-608 requires control codes sent twice; `_handle_double_command`
  deduplicates

### WebVTT Reader Internals

The WebVTT reader handles the richest input format with:

- **STYLE blocks**: `::cue(.class)` rules parsed and stored as CaptionSet styles
- **REGION blocks**: Key-value settings stored as CaptionSet regions
- **Cue settings**: `line`, `position`, `size`, `align`, `vertical`, `region` parsed into
  Layout objects with origin/extent/alignment/writing-direction
- **Inline tags**: `<b>`, `<i>`, `<u>`, `<c.class>`, `<lang>`, `<ruby>`, `<v>` converted to
  CaptionNode STYLE nodes with appropriate attributes
- **Cue ID tracking**: Detects and warns on duplicate cue identifiers via `seen_ids`
- **Base style wrapping**: `::cue` global styles applied to bare text nodes via synthetic STYLE nodes;
  `_covers_base()` uses key-presence to avoid double-wrapping when a class overrides a base property
- **State machine parsing**: `_ParseState` tracks block type (NOTE/STYLE/REGION), timing found, pending cue ID

### DFXP Reader Internals

The DFXP/TTML reader handles XML-based captions with:

- **LayoutInfoScraper**: Resolves region positioning from `<region>` elements
  (origin, extent, padding, alignment, writing-direction) as a 5-tuple
- **LayoutAwareDFXPParser**: BeautifulSoup subclass that propagates layout to child elements
- **Style resolution**: Handles inline `tts:` attributes, `style` references, and inheritance
- **Time expression parsing**: Clock-time (`HH:MM:SS.mmm`), offset-time (`Ns`, `Nms`, `Nf`),
  tick-based (`Nt`), and frame-based (`HH:MM:SS:FF`) all supported

### SAMI Reader Internals

The SAMI reader uses a two-phase approach:

1. **SAMIParser** (extends `HTMLParser`): Normalizes malformed SAMI HTML into well-formed XML,
   extracts CSS styles, detects languages, resolves entities
2. **SAMIReader**: Walks the normalized DOM, building captions per-language with timing from
   `<SYNC start=>` elements, backfilling end times from subsequent sync points

### Key Design Decisions

1. **Times in microseconds**: All internal timing uses microseconds as integers/floats
2. **CaptionNode tree**: Captions are flat lists of text/style/break nodes (not nested DOM)
3. **Layout via geometry**: Positioning uses `Point`, `Size`, `Padding`, `Alignment` primitives
4. **Timing correction is implicit**: `TimingCorrectingCaptionList` silently adjusts end times
   when the next caption arrives — there is no explicit validation
5. **Fit-to-screen clamping**: Writer clamps extent to 90% horizontal / 95% vertical to prevent
   overflow (not 100% as might be expected)
6. **Style filtering**: Writers filter internal keys (e.g. `classes`, `webvtt_positioning`) from
   output via format-specific exclusion sets

---

## How pycaption Fits in PBS's Pipeline

```
Video Upload -> Skylab Ingestion -> Caption File (SCC/DFXP/SRT/SAMI/WebVTT)
                                         |
                                    pycaption.read()
                                         |
                                    CaptionSet (internal model)
                                     /    |    \
                    pycaption.write()  ...  pycaption.write()
                         |                       |
                    WebVTT output            SCC output
                         |                       |
                    HLS streaming           Broadcast delivery
```

The primary production paths are:
- **SCC → WebVTT/DFXP/SAMI/SRT** for broadcast content ingestion
- **WebVTT → SCC** for web-to-broadcast delivery
- **WebVTT input → HLS m3u8** via VTT writer output (OCTO-11514)

---

## Conversion Behavior

Each format conversion has documented differences in:
`pycaption/scripts/differences/{format}.txt`

Key behaviors across all conversions:

| Aspect | Behavior |
|---|---|
| Timing precision | Microseconds internally; output format determines display precision |
| Positioning | Best-effort mapping between row/col (SCC), percentages (DFXP/VTT), none (SRT) |
| Styling | Bold/italic/underline preserved where supported; color/background-color preserved in DFXP/SAMI/VTT |
| Writing direction | Vertical modes (VTT `vertical:rl`) → DFXP `tts:writingMode="tbrl"`; dropped in SCC/SAMI |
| Classes | VTT classes → DFXP `<style>` elements; SAMI `class=` attributes; filtered from SCC |
| Multi-language | SAMI/DFXP support natively; SCC/SRT/VTT output single language (use `force=`) |

---

## CI / Testing

### CI Pipeline

Tests run in GitHub Actions via `run_tests.sh`.

- **Matrix**: py310, py311, py312 (maps to `run_tests.sh test_py310`, etc.)
- **Artifacts**: `junit.xml` (test report) and `coverage.xml` (coverage report)
- **Notifications**: Slack messages on pass/fail (requires `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID` secrets)
- **Triggers**: push to main, PRs targeting main, workflow_dispatch, workflow_call

### Compliance Checks (GitHub Actions)

Additional workflows for format spec compliance:

- `scc_compliance_check.yml` — SCC reader/writer vs CEA-608 spec
- `webvtt_compliance_check.yml` — WebVTT reader/writer vs W3C spec
- `dfxp_compliance_check.yml` — DFXP reader/writer vs TTML 1.0 spec
- `sami_compliance_check.yml` — SAMI writer vs SAMI spec
- `all_compliance_checks.yml` — Runs all 4 checks with combined reporting
- `pr_compliance_check.yml` — Triggered on PRs, checks only affected formats

### Running Tests Locally

```bash
# Run all tests (504 tests, ~0.5s)
python -m pytest tests/ -q

# Run specific format tests
python -m pytest tests/test_scc.py tests/test_scc_writer.py -q

# Run with verbose output
python -m pytest tests/ -v

# Run conversion tests only
python -m pytest tests/test_webvtt_conversion.py -q
```

- Tests cover all formats (504 tests total)
- Fixtures defined in `tests/fixtures/` as pytest session-scoped fixtures
- Each fixture is an inline string containing a complete caption file
- Conversion tests verify round-trip and cross-format fidelity

---

## Version Management

Version is in `setup.py`. Single source of truth.

- **Bug fix**: bump patch
- **New feature**: bump minor

---

## Documentation

Format specification summaries used for compliance checking:
`ai_artifacts/specs/{format}/`

---

## Known Complexity Areas

1. **SCC reader timing**: Most bugs historically live here. The pop-on queue, implicit buffer
   flushing, and timing correction interact in subtle ways.
2. **SCC control code handling**: 700+ hex codes, doubling rules, mode-specific behavior.
3. **SCC writer backshift**: Timestamps shift earlier to account for decoder buffer fill time
   (MICROSECONDS_PER_CODEWORD × number of codes). Can cause 1-3 frame drift.
4. **DFXP styling inheritance**: Styles can be defined inline, by reference, or inherited.
   Writer uses `_span_stack` for proper nested span support (not flat open/close).
5. **DFXP fit-to-screen**: Thresholds are 90%/95% (not 100%) — applied automatically unless
   `fit_to_screen=False`.
6. **Positioning round-trip**: SCC uses row/column (15 rows × 32 cols), DFXP uses percentages,
   WebVTT uses cue settings — conversions are lossy.
7. **WebVTT reader complexity**: Handles STYLE blocks, REGION blocks, cue settings, inline tags,
   voice spans, ruby annotations — the richest input format.
8. **SAMI parser tolerance**: Must handle malformed HTML (unclosed tags, invalid entities,
   non-standard attributes) common in real-world SAMI files.
