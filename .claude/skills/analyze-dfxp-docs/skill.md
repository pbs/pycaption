---
name: analyze-dfxp-docs
description: Generates EXHAUSTIVE DFXP/TTML specification summary from web sources with complete rule coverage, all elements/attributes/styling, and self-validation.
---

# analyze-dfxp-docs

## What this skill does

Generates comprehensive, exhaustive DFXP/TTML specification (`dfxp_specs_summary.md`) as single source of truth for compliance checking.

**Outputs:**
1. **60+ RULE-XXX specifications** with unique IDs and test patterns
2. **12+ IMPL-XXX requirements** (generic, no pycaption references)
3. **All content elements** individually documented (p, span, br, div, body)
4. **All styling attributes** individually documented (color, backgroundColor, fontSize, fontFamily, fontStyle, fontWeight, textDecoration, textAlign, direction, writingMode, etc.)
5. **All timing attributes** (begin, end, dur) with all supported time expressions
6. **All layout/region properties** (origin, extent, displayAlign, overflow, padding, etc.)
7. **Metadata elements** (ttm:title, ttm:desc, ttm:copyright, ttm:agent, ttm:actor)
8. **Self-validation report** (rule counts, completeness check)
9. **Source attribution** per rule

**Key:** Ensures NO requirements missed - exhaustive coverage from W3C TTML1 spec + web search.

**Pre-flight:** Read `.claude/skills/gotchas.md` before generating specs. Pay special attention to gotcha #3 (W3C license attribution required).

**Post-run:** If you discover a new gotcha during spec generation (a copyright/licensing trap, a W3C attribution pattern that should be avoided, a web source that returns misleading data, or a spec structure issue that could cause downstream compliance check failures), append it to `.claude/skills/gotchas.md` with the same numbered format.

**Usage:**
```bash
/analyze-dfxp-docs
```
Single command - fetches web sources, performs comprehensive analysis, generates complete spec.

---

## Implementation

### Step 0: Check Existing Sources

**Read existing documentation:**
```bash
# Check what we already have
ls -la ai_artifacts/specs/dfxp/
cat ai_artifacts/specs/dfxp/dfxp_web_sources.md
```

**If `dfxp_specs_summary.md` exists:**
- Read it to assess completeness
- Identify gaps using completeness checklist (Step 2)
- Only fetch new sources if gaps exist

### Step 1: Fetch Known Web Sources (WebFetch Tool Required)

**IMPORTANT:** This step requires the WebFetch tool to be loaded first.

**Check if WebFetch is available, load if needed:**
```python
# WebFetch is a deferred tool - load it before use
# Use ToolSearch to load: ToolSearch("select:WebFetch")
```

**Read URLs from `ai_artifacts/specs/dfxp/dfxp_web_sources.md`:**
```python
import re

with open("ai_artifacts/specs/dfxp/dfxp_web_sources.md") as _f:
    sources_content = _f.read()

# Extract URLs from markdown links: [Text](URL)
url_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
existing_sources = []

for match in re.findall(url_pattern, sources_content):
    title, url = match
    existing_sources.append({'title': title, 'url': url})

print(f"Found {len(existing_sources)} existing sources")
for s in existing_sources:
    print(f"   - {s['title']}")
```

#### Step 1a: Fetch W3C TTML1 Table of Contents first

**CRITICAL:** The full TTML1 spec is too large for a single WebFetch (it gets truncated mid-document). Fetch the TOC first to discover all normative sections, then fetch individual sections.

**Use the WebFetch tool** with the following parameters:
- URL: `https://www.w3.org/TR/2018/REC-ttml1-20181108/`
- Prompt: "Extract ONLY the complete Table of Contents with all section numbers and titles. List every section and subsection number (e.g., 6.2.1, 8.2.3, 10.3.1). Also extract every Appendix letter and title (A through P). I need the full hierarchy to plan section-by-section fetches."

```python
w3c_base = 'https://www.w3.org/TR/2018/REC-ttml1-20181108/'
# toc_content = <result from WebFetch tool above>
```

**Parse TOC to build section fetch plan:**
```python
# Identify all normative sections that need individual fetching
normative_sections = [
    # Each tuple: (fragment, description, what to extract)
    ('#content',      'Section 7: Content',     'All content elements: body, div, p, span, br, set. '
                                                 'Child elements, allowed attributes, content models.'),
    ('#styling',      'Section 8: Styling',     'ALL 25 tts:* attributes with EXACT valid values, '
                                                 'defaults, inheritance, applies-to. '
                                                 'ALL named colors. ALL color formats. '
                                                 'ALL length units. Style resolution rules.'),
    ('#layout',       'Section 9: Layout',      'Region element, all region properties, content association, '
                                                 'default region behavior.'),
    ('#timing',       'Section 10: Timing',     'ALL time expression formats with EXACT syntax/BNF. '
                                                 'begin/end/dur interaction. timeContainer par/seq. '
                                                 'Time containment rules.'),
    ('#animation',    'Section 11: Animation',  'set element, animation semantics.'),
    ('#metadata-vocabulary', 'Section 12: Metadata', 'ALL ttm:* elements and attributes. '
                                                      'ttm:role predefined values.'),
    ('#parameter-vocabulary', 'Section 6: Parameters', 'ALL ttp:* attributes with exact valid values '
                                                        'and defaults. timeBase, frameRate, dropMode, etc.'),
    ('#profiles',     'Section 5: Profiles',    'Profile mechanism, ttp:profile element vs attribute, '
                                                 'feature/extension vocabulary.'),
    ('#conformance',  'Section 3: Conformance', 'ALL MUST/SHOULD/MAY/MUST NOT requirements. '
                                                 'Document conformance. Processor conformance.'),
]
```

#### Step 1b: Fetch each normative section individually

For each normative section, **use the WebFetch tool** with:
- URL: `w3c_base + fragment` (e.g., `https://www.w3.org/TR/2018/REC-ttml1-20181108/#styling`)
- Prompt: "Extract ALL specification details from {description}. Specifically: {extract_prompt}. Include section numbers. List ALL valid enum values for each attribute. Include ALL MUST/SHOULD/MAY requirements."

Process each section immediately after fetching; don't hold all in memory.

**CRITICAL: Fetch Appendix D (Feature Designations) separately:**
**Use the WebFetch tool** with:
- URL: `https://www.w3.org/TR/2018/REC-ttml1-20181108/#feature-designations`
- Prompt: "Extract the COMPLETE list of all feature designations from Appendix D. For each feature, extract: feature name/URI, which profile(s) require it (Transformation/Presentation/Full), and whether it is required/optional/use. I need ALL 114 feature designations as a checklist."

**Fetch Appendix E (Profiles) separately:**
**Use the WebFetch tool** with:
- URL: `https://www.w3.org/TR/2018/REC-ttml1-20181108/#profile-dfxp-transformation`
- Prompt: "Extract the complete feature requirements for each DFXP profile: Transformation, Presentation, and Full. For each profile, list which features are required, optional, and prohibited."

#### Step 1c: Context optimization

- **Section-by-section fetching** prevents truncation of the large TTML1 spec
- Fetch sections sequentially, not in parallel (avoid context overflow)
- Extract text content only, discard HTML tags
- Process each section immediately after fetching, generate rules inline
- Save to temp files if needed, don't hold all in memory
- **Expect 8-10 fetches** for full coverage

### Step 2: Supplementary Sources (Web Search + Hardcoded Fallbacks)

#### Step 2a: Try WebSearch if available

**Check if WebSearch tool is available:**
```python
# WebSearch may not be available in all environments
# Try: ToolSearch("select:WebSearch")
# If not found, skip directly to Step 2b fallback URLs
```

