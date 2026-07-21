---
name: analyze-sami-docs
description: Generates EXHAUSTIVE SAMI specification summary from web sources with complete rule coverage, all elements/attributes/styling, and self-validation.
---

# analyze-sami-docs

## What this skill does

Generates comprehensive, exhaustive SAMI specification (`sami_spec_summary.md`) as single source of truth for compliance checking.

**Outputs:**
1. **40+ RULE-XXX specifications** with unique IDs and test patterns
2. **10+ IMPL-XXX requirements** (generic, no pycaption references)
3. **All elements** individually documented (SAMI, HEAD, BODY, STYLE, SYNC, P, BR, FONT, etc.)
4. **All styling properties** individually documented (CSS-based: color, background-color, font-family, font-size, font-weight, text-align, margin, etc.)
5. **Timing model** (SYNC START= millisecond-based)
6. **Multi-language support** (CLASS-based language switching)
7. **Self-validation report** (rule counts, completeness check)
8. **Source attribution** per rule

**Key:** Ensures NO requirements missed - exhaustive coverage from Microsoft SAMI 1.0 spec + web search.

**Pre-flight:** Read `.claude/skills/gotchas.md` before generating specs. Pay special attention to gotcha #3 (license attribution).

**Post-run:** If you discover a new gotcha during spec generation (a copyright/licensing trap, a web source that returns misleading data, or a spec structure issue that could cause downstream compliance check failures), append it to `.claude/skills/gotchas.md` with the same numbered format.

**Usage:**
```bash
/analyze-sami-docs
```
Single command - fetches web sources, performs comprehensive analysis, generates complete spec.

---

## Implementation

### Step 0: Check Existing Sources

**Read existing documentation:**
```bash
# Check what we already have
ls -la ai_artifacts/specs/SAMI/
cat ai_artifacts/specs/SAMI/sami_web_sources.md
```

**If `sami_spec_summary.md` exists:**
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

**Read URLs from `ai_artifacts/specs/SAMI/sami_web_sources.md`:**
```python
import re

with open("ai_artifacts/specs/SAMI/sami_web_sources.md") as _f:
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

#### Step 1a: Fetch each known source

For each source in `sami_web_sources.md`, **use the WebFetch tool** with:
- URL: the source URL
- Prompt: "Extract ALL specification details about SAMI (Synchronized Accessible Media Interchange) format. Include: document structure, elements, attributes, timing model, styling/CSS support, multi-language mechanism, file encoding requirements, and any MUST/SHOULD/MAY requirements."

**Track fetched URLs to avoid duplicates:**
```python
fetched_urls = set()
for source in existing_sources:
    fetched_urls.add(source['url'])
    print(f"Fetching: {source['title']}...")
    # Use WebFetch tool with url=source['url']
```

#### Step 1b: Context optimization

- Fetch sources sequentially, not in parallel (avoid context overflow)
- Extract text content only, discard HTML tags
- Process each source immediately after fetching, generate rules inline
- Save to temp files if needed, don't hold all in memory

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
    "SAMI Synchronized Accessible Media Interchange specification",
    "SAMI caption format complete reference elements attributes",
    "SAMI 1.0 Microsoft accessibility captioning format",
    "SAMI file format CSS styling properties supported",
    "SAMI caption multi-language support CLASS selector",
    "SAMI to SRT DFXP WebVTT conversion rules differences",
    "SAMI caption format best practices encoding",
    "SAMI .smi file format timing synchronization",
]

search_results = []
for query in search_queries:
    print(f"Searching: {query}")
    # Use the WebSearch tool for each query
    results = []  # populated by WebSearch tool
    search_results.append({'query': query, 'results': results})
```

**Identify new authoritative sources (skip already-fetched URLs):**
```python
import re

# Re-read existing sources (each block is independent)
with open("ai_artifacts/specs/SAMI/sami_web_sources.md") as _f:
    _sources_content = _f.read()
_existing_urls = {m[1] for m in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', _sources_content)}

# Combine with fetched_urls to avoid double-checking
_all_known_urls = _existing_urls | fetched_urls

# Agent: for each URL found in the search step above, check if it is
# authoritative (microsoft.com, w3.org, github.com, accessibility sites)
# and NOT in _all_known_urls. Collect matches into new_sources list:
new_sources = []  # Agent fills this from search results
# new_sources.append({'title': <title>, 'url': <url>, 'query': <query>})

print(f"\nFound {len(new_sources)} new authoritative sources")
```

