# SCC Format Web-Based Technical Reference

**Format:** Scenarist Closed Caption (SCC)  
**Purpose:** Comprehensive web-sourced specifications for SCC file format compliance

---

## 1. Format Overview

### 1.1 Description
SCC (Scenarist Closed Caption) is a text-based file format for storing CEA-608 Line 21 closed caption data. Originally developed by Sonic Solutions for their Scenarist DVD authoring system, it has become a widely-used industry standard for caption interchange.

### 1.2 Key Characteristics
- **Encoding:** ASCII text file
- **Extension:** `.scc`
- **Based on:** CEA-608 / EIA-608 standard
- **Data format:** Hexadecimal byte pairs
- **Use case:** Broadcast television, DVD authoring, online video

---

## 2. File Structure

### 2.1 File Header

**Required First Line:**
```
Scenarist_SCC V1.0
```

**Requirements:**
- Must be exact match (case-sensitive)
- Must be first line of file
- No variations allowed (e.g., "v1.0" or "V1.1" invalid)
- Blank line after header is optional but common

### 2.2 Caption Data Lines

**Format:**
```
HH:MM:SS:FF<separator>XXXX XXXX XXXX ...
```

**Components:**
- **Timecode:** When caption data should be processed
- **Separator:** TAB or SPACE character
- **Hex pairs:** 4-character hexadecimal pairs (2 bytes each)
- **Spacing:** Single space between hex pairs

### 2.3 Complete File Example

```scc
Scenarist_SCC V1.0

00:00:00:00	9420 9420 94ad 94ad 9470 9470 54c5 5354

00:00:03:00	942f 942f

00:00:05:15	9420 9420 9470 9470 4845 4c4c 4f21

00:00:08:00	942c 942c
```

---

## 3. Timecode Format

### 3.1 Non-Drop-Frame Timecode

**Format:** `HH:MM:SS:FF`

**Components:**
- `HH` - Hours (00-23)
- `MM` - Minutes (00-59)
- `SS` - Seconds (00-59)
- `FF` - Frames (00-29 for 30fps, 00-23 for 24fps)

**Separator:** Colon (`:`) between all components

**Example:** `01:23:45:12`

### 3.2 Drop-Frame Timecode

**Format:** `HH:MM:SS;FF`

**Difference:** Semicolon (`;`) before frame number

**Example:** `01:23:45;12`

**Purpose:** Compensates for 29.97fps NTSC frame rate

**Drop-Frame Rules:**
- Frames 0 and 1 are dropped at the start of each minute
- EXCEPT every 10th minute (00, 10, 20, 30, 40, 50)
- Keeps timecode aligned with actual clock time

### 3.3 Supported Frame Rates

| Frame Rate | Type | Timecode Format | Max Frame |
|------------|------|-----------------|-----------|
| 23.976 fps | Film | NDF | 23 |
| 24 fps | Film | NDF | 23 |
| 25 fps | PAL | NDF | 24 |
| 29.97 fps | NTSC | DF or NDF | 29 |
| 30 fps | NTSC | NDF | 29 |

### 3.4 Timecode Requirements

- **Monotonic:** Timecodes must increase (never go backwards)
- **No duplicates:** Each timecode should be unique
- **Frame accuracy:** Frame numbers must be valid for frame rate
- **Gaps allowed:** Time gaps between entries are acceptable

---

## 4. Hexadecimal Encoding

### 4.1 Byte Pair Format

Each control code or character is encoded as a 4-digit hexadecimal value representing 2 bytes.

**Format:** `XXYY` where:
- `XX` = First byte (hex)
- `YY` = Second byte (hex)

**Example:**
- `9420` = Byte 1: 0x94, Byte 2: 0x20 (RCL command)
- `4865` = Byte 1: 0x48 ('H'), Byte 2: 0x65 ('e')

### 4.2 Case Convention

Both uppercase and lowercase hex digits are valid:
- `9420` (uppercase - preferred)
- `9420` (lowercase - acceptable)

**Best Practice:** Use uppercase for consistency

### 4.3 Spacing and Separation

**Between hex pairs:** Single space
```
9420 9470 4865 6c6c 6f
```

**Not allowed:**
- No spaces: `94209470486c6c6f` ❌
- Multiple spaces: `9420  9470` ❌
- Other separators: `9420,9470` ❌

### 4.4 Control Code Doubling

**Convention:** Send control codes twice in succession for reliability

**Example:**
```
9420 9420    (RCL sent twice)
942f 942f    (EOC sent twice)
```

**Rationale:**
- Mimics transmission protocol of CEA-608
- Provides error resilience
- Some decoders require doubling
- Industry best practice

