py-caption
==========

|Build Status| |Pre-Commit|

``pycaption`` is a caption reading/writing module. Use one of the given Readers
to read content into a CaptionSet object, and then use one of the Writers to
output the CaptionSet into captions of your desired format.

Tested with Python versions 3.6, 3.7, 3.8 and 3.9.
(for Python 2 use pycaption < 1.0.0)

For details, see the `documentation <http://pycaption.readthedocs.org>`__.

Changelog
---------
Unreleased
^^^^^^^^^^
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

License
-------

This module is Copyright 2012 PBS.org and is available under the `Apache
License, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0>`__.

.. |Build Status| image:: https://travis-ci.org/pbs/pycaption.png?branch=master
   :target: https://travis-ci.org/pbs/pycaption

.. |Pre-Commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