#### Step 2b: Hardcoded fallback URLs (ALWAYS try these)

**CRITICAL:** WebSearch is often unavailable. These known-good URLs MUST be tried regardless of whether WebSearch worked. Skip any URL that is already in `fetched_urls` or `_existing_urls`.

```python
import re

# Re-read existing sources (each block is independent)
with open("ai_artifacts/specs/SAMI/sami_web_sources.md") as _f:
    _sources_content = _f.read()
_existing_urls = {m[1] for m in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', _sources_content)}
_all_known_urls = _existing_urls | fetched_urls

# Track new sources discovered in this block
new_sources = []

# Hardcoded authoritative SAMI supplementary sources
fallback_sources = [
    {
        'title': 'Microsoft: Understanding SAMI 1.0',
        'url': 'http://learn.microsoft.com/en-us/previous-versions/windows/desktop/dnacc/understanding-sami-1.0',
        'prompt': 'Extract ALL SAMI specification details: document structure, '
                  'HEAD/BODY/SYNC/P elements, STYLE section, CSS properties, '
                  'timing model, multi-language support, CLASS mechanism, '
                  'all attributes and valid values.',
    },
    {
        'title': 'W3C WAI SAMI Overview',
        'url': 'https://www.w3.org/WAI/sami.html',
        'prompt': 'Extract all SAMI format details: purpose, structure, '
                  'accessibility features, supported elements and styling.',
    },
    {
        'title': 'Recap Innovations: Caption Formats Guide',
        'url': 'https://recap-innovations.com/blog/understanding-caption-formats-complete-guide',
        'prompt': 'Extract ALL details about the SAMI format section: '
                  'structure, elements, timing, styling, limitations, '
                  'comparison with other formats.',
    },
    {
        'title': 'Wikipedia: SAMI Format',
        'url': 'https://en.wikipedia.org/wiki/SAMI',
        'prompt': 'Extract all technical details about SAMI format: history, '
                  'structure, elements, attributes, timing, CSS support, '
                  'player support, limitations.',
    },
    {
        'title': 'Microsoft SAMI Reference (MSDN Archive)',
        'url': 'https://learn.microsoft.com/en-us/windows/win32/wmp/adding-closed-captions-to-digital-media',
        'prompt': 'Extract SAMI-related technical details: how Windows Media Player '
                  'processes SAMI files, supported features, limitations.',
    },
    {
        'title': 'Subtitle Edit SAMI Documentation',
        'url': 'https://www.nikse.dk/subtitleedit/formats',
        'prompt': 'Extract SAMI format details: structure, supported features, '
                  'known quirks, conversion notes.',
    },
    {
        'title': 'CaptionHub SAMI Format Guide',
        'url': 'https://captionhub.com/resources/sami-format',
        'prompt': 'Extract SAMI format technical details and best practices.',
    },
    {
        'title': '3Play Media Caption Format Guide',
        'url': 'https://www.3playmedia.com/blog/caption-format-guide/',
        'prompt': 'Extract SAMI/SMI format details: structure, limitations, '
                  'comparison with other formats, conversion considerations.',
    },
]

# Try each fallback source; skip if already known or already fetched
for source in fallback_sources:
    if source['url'] in _all_known_urls:
        print(f"   Skipping (already known): {source['title']}")
        continue
    try:
        print(f"Fetching fallback: {source['title']}...")
        # Use the WebFetch tool with url=source['url'] and prompt=source['prompt']
        fetched_urls.add(source['url'])
        new_sources.append({'title': source['title'], 'url': source['url']})
        print(f"   Success: {source['title']}")
    except Exception:
        print(f"   Failed (skipping): {source['title']}")
        continue
```