---

## 5. CEA-608 Control Codes

### 5.1 Caption Mode Commands

| Hex Code | Command | Mode | Description |
|----------|---------|------|-------------|
| 9420 | RCL | Pop-on | Resume Caption Loading - buffered captions |
| 9425 | RU2 | Roll-up | Roll-Up 2 rows - live scrolling |
| 9426 | RU3 | Roll-up | Roll-Up 3 rows - live scrolling |
| 9427 | RU4 | Roll-up | Roll-Up 4 rows - live scrolling |
| 9429 | RDC | Paint-on | Resume Direct Captioning - immediate display |

### 5.2 Display Control Commands

| Hex Code | Command | Function |
|----------|---------|----------|
| 942c | EDM | Erase Displayed Memory - clear screen |
| 942e | ENM | Erase Non-Displayed Memory - clear buffer |
| 942f | EOC | End Of Caption - display pop-on caption |

### 5.3 Cursor Control Commands

| Hex Code | Command | Function |
|----------|---------|----------|
| 9421 | BS | Backspace - move cursor left, delete char |
| 94ad | CR | Carriage Return - roll up one line |
| 9721 | TO1 | Tab Offset 1 - move cursor right 1 column |
| 9722 | TO2 | Tab Offset 2 - move cursor right 2 columns |
| 9723 | TO3 | Tab Offset 3 - move cursor right 3 columns |

### 5.4 Preamble Address Codes (PACs)

PACs set row position, column indent, and optionally text attributes.

**Structure:** Two bytes
- First byte: Determines row
- Second byte: Determines column indent and style

**Row Positioning Examples:**

| Hex Code | Row | Indent | Style |
|----------|-----|--------|-------|
| 9140 | 1 | 0 | White |
| 9141 | 1 | 4 | White |
| 91d0 | 2 | 0 | White |
| 9240 | 3 | 0 | White |
| 9470 | 11 | 0 | White |
| 1340 | 13 | 0 | White |
| 1640 | 14 | 0 | White |
| 9670 | 15 | 0 | White |

**Column Indents:**
- Indent 0: Column 1
- Indent 4: Column 5
- Indent 8: Column 9
- Indent 12: Column 13
- Indent 16: Column 17
- Indent 20: Column 21
- Indent 24: Column 25
- Indent 28: Column 29

**Fine Positioning:**
Use PAC for coarse positioning, then Tab Offset (TO1-TO3) for exact column.

### 5.5 Mid-Row Codes

Change text attributes mid-row (color, italics, underline).

**Format:** 91xx where xx determines attribute

**Effect:** Inserts space and applies attribute to following text

**Examples:**
- `912e` - Italics on
- `912f` - Italics off, white text

### 5.6 Field Selection

**Field 1 Commands:** 0x9xxx, 0x1xxx
- CC1 (primary)
- CC2 (secondary)

**Field 2 Commands:** 0x1xxx (different range)
- CC3
- CC4

---

## 6. Caption Modes

### 6.1 Pop-On Mode (Buffered)

**Description:** Captions built off-screen, displayed all at once

**Use Case:** Pre-produced content, precise timing control

**Command Sequence:**
```
1. 9420 9420    - RCL (select pop-on mode)
2. 94ae 94ae    - ENM (clear buffer, optional)
3. 9470 9470    - PAC (position row 11, column 1)
4. [text bytes] - Caption text
5. 942f 942f    - EOC (display caption)
```

**Example SCC:**
```
00:00:01:00	9420 9420 94ae 94ae 9470 9470 4845 4c4c 4f20 574f 524c 44
00:00:03:00	942f 942f
00:00:06:00	942c 942c
```

**Characteristics:**
- Most common mode for scripted content
- Captions "pop" onto screen instantly
- Allows 1-4 rows simultaneously
- Precise positioning control

### 6.2 Roll-Up Mode (Scrolling)

**Description:** Text scrolls up from bottom, typically 2-4 rows visible

**Use Case:** Live broadcasts, news, sports

**Command Sequence:**
```
1. 9425 9425    - RU2 (2-row roll-up mode)
   OR
   9426 9426    - RU3 (3-row roll-up mode)
   OR
   9427 9427    - RU4 (4-row roll-up mode)
2. 9670 9670    - PAC (set base row 15)
3. [text bytes] - Caption text
4. 94ad 94ad    - CR (carriage return - triggers roll)
```

**Example SCC:**
```
00:00:00:00	9425 9425 9670 9670 4c69 6e65 206f 6e65
00:00:02:00	94ad 94ad 4c69 6e65 2074 776f
00:00:04:00	94ad 94ad 4c69 6e65 2074 6872 6565
```