**If WebSearch IS available, perform targeted searches:**
```python
search_queries = [
    "DFXP TTML specification complete W3C",
    "TTML1 styling attributes complete list",
    "DFXP timing expressions format specification",
    "TTML layout region properties specification",
    "DFXP metadata elements specification",
    "TTML parameter attributes specification",
    "DFXP TTML profile specification EBU-TT",
    "TTML color expressions named colors hex rgba",
]

search_results = []
for query in search_queries:
    print(f"Searching: {query}")
    # Use the WebSearch tool for each query
    results = []  # populated by WebSearch tool
    search_results.append({'query': query, 'results': results})
```

**Identify new authoritative sources:**
```python
import re

# Re-read existing sources (each block is independent)
with open("ai_artifacts/specs/dfxp/dfxp_web_sources.md") as _f:
    _sources_content = _f.read()
_existing_urls = {m[1] for m in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', _sources_content)}

# Agent: for each URL found in the search step above, check if it is
# authoritative (w3.org, github.com/w3c, ebu.ch, smpte.org) and not
# already in _existing_urls. Collect matches into new_sources list:
new_sources = []  # Agent fills this from search results
# new_sources.append({'title': <title>, 'url': <url>, 'query': <query>})

print(f"\nFound {len(new_sources)} new authoritative sources")
```

#### Step 2b: Hardcoded fallback URLs (ALWAYS try these)

**CRITICAL:** WebSearch is often unavailable. These known-good URLs MUST be tried regardless of whether WebSearch worked. For each URL, attempt a WebFetch; if it fails (403, 404, timeout), skip and continue.

```python
import re

# Re-read existing sources (each block is independent)
with open("ai_artifacts/specs/dfxp/dfxp_web_sources.md") as _f:
    _sources_content = _f.read()
_existing_urls = {m[1] for m in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', _sources_content)}

# Track new sources discovered in this block
new_sources = []

# Hardcoded authoritative DFXP/TTML supplementary sources
# These complement the W3C TTML1 spec with practical details and profiles
fallback_sources = [
    {
        'title': 'TTML1 Third Edition (2018 Recommendation)',
        'url': 'https://www.w3.org/TR/2018/REC-ttml1-20181108/',
        'prompt': 'Extract any clarifications, errata corrections, or updates from '
                  'the 2018 Third Edition that differ from the original TTML1.',
    },
    {
        'title': 'TTML2 Specification (backward-compat notes)',
        'url': 'https://www.w3.org/TR/ttml2/',
        'prompt': 'Extract backward-compatibility notes with TTML1, clarifications on '
                  'TTML1 styling attributes, and any TTML1 errata addressed in TTML2.',
    },
    {
        'title': 'W3C TTML1 Test Suite',
        'url': 'https://github.com/nicta/ttml-testcases',
        'prompt': 'Extract list of test case categories and what spec areas they cover.',
    },
    {
        'title': 'Speechpad TTML Reference',
        'url': 'https://www.speechpad.com/captions/ttml',
        'prompt': 'Extract all TTML/DFXP technical details: document structure, '
                  'timing formats, styling, regions, best practices.',
    },
    {
        'title': 'EBU-TT Part 1 (Tech 3380)',
        'url': 'https://tech.ebu.ch/docs/tech/tech3380.pdf',
        'prompt': 'Extract EBU-TT profile requirements, constraints on TTML1, '
                  'required elements/attributes, timing/styling/region restrictions.',
    },
    {
        'title': 'EBU-TT-D (Tech 3380 Distribution)',
        'url': 'https://tech.ebu.ch/publications/ebu-tt-d',
        'prompt': 'Extract EBU-TT-D distribution profile details and how it constrains TTML1.',
    },
    {
        'title': 'W3C TTML Overview Wiki',
        'url': 'https://www.w3.org/wiki/TTML_Profiles',
        'prompt': 'Extract overview of all TTML profiles, their relationships, '
                  'and feature sets.',
    },
]

# Try each fallback source; skip on failure
for source in fallback_sources:
    if source['url'] in _existing_urls:
        print(f"   Skipping (already known): {source['title']}")
        continue
    try:
        print(f"Fetching fallback: {source['title']}...")
        # Use the WebFetch tool with url=source['url'] and prompt=source['prompt']
        new_sources.append({'title': source['title'], 'url': source['url']})
        print(f"   Success: {source['title']}")
    except Exception:
        print(f"   Failed (skipping): {source['title']}")
        continue
```

**Fetch new search-discovered sources (if WebSearch was available):**
```python
# Agent: for each source in new_sources (up to 5), use WebFetch to
# retrieve the content. new_sources was built in the filtering step above.
# for source in new_sources[:5]:
#     print(f"Fetching: {source['title']}")
#     # Use the WebFetch tool with url=source['url']
```

### Step 3: Exhaustive Completeness Verification

#### Step 3a: Cross-check against Appendix D Feature Designations

**CRITICAL:** TTML1 Appendix D defines **114 feature designations** that serve as the AUTHORITATIVE master checklist. Every feature designation must map to at least one RULE-* in the output. This is the primary mechanism for ensuring no rules are missed.

