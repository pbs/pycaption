Changelog
---------
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