**Fetch new search-discovered sources (if WebSearch was available):**
```python
# Agent: for each source in new_sources from search (up to 5),
# use WebFetch to retrieve the content. SKIP if URL is in fetched_urls.
# for source in new_sources[:5]:
#     if source['url'] in fetched_urls:
#         continue
#     print(f"Fetching: {source['title']}")
#     # Use the WebFetch tool with url=source['url']
#     fetched_urls.add(source['url'])
```

### Step 3: Exhaustive Completeness Verification

**CRITICAL:** Verify ALL these areas covered in fetched content (100% coverage required):

**Document Structure (HTML-like):**
- Root element: `<SAMI>` (case-insensitive)
- `<HEAD>` section (metadata + styling)
- `<BODY>` section (content)
- `<STYLE>` element within HEAD (CSS-like styling)
- `<SYNC>` elements (timing markers)
- `<P>` elements (text content per language/class)
- Optional: `<BR>`, `<FONT>`, `<B>`, `<I>`, `<U>`, `<SPAN>`
- Optional: `<TITLE>` within HEAD
- Optional: `<SAMIParam>` for parameters
- File extension: .smi or .sami
- MIME type: application/x-sami

**Timing Model:**
- `SYNC START=` attribute (milliseconds from media start)
- Millisecond-based (integer values)
- No end time — caption ends when next SYNC begins
- Empty `<P>` with `&nbsp;` to clear captions
- Timing is absolute (from beginning of media)

**Multi-Language Support:**
- CSS class selectors in STYLE section
- `CLASS` attribute on `<P>` elements
- SAMIParam `Name="Langxx"` declarations
- Multiple `<P>` elements per SYNC for different languages
- Language class naming convention (e.g., ENCC, ESCC)

**Styling (CSS Subset):**
- Supported properties in STYLE section:
  - `color` (text color)
  - `background-color` (background)
  - `font-family` (font name)
  - `font-size` (size in pt, px)
  - `font-weight` (bold)
  - `font-style` (italic)
  - `text-align` (left, center, right)
  - `margin-left`, `margin-right`, `margin-top`, `margin-bottom`
  - `text-decoration` (underline)
  - `background-image` (for background)
- P selector styling (global paragraph style)
- Class-based styling (.ENCC, .ESCC, etc.)
- Inline styling via HTML attributes (STYLE=, COLOR=, FACE=, SIZE=)

**Inline HTML Elements:**
- `<BR>` — line break
- `<FONT>` — font styling (COLOR, FACE, SIZE attributes)
- `<B>` — bold
- `<I>` — italic
- `<U>` — underline
- `<SPAN>` — inline container with style
- `<A>` — hyperlink (rarely used)

**SAMIParam Element:**
- Language declaration parameters
- Source media parameters
- Player configuration

