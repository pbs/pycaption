# SCC Master Checklist

Authoritative list of every rule ID, control code category, enum value, and coverage item
that `analyze-scc-docs` MUST produce in `scc_specs_summary.md`.

A post-generation validation script reads this file and diffs it against the generated spec.
Any item listed here but missing from the spec is a FAIL.

---

## Required Rule IDs

### File Format (RULE-FMT)
- RULE-FMT-001  # Header "Scenarist_SCC V1.0"

### Timecode (RULE-TMC)
- RULE-TMC-001  # HH:MM:SS:FF / HH:MM:SS;FF format
- RULE-TMC-002  # Frame number valid for frame rate
- RULE-TMC-003  # Monotonically increasing timecodes
- RULE-TMC-004  # Drop-frame skips frames 0,1

### Hex Data (RULE-HEX)
- RULE-HEX-001  # 4-digit hex pairs
- RULE-HEX-002  # Space-separated pairs
- RULE-HEX-003  # Control code doubling

### Character Sets (RULE-CHAR)
- RULE-CHAR-001  # Standard ASCII mapping
- RULE-CHAR-002  # Special characters (two-byte)
- RULE-CHAR-003  # Extended character languages

### Pop-On (RULE-POPON)
- RULE-POPON-001  # RCL -> PAC -> text -> EOC

### Roll-Up (RULE-ROLLUP)
- RULE-ROLLUP-001  # RU2/3/4 -> PAC -> text -> CR
- RULE-ROLLUP-002  # Base row accommodates depth

### Paint-On (RULE-PAINTON)
- RULE-PAINTON-001  # RDC -> PAC -> text

### Layout (RULE-LAY)
- RULE-LAY-001  # 15 rows x 32 columns
- RULE-LAY-002  # Max 32 characters per row
- RULE-LAY-003  # Max 15 visible rows

### PAC Positioning (RULE-PAC)
- RULE-PAC-001  # Valid row 1-15
- RULE-PAC-002  # Indent 0,4,8,12,16,20,24,28

### Tab Offsets (RULE-TAB)
- RULE-TAB-001  # TO1/TO2/TO3 fine positioning

### Frame Rates (RULE-FPS)
- RULE-FPS-001  # 23.976 fps
- RULE-FPS-002  # 24 fps
- RULE-FPS-003  # 25 fps
- RULE-FPS-004  # 29.97 fps NDF
- RULE-FPS-005  # 29.97 fps DF
- RULE-FPS-006  # 30 fps

### Byte Encoding (RULE-ENC)
- RULE-ENC-001  # Odd parity (N/A for SCC text)
- RULE-ENC-002  # Bit 7 must be 0

### Mid-Row Codes (RULE-MID)
- RULE-MID-001  # Mid-row style changes

### Color (RULE-COLOR)
- RULE-COLOR-001  # 8 foreground colors
- RULE-COLOR-002  # Background colors

### XDS (RULE-XDS)
- RULE-XDS-001  # XDS packets on Field 2

### Implementation (IMPL)
- IMPL-FMT-001    # Parser validates header
- IMPL-TMC-001    # Parser validates timecode
- IMPL-TMC-003    # Parser verifies monotonic
- IMPL-HEX-003    # Control code doubling (parser/writer)
- IMPL-POPON-001  # Parser recognizes pop-on
- IMPL-ROLLUP-001 # Parser enforces base row
- IMPL-PAINTON-001 # Parser paint-on immediate display
- IMPL-FPS-001    # Parser detects frame rate
- IMPL-ENC-001    # Parser MAY skip parity

---

## Required Control Code Categories

Each category must have its codes enumerated in the spec.

- CTRL-001 through CTRL-019  # 19 miscellaneous control codes
- PAC codes                   # 480+ preamble address codes
- MID-row codes               # 64 mid-row codes
- Special characters          # 32 special character codes
- Extended characters         # 128 extended character codes
- XDS codes                   # 15 XDS control codes

### Required Miscellaneous Control Codes (by hex value)
- 9420  # RCL
- 9421  # BS
- 9422  # AOF
- 9423  # AON
- 9424  # DER
- 9425  # RU2
- 9426  # RU3
- 9427  # RU4
- 9428  # FON
- 9429  # RDC
- 942a  # TR
- 942b  # RTD
- 942c  # EDM
- 94ad  # CR
- 942e  # ENM
- 942f  # EOC
- 1721  # TO1
- 1722  # TO2
- 1723  # TO3

---

## Required Enum Values

### Caption Modes
- Pop-on
- Roll-up
- Paint-on

### Frame Rates
- 23.976
- 24
- 25
- 29.97 DF
- 29.97 NDF
- 30

### Foreground Colors
- White
- Green
- Blue
- Cyan
- Red
- Yellow
- Magenta
- Black

### PAC Indent Positions
- 0
- 4
- 8
- 12
- 16
- 20
- 24
- 28

### Roll-Up Depths
- RU2
- RU3
- RU4

---

## Required Severity Distribution

Minimum counts (the spec may exceed these):
- MUST: 25
- SHOULD: 3
- MAY: 1
- MUST NOT: 1
