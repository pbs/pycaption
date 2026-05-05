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
│   │   ├── __init__.py           # SCCReader, SCCWriter
│   │   ├── constants.py          # Character maps, control codes, PAC tables
│   │   ├── specialized_collections.py  # TimingCorrectingCaptionList, CaptionCreator, PopOnCue
│   │   ├── state_machines.py     # Position tracking
│   │   └── translator.py         # SCC command translation/debugging
│   ├── dfxp/                     # DFXP/TTML format
│   │   ├── __init__.py           # DFXPReader (re-export)
│   │   ├── base.py               # DFXPReader, DFXPWriter
│   │   └── extras.py             # LegacyDFXPWriter
│   ├── webvtt.py                 # WebVTT format (reader + writer)
│   ├── srt.py                    # SRT format (reader + writer)
│   ├── sami.py                   # SAMI format (reader + writer)
│   ├── microdvd.py               # MicroDVD format (reader + writer)
│   └── transcript.py             # Plain text transcript (writer only, uses nltk)
├── tests/                        # Test suite
│   ├── conftest.py               # Fixture imports (re-exports from fixtures/)
│   ├── fixtures/                 # Pytest fixture modules (inline caption strings)
│   │   ├── scc.py, translated_scc.py, dfxp.py, webvtt.py, srt.py, sami.py, microdvd.py
│   ├── captions/                 # Raw caption files used as test data
│   ├── mixins.py                 # Shared test helpers (ReaderTestingMixIn)
│   ├── test_scc.py               # SCC reader tests
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
│   ├── specs/                    # Format specification summaries (SCC, DFXP, WebVTT)
│   └── compliance_checks/        # Code-vs-spec compliance reports
├── examples/                     # Sample caption files
├── docs/                         # Sphinx documentation
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
- **BaseWriter** (`base.py`): Abstract base with `write()` method
- **CaptionSet**: Container mapping language codes to lists of `Caption` objects
- **Caption**: Single cue with `start`, `end` (microseconds), and a list of `CaptionNode`s
- **CaptionNode**: Text, style, or line break node with optional `layout_info`

### Supported Formats

| Format | Reader | Writer | Spec |
|---|---|---|---|
| SCC (CEA-608) | SCCReader | SCCWriter | Broadcast closed captions |
| DFXP/TTML | DFXPReader | DFXPWriter | XML-based timed text |
| WebVTT | WebVTTReader | WebVTTWriter | Web video captions |
| SRT | SRTReader | SRTWriter | SubRip subtitle format |
| SAMI | SAMIReader | SAMIWriter | Microsoft Synchronized Accessible Media |
| MicroDVD | MicroDVDReader | MicroDVDWriter | Frame-based subtitles |
| Transcript | - | TranscriptWriter | Plain text (nltk sentence splitting) |

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

### Key Design Decisions

1. **Times in microseconds**: All internal timing uses microseconds as integers/floats
2. **CaptionNode tree**: Captions are flat lists of text/style/break nodes (not nested DOM)
3. **Layout via geometry**: Positioning uses `Point`, `Size`, `Padding`, `Alignment` primitives
4. **Timing correction is implicit**: `TimingCorrectingCaptionList` silently adjusts end times
   when the next caption arrives — there is no explicit validation

---

## How pycaption Fits in PBS's Pipeline

```
Video Upload -> Skylab Ingestion -> Caption File (SCC/DFXP/SRT)
                                         |
                                    pycaption.read()
                                         |
                                    CaptionSet (internal model)
                                         |
                                    pycaption.write()
                                         |
                                    WebVTT output -> M3U8 playlist -> HLS streaming
```

The primary production path is **SCC -> WebVTT** for broadcast content.

---

## CI / Testing

### CI Pipeline

Tests run in GitHub Actions via `run_tests.sh`.

- **Matrix**: py310, py311, py312 (maps to `run_tests.sh test_py310`, etc.)
- **Artifacts**: `junit.xml` (test report) and `coverage.xml` (coverage report)
- **Notifications**: Slack messages on pass/fail (requires `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID` secrets)
- **Triggers**: push to main, PRs targeting main, workflow_dispatch, workflow_call

To run tests locally (without Docker):

```bash
# Run all tests
python -m pytest tests/ -q

# Run specific format tests
python -m pytest tests/test_scc.py -q

# Run with verbose output
python -m pytest tests/ -v
```

- Tests cover all formats
- Fixtures defined in `tests/fixtures/` as pytest session-scoped fixtures
- Each fixture is an inline string containing a complete caption file
- Conversion tests verify round-trip and cross-format fidelity

---

## Version Management

Version is in `setup.py`. Single source of truth.

- **Bug fix**: bump patch
- **New feature**: bump minor

---

## Known Complexity Areas

1. **SCC reader timing**: Most bugs historically live here. The pop-on queue, implicit buffer
   flushing, and timing correction interact in subtle ways.
2. **SCC control code handling**: 700+ hex codes, doubling rules, mode-specific behavior.
3. **DFXP styling inheritance**: Styles can be defined inline, by reference, or inherited.
4. **Positioning round-trip**: SCC uses row/column, DFXP uses percentages, WebVTT uses
   cue settings — conversions are lossy.