**Character Encoding:**
- Originally Windows-1252 (Western European)
- Unicode/UTF-8 support in modern implementations
- HTML entities supported (&amp;, &lt;, &gt;, &nbsp;, &quot;)
- Numeric character references (&#NNN;)

**Edge Cases & Common Pitfalls:**
- Case-insensitive element/attribute names
- Missing closing tags (tolerant parsing required)
- Non-standard HTML in STYLE section
- Comments: `<!-- -->` within HEAD or BODY
- Empty P tags for clearing (with &nbsp; or blank Class)
- SYNC with Start=0 (beginning of media)
- Multiple P elements within same SYNC
- Overlapping styles (inline vs class vs P selector)
- Windows line endings (CRLF)
- BOM (Byte Order Mark) at file start

**Known Limitations:**
- No standard end time (implicit from next SYNC)
- CSS support is limited subset (not full CSS)
- No positioning beyond margins and text-align
- No animation or transition support
- Microsoft-proprietary (limited cross-platform support)
- No official W3C standard (informal specification)
- No support for vertical text
- No cue identifier mechanism

**Completeness Checklist (MUST achieve 100%):**
```python
completeness_check = {
    'document_structure': {
        'sami_root': False,       # <SAMI> root element
        'head_section': False,    # <HEAD> section
        'body_section': False,    # <BODY> section
        'style_element': False,   # <STYLE> in HEAD
        'sync_element': False,    # <SYNC> elements
        'p_element': False,       # <P> elements
        'title_element': False,   # <TITLE> optional
        'samiparam': False,       # <SAMIParam> optional
    },
    'timing_model': {
        'sync_start': False,      # SYNC START= milliseconds
        'implicit_end': False,    # End when next SYNC begins
        'clear_mechanism': False, # Empty P / &nbsp; to clear
        'absolute_timing': False, # From media start
    },
    'multi_language': {
        'class_selector': False,  # CLASS= on P elements
        'style_classes': False,   # .ENCC, .ESCC in STYLE
        'samiparam_lang': False,  # SAMIParam language declarations
        'multiple_p': False,      # Multiple P per SYNC
    },
    'styling_properties': {
        'color': False,             # color
        'background_color': False,  # background-color
        'font_family': False,       # font-family
        'font_size': False,         # font-size
        'font_weight': False,       # font-weight
        'font_style': False,        # font-style
        'text_align': False,        # text-align
        'margin': False,            # margin-left/right/top/bottom
        'text_decoration': False,   # text-decoration
    },
    'inline_elements': {
        'br': False,      # <BR> line break
        'font': False,    # <FONT> with COLOR/FACE/SIZE
        'bold': False,    # <B>
        'italic': False,  # <I>
        'underline': False, # <U>
        'span': False,    # <SPAN>
    },
    'encoding': {
        'windows_1252': False,    # Default encoding
        'utf8': False,            # Modern encoding
        'html_entities': False,   # &amp; &lt; &gt; &nbsp;
        'numeric_refs': False,    # &#NNN;
    },
    'edge_cases': {
        'case_insensitive': False,  # Element/attribute names
        'tolerant_parsing': False,  # Missing close tags
        'comments': False,          # <!-- -->
        'empty_clear': False,       # Empty P for clearing
        'bom': False,               # Byte Order Mark
    },
}
```

**If new sources found during search, update sami_web_sources.md:**
```python
import re as _re, os
_sources_path = "ai_artifacts/specs/SAMI/sami_web_sources.md"
if os.path.exists(_sources_path):
    with open(_sources_path) as _f:
        _current = _f.read()
    _known_urls = {m[1] for m in _re.findall(r'\[([^\]]+)\]\(([^)]+)\)', _current)}
    # Agent: for each new source discovered above, if url not in _known_urls:
    #   append: f"- [{title}]({url})\n"
    # Then write back to _sources_path
    print("Source file update complete")
else:
    print(f"WARNING: {_sources_path} not found — skipping source update")
```

### Step 4: Generate Exhaustive Specification

Create `ai_artifacts/specs/SAMI/sami_spec_summary.md`.

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

**Part 1 (Document Structure):** Root `<SAMI>` element, HEAD/BODY sections, STYLE element, SYNC/P elements
**Part 2 (Timing Model):** SYNC START= milliseconds, implicit end times, clearing mechanism
**Part 3 (Multi-Language):** CLASS attribute, language classes, SAMIParam declarations
**Part 4 (Styling Properties):** All CSS properties supported (color, font, margin, text-align, etc.)
**Part 5 (Inline Elements):** BR, FONT, B, I, U, SPAN with attributes
**Part 6 (Character Encoding):** Windows-1252, UTF-8, HTML entities, numeric references
**Part 7 (SAMIParam):** Language parameters, source parameters
**Part 8 (Parsing Requirements):** Case insensitivity, tolerant parsing, comment handling
**Part 9 (Conversion Rules):** Mapping to/from other formats (DFXP, WebVTT, SRT, SCC)
**Part 10 (Implementation):** Generic IMPL-* rules for Parser/Writer/Validator
**Part 11 (Validation Summary):** Rule counts, self-validation report
**Part 12 (Quick Reference):** Tables for elements, CSS properties, timing format

**Target Rule Counts (Exhaustive):**
- **RULE-DOC-###**: 6-8 document structure rules (SAMI, HEAD, BODY, STYLE, SYNC, P)
- **RULE-TIME-###**: 4-6 timing rules (SYNC START, implicit end, clearing, absolute)
- **RULE-LANG-###**: 4-6 multi-language rules (CLASS, selectors, SAMIParam)
- **RULE-STY-###**: 10-14 styling rules (all CSS properties + inheritance/cascade)
- **RULE-ELEM-###**: 6-8 inline element rules (BR, FONT, B, I, U, SPAN)
- **RULE-ENC-###**: 4-5 encoding rules (charset, entities, BOM)
- **RULE-PARSE-###**: 4-6 parsing rules (case insensitivity, tolerant, comments)
- **RULE-CONV-###**: 4-6 conversion rules (mapping to DFXP, VTT, SRT)
- **IMPL-###**: 10-12 implementation requirements (parser, writer, validator)
- **Total: 55-75 rules** (comprehensive coverage)

**Level Distribution (Exhaustive):**
- **MUST**: 25-35 rules (critical requirements)
- **SHOULD**: 15-20 rules (recommended practices)
- **MAY**: 8-12 rules (optional features)
- **MUST NOT**: 3-5 rules (forbidden patterns)

**Generate spec with incremental writing (context-efficient):**
```python
from datetime import datetime
import os

os.makedirs("ai_artifacts/specs/SAMI", exist_ok=True)
spec_path = "ai_artifacts/specs/SAMI/sami_spec_summary.md"

# Write spec header
spec_content = f"""# SAMI (Synchronized Accessible Media Interchange) Specification - Complete Reference

**Generated**: {datetime.now().strftime("%Y-%m-%d")}
**Sources**: Microsoft SAMI 1.0 Specification, W3C WAI, Web Research
**Version**: SAMI 1.0 (Microsoft proprietary format)
**Total Rules**: [TO BE CALCULATED]
**License**: Requirements summarized from Microsoft documentation and public references.

---

"""

with open(spec_path, "w") as _f:
    _f.write(spec_content)

# Then generate and append each part section by section:
# Part 1: Document Structure rules
# Part 2: Timing Model rules
# ... continue for all parts (Parts 1-12)
# Append each part with: with open(spec_path, "a") as _f: _f.write(part)
```

### Step 5: Exhaustive Quality Validation

**Structure checks:**
- All rule IDs unique
- Sequential numbering within each category
- Valid test patterns (regex, algorithm)
- Level indicators present (MUST/SHOULD/MAY/MUST NOT)

**Content checks (Exhaustive - 100% required):**
- 55-75 total rules documented (RULE-* + IMPL-*)
- 25-35 MUST rules (all critical requirements)
- 15-20 SHOULD rules (best practices)
- 8-12 MAY rules (optional features)
- 10-12 IMPL-* rules (generic, no pycaption references)
- All 8 document structure elements documented
- All 9+ styling properties documented
- All 6 inline elements documented
- Timing model complete
- Multi-language mechanism complete
- Encoding requirements complete
- Parsing rules complete
- Conversion mapping rules present

**Generate exhaustive validation report in spec file:**
```markdown
## Part 11: Exhaustive Validation Summary

### Rule Counts by Category
- RULE-DOC-###: X document structure rules (Target: 6-8)
- RULE-TIME-###: X timing rules (Target: 4-6)
- RULE-LANG-###: X multi-language rules (Target: 4-6)
- RULE-STY-###: X styling rules (Target: 10-14)
- RULE-ELEM-###: X inline element rules (Target: 6-8)
- RULE-ENC-###: X encoding rules (Target: 4-5)
- RULE-PARSE-###: X parsing rules (Target: 4-6)
- RULE-CONV-###: X conversion rules (Target: 4-6)
- IMPL-###: X implementation requirements (Target: 10-12)
- **Total: Y rules** (Target: 55-75 for exhaustive coverage)

### By Level (Exhaustive Distribution)
- MUST: X rules (Target: 25-35)
- SHOULD: X rules (Target: 15-20)
- MAY: X rules (Target: 8-12)
- MUST NOT: X rules (Target: 3-5)

### Coverage Verification (100% Required)

**Document Structure Elements (8 total - ALL must be documented):**
- SAMI (root element)
- HEAD
- BODY
- STYLE
- SYNC
- P
- TITLE
- SAMIParam
**Status: X/8 elements documented**

**Styling Properties (9+ total - ALL must be documented):**
- color
- background-color
- font-family
- font-size
- font-weight
- font-style
- text-align
- margin (left/right/top/bottom)
- text-decoration
**Status: X/9 properties documented**

**Inline Elements (6 total - ALL must be documented):**
- BR
- FONT (COLOR, FACE, SIZE)
- B
- I
- U
- SPAN
**Status: X/6 elements documented**

**Timing Model (4 aspects - ALL must be documented):**
- SYNC START= milliseconds
- Implicit end time
- Clear/blank mechanism
- Absolute timing from media start
**Status: X/4 aspects documented**

**Multi-Language (4 aspects - ALL must be documented):**
- CLASS attribute on P
- CSS class selectors in STYLE
- SAMIParam language declarations
- Multiple P per SYNC
**Status: X/4 aspects documented**

### Self-Validation Checklist
- All rule IDs unique
- Sequential numbering within categories
- All document structure elements documented
- All styling properties documented
- All inline elements documented
- Timing model complete
- Multi-language mechanism complete
- Encoding requirements present
- Parsing rules present (case insensitivity, tolerant)
- Conversion mapping rules present
- Generic IMPL rules (no pycaption-specific code)
- Test patterns present for all rules
- Source attribution present
- 55-75 total rules (exhaustive coverage target)
- 25-35 MUST rules documented

### Overall Status
- **Completeness**: X% (100% required)
- **Overall Status**: PASS (all checks pass) | FAIL (requires fixes)

**If FAIL**: Missing items listed above must be added before spec is complete.
```

**If validation FAILS:**
1. Identify missing rules/categories
2. Fetch additional sources if needed
3. Add missing rules
4. Re-validate until PASS

### Step 6: Source Attribution

Track sources for each rule:
- Microsoft SAMI 1.0 documentation (Primary)
- W3C WAI reference (Confirms)
- Additional web sources (Supplements)
- Confidence: High/Medium/Low

Document conflicts and resolutions.

### Step 7: Update Web Sources

Append new URLs (if any) to `ai_artifacts/specs/SAMI/sami_web_sources.md`:
```markdown
- [New Source Title](https://url.example.com)
```

**CRITICAL:** Only add URLs that were actually successfully fetched and provided useful content. Do NOT add URLs that returned 404, 403, or empty content.

### Step 8: Post-Generation Validation

```python
import re

print("=" * 60)
print("POST-GENERATION VALIDATION: SAMI")
print("Checking sami_spec_summary.md")
print("=" * 60)

with open('ai_artifacts/specs/SAMI/sami_spec_summary.md') as _f:
    spec = _f.read()

failures = []
warnings = []

# 1. Check rule count
rule_ids = set(re.findall(r'\*\*\[(RULE-[A-Z]+-\d{3}|IMPL-\d{3})\]\*\*', spec))
print(f"[1/6] Total rules: {len(rule_ids)} (target: 55-75)")
if len(rule_ids) < 55:
    failures.append(f"Too few rules: {len(rule_ids)} (minimum 55)")

# 2. Check required elements
required_elements = ['SAMI', 'HEAD', 'BODY', 'STYLE', 'SYNC', '<P>']
for elem in required_elements:
    if elem not in spec:
        failures.append(f"MISSING ELEMENT: {elem}")
print(f"[2/6] Required elements: {len(required_elements) - len([f for f in failures if 'ELEMENT' in f])}/{len(required_elements)}")

# 3. Check required styling properties
required_props = ['color', 'background-color', 'font-family', 'font-size',
                  'font-weight', 'font-style', 'text-align', 'margin', 'text-decoration']
for prop in required_props:
    if prop not in spec:
        warnings.append(f"MISSING PROPERTY: {prop}")
print(f"[3/6] Styling properties: {len(required_props) - len([w for w in warnings if 'PROPERTY' in w])}/{len(required_props)}")

# 4. Check timing model
timing_terms = ['START=', 'millisecond', 'implicit end', 'clear']
for term in timing_terms:
    if term.lower() not in spec.lower():
        warnings.append(f"MISSING TIMING: {term}")
print(f"[4/6] Timing model: {len(timing_terms) - len([w for w in warnings if 'TIMING' in w])}/{len(timing_terms)}")

# 5. Check multi-language
lang_terms = ['CLASS', 'multi-language', 'SAMIParam']
for term in lang_terms:
    if term not in spec:
        warnings.append(f"MISSING LANG: {term}")
print(f"[5/6] Multi-language: {len(lang_terms) - len([w for w in warnings if 'LANG' in w])}/{len(lang_terms)}")

# 6. Check severity distribution
must_count = len(re.findall(r'\*\*Level:\*\*\s*MUST\b', spec))
should_count = len(re.findall(r'\*\*Level:\*\*\s*SHOULD\b', spec))
print(f"[6/6] MUST: {must_count} (min 25), SHOULD: {should_count} (min 15)")
if must_count < 25:
    failures.append(f"SEVERITY MUST: found {must_count}, need >= 25")
if should_count < 15:
    warnings.append(f"SEVERITY SHOULD: found {should_count}, need >= 15")

# Report
print("\n" + "=" * 60)
if failures:
    print(f"FAIL: {len(failures)} failures, {len(warnings)} warnings\n")
    for f in failures:
        print(f"  FAIL: {f}")
    for w in warnings[:10]:
        print(f"  WARN: {w}")
    print("\nFix the spec and re-run this validation.")
else:
    print(f"PASS: All checks passed ({len(warnings)} warnings)")
    for w in warnings[:5]:
        print(f"  WARN: {w}")
print("=" * 60)
```

**If FAIL:** Fix the missing items in the spec, then re-run the validation script. Repeat until PASS.

---

## Output Files

1. **`ai_artifacts/specs/SAMI/sami_spec_summary.md`** - Complete specification with 55-75 rules
2. **`ai_artifacts/specs/SAMI/sami_web_sources.md`** - Updated URL list (if new sources found)

---

## Success Criteria (Exhaustive - 100% Required)

**Completeness:**
- 55-75 total rules documented (RULE-* + IMPL-*)
- All 8 document structure elements documented
- All 9+ styling properties documented
- All 6 inline elements documented
- Timing model fully documented (4 aspects)
- Multi-language mechanism fully documented (4 aspects)
- Encoding requirements documented
- Parsing rules documented (case insensitivity, tolerant parsing)
- Conversion mapping rules present (to/from DFXP, WebVTT, SRT)
- 10-12 IMPL rules (generic, no pycaption-specific code)

**Quality:**
- Unique rule IDs (no duplicates)
- Sequential numbering within categories
- Valid test patterns for all rules
- Source attribution (Microsoft docs, W3C, web references)
- Generic IMPL rules (no pycaption-specific references)

**Web Sources:**
- All URLs in sami_web_sources.md fetched first
- Extensive web search performed (8 queries minimum)
- No URL checked twice (deduplication enforced)
- All NEW sources added to sami_web_sources.md
- Fallback URLs attempted regardless of WebSearch availability

---

## Context Window Optimization

**Token usage target:** < 40K per invocation

**Strategies:**
1. **Source deduplication** - Track fetched_urls set, never fetch same URL twice
2. **Targeted WebFetch prompts** - Each fetch uses a focused prompt
3. **Incremental writing** - Save spec file as rules are generated, not at end
4. **Process-then-discard** - Generate rules from each source immediately
5. **Fallback-first, search-second** - Try hardcoded URLs before WebSearch
6. **SAMI is simpler than TTML** - Fewer sections, fewer attributes, faster generation

**Estimated token usage:**
- Known source fetches (3 URLs): 8-10K tokens
- Fallback source fetches (5-8 sources): 10-15K tokens
- Web search + new source fetches: 5-8K tokens
- Rule generation (55-75 rules): 12-15K tokens
- Validation: 3-5K tokens
- **Total: ~40K tokens**

---

## Error Handling

- **sami_web_sources.md not found**: Create it with Microsoft SAMI URL
- **No URLs in file**: Proceed with hardcoded fallback URLs
- **WebFetch fails for a URL**: Log and skip; continue with remaining sources
- **Web search unavailable**: Skip entirely; use hardcoded fallback URLs (expected)
- **Fallback URL fails (403/404/timeout)**: Log and skip; continue
- **Cannot write output**: Report error with path
- **Validation FAILS**: Fix missing items in spec and re-run validation
- **Duplicate URL detected**: Skip silently (already in fetched_urls set)
