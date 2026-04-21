---
name: analyze-vtt-docs
description: Generates EXHAUSTIVE WebVTT specification summary from web sources with complete rule coverage, all tags/settings/entities, and self-validation.
---

# analyze-vtt-docs

## What this skill does

Generates comprehensive, exhaustive WebVTT specification (`vtt_specs_summary.md`) as single source of truth for compliance checking.

**Outputs:**
1. **50+ RULE-XXX specifications** with unique IDs and test patterns
2. **12+ IMPL-XXX requirements** (generic, no pycaption references)
3. **All 8 markup tags** individually documented (c, i, b, u, v, lang, ruby, timestamp)
4. **All 8 cue settings** individually documented (vertical, line, position, size, align, region, etc.)
5. **All required HTML entities** (&amp;, &lt;, &gt;, &nbsp;, &lrm;, &rlm;)
6. **Region specifications** complete (REGION block properties)
7. **STYLE/NOTE blocks** documented
8. **Self-validation report** (rule counts, completeness check)
9. **Source attribution** per rule

**Key:** Ensures NO requirements missed - exhaustive coverage from W3C spec + MDN + web search.

**Usage:**
```bash
/analyze-vtt-docs
```
Single command - fetches web sources, performs comprehensive analysis, generates complete spec.

---

## Implementation

### Step 0: Check Existing Sources

**Read existing documentation:**
```bash
# Check what we already have
ls -la pycaption/specs/vtt/
cat pycaption/specs/vtt/vtt_web_sources.md
```

**If `vtt_specs_summary.md` exists:**
- Read it to assess completeness
- Identify gaps using completeness checklist (Step 2)
- Only fetch new sources if gaps exist

### Step 1: Fetch Known Web Sources (WebFetch Tool Required)

**IMPORTANT:** This step requires the WebFetch tool to be loaded first.

**Check if WebFetch is available, load if needed:**
```python
# WebFetch is a deferred tool - load it before use
# Use ToolSearch to load WebFetch
```

**Read URLs from `pycaption/specs/vtt/vtt_web_sources.md`:**
```python
import re

sources_content = read("pycaption/specs/vtt/vtt_web_sources.md")

# Extract URLs from markdown links: [Text](URL)
url_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
existing_sources = []

for match in re.findall(url_pattern, sources_content):
    title, url = match
    existing_sources.append({'title': title, 'url': url})

print(f"📋 Found {len(existing_sources)} existing sources")
for s in existing_sources:
    print(f"   - {s['title']}")
```

**Fetch W3C WebVTT Specification (Primary Source):**
```python
# Fetch W3C spec - most authoritative source
w3c_url = 'https://www.w3.org/TR/webvtt1/'
print(f"🌐 Fetching W3C WebVTT Specification...")

w3c_content = WebFetch(w3c_url)

# Extract key sections (focus on specification text, skip navigation)
# Store in temporary file for processing
write("/tmp/w3c_webvtt_spec.txt", w3c_content)
```

**Fetch MDN Documentation (Supplementary):**
```python
# MDN provides practical examples and browser compatibility info
mdn_url = 'https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API'
print(f"🌐 Fetching MDN WebVTT Documentation...")

mdn_content = WebFetch(mdn_url)
write("/tmp/mdn_webvtt_docs.txt", mdn_content)
```

**Context optimization:**
- Fetch sources sequentially, not in parallel (avoid context overflow)
- Extract text content only, discard HTML tags
- Focus on specification sections
- Save to temp files, don't hold in memory

### Step 2: Comprehensive Web Search for Missing Details

**Perform targeted web searches to fill gaps:**

```python
# Define search queries for comprehensive coverage
search_queries = [
    "WebVTT specification complete W3C",
    "WebVTT cue settings all options",
    "WebVTT markup tags complete list",
    "WebVTT HTML entities supported",
    "WebVTT REGION block specification",
    "WebVTT STYLE block CSS",
    "WebVTT NOTE comment syntax",
    "WebVTT timestamp format validation",
    "WebVTT best practices implementation",
    "WebVTT validation rules MUST SHOULD",
]

# Execute searches and collect results
search_results = []
for query in search_queries:
    print(f"🔍 Searching: {query}")
    results = WebSearch(query)
    search_results.append({
        'query': query,
        'results': results
    })
    # Brief delay to avoid rate limiting
```

