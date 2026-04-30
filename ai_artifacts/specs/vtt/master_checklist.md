# WebVTT Master Checklist

Authoritative list of every rule ID, tag, setting, entity, region property, and enum value
that `analyze-vtt-docs` MUST produce in `vtt_specs_summary.md`.

A post-generation validation script reads this file and diffs it against the generated spec.
Any item listed here but missing from the spec is a FAIL.

---

## Required Rule IDs

### File Format (RULE-FMT)
- RULE-FMT-001  # "WEBVTT" header
- RULE-FMT-002  # UTF-8 encoding
- RULE-FMT-003  # Optional UTF-8 BOM
- RULE-FMT-004  # Blank line after header
- RULE-FMT-005  # Line terminators CR/LF/CRLF

### Timestamps (RULE-TIME)
- RULE-TIME-001  # Format [HH:]MM:SS.mmm
- RULE-TIME-002  # Hours optional if < 1h
- RULE-TIME-003  # Milliseconds exactly 3 digits
- RULE-TIME-004  # Minutes/seconds 0-59
- RULE-TIME-005  # Start time <= end time
- RULE-TIME-006  # Start times non-decreasing (SHOULD)
- RULE-TIME-007  # Internal timestamps within cue boundaries

### Cue Structure (RULE-CUE)
- RULE-CUE-001  # Timing separator ` --> `
- RULE-CUE-002  # Identifier must not contain "-->"
- RULE-CUE-003  # Identifier must not contain line terminators
- RULE-CUE-004  # Identifier should be unique
- RULE-CUE-005  # Blank line terminates cue
- RULE-CUE-006  # Payload must not contain "-->"

### Cue Settings (RULE-SET)
- RULE-SET-001  # vertical: rl | lr
- RULE-SET-002  # line: N | N%
- RULE-SET-003  # position: N%
- RULE-SET-004  # size: N%
- RULE-SET-005  # align: start|center|end|left|right
- RULE-SET-006  # region: id
- RULE-SET-007  # Each setting max once per cue
- RULE-SET-008  # Region excludes vertical/line/size

### Tags / Markup (RULE-TAG)
- RULE-TAG-001  # <c> class span
- RULE-TAG-002  # <i> italics
- RULE-TAG-003  # <b> bold
- RULE-TAG-004  # <u> underline
- RULE-TAG-005  # <v> voice/speaker
- RULE-TAG-006  # <lang> language
- RULE-TAG-007  # <ruby><rt> ruby text
- RULE-TAG-008  # <HH:MM:SS.mmm> internal timestamp
- RULE-TAG-009  # Tags support class notation
- RULE-TAG-010  # HTML character references permitted
- RULE-TAG-011  # Tags must be properly closed

### HTML Entities (RULE-ENT)
- RULE-ENT-001  # &amp;
- RULE-ENT-002  # &lt;
- RULE-ENT-003  # &gt;
- RULE-ENT-004  # &nbsp;
- RULE-ENT-005  # &lrm;
- RULE-ENT-006  # &rlm;
- RULE-ENT-007  # Numeric character references &#NNNN; / &#xHHHH;

### Regions (RULE-REG)
- RULE-REG-001  # REGION block definition
- RULE-REG-002  # id (required)
- RULE-REG-003  # width (percentage)
- RULE-REG-004  # lines (integer)
- RULE-REG-005  # regionanchor (x%,y%)
- RULE-REG-006  # viewportanchor (x%,y%)
- RULE-REG-007  # scroll (up)
- RULE-REG-008  # Each region setting max once
- RULE-REG-009  # Region identifiers unique

### Special Blocks (RULE-BLK)
- RULE-BLK-001  # NOTE blocks
- RULE-BLK-002  # STYLE blocks
- RULE-BLK-003  # STYLE must precede first cue
- RULE-BLK-004  # STYLE cannot contain "-->"

### Validation (RULE-VAL)
- RULE-VAL-001  # Keywords case-sensitive
- RULE-VAL-002  # Cue identifiers unique
- RULE-VAL-003  # Region identifiers unique
- RULE-VAL-004  # Timestamps ordered
- RULE-VAL-005  # Unicode must not be normalized
- RULE-VAL-006  # Authoring tools produce conforming files
- RULE-VAL-007  # Parsers should be tolerant

### Implementation (IMPL)
- IMPL-PARSE-001  # Decode UTF-8
- IMPL-PARSE-002  # Validate header
- IMPL-PARSE-003  # Parse timestamps
- IMPL-PARSE-004  # Validate cue timing
- IMPL-PARSE-005  # Handle cue settings
- IMPL-PARSE-006  # Parse tags
- IMPL-PARSE-007  # Handle HTML entities
- IMPL-PARSE-008  # Handle regions
- IMPL-WRITE-001  # Output valid UTF-8
- IMPL-WRITE-002  # Escape special chars
- IMPL-WRITE-003  # Format timestamps correctly
- IMPL-WRITE-004  # Use ` --> ` separator

---

## Required Tags (8 total)

Each must have its own rule AND appear in the spec with syntax/examples:

- `<c>` / `<c.class>`
- `<i>`
- `<b>`
- `<u>`
- `<v>`
- `<lang>`
- `<ruby>` / `<rt>`
- `<HH:MM:SS.mmm>` (internal timestamp)

---

## Required Cue Settings (6 total)

Each must have its own rule AND valid values documented:

- vertical: rl, lr
- line: N, N%, with optional alignment (start, center, end)
- position: N%, with optional alignment (line-left, center, line-right)
- size: N%
- align: start, center, end, left, right
- region: id

---

## Required HTML Entities (7 total)

- &amp;
- &lt;
- &gt;
- &nbsp;
- &lrm;
- &rlm;
- &#NNNN; / &#xHHHH; (numeric references)

---

## Required Region Properties (6 total)

- id
- width
- lines
- regionanchor
- viewportanchor
- scroll

---

## Required Enum Values

### align setting
- start
- center
- end
- left
- right

### vertical setting
- rl
- lr

### scroll setting
- up

### line alignment
- start
- center
- end

### position alignment
- line-left
- center
- line-right

---

## Required Severity Distribution

Minimum counts:
- MUST: 30
- SHOULD: 3
- MAY: 5
- MUST NOT: 3