```python
import re, os
import glob as _glob

# Appendix D features are organized into these categories:
appendix_d_feature_categories = {
    '#animation':       'Animation features (set element)',
    '#content':         'Content features (body, div, p, span, br)',
    '#core':            'Core features (tt, head, body structure)',
    '#layout':          'Layout features (layout, region)',
    '#metadata':        'Metadata features (ttm:*)',
    '#parameter':       'Parameter features (ttp:*)',
    '#presentation':    'Presentation features (rendering)',
    '#profile':         'Profile features',
    '#structure':       'Document structure features',
    '#styling':         'Styling features (all tts:* attributes)',
    '#styling-attribute': 'Individual styling attributes',
    '#time-value-expression': 'Time expression features',
    '#timing':          'Timing features (begin, end, dur, timeContainer)',
    '#transformation':  'Transformation features',
}

# For each Appendix D feature, verify a corresponding RULE exists
# Example features to verify:
appendix_d_checklist = [
    # Styling features - one per tts:* attribute
    ('#styling-attribute-backgroundColor',  'RULE-STY-002'),
    ('#styling-attribute-color',            'RULE-STY-001'),
    ('#styling-attribute-direction',        'RULE-STY-009'),
    ('#styling-attribute-display',          'RULE-STY-011'),
    ('#styling-attribute-displayAlign',     'RULE-STY-012'),
    ('#styling-attribute-extent',           'RULE-STY-017'),
    ('#styling-attribute-fontFamily',       'RULE-STY-004'),
    ('#styling-attribute-fontSize',         'RULE-STY-003'),
    ('#styling-attribute-fontStyle',        'RULE-STY-005'),
    ('#styling-attribute-fontWeight',       'RULE-STY-006'),
    ('#styling-attribute-lineHeight',       'RULE-STY-013'),
    ('#styling-attribute-opacity',          'RULE-STY-014'),
    ('#styling-attribute-origin',           'RULE-STY-018'),
    ('#styling-attribute-overflow',         'RULE-STY-019'),
    ('#styling-attribute-padding',          'RULE-STY-016'),
    ('#styling-attribute-showBackground',   'RULE-STY-020'),
    ('#styling-attribute-textAlign',        'RULE-STY-007'),
    ('#styling-attribute-textDecoration',   'RULE-STY-008'),
    ('#styling-attribute-textOutline',      'RULE-STY-015'),
    ('#styling-attribute-unicodeBidi',      'RULE-STY-023'),
    ('#styling-attribute-visibility',       'RULE-STY-021'),
    ('#styling-attribute-wrapOption',       'RULE-STY-022'),
    ('#styling-attribute-writingMode',      'RULE-STY-010'),
    ('#styling-attribute-zIndex',           'RULE-STY-024'),
    # Timing features
    ('#timing-attribute-begin',     'RULE-TIME-009'),
    ('#timing-attribute-end',       'RULE-TIME-010'),
    ('#timing-attribute-dur',       'RULE-TIME-011'),
    ('#timing-attribute-timeContainer', 'RULE-TIME-012'),
    ('#timing-time-value-expression-clock-time', 'RULE-TIME-001'),
    ('#timing-time-value-expression-offset-time', 'RULE-TIME-003 through 008'),
    # Content features
    ('#content-element-body',   'RULE-CONT-001'),
    ('#content-element-div',    'RULE-CONT-002'),
    ('#content-element-p',      'RULE-CONT-003'),
    ('#content-element-span',   'RULE-CONT-004'),
    ('#content-element-br',     'RULE-CONT-005'),
    # Animation
    ('#animation-element-set',  'RULE-CONT-006'),
    # Layout
    ('#layout-element-layout',  'RULE-LAY-001'),
    ('#layout-element-region',  'RULE-LAY-002'),
    # Metadata
    ('#metadata-element-title',     'RULE-META-001'),
    ('#metadata-element-desc',      'RULE-META-002'),
    ('#metadata-element-copyright', 'RULE-META-003'),
    ('#metadata-element-agent',     'RULE-META-004'),
    ('#metadata-element-actor',     'RULE-META-005'),
    # Parameters
    ('#parameter-attribute-cellResolution',      'RULE-PAR-009'),
    ('#parameter-attribute-clockMode',           'RULE-PAR-007'),
    ('#parameter-attribute-dropMode',            'RULE-PAR-006'),
    ('#parameter-attribute-frameRate',           'RULE-PAR-002'),
    ('#parameter-attribute-frameRateMultiplier', 'RULE-PAR-004'),
    ('#parameter-attribute-markerMode',          'RULE-PAR-008'),
    ('#parameter-attribute-pixelAspectRatio',    'RULE-PAR-010'),
    ('#parameter-attribute-profile',             'RULE-PAR-011'),
    ('#parameter-attribute-subFrameRate',        'RULE-PAR-003'),
    ('#parameter-attribute-tickRate',            'RULE-PAR-005'),
    ('#parameter-attribute-timeBase',            'RULE-PAR-001'),
]

# Load generated spec and extract rule IDs for cross-check
import glob as _glob
_spec_files = _glob.glob('ai_artifacts/specs/dfxp/dfxp_specs_summary*.md') + _glob.glob('pycaption/specs/dfxp/dfxp_specs_summary*.md')
generated_rule_ids = set()
if _spec_files:
    with open(max(_spec_files, key=os.path.getmtime)) as _f:
        for _m in re.finditer(r'\*\*\[(RULE-[A-Z]+-\d{3}|IMPL-\d{3})\]\*\*', _f.read()):
            generated_rule_ids.add(_m.group(1))

# After generating rules, cross-check:
missing_features = []
for feature_uri, expected_rule in appendix_d_checklist:
    if expected_rule not in generated_rule_ids:
        missing_features.append((feature_uri, expected_rule))

if missing_features:
    print(f"FAIL: {len(missing_features)} Appendix D features missing rules!")
    for feature, rule in missing_features:
        print(f"   {feature} -> expected {rule}")
    # MUST add missing rules before proceeding
else:
    print("PASS: All Appendix D features have corresponding rules")
```

#### Step 3b: Enum Value Deep Verification

**CRITICAL:** For each styling attribute, verify that ALL valid enum values are explicitly listed in the generated rule. A rule that says "tts:textAlign" exists but doesn't list `justify` as a valid value is incomplete.

```python
import re, os
import glob as _glob

# Load the generated spec to verify enum values are present
_spec_files = _glob.glob('ai_artifacts/specs/dfxp/dfxp_specs_summary*.md') + _glob.glob('pycaption/specs/dfxp/dfxp_specs_summary*.md')
spec_content = ""
if _spec_files:
    with open(max(_spec_files, key=os.path.getmtime)) as _f:
        spec_content = _f.read()

# Master enum value checklist - every value must appear in the corresponding rule
enum_value_checklist = {
    'tts:textAlign':       ['left', 'center', 'right', 'start', 'end'],
    'tts:fontStyle':       ['normal', 'italic', 'oblique'],
    'tts:fontWeight':      ['normal', 'bold'],
    'tts:direction':       ['ltr', 'rtl'],
    'tts:display':         ['auto', 'none'],
    'tts:displayAlign':    ['before', 'center', 'after'],
    'tts:overflow':        ['visible', 'hidden'],
    'tts:showBackground':  ['always', 'whenActive'],
    'tts:visibility':      ['visible', 'hidden'],
    'tts:wrapOption':      ['wrap', 'noWrap'],
    'tts:unicodeBidi':     ['normal', 'embed', 'bidiOverride'],
    'tts:writingMode':     ['lrtb', 'rltb', 'tbrl', 'tblr', 'lr', 'rl', 'tb'],
    'tts:textDecoration':  ['none', 'underline', 'noUnderline', 'overline',
                            'noOverline', 'lineThrough', 'noLineThrough'],
    'tts:fontFamily':      ['default', 'monospace', 'monospaceSansSerif',
                            'monospaceSerif', 'proportionalSansSerif',
                            'proportionalSerif', 'sansSerif', 'serif'],
    'ttp:timeBase':        ['media', 'smpte', 'clock'],
    'ttp:dropMode':        ['dropNTSC', 'dropPAL', 'nonDrop'],
    'ttp:clockMode':       ['local', 'gps', 'utc'],
    'ttp:markerMode':      ['continuous', 'discontinuous'],
}

# Named colors that MUST all be listed
required_named_colors = [
    'transparent', 'black', 'silver', 'gray', 'white', 'maroon', 'red',
    'purple', 'fuchsia', 'magenta', 'green', 'lime', 'olive', 'yellow',
    'navy', 'blue', 'teal', 'aqua', 'cyan',
]

# Color formats that MUST all be documented
required_color_formats = [
    '#RRGGBB',       # 6-digit hex
    '#RRGGBBAA',     # 8-digit hex with alpha
    'rgb(R,G,B)',    # Functional RGB (integers 0-255)
    'rgba(R,G,B,A)', # Functional RGBA (all integers 0-255)
    'named-color',   # Named color keyword
]

# Length units that MUST all be documented
required_length_units = ['px', 'em', 'c', '%']

# After generating the spec, scan it to verify every enum value appears:
for attr, values in enum_value_checklist.items():
    for value in values:
        if value not in spec_content:
            print(f"MISSING enum value: {attr} -> '{value}'")
            # MUST add the missing value to the corresponding rule

for color in required_named_colors:
    if color not in spec_content:
        print(f"MISSING named color: '{color}'")

for fmt in required_color_formats:
    if fmt not in spec_content:
        print(f"MISSING color format: '{fmt}'")
```

#### Step 3c: TOC-based Section Coverage Verification