**Characteristics:**
- Base row = bottom row (typically 14 or 15)
- New text appears at base row
- Old text scrolls up
- Top row disappears when new line added
- Cursor stays at base row

**Roll-Up Variants:**
- **RU2:** 2 rows visible
- **RU3:** 3 rows visible
- **RU4:** 4 rows visible

### 6.3 Paint-On Mode (Real-Time)

**Description:** Characters appear immediately as received

**Use Case:** Character-by-character effects, corrections

**Command Sequence:**
```
1. 9429 9429    - RDC (select paint-on mode)
2. 9470 9470    - PAC (position)
3. [text bytes] - Appear immediately
```

**Example SCC:**
```
00:00:01:00	9429 9429 9470 9470 48
00:00:01:02	65
00:00:01:04	6c
00:00:01:06	6c
00:00:01:08	6f
```

**Characteristics:**
- No buffering - instant display
- Less commonly used
- Can combine with DER for selective erasure
- Useful for live corrections

---

## 7. Character Encoding

### 7.1 Basic ASCII Characters

Characters 0x20-0x7F map directly to ASCII:

| Hex | Char | Hex | Char | Hex | Char |
|-----|------|-----|------|-----|------|
| 20 | space | 41 | A | 61 | a |
| 21 | ! | 42 | B | 62 | b |
| 30 | 0 | 43 | C | 63 | c |
| 31 | 1 | 44 | D | 64 | d |

**Full ASCII Range:** Space through lowercase z

**Note:** Some codes have special meanings in CEA-608 context

### 7.2 Special Characters

Accessed via two-byte special character codes:

| Hex Code | Character | Description |
|----------|-----------|-------------|
| 1130 | ® | Registered mark |
| 1131 | ° | Degree sign |
| 1132 | ½ | One half |
| 1133 | ¿ | Inverted question |
| 1134 | ™ | Trademark |
| 1135 | ¢ | Cent sign |
| 1136 | £ | Pound sterling |
| 1137 | ♪ | Music note |
| 1138 | à | a with grave |
| 1139 | [space] | Transparent space |
| 113a | è | e with grave |
| 113b | â | a with circumflex |
| 113c | ê | e with circumflex |
| 113d | î | i with circumflex |
| 113e | ô | o with circumflex |
| 113f | û | u with circumflex |

### 7.3 Extended Characters

Accessed via two-byte extended character codes (language-specific):

**Spanish:**
- Á, É, Í, Ó, Ú (accented capitals)
- á, é, í, ó, ú (accented lowercase)
- ¡, Ñ, ñ, ü

**French:**
- À, È, Ì, Ò, Ù
- Ç, ç, ë, ï, ÿ

**German:**
- Ä, Ö, Ü
- ä, ö, ü, ß

**Portuguese:**
- Ã, õ, Õ
- Additional accented characters

### 7.4 Text Encoding in SCC

**Standard character example:**
```
"Hello" = 4865 6c6c 6f
```

Where:
- 48 = 'H'
- 65 = 'e'
- 6c = 'l'
- 6c = 'l'
- 6f = 'o'

**With spaces:**
```
"Hi there" = 4869 2074 6865 7265
```

Where:
- 20 = space

---

## 8. Screen Layout and Positioning

### 8.1 Caption Grid

**Dimensions:**
- **Rows:** 15 (numbered 1-15)
- **Columns:** 32 (numbered 1-32)

**Coordinate System:**
- Row 1 = Top
- Row 15 = Bottom
- Column 1 = Leftmost
- Column 32 = Rightmost

### 8.2 Safe Caption Area

**Recommended Bounds:**
- **Rows:** 2-14 (avoid row 1 and 15)
- **Columns:** 3-30 (avoid columns 1-2 and 31-32)

**Rationale:**
- Prevents caption cutoff on overscan displays
- Ensures readability across all display types
- Industry standard practice

### 8.3 Positioning Strategy

**Two-Step Positioning:**

1. **PAC (coarse):** Set row and column indent (0, 4, 8, 12, 16, 20, 24, 28)
2. **Tab Offset (fine):** Adjust +1, +2, or +3 columns

**Example - Position at Row 11, Column 10:**
```
9470 9470    PAC: Row 11, Indent 8 (Column 9)
9722 9722    TO2: Tab forward 2 columns (now at Column 11)
            (Actually lands at Column 11, close to target 10)
```

**Alternative - Use Indent 4:**
```
9471 9471    PAC: Row 11, Indent 4 (Column 5)
9723 9723    TO3: Tab forward 3 columns (Column 8)
9722 9722    TO2: Tab forward 2 more (Column 10)
```

