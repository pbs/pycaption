Supported formats
==================

Read: - DFXP/TTML - SAMI - SCC - SRT - WebVTT

Write: - DFXP/TTML - SAMI - SRT - Transcript - WebVTT

See the `examples
folder <https://github.com/pbs/pycaption/tree/master/examples/>`__ for
example captions that currently can be read correctly.

SAMI Reader / Writer :: `spec <http://msdn.microsoft.com/en-us/library/ms971327.aspx>`__
----------------------------------------------------------------------------------------

Microsoft Synchronized Accessible Media Interchange. Supports multiple
languages.

Supported Styling: - text-align - italics - font-size - font-family -
color

If the SAMI file is not valid XML (e.g. unclosed tags), will still
attempt to read it.

DFXP/TTML Reader / Writer :: `spec <http://www.w3.org/TR/ttaf1-dfxp/>`__
-------------------------------------------------------------------

The W3 standard. Supports multiple languages.

Supported Styling: - text-align - italics - font-size - font-family -
color

SRT Reader / Writer :: `spec <http://matroska.org/technical/specs/subtitles/srt.html>`__
----------------------------------------------------------------------------------------

SubRip captions. If given multiple languages to write, will output all
joined together by a 'MULTI-LANGUAGE SRT' line.

Supported Styling: - None

Assumes input language is english. To change:

::

    pycaps = SRTReader().read(srt_content, lang='fr')

WebVTT Reader / Writer :: `spec <http://dev.w3.org/html5/webvtt/>`__
-----------------------------------------------------------------

**WebVTT** is a W3C standard for displaying timed text in HTML5. Its
specification is currently (as of February 2015) in draft stage and
therefore not all features are implemented by major players, the same
being true for ``pycaption``.

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

Styling in WebVTT can be done via inline tags (e.g. ``<b>``, ``<i>`` etc.) or external
CSS rules applied to text wrapped in class (``<c>``) or voice (``<v>``) tags.

``pycaption`` currently only keeps *voice tags* on conversion.

Example:

::

    <v Fred>Hi, my name is Fred

is converted to

::

    Fred: Hi, my name is Fred

The following WebVTT supported tags are stripped off the cue text:

    - ``<c>``, ``<i>``, ``<b>``, ``<u>``, ``<ruby>``, ``<rt>``, ``<lang>`` and timestamp tags (``<h:mm:ss.sss>``)

Non-supported tags are left unchanged as a natural part of the cue text with no
special meaning.

Positioning
^^^^^^^^^^^

The WebVTT specs allow customizing the position of cues by configuring a
number of cue settings. ``pycaption`` currently only *maintains positioning
information on writing*, in which case it supports the following settings:

-  A WebVTT line position cue setting.
-  A WebVTT text position cue setting.
-  A WebVTT size cue setting.
-  A WebVTT alignment cue setting.

``pycaption`` **does not** support:

-  A WebVTT vertical text cue setting.
-  A WebVTT region cue setting.

Refer to the `official WebVTT specification`_ for details about the cue
settings.

.. _official WebVTT specification: http://dev.w3.org/html5/webvtt/#webvtt-cue-settings

SCC Reader :: `spec <http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/SCC_FORMAT.HTML>`__
-----------------------------------------------------------------------------------------------

Scenarist Closed Caption format. Assumes Channel 1 input.

Supported Styling: - italics

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

Transcript Writer
-----------------

Text stripped of styling, arranged in sentences.

Supported Styling: - None

The transcript writer uses natural sentence boundary detection
algorithms to create the transcript.
