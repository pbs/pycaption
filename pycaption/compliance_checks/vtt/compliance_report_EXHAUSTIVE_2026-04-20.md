# WebVTT EXHAUSTIVE Compliance Report

**Generated**: 2026-04-20
**Coverage**: 76/76 rules (100%)
**Total Issues**: 29
**MUST violations**: 22

## 1. Validation Gaps (0)

## 2. Partial Validation (1)
1. **RULE-FMT-001**: WEBVTT header (50%)

## 3. Missing MUST Rules (15)
1. **RULE-TIME-001**: Timestamp format: `[HH:]MM:SS.mmm`
2. **RULE-TIME-002**: Hours optional unless non-zero
3. **RULE-TIME-003**: Milliseconds require exactly 3 digits
4. **RULE-TIME-004**: Minutes and seconds range 0-59
5. **RULE-TIME-005**: Cue start time MUST be ≤ end time
6. **RULE-TIME-007**: Internal timestamps within cue boundaries
7. **RULE-REG-001**: REGION block defines region
8. **RULE-REG-002**: Region setting: id (required)
9. **RULE-REG-003**: Region setting: width (percentage)
10. **RULE-REG-004**: Region setting: lines (integer)
11. **RULE-REG-005**: Region setting: regionanchor (x%,y%)
12. **RULE-REG-006**: Region setting: viewportanchor (x%,y%)
13. **RULE-REG-007**: Region setting: scroll (up)
14. **RULE-REG-008**: Each region setting appears once maximum
15. **RULE-REG-009**: All region identifiers MUST be unique

## 4. Coverage
**Tags** (3/8): ❌<c> ✅<i> ✅<b> ✅<u> ❌<v> ❌<lang> ❌<ruby> ❌<timestamp>
**Settings** (5/6): ✅vertical ✅line ✅position ✅size ✅align ❌region
**Entities** (6/7): ✅&amp; ✅&lt; ✅&gt; ✅&nbsp; ✅&lrm; ✅&rlm; ❌&#

## 5. Test Gaps (6)
1. **RULE-FMT-001**: WEBVTT header
2. **RULE-FMT-002**: UTF-8 encoding
3. **RULE-TIME-005**: Start<=end time
4. **RULE-TIME-006**: Monotonic time
5. **RULE-VAL-002**: Cue ID unique
6. **RULE-VAL-003**: Region ID unique

---
**Generated**: 2026-04-20 19:44