---

## 9. Color and Styling

### 9.1 Text Colors

**Supported Foreground Colors:**
- White (default)
- Green
- Blue
- Cyan
- Red
- Yellow
- Magenta
- Black (with italics)

### 9.2 Background Colors

**Supported Background Colors:**
- Black (default)
- White
- Green
- Blue
- Cyan
- Red
- Yellow
- Magenta

### 9.3 Text Attributes

**Styles:**
- Normal (default)
- Italics
- Underline
- Flash (blinking - rarely supported)

### 9.4 Attribute Setting Methods

**Via PAC:** Set color/style when positioning
```
9170    Row 1, white text
9171    Row 1, white underline
9172    Row 1, green text
```

**Via Mid-Row Code:** Change attributes mid-text
```
4865 6c6c    "Hell"
912e         Italics on
6f21         "o!"
             Result: "Hell" in normal, "o!" in italics
```

**Via Background Attribute Code:** Set background color/transparency

---

## 10. Timing and Synchronization

### 10.1 Processing Time

**Data Rate:** 2 bytes per frame (in broadcast)

**SCC File:** All data at timecode is processed "instantly"

**Practical Limits:**
- Don't exceed 32 characters per row
- Allow minimum 1.5 seconds per caption for readability
- Consider reading speed: ~180 words/minute max

### 10.2 Caption Duration

**Not Explicit in SCC:** Duration determined by next erase command

**Example:**
```
00:00:01:00  [display caption]
00:00:04:00  [erase]
             Duration: 3 seconds
```

**Best Practices:**
- Minimum: 1.5 seconds
- Maximum: 6-7 seconds
- Longer for complex text

### 10.3 Timing Precision

**Frame Accuracy:** SCC provides frame-accurate timing

**Example at 29.97fps:**
- Frame 0 = 0.000 seconds
- Frame 15 = 0.500 seconds
- Frame 29 = 0.967 seconds

---

## 11. SCC File Validation

### 11.1 Required Elements

✓ Header line: `Scenarist_SCC V1.0`  
✓ Valid timecodes (monotonically increasing)  
✓ Hex pairs in valid format  
✓ Valid CEA-608 control codes  
✓ Proper command sequences for caption mode  

### 11.2 Common Errors

**❌ Invalid Header:**
```
Scenarist_SCC v1.0    (lowercase v)
SCC V1.0              (missing "Scenarist_")
```

**❌ Malformed Timecode:**
```
1:23:45:12            (missing leading zero)
01:23:45              (missing frame component)
01:23:60:00           (invalid seconds)
```

**❌ Invalid Hex:**
```
94G0                  (G is not hex)
942                   (incomplete pair)
9420:9470             (wrong separator)
```

**❌ Non-Monotonic:**
```
00:00:05:00
00:00:03:00           (goes backwards)
```

### 11.3 Validation Checklist

- [ ] Header present and correct
- [ ] All timecodes properly formatted
- [ ] Timecodes in ascending order
- [ ] All hex pairs are 4 characters
- [ ] Only valid hex digits (0-9, A-F)
- [ ] Control codes properly doubled
- [ ] Valid command sequences for mode
- [ ] Characters within 0x20-0x7F range (or valid special/extended)
- [ ] Row positions 1-15
- [ ] No orphaned text (text without mode/position commands)

---

## 12. Advanced Features

### 12.1 Multi-Channel Support

SCC can contain data for multiple caption channels:

**CC1:** Primary captions (most common)  
**CC2:** Secondary language or service  
**CC3:** Additional service (Field 2)  
**CC4:** Additional service (Field 2)  

**Implementation:** Use appropriate control codes for each channel

**Example:**
```
00:00:01:00  9420 9420 ...    (CC1 data)
00:00:01:00  1C20 1C20 ...    (CC3 data - Field 2)
```

### 12.2 XDS Data

SCC files can contain XDS (eXtended Data Services) packets in Field 2:
- Program metadata
- V-chip ratings
- Network identification
- Time of day

**Format:** Special packet structure starting with 0x01-0x0F class codes

### 12.3 Empty Frames

**Padding:** `8080 8080` or omit line entirely

**Purpose:**
- Maintain timing in broadcast transmission
- Not typically needed in file format

---

## 13. Best Practices

### 13.1 File Creation

1. Always include proper header
2. Use drop-frame timecode for 29.97fps content
3. Double all control codes
4. Use uppercase hex (consistency)
5. Add blank line after header (readability)
6. Group related commands on same timecode line

### 13.2 Caption Content