**Identify high-value sources from search results:**
```python
# Filter for authoritative sources:
# - w3.org (W3C specs)
# - developer.mozilla.org (MDN)
# - webvtt.org (if exists)
# - github.com/w3c (spec repos)
# - Major browser documentation

new_sources = []
for result in search_results:
    for item in result['results']:
        url = item['url']
        if any(domain in url for domain in ['w3.org', 'developer.mozilla.org', 'github.com/w3c']):
            if url not in [s['url'] for s in existing_sources]:
                new_sources.append({
                    'title': item['title'],
                    'url': url,
                    'query': result['query']
                })
                print(f"   ✅ New source found: {item['title']}")

print(f"\n📚 Found {len(new_sources)} new authoritative sources")
```

**Fetch new sources:**
```python
for source in new_sources[:5]:  # Limit to top 5 to manage context
    print(f"🌐 Fetching: {source['title']}")
    content = WebFetch(source['url'])
    # Extract and save relevant sections
    write(f"/tmp/webvtt_source_{len(existing_sources) + new_sources.index(source)}.txt", content)
```

### Step 3: Exhaustive Completeness Verification

**CRITICAL:** Verify ALL these areas covered in fetched content (100% coverage required):

**File Format:**
- Header: "WEBVTT" exact match (case-sensitive), optional space + comment
- UTF-8 encoding requirement (MUST)
- Optional UTF-8 BOM handling
- Line endings: CR, LF, CRLF all valid
- Blank line after header before first cue

**Timestamp Format:**
- Format: `[HH:]MM:SS.mmm` (hours optional if < 1 hour)
- Milliseconds required (3 digits)
- Separator: ` --> ` (spaces required)
- Start time <= end time (MUST)
- Sequential ordering (SHOULD)
- Valid ranges: HH (00-99), MM (00-59), SS (00-59), mmm (000-999)

**Cue Structure:**
- Optional cue identifier (any text except "-->", "NOTE", or looks like timestamp)
- Required: start --> end [optional settings]
- Cue payload (can span multiple lines)
- Blank line terminates cue

**Cue Settings:**
- vertical: rl, lr (text direction)
- line: N or N% (vertical position, can be negative)
- position: N% (horizontal position 0-100)
- size: N% (cue box width 0-100)
- align: start, center, end, left, right
- region: region_id (reference to defined region)

**Tags (Markup):**
- Class spans: `<c.classname>text</c>` (multiple classes: `<c.class1.class2>`)
- Italics: `<i>text</i>`
- Bold: `<b>text</b>`
- Underline: `<u>text</u>`
- Ruby: `<ruby>base<rt>annotation</rt></ruby>`
- Voice: `<v Speaker>text</v>` (optional annotation)
- Language: `<lang code>text</lang>`
- Internal timestamps: `<00:01:23.456>` (karaoke-style)
- Tag nesting rules and restrictions
- Escape sequences: &amp; &lt; &gt; &nbsp; &lrm; &rlm;

**Regions (Optional Feature):**
- REGION block definition before cues
- Properties: id, width, lines, regionanchor, viewportanchor, scroll
- Association with cues via `region:id` setting

**Special Blocks:**
- NOTE blocks (comments, ignored by parser)
- STYLE blocks (CSS for cue pseudo-elements)
- Syntax and placement rules

**Validation Requirements:**
- All MUST requirements from W3C spec
- All SHOULD requirements
- All MAY optional features
- All MUST NOT forbidden patterns
- Error handling strategies

**Edge Cases & Common Pitfalls:**
- Extra text on first line after "WEBVTT"
- Missing milliseconds in timestamps
- Missing spaces around -->
- Invalid cue settings
- Unclosed tags
- Un-escaped special characters
- Percentage out of range (0-100)
- Start > end time
- Invalid UTF-8 sequences

**Implementation Requirements:**
- Parser requirements (UTF-8 decoder, timestamp parser, tag parser, settings parser)
- Writer requirements (UTF-8 encoder, escaping, formatting)
- Error handling strategies
- Performance considerations

**Browser Compatibility:**
- Feature support across browsers
- Cue settings support
- Region support (limited)
- STYLE block support (varies)
- Graceful degradation