**Verify every normative spec section maps to at least one rule:**
```python
import re, os
import glob as _glob

# Load the generated spec for section reference checking
_spec_files = _glob.glob('ai_artifacts/specs/dfxp/dfxp_specs_summary*.md') + _glob.glob('pycaption/specs/dfxp/dfxp_specs_summary*.md')
spec_content = ""
if _spec_files:
    with open(max(_spec_files, key=os.path.getmtime)) as _f:
        spec_content = _f.read()

# From the TOC fetched in Step 1a, extract all normative section numbers
# Then verify each section is referenced in at least one rule's Sources field
normative_toc_sections = [
    '3.1',   # Document Conformance
    '3.2',   # Processor Conformance
    '5.2',   # Profile
    '6.2.1', # ttp:cellResolution
    '6.2.2', # ttp:dropMode
    '6.2.3', # ttp:frameRate
    '6.2.4', # ttp:frameRateMultiplier
    '6.2.5', # ttp:markerMode
    '6.2.6', # ttp:pixelAspectRatio
    '6.2.7', # ttp:subFrameRate
    '6.2.8', # ttp:timeBase
    '6.2.9', # ttp:tickRate
    '7.1.1', # tt element
    '7.1.2', # head element
    '7.1.3', # body element
    '7.1.4', # div element
    '7.1.5', # p element
    '7.1.6', # span element
    '7.1.7', # br element
    '8.1.1', # styling element
    '8.1.2', # style element
    '8.2.1', # tts:backgroundColor
    '8.2.2', # tts:color  (note: numbering may vary by edition)
    # ... all 8.2.X subsections for each styling attribute
    '8.3',   # Style Value Expressions
    '8.4',   # Style Resolution
    '9.1.1', # layout element
    '9.1.2', # region element
    '9.3',   # Region Association
    '10.2.1', # begin
    '10.2.2', # end
    '10.2.3', # dur
    '10.2.4', # timeContainer
    '10.3',   # Time Value Expressions
    '10.4',   # Time Intervals
    '11.1.1', # set element
    '12.1',   # Metadata
]

# Check each section is referenced somewhere in the spec
for section in normative_toc_sections:
    if f'Section {section}' not in spec_content and f'§{section}' not in spec_content:
        print(f"WARNING: Normative section {section} not referenced in any rule")
```

**Now proceed with the area-by-area content checklist:**

**CRITICAL:** Verify ALL these areas covered in fetched content (100% coverage required):

**Document Structure (XML):**
- Root element: `<tt>` with required namespace `http://www.w3.org/ns/ttml`
- XML declaration: `<?xml version="1.0" encoding="UTF-8"?>`
- Required namespaces: tt, tts (styling), ttp (parameter), ttm (metadata)
- Optional namespaces: custom extensions
- Document structure: `<tt>` > `<head>` + `<body>`
- Head contains: `<metadata>`, `<styling>`, `<layout>`
- Body contains: `<div>` > `<p>` > `<span>` / `<br>`

**Timing Model:**
- Clock time: `HH:MM:SS.fraction` or `HH:MM:SS:frames`
- Offset time: `N{h|m|s|ms|f|t}` (hours, minutes, seconds, milliseconds, frames, ticks)
- `begin` attribute (start time)
- `end` attribute (end time)
- `dur` attribute (duration, alternative to `end`)
- Time containment: children constrained by parent timing
- Sequential vs parallel timing semantics
- `timeBase` parameter: "media" | "smpte" | "clock"
- `frameRate`, `subFrameRate`, `frameRateMultiplier`, `tickRate` parameters
- `dropMode`: "dropNTSC" | "dropPAL" | "nonDrop"

**Content Elements:**
- `<body>` - root content container
- `<div>` - division/grouping element (required wrapper for `<p>`)
- `<p>` - paragraph (subtitle/caption unit)
- `<span>` - inline text container (for styling ranges)
- `<br>` - line break (empty element)
- `<set>` - animation element
- Anonymous spans (text nodes directly in `<p>`)

