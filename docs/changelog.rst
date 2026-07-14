Changelog
---------
2.2.29
^^^^^^
  - Re-emit STYLE blocks on WebVTT→WebVTT roundtrip (global ::cue
    rules before class-specific rules).
  - Emit writing direction (vertical:rl|lr) from Layout when
    webvtt_positioning passthrough isn't available; preserve it through
    as_percentage_of() and fit_to_screen().
  - Fix _format_css_declarations to reverse-map internal keys
    (italics → font-style: italic, etc.) instead of emitting invalid CSS.
  - Split pycaption/webvtt.py into pycaption/webvtt/ package
    (reader.py, writer.py, constants.py). Public API unchanged.
  - Propagate ::cue base text-decoration (italic/bold/underline) onto
    bare text as STYLE node wrappers so all writers emit inline
    formatting. Already-styled cues are not double-wrapped.
  - Add CaptionReadWarning (non-fatal) when a multiline cue's line:%
    would place text partially off-screen.
  - Preserve REGION blocks through VTT→VTT roundtrip via raw settings
    on CaptionSet; region:id cue references stay valid.
  - Add ``regions`` param to CaptionSet (defaults to {}) with
    get_regions()/set_regions().
  - SCC writer: map WebVTT positioning and styles to CEA-608 codes
    (line:% → PAC rows, align → column indents + tab offsets,
    italics/underline → mid-row codes, unsupported styles dropped).
  - WebVTT writer: re-emit STYLE blocks on roundtrip, emit
    vertical:rl|lr, preserve writing_direction through Layout
    transforms, fix _format_css_declarations to output valid CSS.
  - Split pycaption/scc/ and pycaption/webvtt/ into reader.py +
    writer.py packages. Public API unchanged.
  - base.py: fix mutable default args (style={} → style=None), remove
    dead code (force_byte_string, Style, CaptionList.__getslice__).

