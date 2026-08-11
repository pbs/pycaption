# DFXP/TTML Master Checklist

Authoritative list of every rule ID, element, attribute, enum value, and coverage item
that `analyze-dfxp-docs` MUST produce in `dfxp_specs_summary.md`.

A post-generation validation script reads this file and diffs it against the generated spec.
Any item listed here but missing from the spec is a FAIL.

---

## Required Rule IDs

### Document Structure (RULE-DOC)
- RULE-DOC-001  # Root `tt` in TT namespace
- RULE-DOC-002  # Well-formed XML
- RULE-DOC-003  # xml:lang on tt element
- RULE-DOC-004  # Required namespaces declared
- RULE-DOC-005  # tt > head? > body? ordering
- RULE-DOC-006  # head child ordering
- RULE-DOC-007  # Media type application/ttml+xml
- RULE-DOC-008  # XML declaration UTF-8

### Timing (RULE-TIME)
- RULE-TIME-001  # Clock-time fractional HH:MM:SS.sss
- RULE-TIME-002  # Clock-time frames HH:MM:SS:FF
- RULE-TIME-003  # Offset hours Nh
- RULE-TIME-004  # Offset minutes Nm
- RULE-TIME-005  # Offset seconds Ns
- RULE-TIME-006  # Offset milliseconds Nms
- RULE-TIME-007  # Offset frames Nf
- RULE-TIME-008  # Offset ticks Nt
- RULE-TIME-009  # begin attribute
- RULE-TIME-010  # end attribute
- RULE-TIME-011  # dur attribute
- RULE-TIME-012  # Default timeContainer par
- RULE-TIME-013  # Time containment
- RULE-TIME-014  # Frame timing requires ttp:frameRate

### Content Elements (RULE-CONT)
- RULE-CONT-001  # body
- RULE-CONT-002  # div
- RULE-CONT-003  # p
- RULE-CONT-004  # span
- RULE-CONT-005  # br
- RULE-CONT-006  # set
- RULE-CONT-007  # Anonymous spans
- RULE-CONT-008  # div nesting

### Styling Attributes (RULE-STY)
- RULE-STY-001  # tts:color
- RULE-STY-002  # tts:backgroundColor
- RULE-STY-003  # tts:fontSize
- RULE-STY-004  # tts:fontFamily
- RULE-STY-005  # tts:fontStyle
- RULE-STY-006  # tts:fontWeight
- RULE-STY-007  # tts:textAlign
- RULE-STY-008  # tts:textDecoration
- RULE-STY-009  # tts:direction
- RULE-STY-010  # tts:writingMode
- RULE-STY-011  # tts:display
- RULE-STY-012  # tts:displayAlign
- RULE-STY-013  # tts:lineHeight
- RULE-STY-014  # tts:opacity
- RULE-STY-015  # tts:textOutline
- RULE-STY-016  # tts:padding
- RULE-STY-017  # tts:extent
- RULE-STY-018  # tts:origin
- RULE-STY-019  # tts:overflow
- RULE-STY-020  # tts:showBackground
- RULE-STY-021  # tts:visibility
- RULE-STY-022  # tts:wrapOption
- RULE-STY-023  # tts:unicodeBidi
- RULE-STY-024  # tts:zIndex
- RULE-STY-025  # Named colors enumeration
- RULE-STY-026  # Color expression formats
- RULE-STY-027  # Length expression units

### Styling Model (RULE-SMOD)
- RULE-SMOD-001  # styling element
- RULE-SMOD-002  # style element
- RULE-SMOD-003  # Style referencing via style attribute
- RULE-SMOD-004  # Inheritance: specified > inherited > initial
- RULE-SMOD-005  # Style chaining
- RULE-SMOD-006  # Inline styling via tts:* attributes
- RULE-SMOD-007  # Style association from region

### Layout / Regions (RULE-LAY)
- RULE-LAY-001  # layout element
- RULE-LAY-002  # region element
- RULE-LAY-003  # Content association via region attribute
- RULE-LAY-004  # Default region
- RULE-LAY-005  # Region tts:origin positioning
- RULE-LAY-006  # Region tts:extent dimensions
- RULE-LAY-007  # Region stacking / z-ordering

### Metadata (RULE-META)
- RULE-META-001  # ttm:title
- RULE-META-002  # ttm:desc
- RULE-META-003  # ttm:copyright
- RULE-META-004  # ttm:agent
- RULE-META-005  # ttm:actor
- RULE-META-006  # ttm:role attribute

### Parameters (RULE-PAR)
- RULE-PAR-001  # ttp:timeBase
- RULE-PAR-002  # ttp:frameRate
- RULE-PAR-003  # ttp:subFrameRate
- RULE-PAR-004  # ttp:frameRateMultiplier
- RULE-PAR-005  # ttp:tickRate
- RULE-PAR-006  # ttp:dropMode
- RULE-PAR-007  # ttp:clockMode
- RULE-PAR-008  # ttp:markerMode
- RULE-PAR-009  # ttp:cellResolution
- RULE-PAR-010  # ttp:pixelAspectRatio
- RULE-PAR-011  # ttp:profile