**Completeness Checklist (MUST achieve 100%):**
```python
completeness_check = {
    'file_format': {
        'header': True/False,  # WEBVTT signature
        'encoding': True/False,  # UTF-8
        'bom': True/False,  # BOM handling
        'line_endings': True/False,  # CR/LF/CRLF
        'blank_line': True/False,  # After header
    },
    'timestamps': {
        'format': True/False,  # [HH:]MM:SS.mmm
        'validation': True/False,  # Start <= end
        'ranges': True/False,  # MM/SS 00-59
        'milliseconds': True/False,  # Exactly 3 digits
        'separator': True/False,  # ` --> `
    },
    'cue_settings': {
        'vertical': True/False,  # rl/lr
        'line': True/False,  # N or N%
        'position': True/False,  # N%
        'size': True/False,  # N%
        'align': True/False,  # start/center/end/left/right
        'region': True/False,  # region_id
    },
    'markup_tags': {
        'class_span': True/False,  # <c>
        'italics': True/False,  # <i>
        'bold': True/False,  # <b>
        'underline': True/False,  # <u>
        'voice': True/False,  # <v>
        'language': True/False,  # <lang>
        'ruby': True/False,  # <ruby><rt>
        'timestamp': True/False,  # <00:01:23.456>
    },
    'html_entities': {
        'required': True/False,  # &amp; &lt; &gt; &nbsp; &lrm; &rlm;
        'escaping': True/False,  # Escape rules
    },
    'regions': {
        'region_block': True/False,  # REGION definition
        'properties': True/False,  # id/width/lines/anchors/scroll
    },
    'special_blocks': {
        'note': True/False,  # NOTE comments
        'style': True/False,  # STYLE CSS
    },
    'validation': {
        'must_rules': True/False,  # All MUST requirements
        'should_rules': True/False,  # All SHOULD requirements
        'error_handling': True/False,  # Error strategies
    },
}

# Calculate completeness percentage
total_items = sum(len(v) for v in completeness_check.values())
covered_items = sum(sum(v.values()) for v in completeness_check.values())
completeness = (covered_items / total_items) * 100

print(f"📊 Completeness: {completeness:.1f}% ({covered_items}/{total_items} items)")

if completeness < 100:
    print("⚠️  Missing items - additional web search required")
    # List what's missing
    for category, items in completeness_check.items():
        missing = [k for k, v in items.items() if not v]
        if missing:
            print(f"   {category}: {', '.join(missing)}")
```

**If new sources found during search, update vtt_web_sources.md:**
```python
if new_sources:
    # Append to vtt_web_sources.md
    current_sources = read("pycaption/specs/vtt/vtt_web_sources.md")
    
    for source in new_sources:
        if source['url'] not in current_sources:
            current_sources += f"- [{source['title']}]({source['url']})\n"
    
    write("pycaption/specs/vtt/vtt_web_sources.md", current_sources)
    print(f"✅ Updated vtt_web_sources.md with {len(new_sources)} new sources")
```

### Step 4: Generate Exhaustive Specification

Create `pycaption/specs/vtt/vtt_specs_summary.md` using structure from `skill_part2.md`.