**Styling Attributes (tts: namespace):**
- `tts:backgroundColor` - background color (named, #RRGGBB, #RRGGBBAA, rgba())
- `tts:color` - foreground/text color
- `tts:direction` - ltr | rtl
- `tts:display` - auto | none
- `tts:displayAlign` - before | center | after
- `tts:extent` - width height (for regions)
- `tts:fontFamily` - font name(s), generic families
- `tts:fontSize` - size value (px, em, c, %)
- `tts:fontStyle` - normal | italic | oblique
- `tts:fontWeight` - normal | bold
- `tts:lineHeight` - normal | length
- `tts:opacity` - 0.0 to 1.0
- `tts:origin` - x y coordinates (for regions)
- `tts:overflow` - visible | hidden
- `tts:padding` - length values (1-4 values)
- `tts:showBackground` - always | whenActive
- `tts:textAlign` - left | center | right | start | end
- `tts:textDecoration` - none | underline | noUnderline | overline | noOverline | lineThrough | noLineThrough
- `tts:textOutline` - color? thickness blur?
- `tts:unicodeBidi` - normal | embed | bidiOverride
- `tts:visibility` - visible | hidden
- `tts:wrapOption` - wrap | noWrap
- `tts:writingMode` - lrtb | rltb | tbrl | tblr | lr | rl | tb
- `tts:zIndex` - integer (for region stacking)
- Style inheritance rules
- Style referencing via `style` attribute

**Layout/Regions:**
- `<layout>` element in `<head>`
- `<region>` element definition
- Region attributes: `xml:id`, `tts:origin`, `tts:extent`, `tts:displayAlign`, `tts:overflow`, `tts:padding`, `tts:showBackground`, `tts:backgroundColor`, `tts:writingMode`, `tts:zIndex`
- Content association via `region` attribute on `<body>`, `<div>`, `<p>`, `<span>`
- Default region behavior
- Region overlap and z-ordering

**Metadata Elements (ttm: namespace):**
- `<ttm:title>` - document title
- `<ttm:desc>` - description
- `<ttm:copyright>` - copyright information
- `<ttm:agent>` - agent (person, character, group)
- `<ttm:actor>` - actor portraying an agent
- `ttm:agent` attribute on content elements
- `ttm:role` attribute (caption, description, dialog, etc.)

**Parameter Attributes (ttp: namespace):**
- `ttp:timeBase` - media | smpte | clock
- `ttp:frameRate` - integer (default 30)
- `ttp:subFrameRate` - integer
- `ttp:frameRateMultiplier` - "numerator denominator"
- `ttp:tickRate` - integer
- `ttp:dropMode` - dropNTSC | dropPAL | nonDrop
- `ttp:clockMode` - local | gps | utc
- `ttp:markerMode` - continuous | discontinuous
- `ttp:cellResolution` - "columns rows"
- `ttp:pixelAspectRatio` - "width height"
- `ttp:profile` - profile URI

**Styling Model:**
- `<styling>` element in `<head>`
- `<style>` element definition (reusable named styles)
- Style referencing: `style` attribute (space-separated list of style IDs)
- Style inheritance: specified > inherited > initial values
- Style chaining: multiple `<style>` references resolved in order
- Inline styling: tts:* attributes directly on elements
- Referential styling: via `style` attribute pointing to `<style>` elements
- Nested styling: `<style>` elements can reference other styles

**Profiles:**
- DFXP Presentation profile (minimum for presentation)
- DFXP Transformation profile (minimum for transformation)
- DFXP Full profile (all features)
- EBU-TT (European broadcasting profile)
- EBU-TT-D (EBU distribution profile)
- SMPTE-TT (SMPTE timed text)
- Profile signaling via `ttp:profile` attribute

**Validation Requirements:**
- All MUST requirements from W3C TTML1 spec
- All SHOULD requirements
- All MAY optional features
- All MUST NOT forbidden patterns
- Well-formed XML requirements
- Namespace validation
- Error handling strategies

**Edge Cases & Common Pitfalls:**
- Missing required namespaces
- Invalid time expressions
- Overlapping timing intervals
- Style inheritance conflicts
- Region not defined before reference
- Invalid color values
- Frame-based timing without frameRate
- dur and end both specified (dur takes precedence? spec behavior)
- Empty `<p>` elements
- Nested `<div>` elements
- Anonymous spans vs explicit `<span>`

**Implementation Requirements:**
- XML parser requirements
- Namespace handling
- Time expression parser (clock-time, offset-time, frame-based)
- Style resolver (inheritance, chaining, inline)
- Region resolver
- Writer requirements (XML serialization, escaping, namespace declarations)
- Error handling strategies
- Performance considerations

**Completeness Checklist (MUST achieve 100%):**
```python
# TEMPLATE: All values start as False. Update each to True as you confirm coverage during spec generation.
completeness_check = {
    'document_structure': {
        'root_element': False,      # <tt> with namespace
        'xml_declaration': False,    # <?xml ...?>
        'namespaces': False,         # tt, tts, ttp, ttm
        'head_body': False,          # <head> + <body>
        'styling_layout': False,     # <styling> + <layout>
    },
    'timing': {
        'clock_time': False,         # HH:MM:SS.fraction
        'offset_time': False,        # N{h|m|s|ms|f|t}
        'begin_end_dur': False,      # begin, end, dur
        'time_containment': False,   # Parent constrains children
        'time_base': False,          # media|smpte|clock
        'frame_rate': False,         # frameRate, subFrameRate, multiplier
    },
    'content_elements': {
        'body': False,    # <body>
        'div': False,     # <div>
        'p': False,       # <p>
        'span': False,    # <span>
        'br': False,      # <br>
        'set': False,     # <set>
    },
    'styling_attributes': {
        'color': False,             # tts:color
        'backgroundColor': False,   # tts:backgroundColor
        'fontSize': False,          # tts:fontSize
        'fontFamily': False,        # tts:fontFamily
        'fontStyle': False,         # tts:fontStyle
        'fontWeight': False,        # tts:fontWeight
        'textAlign': False,         # tts:textAlign
        'textDecoration': False,    # tts:textDecoration
        'direction': False,         # tts:direction
        'writingMode': False,       # tts:writingMode
        'display': False,           # tts:display
        'displayAlign': False,      # tts:displayAlign
        'lineHeight': False,        # tts:lineHeight
        'opacity': False,           # tts:opacity
        'textOutline': False,       # tts:textOutline
        'padding': False,           # tts:padding
        'extent': False,            # tts:extent
        'origin': False,            # tts:origin
        'overflow': False,          # tts:overflow
        'showBackground': False,    # tts:showBackground
        'visibility': False,        # tts:visibility
        'wrapOption': False,        # tts:wrapOption
        'unicodeBidi': False,       # tts:unicodeBidi
        'zIndex': False,            # tts:zIndex
    },
    'styling_model': {
        'style_element': False,     # <style> definition
        'style_reference': False,   # style attribute
        'inheritance': False,       # Specified > inherited > initial
        'chaining': False,          # Multiple style references
        'inline_styling': False,    # tts:* on elements
    },
    'layout_regions': {
        'layout_element': False,    # <layout>
        'region_element': False,    # <region>
        'region_attributes': False, # origin, extent, displayAlign, etc.
        'content_association': False,# region attribute on content
        'default_region': False,    # Default behavior
    },
    'metadata': {
        'title': False,      # ttm:title
        'desc': False,       # ttm:desc
        'copyright': False,  # ttm:copyright
        'agent': False,      # ttm:agent
        'actor': False,      # ttm:actor
    },
    'parameters': {
        'timeBase': False,          # ttp:timeBase
        'frameRate': False,         # ttp:frameRate
        'tickRate': False,          # ttp:tickRate
        'dropMode': False,          # ttp:dropMode
        'clockMode': False,         # ttp:clockMode
        'cellResolution': False,    # ttp:cellResolution
        'profile': False,           # ttp:profile
    },
    'profiles': {
        'presentation': False,  # DFXP Presentation profile
        'transformation': False,# DFXP Transformation profile
        'full': False,          # DFXP Full profile
    },
    'validation': {
        'must_rules': False,        # All MUST requirements
        'should_rules': False,      # All SHOULD requirements
        'xml_wellformed': False,    # Well-formed XML
        'error_handling': False,    # Error strategies
    },
}

# Calculate completeness percentage
total_items = sum(len(v) for v in completeness_check.values())
covered_items = sum(sum(v.values()) for v in completeness_check.values())
completeness = (covered_items / total_items) * 100

print(f"Completeness: {completeness:.1f}% ({covered_items}/{total_items} items)")

if completeness < 100:
    print("Missing items - additional web search required")
    for category, items in completeness_check.items():
        missing = [k for k, v in items.items() if not v]
        if missing:
            print(f"   {category}: {', '.join(missing)}")
```

**If new sources found during search, update dfxp_web_sources.md:**
```python
# Agent: if you discovered new sources during the search/filter steps,
# append them to dfxp_web_sources.md now. For each new source URL not
# already in the file, add a markdown link line.
import re as _re, os
_sources_path = "ai_artifacts/specs/dfxp/dfxp_web_sources.md"
if os.path.exists(_sources_path):
    with open(_sources_path) as _f:
        _current = _f.read()
    _known_urls = {m[1] for m in _re.findall(r'\[([^\]]+)\]\(([^)]+)\)', _current)}
    # Agent: for each new source discovered above, if url not in _known_urls:
    #   _current += f"- [{title}]({url})\n"
    # Then write back:
    # with open(_sources_path, "w") as _f:
    #     _f.write(_current)
    print("Source file update complete")
else:
    print(f"WARNING: {_sources_path} not found — skipping source update")
```

### Step 4: Generate Exhaustive Specification

Create `ai_artifacts/specs/dfxp/dfxp_specs_summary.md`.

**Rule Format:**
```markdown
**[RULE-XXX-###]** Brief requirement
- **Requirement:** What must be true
- **Level:** MUST | SHOULD | MAY | MUST NOT
- **Validation:** How to check
- **Test Pattern:** Regex, XPath, or algorithm
- **Sources:** [Attribution]
```

**Implementation Rule Format (GENERIC):**
```markdown
**[IMPL-XXX-###]** Component MUST do X
- **Spec Rule:** RULE-XXX-###
- **Component:** Parser | Writer | Validator
- **Implementation Requirement:** What ANY compliant implementation must do
- **Expected Behavior:** Input -> Output examples
- **Validation Criteria:** What to verify
- **Common Patterns:** Correct vs incorrect (generic)
- **Test Coverage:** Required test scenarios
```

**Critical requirements** (must be included as rules):

**Part 1 (Document Structure):** Root `<tt>` element, namespaces, XML declaration, head/body structure
**Part 2 (Timing):** Clock-time, offset-time, frame-based, begin/end/dur, time containment, timeBase/frameRate params
**Part 3 (Content Elements):** body, div, p, span, br, set, anonymous spans
**Part 4 (Styling Attributes):** All 24+ tts:* attributes with valid values and defaults
**Part 5 (Styling Model):** Style elements, referencing, inheritance, chaining, inline styling
**Part 6 (Layout/Regions):** layout element, region definition, all region properties, content association
**Part 7 (Metadata):** ttm:title, ttm:desc, ttm:copyright, ttm:agent, ttm:actor
**Part 8 (Parameters):** All ttp:* attributes (timeBase, frameRate, tickRate, dropMode, etc.)
**Part 9 (Profiles):** Presentation, Transformation, Full profiles
**Part 10 (Implementation):** Generic IMPL-* rules for Parser/Writer/Validator
**Part 11 (Validation Summary):** Rule counts, self-validation report
**Part 12 (Quick Reference):** Tables for styling attributes, timing expressions, content elements

**Target Rule Counts (Exhaustive):**
- **RULE-DOC-###**: 6-8 document structure rules (root, namespaces, XML, head/body)
- **RULE-TIME-###**: 10-14 timing rules (clock-time, offset-time, frames, begin/end/dur, containment, parameters)
- **RULE-CONT-###**: 6-8 content element rules (body, div, p, span, br, set, anonymous spans)
- **RULE-STY-###**: 26-30 styling attribute rules (all 24+ tts:* attributes + color expressions + inheritance)
- **RULE-SMOD-###**: 5-7 styling model rules (style element, referencing, inheritance, chaining, inline)
- **RULE-LAY-###**: 6-8 layout/region rules (layout, region, properties, association, defaults)
- **RULE-META-###**: 5-6 metadata rules (title, desc, copyright, agent, actor, role)
- **RULE-PAR-###**: 8-10 parameter rules (timeBase, frameRate, tickRate, dropMode, clockMode, cellResolution, profile)
- **RULE-PROF-###**: 3-5 profile rules (presentation, transformation, full)
- **RULE-VAL-###**: 5-8 validation rules (error handling, recovery, XML well-formedness)
- **IMPL-###**: 12-15 implementation requirements (parser, writer, validator)
- **Total: 90-120 rules** (comprehensive coverage)

**Level Distribution (Exhaustive):**
- **MUST**: 40-55 rules (critical requirements)
- **SHOULD**: 20-30 rules (recommended practices)
- **MAY**: 10-15 rules (optional features)
- **MUST NOT**: 5-8 rules (forbidden patterns)

**Critical Inclusions (MUST be documented):**

**All Content Elements (Individual Rules):**
1. `<body>` - root content container (RULE-CONT-001)
2. `<div>` - division/grouping (RULE-CONT-002)
3. `<p>` - paragraph/subtitle (RULE-CONT-003)
4. `<span>` - inline text (RULE-CONT-004)
5. `<br>` - line break (RULE-CONT-005)
6. `<set>` - animation (RULE-CONT-006)

**All Core Styling Attributes (Individual Rules):**
1. `tts:color` (RULE-STY-001)
2. `tts:backgroundColor` (RULE-STY-002)
3. `tts:fontSize` (RULE-STY-003)
4. `tts:fontFamily` (RULE-STY-004)
5. `tts:fontStyle` (RULE-STY-005)
6. `tts:fontWeight` (RULE-STY-006)
7. `tts:textAlign` (RULE-STY-007)
8. `tts:textDecoration` (RULE-STY-008)
9. `tts:direction` (RULE-STY-009)
10. `tts:writingMode` (RULE-STY-010)
11. `tts:display` (RULE-STY-011)
12. `tts:displayAlign` (RULE-STY-012)
13. `tts:lineHeight` (RULE-STY-013)
14. `tts:opacity` (RULE-STY-014)
15. `tts:textOutline` (RULE-STY-015)
16. `tts:padding` (RULE-STY-016)
17. `tts:extent` (RULE-STY-017)
18. `tts:origin` (RULE-STY-018)
19. `tts:overflow` (RULE-STY-019)
20. `tts:showBackground` (RULE-STY-020)
21. `tts:visibility` (RULE-STY-021)
22. `tts:wrapOption` (RULE-STY-022)
23. `tts:unicodeBidi` (RULE-STY-023)
24. `tts:zIndex` (RULE-STY-024)

**All Time Expression Formats:**
1. Clock-time with fractional seconds: `HH:MM:SS.sss` (RULE-TIME-001)
2. Clock-time with frames: `HH:MM:SS:FF` (RULE-TIME-002)
3. Offset-time hours: `Nh` (RULE-TIME-003)
4. Offset-time minutes: `Nm` (RULE-TIME-004)
5. Offset-time seconds: `Ns` or `N.Ns` (RULE-TIME-005)
6. Offset-time milliseconds: `Nms` (RULE-TIME-006)
7. Offset-time frames: `Nf` (RULE-TIME-007)
8. Offset-time ticks: `Nt` (RULE-TIME-008)

**All Parameter Attributes (Individual Rules):**
1. `ttp:timeBase` (RULE-PAR-001)
2. `ttp:frameRate` (RULE-PAR-002)
3. `ttp:subFrameRate` (RULE-PAR-003)
4. `ttp:frameRateMultiplier` (RULE-PAR-004)
5. `ttp:tickRate` (RULE-PAR-005)
6. `ttp:dropMode` (RULE-PAR-006)
7. `ttp:clockMode` (RULE-PAR-007)
8. `ttp:markerMode` (RULE-PAR-008)
9. `ttp:cellResolution` (RULE-PAR-009)
10. `ttp:pixelAspectRatio` (RULE-PAR-010)
11. `ttp:profile` (RULE-PAR-011)

**All Metadata Elements (Individual Rules):**
1. `<ttm:title>` (RULE-META-001)
2. `<ttm:desc>` (RULE-META-002)
3. `<ttm:copyright>` (RULE-META-003)
4. `<ttm:agent>` (RULE-META-004)
5. `<ttm:actor>` (RULE-META-005)

**Generate spec with incremental writing (context-efficient):**
```python
from datetime import datetime
import os

os.makedirs("ai_artifacts/specs/dfxp", exist_ok=True)
spec_path = "ai_artifacts/specs/dfxp/dfxp_specs_summary.md"

# Write spec header
spec_content = f"""# DFXP/TTML1 Specification - Complete Reference

**Generated**: {datetime.now().strftime("%Y-%m-%d")}
**Sources**: W3C TTML1 Specification (https://www.w3.org/TR/ttml1/)
**Version**: W3C Recommendation (November 2013)
**Total Rules**: [TO BE CALCULATED]

---

"""

with open(spec_path, "w") as _f:
    _f.write(spec_content)

# Then generate and append each part section by section:
# Part 1: Document Structure rules
# Part 2: Timing rules
# ... continue for all parts (Parts 1-12)
# Append each part with: with open(spec_path, "a") as _f: _f.write(part)
```

### Step 5: Exhaustive Quality Validation

**Structure checks:**
- All rule IDs unique
- Sequential numbering within each category
- Valid test patterns (XPath, regex, algorithm)
- Level indicators present (MUST/SHOULD/MAY/MUST NOT)

**Appendix D cross-check (MANDATORY - run Step 3a verification):**
- Every Appendix D feature designation maps to at least one RULE-*
- Missing features MUST be added as rules before proceeding
- Log which Appendix D features mapped to which rules

**Enum value deep verification (MANDATORY - run Step 3b verification):**
- Every valid enum value for every attribute appears explicitly in the spec
- All 19 named colors listed individually
- All 5 color formats documented
- All 4 length units documented
- All 8 generic font family names listed
- All 7 writingMode values listed
- All 7 textDecoration tokens listed
- Missing values MUST be added to the corresponding rule

**TOC section coverage (MANDATORY - run Step 3c verification):**
- Every normative spec section referenced in at least one rule's Sources field
- Unreferenced sections investigated for missing rules

**Content checks (Exhaustive - 100% required):**
- 90-120 total rules documented (RULE-* + IMPL-*)
- 40-55 MUST rules (all critical requirements)
- 20-30 SHOULD rules (best practices)
- 10-15 MAY rules (optional features)
- 12-15 IMPL-* rules (generic, no pycaption references)
- All 6 content elements individually documented (body, div, p, span, br, set)
- All 24 styling attributes individually documented
- All 8 time expression formats individually documented
- All 11 parameter attributes individually documented
- All 5 metadata elements individually documented
- Styling model complete (style element, referencing, inheritance, chaining)
- Layout/region specification complete
- Profile specifications documented
- Validation rules complete (error handling, recovery strategies)

**Generate exhaustive validation report in spec file:**
```markdown
## Part 11: Exhaustive Validation Summary

### Rule Counts by Category
- RULE-DOC-###: X document structure rules (Target: 6-8)
- RULE-TIME-###: X timing rules (Target: 10-14)
- RULE-CONT-###: X content element rules (Target: 6-8)
- RULE-STY-###: X styling attribute rules (Target: 26-30)
- RULE-SMOD-###: X styling model rules (Target: 5-7)
- RULE-LAY-###: X layout/region rules (Target: 6-8)
- RULE-META-###: X metadata rules (Target: 5-6)
- RULE-PAR-###: X parameter rules (Target: 8-10)
- RULE-PROF-###: X profile rules (Target: 3-5)
- RULE-VAL-###: X validation rules (Target: 5-8)
- IMPL-###: X implementation requirements (Target: 12-15)
- **Total: Y rules** (Target: 90-120 for exhaustive coverage)

### By Level (Exhaustive Distribution)
- MUST: X rules (Target: 40-55)
- SHOULD: X rules (Target: 20-30)
- MAY: X rules (Target: 10-15)
- MUST NOT: X rules (Target: 5-8)

### Coverage Verification (100% Required)

**Content Elements (6 total - ALL must be documented):**
- body (RULE-CONT-001)
- div (RULE-CONT-002)
- p (RULE-CONT-003)
- span (RULE-CONT-004)
- br (RULE-CONT-005)
- set (RULE-CONT-006)
**Status: X/6 elements documented**

**Core Styling Attributes (24 total - ALL must be documented):**
- tts:color (RULE-STY-001)
- tts:backgroundColor (RULE-STY-002)
- tts:fontSize (RULE-STY-003)
- tts:fontFamily (RULE-STY-004)
- tts:fontStyle (RULE-STY-005)
- tts:fontWeight (RULE-STY-006)
- tts:textAlign (RULE-STY-007)
- tts:textDecoration (RULE-STY-008)
- tts:direction (RULE-STY-009)
- tts:writingMode (RULE-STY-010)
- tts:display (RULE-STY-011)
- tts:displayAlign (RULE-STY-012)
- tts:lineHeight (RULE-STY-013)
- tts:opacity (RULE-STY-014)
- tts:textOutline (RULE-STY-015)
- tts:padding (RULE-STY-016)
- tts:extent (RULE-STY-017)
- tts:origin (RULE-STY-018)
- tts:overflow (RULE-STY-019)
- tts:showBackground (RULE-STY-020)
- tts:visibility (RULE-STY-021)
- tts:wrapOption (RULE-STY-022)
- tts:unicodeBidi (RULE-STY-023)
- tts:zIndex (RULE-STY-024)
**Status: X/24 attributes documented**

**Time Expression Formats (8 total - ALL must be documented):**
- Clock-time fractional: HH:MM:SS.sss (RULE-TIME-001)
- Clock-time frames: HH:MM:SS:FF (RULE-TIME-002)
- Offset hours: Nh (RULE-TIME-003)
- Offset minutes: Nm (RULE-TIME-004)
- Offset seconds: Ns (RULE-TIME-005)
- Offset milliseconds: Nms (RULE-TIME-006)
- Offset frames: Nf (RULE-TIME-007)
- Offset ticks: Nt (RULE-TIME-008)
**Status: X/8 formats documented**

**Parameter Attributes (11 total - ALL must be documented):**
- ttp:timeBase (RULE-PAR-001)
- ttp:frameRate (RULE-PAR-002)
- ttp:subFrameRate (RULE-PAR-003)
- ttp:frameRateMultiplier (RULE-PAR-004)
- ttp:tickRate (RULE-PAR-005)
- ttp:dropMode (RULE-PAR-006)
- ttp:clockMode (RULE-PAR-007)
- ttp:markerMode (RULE-PAR-008)
- ttp:cellResolution (RULE-PAR-009)
- ttp:pixelAspectRatio (RULE-PAR-010)
- ttp:profile (RULE-PAR-011)
**Status: X/11 parameters documented**

**Metadata Elements (5 total - ALL must be documented):**
- ttm:title (RULE-META-001)
- ttm:desc (RULE-META-002)
- ttm:copyright (RULE-META-003)
- ttm:agent (RULE-META-004)
- ttm:actor (RULE-META-005)
**Status: X/5 elements documented**

### Self-Validation Checklist
- All rule IDs unique
- Sequential numbering within categories
- All 6 content elements individually documented
- All 24 styling attributes individually documented
- All 8 time expression formats individually documented
- All 11 parameter attributes individually documented
- All 5 metadata elements individually documented
- Styling model complete (inheritance, chaining, referencing)
- Layout/region specification complete
- Profile specifications documented
- Generic IMPL rules (no pycaption-specific code)
- Test patterns present for all rules
- Source attribution present
- 90-120 total rules (exhaustive coverage target)
- 40-55 MUST rules documented

### Appendix D Cross-Check Results
- Total Appendix D features checked: 114
- Features with corresponding RULE-*: X/114
- Unmapped features: [list any gaps]
- **Status**: PASS (all features mapped) | FAIL (gaps found)

### Enum Value Verification Results
- Attributes verified: X/18 enum attributes
- Named colors verified: X/19
- Color formats verified: X/5
- Length units verified: X/4
- **Missing values found**: [list any]
- **Status**: PASS (all values present) | FAIL (missing values)

### TOC Section Coverage Results
- Normative sections checked: X
- Sections with rule references: X
- Unreferenced sections: [list any]
- **Status**: PASS | FAIL

### Overall Status
- **Completeness**: X% (100% required)
- **Appendix D**: PASS | FAIL
- **Enum Values**: PASS | FAIL
- **TOC Coverage**: PASS | FAIL
- **Overall Status**: PASS (all three checks pass) | FAIL (requires fixes)

**If FAIL**: Missing items listed above must be added before spec is complete.
```

**If validation FAILS:**
1. Identify missing rules/categories from Appendix D cross-check
2. Identify missing enum values from deep verification
3. Identify unreferenced TOC sections
4. Fetch additional source sections if needed (use section-by-section fetching from Step 1b)
5. Add missing rules and values
6. Re-validate until ALL THREE checks PASS

### Step 6: Source Attribution

Track sources for each rule:
- W3C TTML1 spec section (Primary)
- W3C TTML1 spec section number (e.g., Section 8.2.1)
- Additional sources (Confirms)
- Confidence: High/Medium/Low

Document conflicts and resolutions.

### Step 7: Update Web Sources

Append new URLs (if any) to `ai_artifacts/specs/dfxp/dfxp_web_sources.md`:
```markdown
- [New Source Title](https://url.example.com)
```

### Step 8: Post-Generation Validation Against Master Checklist

**CRITICAL:** After generating the spec, run this validation script. If it reports FAIL, fix the spec and re-run until PASS.

```python
import re

print("=" * 60)
print("POST-GENERATION VALIDATION: DFXP/TTML")
print("Checking dfxp_specs_summary.md against master_checklist.md")
print("=" * 60)

with open('ai_artifacts/specs/dfxp/master_checklist.md') as _f:
    checklist = _f.read()
with open('ai_artifacts/specs/dfxp/dfxp_specs_summary.md') as _f:
    spec = _f.read()

failures = []
warnings = []

# 1. Check all required rule IDs
rule_ids = re.findall(r'^- ((?:RULE|IMPL)-[A-Z]*-?\d{3})', checklist, re.M)
for rid in rule_ids:
    if rid not in spec:
        failures.append(f"MISSING RULE: {rid}")
found_rules = len(rule_ids) - len([f for f in failures if 'MISSING RULE' in f])
print(f"[1/7] Rule IDs: {found_rules}/{len(rule_ids)}")

# 2. Check required styling attributes
styling_section = re.search(r'## Required Styling Attributes.*?\n((?:- .+\n)+)', checklist)
if styling_section:
    attrs = re.findall(r'^- (tts:\w+)', styling_section.group(1), re.M)
    for attr in attrs:
        if attr not in spec:
            failures.append(f"MISSING STYLING ATTR: {attr}")
    print(f"[2/7] Styling attrs: {len(attrs) - len([f for f in failures if 'STYLING' in f])}/{len(attrs)}")

# 3. Check required content elements
elements_section = re.search(r'## Required Content Elements.*?\n((?:- .+\n)+)', checklist)
if elements_section:
    elements = re.findall(r'^- (\w+)', elements_section.group(1), re.M)
    for elem in elements:
        if not re.search(rf'\b{re.escape(elem)}\b', spec):
            warnings.append(f"MISSING ELEMENT: {elem}")
    print(f"[3/7] Content elements: {len(elements) - len([w for w in warnings if 'ELEMENT' in w])}/{len(elements)}")

# 4. Check required time formats
time_section = re.search(r'## Required Time Expression Formats.*?\n((?:- .+\n)+)', checklist)
if time_section:
    formats = re.findall(r'^- (.+?)$', time_section.group(1), re.M)
    for fmt in formats:
        # Extract the key identifier (e.g., "Nh", "HH:MM:SS.sss")
        key = fmt.split(':')[-1].strip() if ':' in fmt else fmt.strip()
        if not re.search(re.escape(key), spec):
            warnings.append(f"MISSING TIME FORMAT: {fmt.strip()}")
    print(f"[4/7] Time formats: {len(formats) - len([w for w in warnings if 'TIME FORMAT' in w])}/{len(formats)}")

# 5. Check required parameter attributes
param_section = re.search(r'## Required Parameter Attributes.*?\n((?:- .+\n)+)', checklist)
if param_section:
    params = re.findall(r'^- (ttp:\w+)', param_section.group(1), re.M)
    for param in params:
        if param not in spec:
            failures.append(f"MISSING PARAM: {param}")
    print(f"[5/7] Params: {len(params) - len([f for f in failures if 'PARAM' in f])}/{len(params)}")

# 6. Check required enum values
enum_sections = re.findall(r'### (.+?)\n((?:- .+\n)+)', checklist)
missing_enums = 0
total_enums = 0
for section_name, values_block in enum_sections:
    values = re.findall(r'^- (.+)$', values_block, re.M)
    for val in values:
        val_clean = val.strip()
        if val_clean.startswith('#') or val_clean.startswith('rgb'):
            # Color formats: check loosely
            total_enums += 1
            if not re.search(re.escape(val_clean.split('(')[0]), spec):
                missing_enums += 1
                warnings.append(f"MISSING ENUM [{section_name}]: {val_clean}")
        else:
            total_enums += 1
            if val_clean not in spec:
                if not re.search(re.escape(val_clean), spec, re.I):
                    missing_enums += 1
                    warnings.append(f"MISSING ENUM [{section_name}]: {val_clean}")
print(f"[6/7] Enum values: {total_enums - missing_enums}/{total_enums}")

# 7. Check severity distribution
severity_section = re.search(r'## Required Severity Distribution\n((?:.*\n)*)', checklist)
if severity_section:
    for match in re.finditer(r'- (MUST|SHOULD|MAY|MUST NOT): (\d+)', severity_section.group(1)):
        level, minimum = match.group(1), int(match.group(2))
        actual = len(re.findall(rf'Level:\*\*\s*{re.escape(level)}\b', spec))
        if actual < minimum:
            failures.append(f"SEVERITY {level}: found {actual}, need >= {minimum}")
        print(f"[7/7] {level}: {actual} (min {minimum}) {'PASS' if actual >= minimum else 'FAIL'}")

# Report
print("\n" + "=" * 60)
if failures:
    print(f"FAIL: {len(failures)} failures, {len(warnings)} warnings\n")
    for f in failures:
        print(f"  FAIL: {f}")
    for w in warnings[:15]:
        print(f"  WARN: {w}")
    if len(warnings) > 15:
        print(f"  ... and {len(warnings) - 15} more warnings")
    print("\nFix the spec and re-run this validation.")
else:
    print(f"PASS: All checks passed ({len(warnings)} warnings)")
    for w in warnings[:10]:
        print(f"  WARN: {w}")
print("=" * 60)
```

**If FAIL:** Fix the missing items in the spec, then re-run the validation script. Repeat until PASS.

---

## Output Files

1. **`ai_artifacts/specs/dfxp/dfxp_specs_summary.md`** - Complete specification with 90-120 rules
2. **`ai_artifacts/specs/dfxp/dfxp_web_sources.md`** - Updated URL list (if new sources found)

---

## Success Criteria (Exhaustive - 100% Required)

**Master Checklist Validation (CRITICAL - must PASS):**
- All rule IDs from `master_checklist.md` present in generated spec
- All 24 styling attributes present
- All 11 parameter attributes present
- All content elements present
- All enum values present (19 colors, 8 fonts, 4 units, 5 color formats, all attribute enums)
- Severity distribution meets minimums

**Completeness:**
- 90-120 total rules documented (RULE-* + IMPL-*)
- All 6 content elements individually documented with examples
- All 24 styling attributes individually documented with valid values and defaults
- All 8 time expression formats individually documented
- All 11 parameter attributes individually documented
- All 5 metadata elements individually documented
- Document structure, styling model, layout/region, profile, validation rules
- 12-15 IMPL rules (generic, no pycaption-specific code)

**Appendix D Cross-Check (supplements master checklist):**
- All 114 Appendix D feature designations checked
- Every feature maps to at least one RULE-*

**Quality:**
- Unique rule IDs (no duplicates)
- Sequential numbering within categories
- Valid test patterns for all rules
- Source attribution (W3C section references)
- Generic IMPL rules (no pycaption-specific references)

**Web Sources:**
- W3C TTML1 spec fetched section-by-section
- Appendix D fetched separately
- Fallback URLs attempted regardless of WebSearch availability
- All new sources added to dfxp_web_sources.md

---

## Context Window Optimization

**Token usage target:** < 60K per invocation (increased due to section-by-section fetching)

**Strategies:**
1. **Section-by-section fetching** - Fetch individual spec sections (#styling, #timing, etc.) instead of the full spec. Prevents truncation that caused missing details in single-fetch approach
2. **Targeted WebFetch prompts** - Each section fetch uses a focused prompt extracting only the needed details (enum values, MUST/SHOULD, valid syntax)
3. **Incremental writing** - Save spec file as rules are generated per section, not at end
4. **Process-then-discard** - Generate rules from each section immediately, don't hold raw spec text
5. **Fallback-first, search-second** - Try hardcoded URLs before WebSearch (faster, more reliable)
6. **Appendix D as checklist** - Fetch once, use as master list to avoid missing features

**Estimated token usage:**
- Section-by-section fetches (8-10 sections): 20-25K tokens
- Appendix D + Profiles fetch: 5K tokens
- Fallback source fetches: 5-8K tokens
- Rule generation (90-120 rules): 20-25K tokens
- Three-way validation (Appendix D + Enum + TOC + master checklist): 5-7K tokens
- **Total: ~58K tokens**

---

## Error Handling

- **dfxp_web_sources.md not found**: Create it with W3C TTML1 spec URL
- **No URLs in file**: Proceed with hardcoded fallback URLs
- **Individual section fetch fails**: Skip that section, try next; use built-in knowledge for skipped sections
- **Appendix D fetch fails**: Use the hardcoded feature checklist in Step 3a as fallback
- **Web search unavailable**: Skip entirely; use hardcoded fallback URLs from Step 2b (this is expected and handled)
- **Fallback URL fails (403/404/timeout)**: Log and skip; continue with remaining sources
- **Cannot write output**: Report error with path
- **Master checklist validation FAILS**: Fix missing items in spec and re-run validation
- **Appendix D cross-check FAILS**: Loop back to fetch missing sections and generate additional rules
- **Enum value verification FAILS**: Add missing values to the corresponding rules inline
- **TOC section coverage FAILS**: Investigate unreferenced sections; add rules or document as out-of-scope