2.2.28
^^^^^^
  - Parse WebVTT cue settings (position, line, size, align, vertical)
    into structured Layout objects. Integer line numbers (line:3) and
    percentage values (line:75%) are both converted to viewport
    percentages; vertical:rl|lr is stored as WritingDirectionEnum.
  - Parse STYLE blocks: extract ::cue CSS rules (font-style,
    font-weight, text-decoration, color, background-color) and resolve
    them onto <c.classname> spans at read time with correct cascade
    (::cue base < ::cue(.class) specificity).
  - Add WritingDirectionEnum to geometry.py and extend Layout with
    writing_direction field (included in __eq__, __hash__, __bool__,
    serialized()).
  - Filter ::cue-prefixed style keys from DFXP and SAMI writers to
    prevent invalid selectors in output.
  - Tag selectors (::cue(b)) are intentionally skipped — only bare
    ::cue and class selectors are supported.
  - Harden WebVTT header validation: detect() now checks the first
    line only (not substring match anywhere in file) and _validate_header()
    enforces a blank line after the WEBVTT signature.
  - Strip UTF-8 BOM (U+FEFF) in both detect() and read() so
    BOM-prefixed files no longer fail to parse.
  - Track NOTE blocks with in_note_block state in _parse(),
    _parse_regions(), and _parse_style_blocks() so that "-->" inside
    comments no longer crashes the parser or triggers false timing lines.
  - Reorder condition checks in _parse_style_blocks() so that "-->"
    inside STYLE block CSS content does not prematurely terminate
    style parsing.
  - Replace manual entity .replace() calls with html.unescape() to
    support numeric character references (&#169;, &#x266B;) and all
    HTML named entities. Note: &nbsp; now correctly decodes to U+00A0
    (non-breaking space) per spec, rather than U+0020.

2.2.27
^^^^^^
  - Implement WebVTT inline markup tag parsing in the reader. The
    tag-stripping regex is replaced with a proper parser that converts
    <i>, <b>, <u>, <c>, <lang>, <ruby>, <rt>, and timestamp tags into
    CaptionNode.STYLE open/close pairs, enabling correct round-trip
    through the WebVTT writer and cross-format conversion (e.g.,
    VTT italic → DFXP tts:fontStyle="italic").
  - WebVTT writer: add _convert_structural_tag() to emit class, lang,
    ruby, and timestamp tags from STYLE nodes. A has_text_style flag
    prevents double-emission when nodes already resolve to i/b/u tags.
  - Unrecognized angle-bracket content (e.g. <LAUGHING>) is now
    preserved as literal text instead of being silently dropped.
  - Auto-close unclosed inline tags at cue end per W3C spec,
    preventing unbalanced nodes that produce invalid output.

2.2.26
^^^^^^
  - Implement WebVTT REGION block parsing in the reader. Cues
    referencing a region now get proper origin/extent geometry
    computed via W3C TTML-WebVTT mapping formulas, enabling correct
    cross-format conversion (e.g., VTT with regions → DFXP produces
    correct tts:origin and tts:extent).
  - Fix .x/.y typo in geometry.py fit_to_screen() — the Y-axis
    safety guard was checking X twice instead of both axes.
  - Fix _remove_noop_off_on_italics typo in SCC specialized_collections.
  - Add empty-collection guard in _remove_spaces_at_end_of_the_line.
  - Replace magic numbers with named _InstructionNode constants.
  - Remove dead _remove_styles() method from WebVTT reader.
  - Remove redundant if-guard and unused class attributes in WebVTT writer.

2.2.25
^^^^^^
  - Add drop-frame timecode support to SCCWriter via a new
    ``drop_frame=False`` parameter. When enabled, timestamps use the
    standard 10-minute block method with semicolon separators.
  - Refactor SCCWriter timing pipeline: exact token counting,
    monotonic frame deduplication, and caption splitting at 80 tokens.
  - Extract ``SCC_TOKENS_PER_CAPTION_MAX`` as a named constant.
  - CI: guard coverage-parsing step on test success.

2.2.24
^^^^^^
  - Fix SCC ingestion error when a doubled italic-off mid-row code
    (9120 9120) appears before punctuation. The punctuation lookahead
    now skips the error-correction duplicate, preventing an unwanted
    space that pushed lines past the 32-character limit.


2.2.23
^^^^^^
  - bumps nltk from 3.9.1 to 3.9.4.
  - Fix SCC writer producing out-of-order timestamps when a short
    caption is immediately followed by a longer one.
    The buffer lead-time calculation could
    push a caption's start before its predecessor;
    now clamped to preserve chronological order.
  - Fix DFXPReader producing None entries in CaptionList when
    empty <p> elements yield zero parsed nodes, causing
    AttributeError in merge_concurrent_captions() and SRTWriter.

2.2.22
^^^^^^
  - Fix: EDM (Erase Displayed Memory) command now
    correctly clears displayed captions in paint-on
    and roll-up modes.

2.2.21
^^^^^^
  - supports multi-row jumps: small jumps (1-3 rows)
    emit the correct number of line breaks,
    large jumps (4+ rows) trigger repositioning instead
  - clear positioning state at caption boundaries
    (EOC, roll-up, paint-on, clear commands)
  - Code reformatted with Black/isort across the codebase
  - Added missing tests for _PositioningTracker,
    Alignment.from_horizontal_and_vertical_align
    - Bump actions/checkout from v2 to v4 in CI workflow
    - Replace unmaintained archive/github-actions-slack with
      slackapi/slack-github-action@v3.0.2 (fixes Node.js and
      set-output deprecation warnings)

2.2.20
^^^^^^
- update apache license and copyright year

2.2.19
^^^^^^
- Remove support for python 3.8 and 3.9.

2.2.18
^^^^^^
- Update changelog and new release tag.

2.2.17
^^^^^^
- Update nltk from 3.8.0 to 3.9.1.

2.2.16
^^^^^^
- Update copyright details.

2.2.15
^^^^^^
- Always skip doubled special characters, not just in case the cue starters are doubled.

2.2.14
^^^^^^
- Fix an issue with WebVTT writer text positioning on break inside a cue.
- Prevent creating a repositioning command to the same coordinates.

2.2.13
^^^^^^
- Mid-row codes only add spaces only if there isn't one before.
- Mid-row codes add spaces only if they affect the text in the same row (not adding if it follows break or PACS).
- Remove spaces to the end of the lines.
- Close italics on receiving another style setting command.
- Throw an CaptionReadNoCaptions error in case of an empty input file is provided.
- Ignore repositioning commands which are not followed by any text before breaks.
- Mid-row codes will not add the space if it is in front of punctuation.
- Fix a bug with background codes when the InstructionNodeCreator collection is empty.
- Fix a bug WebVTT writer adding double line breaks.

2.2.12
^^^^^^
- Pinned nltk to 3.8.0

2.2.11
^^^^^^
- A space should not be placed before a mid row code if it follows a PAC command or a Tab Offset
- The backspace command should be treated like other commands and duplicates should be skipped if PAC commands are duplicated
- Prevent webvtt writer from creating a new cue in case of line break
- In case of style setting PAC which also breaks the line, we add the break first, then the style tag

2.2.10
^^^^^
- Yanked.

2.2.9
^^^^^
- Yanked.

2.2.8
^^^^^
- Honor backspaces on captions in scc files
- When mid-row codes which are preceded by a PAC command don't add spaces
- Mid row codes which don't follow after a PAC and don't have a style reset command before will add a space to the end of the previous text node
- Mid row codes which don't follow after a PAC and have a style reset command before will add a space to the beginning of the next text node
- Background color codes to delete the space in front

2.2.7
^^^^^
- The cursor moves automatically one column to the right after each character or Mid-Row Code received.

2.2.6
^^^^^
- Pass the caption cue time with all error messages.

2.2.5
^^^^^
- Yanked.

2.2.4
^^^^^
- Skip duplicated extended characters.

2.2.3
^^^^^
- Add new substitute character to ignore before extended character in SCC input files

2.2.2
^^^^^
- Remove support for Python 3.6 & 3.7
- Restrict SCC source files to 31 characters per line (32 will throw an exception)
- Bump readthedocs-sphinx-search from 0.3.1 to 0.3.2
- Change Apache copyright licensing (ending) copyright year

2.2.1
^^^^^
- Ignore the substitute character that comes before the extended character in SCC files.

2.2.0
^^^^^
- Added support for Python 3.11
- Added support for Beautifulsoup 4.12.2
- Remove support for Beautifulsoup < 4.12.1
- DFXP captions now end consistently with a newline

2.1.1
^^^^^
- Added nltk as transcript dependency

2.1.0
^^^^^
- Remove upper limit for dependency versions to solve vulnerabilities

2.0.9
^^^^^
- Changed DFXPReader default horizontal alignment from 'center' to 'start'
- Updated WebVTT horizontal alignment from 'middle' to 'center'

2.0.8
^^^^^
- Added support for Python 3.10
- Added default start align to WebVTTWriter

2.0.7
^^^^^
- Implemented skipping duplicate special characters for SCCReader
- Added support for beautifulsoup 4.10 and lxml 4.8
- Added pytest and pytest-lazy-fixture as development dependencies

2.0.6
^^^^^
- Updated Size.from_string() to accept 0 size without measuring unit
- Replaced ValueError with CaptionReadSyntaxError for invalid sizes passed to Size.from_string()
- Updated DFXPReader timestamp validation according to TTML time expression specs
- Updated flashing cues validation for SCCReader to raise a CaptionReadTimingError
- Fixed SCC translator not recognising special and extended characters
- Raise CaptionReadTimingError for missing 'start' on SAMIReader

2.0.5
^^^^^
- Updated DFXPReader to ignore paragraphs that only contain spaces, tabs or new lines
- Added CaptionReadTimingError for invalid SCC timestamps
- Added CaptionReadSyntaxError for invalid colors in SAMIReader
- Raise CaptionReadTimingError when missing 'begin' or 'end' and 'dur' time on DFXPReader

2.0.4
^^^^^
- Updated the counting of frames to happen after processing SCC commands
- Made all SCC-sourced captions which have a difference of up to 5 frames between them more fluid

2.0.3
^^^^^
- Implemented time shift for WebVTTReader
- Removed WebVTTWriter 'start' position alignment
- Updated the SCC Pop-On caption timing logic
- Fixed the correction of end times for multiple last captions
- Fixed bug when flushing implicit buffers and old key was None

2.0.2
^^^^^
- Implemented Tab Offset commands for SCCReader
- Implemented caption safe area limits (80% horizontally and 90% vertically)
- Implemented SCC translator

2.0.1
^^^^^
- Added newline between merged SRT captions with overlapping timestamps
- Updated tests for SAMI format
- Updated tests for SRT format
- Added zero padding to 1-digit hours outputted by WebVTTWriter

2.0.0
^^^^^
- Dropped support for Python 3.5
- Updated tests to run using pytest
- Added pre-commit config

1.0.7
^^^^^
- Fixed issue with SCC paint-on buffer not being cleared after storing
- Removed null DFXPReader captions from the resulting caption list
- Updated SCCReader double command handling to include the positioning and tab offset case

1.0.6
^^^^^
- Added MicroDVD format
- Fix for missing end times when reading multiple SAMI paragraphs inside a SYNC
- Fix for wrong order when multiple SRT captions have the same timestamp
- Fix for DFXP timestamps adding leading zeros to 2-digit hours
- Added support for BeautifulSoup 4.9
- Added tests for SCC to DFXP conversion when the source contains ampersands
- Added support for Python 3.9

1.0.5
^^^^^
- Added language parameter to WebVTTWriter
- Fix for TranscriptWriter merging words at caption boundary
- Updated documentation with positioning information
- Updated DFXP reader to fallback to the document's language if no language is present on individual <div>
- Introduced PYCAPTION_DEFAULT_LANG environment variable and set it to default to 'und'
- Fixed DFXPReader timestamp validation to accept frames and frames conversion to microseconds

1.0.4
^^^^^
- Included tests in PyPI tarball
- Ignore WebVTT empty cues instead of raising an exception
- Updated BeautifulSoup version to >=4.8.1,<4.9 and fixed failing tests
- Handled index error when sending bad timestamp for DFXP format

1.0.3
^^^^^
- Fixed issue with SCC reader including both special characters and their potential substitute
- Modified enum34 dependency to versions under Python 3.4
- Removed Python 3.4 and added 3.6, 3.7 and 3.8 to Travis tests

1.0.2
^^^^^
- Fixed typos in SCC positioning codes
- Added missing SCC positioning codes to positioning map

1.0.0
^^^^^
- Added Python 3 support

0.5.x
^^^^^
- Added positioning support
- Created documentation