**Key differences from old approach:**
- Rule-based format with unique IDs (RULE-FMT-###, RULE-TIME-###, etc.)
- Generic IMPL-### rules (no pycaption-specific code references)
- Test patterns for automated validation
- Level indicators (MUST/SHOULD/MAY/MUST NOT)
- Source attribution per rule

**See `skill_part2.md` for complete structure template.**

**Rule Format:**
```markdown
**[RULE-XXX-###]** Brief requirement
- **Requirement:** What must be true
- **Level:** MUST | SHOULD | MAY | MUST NOT
- **Validation:** How to check
- **Test Pattern:** Regex or algorithm
- **Sources:** [Attribution]
```

**Implementation Rule Format (GENERIC):**
```markdown
**[IMPL-XXX-###]** Component MUST do X
- **Spec Rule:** RULE-XXX-###
- **Component:** Parser | Writer | Validator
- **Implementation Requirement:** What ANY compliant implementation must do
- **Expected Behavior:** Input → Output examples
- **Validation Criteria:** What to verify
- **Common Patterns:** Correct vs incorrect (generic)
- **Test Coverage:** Required test scenarios
```

**Critical requirements** (must be included as rules):

**Part 1 (File Format):** Header format, UTF-8, BOM handling, blank line after header  
**Part 2 (Timestamps):** Format `[HH:]MM:SS.mmm`, ranges, start<=end, sequential  
**Part 3 (Cue Structure):** Identifier restrictions, ` --> ` separator, blank line terminator  
**Part 4 (Cue Settings):** vertical, line, position, size, align, region (6 settings)  
**Part 5 (Tags):** c, i, b, u, v, lang, ruby, timestamp (8 tags), closing rules, escaping  
**Part 6 (Regions):** REGION block, id/width/lines/regionanchor/viewportanchor/scroll  
**Part 7 (Special Blocks):** NOTE (comments), STYLE (CSS)  
**Part 8 (Implementation):** Generic IMPL-* rules for Parser/Writer/Validator  
**Part 9 (Validation Summary):** Rule counts, self-validation report  
**Part 10 (Quick Reference):** Tables for settings and tags

**Target Rule Counts (Exhaustive):**
- **RULE-FMT-###**: 5-7 file format rules (header, encoding, BOM, line endings, blank line)
- **RULE-TIME-###**: 7-10 timestamp rules (format, validation, ranges, separator, sequential)
- **RULE-CUE-###**: 5-8 cue structure rules (identifier, timing line, payload, blank line)
- **RULE-SET-###**: 8 cue setting rules (vertical, line, position, size, align, region, + constraints)
- **RULE-TAG-###**: 11-15 tag/markup rules (all 8 tags + closing rules + nesting + escaping)
- **RULE-ENT-###**: 3-5 HTML entity rules (&amp;, &lt;, &gt;, &nbsp;, &lrm;, &rlm;)
- **RULE-REG-###**: 5-8 region rules (REGION block, all properties, association)
- **RULE-BLK-###**: 3-5 special block rules (NOTE, STYLE, metadata)
- **RULE-VAL-###**: 5-8 validation rules (error handling, recovery, strict vs. lenient)
- **IMPL-###**: 12-15 implementation requirements (parser, writer, validator)
- **Total: 60-80 rules** (comprehensive coverage)

**Level Distribution (Exhaustive):**
- **MUST**: 30-40 rules (critical requirements)
- **SHOULD**: 15-20 rules (recommended practices)
- **MAY**: 5-10 rules (optional features)
- **MUST NOT**: 3-5 rules (forbidden patterns)

**Critical Inclusions (MUST be documented):**

**All 8 Markup Tags (Individual Rules):**
1. `<c>` / `<c.class>` - Class spans (RULE-TAG-001)
2. `<i>` - Italics (RULE-TAG-002)
3. `<b>` - Bold (RULE-TAG-003)
4. `<u>` - Underline (RULE-TAG-004)
5. `<v>` - Voice/speaker (RULE-TAG-005)
6. `<lang>` - Language (RULE-TAG-006)
7. `<ruby><rt>` - Ruby text (RULE-TAG-007)
8. `<HH:MM:SS.mmm>` - Internal timestamp (RULE-TAG-008)

**All 6 Cue Settings (Individual Rules):**
1. vertical: rl | lr (RULE-SET-001)
2. line: N | N% (RULE-SET-002)
3. position: N% (RULE-SET-003)
4. size: N% (RULE-SET-004)
5. align: start|center|end|left|right (RULE-SET-005)
6. region: id (RULE-SET-006)

**All Required HTML Entities (Individual Rules):**
1. &amp; (ampersand) - RULE-ENT-001
2. &lt; (less than) - RULE-ENT-002
3. &gt; (greater than) - RULE-ENT-003
4. &nbsp; (non-breaking space) - RULE-ENT-004
5. &lrm; (left-to-right mark) - RULE-ENT-005
6. &rlm; (right-to-left mark) - RULE-ENT-006

**REGION Properties (Individual Rules):**
1. id (required) - RULE-REG-001
2. width (percentage) - RULE-REG-002
3. lines (integer) - RULE-REG-003
4. regionanchor (percentage pair) - RULE-REG-004
5. viewportanchor (percentage pair) - RULE-REG-005
6. scroll (up/none) - RULE-REG-006

**Generate spec with incremental writing (context-efficient):**
```python
# Write spec section by section, not all at once
spec_content = f"""# WebVTT Specification - Complete Reference

**Generated**: {datetime.now().strftime("%Y-%m-%d")}
**Sources**: W3C WebVTT Specification (https://www.w3.org/TR/webvtt1/), MDN Web Docs
**Version**: W3C Candidate Recommendation
**Total Rules**: [TO BE CALCULATED]

---

"""

# Write initial header
write("pycaption/specs/vtt/vtt_specs_summary.md", spec_content)

# Generate Part 1: File Format (write immediately)
part1 = generate_file_format_rules()
append_to_spec(part1)

# Generate Part 2: Timestamps (write immediately)
part2 = generate_timestamp_rules()
append_to_spec(part2)

# ... continue for all parts

# This avoids holding entire spec in memory
```

### Step 5: Exhaustive Quality Validation

**Structure checks:**
- All rule IDs unique
- Sequential numbering within each category
- Valid test patterns  
- Level indicators present (MUST/SHOULD/MAY/MUST NOT)

**Content checks (Exhaustive - 100% required):**
- ✅ 60-80 total rules documented (RULE-* + IMPL-*)  
- ✅ 30-40 MUST rules (all critical requirements)
- ✅ 15-20 SHOULD rules (best practices)
- ✅ 5-10 MAY rules (optional features)
- ✅ 12-15 IMPL-* rules (generic, no pycaption references)
- ✅ All 8 markup tags individually documented (c, i, b, u, v, lang, ruby, timestamp)
- ✅ All 6 cue settings individually documented (vertical, line, position, size, align, region)
- ✅ All 6 HTML entities individually documented (&amp;, &lt;, &gt;, &nbsp;, &lrm;, &rlm;)
- ✅ All 6 REGION properties individually documented (id, width, lines, regionanchor, viewportanchor, scroll)
- ✅ STYLE block specification complete
- ✅ NOTE block specification complete
- ✅ Timestamp validation rules complete (format, ranges, start<=end, sequential)
- ✅ Validation rules complete (error handling, recovery strategies)
- ✅ Best practices documented (interoperability, browser compatibility)

**Generate exhaustive validation report in spec file:**
```markdown
## Part 10: Exhaustive Validation Summary

### Rule Counts by Category
- RULE-FMT-###: X file format rules (Target: 5-7)
- RULE-TIME-###: X timestamp rules (Target: 7-10)
- RULE-CUE-###: X cue structure rules (Target: 5-8)
- RULE-SET-###: X cue setting rules (Target: 8 - ALL settings)
- RULE-TAG-###: X tag/markup rules (Target: 11-15 - ALL 8 tags + rules)
- RULE-ENT-###: X HTML entity rules (Target: 3-5 - ALL 6 entities)
- RULE-REG-###: X region rules (Target: 5-8 - ALL 6 properties)
- RULE-BLK-###: X special block rules (Target: 3-5)
- RULE-VAL-###: X validation rules (Target: 5-8)
- IMPL-###: X implementation requirements (Target: 12-15)
- **Total: Y rules** (Target: 60-80 for exhaustive coverage)

### By Level (Exhaustive Distribution)
- MUST: X rules (Target: 30-40)
- SHOULD: X rules (Target: 15-20)
- MAY: X rules (Target: 5-10)
- MUST NOT: X rules (Target: 3-5)

### Coverage Verification (100% Required)

**Markup Tags (8 total - ALL must be documented):**
- ✅/❌ `<c>` class spans (RULE-TAG-001)
- ✅/❌ `<i>` italics (RULE-TAG-002)
- ✅/❌ `<b>` bold (RULE-TAG-003)
- ✅/❌ `<u>` underline (RULE-TAG-004)
- ✅/❌ `<v>` voice (RULE-TAG-005)
- ✅/❌ `<lang>` language (RULE-TAG-006)
- ✅/❌ `<ruby><rt>` ruby text (RULE-TAG-007)
- ✅/❌ `<HH:MM:SS.mmm>` timestamp (RULE-TAG-008)
**Status: X/8 tags documented**

**Cue Settings (6 total - ALL must be documented):**
- ✅/❌ vertical: rl|lr (RULE-SET-001)
- ✅/❌ line: N|N% (RULE-SET-002)
- ✅/❌ position: N% (RULE-SET-003)
- ✅/❌ size: N% (RULE-SET-004)
- ✅/❌ align: start|center|end|left|right (RULE-SET-005)
- ✅/❌ region: id (RULE-SET-006)
**Status: X/6 settings documented**

**HTML Entities (6 required - ALL must be documented):**
- ✅/❌ &amp; ampersand (RULE-ENT-001)
- ✅/❌ &lt; less than (RULE-ENT-002)
- ✅/❌ &gt; greater than (RULE-ENT-003)
- ✅/❌ &nbsp; non-breaking space (RULE-ENT-004)
- ✅/❌ &lrm; left-to-right mark (RULE-ENT-005)
- ✅/❌ &rlm; right-to-left mark (RULE-ENT-006)
**Status: X/6 entities documented**

**REGION Properties (6 total - ALL must be documented):**
- ✅/❌ id (required) (RULE-REG-001)
- ✅/❌ width: N% (RULE-REG-002)
- ✅/❌ lines: N (RULE-REG-003)
- ✅/❌ regionanchor: X%,Y% (RULE-REG-004)
- ✅/❌ viewportanchor: X%,Y% (RULE-REG-005)
- ✅/❌ scroll: up|none (RULE-REG-006)
**Status: X/6 properties documented**

### Self-Validation Checklist
- ✅/❌ All rule IDs unique
- ✅/❌ Sequential numbering within categories
- ✅/❌ All 8 markup tags individually documented
- ✅/❌ All 6 cue settings individually documented
- ✅/❌ All 6 HTML entities individually documented
- ✅/❌ All 6 REGION properties individually documented
- ✅/❌ Generic IMPL rules (no pycaption-specific code)
- ✅/❌ Test patterns present for all rules
- ✅/❌ Source attribution present
- ✅/❌ 60-80 total rules (exhaustive coverage target)
- ✅/❌ 30-40 MUST rules documented

### Overall Status
- **Completeness**: X% (100% required)
- **Status**: ✅ PASS | ❌ FAIL (requires fixes)

**If FAIL**: Missing items listed above must be added before spec is complete.
```

**If validation FAILS:**
1. Identify missing rules/categories
2. Search additional sources for missing details
3. Add missing rules
4. Re-validate until PASS

### Step 6: Source Attribution

Track sources for each rule:
- W3C WebVTT spec section (Primary)
- MDN docs (Confirms)
- Confidence: High/Medium/Low

Document conflicts and resolutions.

### Step 7: Update Web Sources

Append new URLs (if any) to `pycaption/specs/vtt/vtt_web_sources.md`:
```markdown
- [New Source Title](https://url.example.com)
```

---

## Output Files

1. **`pycaption/specs/vtt/vtt_specs_summary.md`** - Complete specification with 40-50 rules
2. **`pycaption/specs/vtt/vtt_web_sources.md`** - Updated URL list (if new sources found)

---

## Success Criteria (Exhaustive - 100% Required)

**Completeness (CRITICAL - All must be ✅):**
- ✅ 60-80 total rules documented (RULE-* + IMPL-*)
- ✅ All 8 markup tags individually documented with examples (c, i, b, u, v, lang, ruby, timestamp)
- ✅ All 6 cue settings individually documented with validation (vertical, line, position, size, align, region)
- ✅ All 6 HTML entities individually documented (&amp;, &lt;, &gt;, &nbsp;, &lrm;, &rlm;)
- ✅ All 6 REGION properties individually documented (id, width, lines, regionanchor, viewportanchor, scroll)
- ✅ Header validation rules (WEBVTT signature, UTF-8, BOM, blank line)
- ✅ Timestamp format and validation rules (format, ranges, start<=end, sequential)
- ✅ Cue structure rules (identifier, timing line, payload, blank line terminator)
- ✅ Special blocks (NOTE comments, STYLE CSS)
- ✅ Validation rules (error handling, recovery strategies)
- ✅ 30-40 MUST rules (all critical requirements)
- ✅ 15-20 SHOULD rules (best practices)
- ✅ 5-10 MAY rules (optional features)
- ✅ 12-15 IMPL rules (generic, no pycaption-specific code)

**Quality (All must be ✅):**
- ✅ Unique rule IDs (no duplicates)
- ✅ Sequential numbering within categories
- ✅ Valid test patterns for all rules
- ✅ Source attribution (W3C section references)
- ✅ Generic IMPL rules (no pycaption-specific references)
- ✅ Self-validation report included
- ✅ Completeness score 100%

**Web Sources:**
- ✅ W3C WebVTT spec fetched
- ✅ MDN documentation fetched
- ✅ Additional sources found via web search (if needed)
- ✅ All new sources added to vtt_web_sources.md
---

## Context Window Optimization

**Token usage target:** < 50K per invocation

**Strategies:**
1. **Targeted web fetch** - Extract text only, not full HTML
2. **Incremental writing** - Save spec file as rules are generated, not at end
3. **On-demand web search** - Only if completeness check finds gaps
4. **Section-by-section** - Process file format → timestamps → cues → tags → etc.
5. **Rule metadata first** - Extract rule IDs/levels, fetch details on-demand

**Estimated token usage:**
- Web source fetches: 10-15K tokens
- Rule generation (40-50 rules): 15-20K tokens  
- Validation & tables: 5K tokens
- **Total: ~35K tokens** (30% safety margin)

---

## Error Handling

- **vtt_web_sources.md not found**: Create it with W3C spec URL
- **No URLs in file**: Proceed with web search
- **Web fetch fails**: Continue with available sources + web search
- **Web search fails**: Use built-in W3C WebVTT knowledge
- **Cannot write output**: Report error with path