### Profiles (RULE-PROF)
- RULE-PROF-001  # Transformation profile
- RULE-PROF-002  # Presentation profile
- RULE-PROF-003  # Full profile
- RULE-PROF-004  # Profile element vs attribute precedence
- RULE-PROF-005  # Feature designations

### Validation (RULE-VAL)
- RULE-VAL-001  # Valid Reduced XML Infoset
- RULE-VAL-002  # cellResolution not zero
- RULE-VAL-003  # IDREF resolves to existing ID
- RULE-VAL-004  # Frame values < frame rate
- RULE-VAL-005  # Minutes/seconds 00-59
- RULE-VAL-006  # xml:lang valid BCP 47
- RULE-VAL-007  # Percentage values in range
- RULE-VAL-008  # Unknown TT namespace elements forbidden

### Implementation (IMPL)
- IMPL-001  # XML parser handles TT namespaces
- IMPL-002  # Time expression parser all formats
- IMPL-003  # Style resolver cascade
- IMPL-004  # Region resolver
- IMPL-005  # Writer valid XML + namespaces
- IMPL-006  # Parser time containment
- IMPL-007  # Color parser all formats
- IMPL-008  # Writer escapes XML
- IMPL-009  # Parser dur/end interaction
- IMPL-010  # Writer length expressions
- IMPL-011  # Parser style chaining no cycles
- IMPL-012  # Processor profile features
- IMPL-013  # Writer correct timing
- IMPL-014  # Processor must not reject conformant docs

---

## Required Styling Attributes (24 total)

Each must have its own rule with valid values, defaults, inheritance, and applies-to:

- tts:color
- tts:backgroundColor
- tts:fontSize
- tts:fontFamily
- tts:fontStyle
- tts:fontWeight
- tts:textAlign
- tts:textDecoration
- tts:direction
- tts:writingMode
- tts:display
- tts:displayAlign
- tts:lineHeight
- tts:opacity
- tts:textOutline
- tts:padding
- tts:extent
- tts:origin
- tts:overflow
- tts:showBackground
- tts:visibility
- tts:wrapOption
- tts:unicodeBidi
- tts:zIndex

---

## Required Content Elements (6 core + 2 structural)

- body
- div
- p
- span
- br
- set
- anonymous spans (text nodes)
- div nesting

---

## Required Time Expression Formats (8 total)

- Clock-time fractional: HH:MM:SS.sss
- Clock-time frames: HH:MM:SS:FF
- Offset hours: Nh
- Offset minutes: Nm
- Offset seconds: Ns
- Offset milliseconds: Nms
- Offset frames: Nf
- Offset ticks: Nt

---

## Required Parameter Attributes (11 total)

- ttp:timeBase
- ttp:frameRate
- ttp:subFrameRate
- ttp:frameRateMultiplier
- ttp:tickRate
- ttp:dropMode
- ttp:clockMode
- ttp:markerMode
- ttp:cellResolution
- ttp:pixelAspectRatio
- ttp:profile

---

## Required Metadata Elements (5 + 1 attribute)

- ttm:title
- ttm:desc
- ttm:copyright
- ttm:agent
- ttm:actor
- ttm:role (attribute)

---

## Required Enum Values

### tts:fontStyle
- normal
- italic
- oblique

### tts:fontWeight
- normal
- bold

### tts:textAlign
- left
- center
- right
- start
- end

### tts:direction
- ltr
- rtl

### tts:writingMode
- lrtb
- rltb
- tbrl
- tblr
- lr
- rl
- tb

### tts:display
- auto
- none

### tts:displayAlign
- before
- center
- after

### tts:overflow
- visible
- hidden

### tts:showBackground
- always
- whenActive

### tts:visibility
- visible
- hidden

### tts:wrapOption
- wrap
- noWrap

### tts:unicodeBidi
- normal
- embed
- bidiOverride

### tts:textDecoration
- none
- underline
- noUnderline
- overline
- noOverline
- lineThrough
- noLineThrough

### ttp:timeBase
- media
- smpte
- clock

### ttp:dropMode
- dropNTSC
- dropPAL
- nonDrop

### ttp:clockMode
- local
- gps
- utc

### ttp:markerMode
- continuous
- discontinuous

### ttp:timeContainer
- par
- seq

### Named Colors (19 total)
- transparent
- black
- silver
- gray
- white
- maroon
- red
- purple
- fuchsia
- magenta
- green
- lime
- olive
- yellow
- navy
- blue
- teal
- aqua
- cyan

### Color Formats
- #RRGGBB
- #RRGGBBAA
- rgb(R,G,B)
- rgba(R,G,B,A)
- named-color

### Generic Font Families (8 total)
- default
- monospace
- monospaceSansSerif
- monospaceSerif
- proportionalSansSerif
- proportionalSerif
- sansSerif
- serif

### Length Units (4 total)
- px
- em
- c
- %

---

## Required Severity Distribution

Minimum counts:
- MUST: 40
- SHOULD: 3
- MAY: 5
- MUST NOT: 1
