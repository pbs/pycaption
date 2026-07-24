Supported formats
==================

Read: - DFXP/TTML - SAMI - SCC - SRT - WebVTT - MicroDVD

Write: - DFXP/TTML - SAMI - SCC - SRT - Transcript - WebVTT - MicroDVD

See the `examples
folder <https://github.com/pbs/pycaption/tree/master/examples/>`__ for
example captions that currently can be read correctly.

SAMI Reader / Writer :: `spec <http://msdn.microsoft.com/en-us/library/ms971327.aspx>`__
----------------------------------------------------------------------------------------

Microsoft Synchronized Accessible Media Interchange. Supports multiple
languages.

Supported Styling: - text-align - italics - font-size - font-family -
color - background-color

If the SAMI file is not valid XML (e.g. unclosed tags), will still
attempt to read it.

The writer emits ``class=`` attributes for WebVTT class spans and produces
valid CSS stylesheet rules for VTT class styles. Non-CSS keys
(webvtt_positioning, writing_direction) are filtered from output.

DFXP/TTML Reader / Writer :: `spec <http://www.w3.org/TR/ttaf1-dfxp/>`__
-------------------------------------------------------------------

The W3 standard. Supports multiple languages.

Supported Styling: - text-align - display-align - italics - font-size -
font-family - color - background-color - writing direction

The reader supports TTML tick time expressions (``Nt``), dynamic frame
rates via ``ttp:frameRate`` and ``ttp:frameRateMultiplier``, and uses a
regex-based ``detect()`` to avoid false positives on non-TTML content.

The writer emits ``tts:writingMode`` on regions for vertical text
(vertical:rl → tbrl, vertical:lr → tblr) and supports nested ``<span>``
elements for inline styles.

SRT Reader / Writer :: `spec <http://matroska.org/technical/specs/subtitles/srt.html>`__
----------------------------------------------------------------------------------------

SubRip captions. If given multiple languages to write, will output all
joined together by a 'MULTI-LANGUAGE SRT' line.

Supported Styling: - None

Assumes input language is english. To change:

::

    pycaps = SRTReader().read(srt_content, lang='fr')

WebVTT Reader / Writer :: `spec <https://www.w3.org/TR/webvtt1/>`__
-----------------------------------------------------------------

**WebVTT** is a W3C standard for displaying timed text in HTML5.

By default, the reader assumes the language is English and the writer
returns the first language it finds in the caption set. You can specify
a language using the ``lang`` parameter:

::

    pycaps = WebVTTReader().read(content, lang='fr')

If you need to adjust all timestamps in a WebVTT, you can use the
``time_shift_milliseconds`` parameter which moves the timestamps
forward (positive integer) or backward (negative integer) with
the specified amount:

::

    pycaps = WebVTTReader(time_shift_milliseconds=1154).read(content)

Styling
^^^^^^^

The reader parses all inline markup tags (``<b>``, ``<i>``, ``<u>``, ``<c>``,
``<lang>``, ``<ruby>``, ``<rt>``, and timestamp tags) into structured
``CaptionNode.STYLE`` open/close pairs, preserving styling information for
cross-format conversion (e.g. VTT italic → DFXP ``tts:fontStyle="italic"``).

STYLE blocks are parsed and ``::cue`` / ``::cue(.class)`` rules are resolved
onto spans with correct cascade (base ``::cue`` < class-specific). Supported
CSS properties: ``font-style``, ``font-weight``, ``text-decoration``, ``color``,
``background-color``.

Voice tags are converted to text prefixes:

::

    <v Fred>Hi, my name is Fred

is converted to

::

    Fred: Hi, my name is Fred

Unrecognized angle-bracket content (e.g. ``<LAUGHING>``) is preserved as
literal text. Unclosed inline tags are auto-closed at cue boundaries per
the W3C spec.

Positioning
^^^^^^^^^^^

The reader parses all cue settings into structured ``Layout`` objects:

-  ``line`` — percentage or integer line numbers (converted to viewport %)
-  ``position`` — horizontal cue position
-  ``size`` — cue box width
-  ``align`` — text alignment (start, center, end, left, right)
-  ``vertical`` — writing direction (rl, lr)
-  ``region`` — reference to a REGION block

REGION blocks are fully parsed with support for ``width``, ``lines``,
``regionanchor``, ``viewportanchor``, and ``scroll``. Region positioning is
computed using W3C TTML-WebVTT mapping formulas and preserved through
roundtrip conversion.

The writer re-emits STYLE blocks, REGION blocks, and all cue settings on
VTT→VTT roundtrip.

Refer to the `official WebVTT specification`_ for details about the cue
settings.

.. _official WebVTT specification: https://www.w3.org/TR/webvtt1/#webvtt-cue-settings

SCC Reader / Writer :: `spec <http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/SCC_FORMAT.HTML>`__
--------------------------------------------------------------------------------------------------------

Scenarist Closed Caption format. Assumes Channel 1 input.

Supported Styling: - italics - underline

**Reader**

By default, the SCC Reader does not simulate roll-up captions. To enable
roll-ups:

::

    pycaps = SCCReader().read(scc_content, simulate_roll_up=True)

Also, assumes input language is english. To change:

::

    pycaps = SCCReader().read(scc_content, lang='fr')

Now has the option of specifying an offset (measured in seconds) for the
timestamp. For example, if the SCC file is 45 seconds ahead of the
video:

::

    pycaps = SCCReader().read(scc_content, offset=45)

The SCC Reader handles both dropframe and non-dropframe captions, and
will auto-detect which format the captions are in.

For debugging purposes, the SCC captions can be translated into a human readable
form as following:

::

    translated_scc = translate_scc(scc_content, brackets="[]")

Square brackets are used by default, but they can be replaced with other
brackets or None.

**Writer**

The SCC Writer converts CaptionSet objects to CEA-608 format, supporting
pop-on, roll-up, and paint-on caption modes. It maps positioning from
Layout objects to PAC codes (line:% → rows, align → column indents + tab
offsets) and styling to mid-row codes (italics, underline). Unsupported
styles are silently dropped.

::

    output = SCCWriter().write(caption_set)
    output = SCCWriter(drop_frame=True).write(caption_set)

MicroDVD Reader / Writer
------------------------

MicroDVD frame-based subtitle format.

Supported Styling: - None

Transcript Writer
-----------------

Text stripped of styling, arranged in sentences.

Supported Styling: - None

The transcript writer uses natural sentence boundary detection
algorithms to create the transcript.