1. Keep lines within safe area (rows 2-14, cols 3-30)
2. Maximum 32 characters per row
3. Aim for 2 rows max per caption (readability)
4. Leave captions on screen 1.5-6 seconds
5. Break lines at logical points (grammar, breath)

### 13.3 Accessibility

1. Caption all speech and significant sounds
2. Identify speakers when not obvious
3. Use `[brackets]` for sound effects
4. Use `♪` for music
5. Maintain reading speed ~180 wpm
6. Use proper punctuation and capitalization

### 13.4 Technical Quality

1. Test in actual decoder/player
2. Verify timecode synchronization
3. Check for positioning errors
4. Validate hex encoding
5. Confirm control code sequences
6. Test on different screen sizes

---

## 14. Tool Support

### 14.1 Libraries and Parsers

**Python:**
- pycaption (this library)
- caption-converter
- aeidon

**JavaScript:**
- caption.js
- video.js plugins

**C/C++:**
- libcaption
- CCExtractor

### 14.2 Commercial Tools

- Adobe Premiere Pro
- Avid Media Composer
- Apple Compressor
- Sonic Scenarist
- Various web-based caption editors

### 14.3 Validation Tools

- Caption validators (online)
- Broadcast compliance checkers
- FCC validation tools
- Platform-specific validators (YouTube, etc.)

---

## 15. Compliance Standards

### 15.1 FCC Requirements (USA)

- 47 CFR §79.1 - Closed captioning of television programs
- Quality standards for accuracy, synchronization, completeness
- Technical standards per CEA-608/CEA-708

### 15.2 Industry Standards

**CEA-608:** Line 21 closed captioning standard  
**CEA-708:** Digital television closed captioning  
**SMPTE:** Various broadcast standards  
**DVD Standards:** Closed caption requirements for DVD media  

### 15.3 International

**PAL Regions:** 25fps timing  
**Multi-language:** Use different channels (CC2, CC3, CC4)  
**Regional Variations:** Character set support for local languages  

---

## 16. Troubleshooting

### 16.1 Captions Don't Appear

**Check:**
- Header line correct?
- Control codes doubled?
- EOC command sent (for pop-on)?
- Proper mode command (RCL/RU2/RU3/RU4/RDC)?
- Valid PAC before text?
- Timecodes in correct format?

### 16.2 Positioning Issues

**Check:**
- PAC values correct for desired row?
- Column indent appropriate?
- Tab offsets applied correctly?
- Not exceeding 32 columns?
- Not using invalid rows (0 or >15)?

### 16.3 Character Display Issues

**Check:**
- Hex encoding correct?
- Special characters using two-byte codes?
- Extended characters properly encoded?
- Character codes in valid range?

### 16.4 Timing Problems

**Check:**
- Frame rate matches content?
- Drop-frame vs non-drop-frame correct?
- Frame numbers valid for frame rate?
- Timecodes monotonically increasing?

---

## 17. Format Limitations

### 17.1 What SCC Cannot Do

- **Rich formatting:** No fonts, sizes, or advanced styling
- **Positioning precision:** Limited to 32x15 grid
- **Unicode:** Only basic ASCII + extended character sets
- **Multiple simultaneous windows:** Limited compared to CEA-708
- **Karaoke-style highlighting:** Not supported
- **Emoji:** Not in character set
- **Complex languages:** Limited support for non-Latin scripts

### 17.2 When to Use Alternatives

**Use WebVTT for:**
- Web-based video
- Rich styling needs
- Modern players
- UTF-8 character support

**Use CEA-708 for:**
- Digital broadcast
- Multiple service streams
- Advanced positioning
- HD/4K content

**Use SRT for:**
- Simple subtitle files
- Maximum compatibility
- Basic timing needs

---

## Sources

This document compiled from:

1. **Technical Specifications:**
   - CEA-608 standard (ANSI/CTA-608-E)
   - EIA-608 specifications
   - Scenarist format documentation

2. **Implementation References:**
   - libcaption (GitHub: szatmary/libcaption)
   - CCExtractor documentation
   - pycaption library specifications

3. **Web Resources Attempted:**
   - http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/ (unavailable)
   - Various closed captioning technical documentation sites
   - Broadcast standards organizations

4. **Industry Knowledge:**
   - DVD authoring specifications
   - Broadcast captioning standards
   - Professional captioning workflows
   - FCC regulations and compliance requirements

**Note:** Many historical web resources for SCC format (particularly mcpoodle SCC_TOOLS documentation) are no longer accessible. This document represents best-practice specifications compiled from available standards documentation and implementation references.

---

**Document Version:** 1.0  
**Last Updated:** 2026-04-17  
**Format:** Markdown for compliance checking tools
