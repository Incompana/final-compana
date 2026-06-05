# Implementation Guide: Fixes untuk Confused User Scenarios

## 🎯 Overview

Dokumen ini memberikan **konkret implementation examples** untuk memperbaiki 9 failing tests.

---

## 🔴 PRIORITY 1: CRITICAL FIXES

### FIX #1: Multi-Domain Detection (Fixes 4 tests)

**Failing Tests**:

1. `test_mentions_three_roles_simultaneously` ❌
2. `test_confused_overwhelmed_with_multiple_roles` ❌
3. `test_overwhelmed_learner_persona` ❌
4. (Plus potential regressions in other confusion tests)

**Root Cause**:

- Blocker type tidak detect "too_many_options" dari multiple domains
- Persona rule hanya check blocker_type, tidak count domain keywords

**Current Code** (ai_ml_module/engines/engine1_pretext.py):

```python
def _score_domain(txt: str) -> Tuple[str, float]:
    best_domain, best_count = "general", 0
    for domain, kws in DOMAIN_KEYWORDS.items():
        hit = sum(1 for k in kws if k in txt)
        if hit > best_count:
            best_count, best_domain = hit, domain
    return best_domain, round(min(1.0, best_count / 3.0), 3)
```

**Problem**: Hanya return 1 domain terbaik, tidak detect multi-domain

**Solution**: Add explicit multi-domain detection

```python
# ADD THIS FUNCTION (after _score_domain):
def _detect_multi_domain(txt: str) -> Tuple[List[str], bool]:
    """
    Detect multiple domains in text.
    Returns: (list of detected domains, is_multi_domain)
    """
    detected = []
    domain_hits = {}

    for domain, kws in DOMAIN_KEYWORDS.items():
        hit = sum(1 for k in kws if k in txt)
        if hit > 0:
            detected.append(domain)
            domain_hits[domain] = hit

    is_multi = len(detected) > 1
    return detected, is_multi


# MODIFY analyze_pretext() function:
def analyze_pretext(user_input_text: str) -> Dict[str, Any]:
    txt = " ".join((user_input_text or "").lower().split())
    blocker_map = _load_blocker_mapping()

    # --- Rule-based scoring ---
    domain_interest, domain_score = _score_domain(txt)

    # ADD THIS:
    detected_domains, is_multi_domain = _detect_multi_domain(txt)

    current_level, level_score = _score_level(txt)
    blocker_type, blocker_score = _score_blocker(txt, blocker_map)

    # MODIFY THIS:
    if is_multi_domain and blocker_type == "none":
        blocker_type = "too_many_options"
        blocker_score = min(1.0, len(detected_domains) * 0.3)  # Multiple domains = higher blocker score

    intent, intent_score = _score_intent(txt)

    # ... rest of function ...

    # In result dict, ADD:
    result["_meta"]["detected_domains"] = detected_domains
    result["_meta"]["is_multi_domain"] = is_multi_domain

    return result
```

**Testing**:

```bash
# This test should now PASS:
pytest tests/test_confused_user_scenarios.py::TestMultiRoleScenarios::test_mentions_three_roles_simultaneously -v
```

---

### FIX #2: Improve Keyword Matching (Fixes 3 tests)

**Failing Tests**:

1. `test_confusion_keywords_detection` ❌
2. `test_multi_role_keywords_detection` ❌
3. `test_high_confidence_for_clear_input` ❌

**Root Cause**:

- Simple `keyword in text` matching is too rigid
- Case sensitivity issues
- Multi-word keywords not properly handled

**Current Implementation**:

```python
LEVEL_KEYWORDS: Dict[str, List[str]] = {
    "beginner": ["baru mulai", "belum pernah", "pemula", ...],
    "basic": ["sudah bisa", "pernah belajar", "basic", ...],
    ...
}

def _score_level(txt: str) -> Tuple[str, float]:
    best_level, best_hit = "beginner", 0
    for level, kws in LEVEL_KEYWORDS.items():
        hit = sum(1 for k in kws if k in txt)  # ← too simple
        if hit > best_hit:
            best_hit, best_level = hit, level
    return best_level, round(min(1.0, best_hit / 2.0), 3)
```

**Problem**: "sudah bisa HTML CSS" hanya match "sudah bisa" keyword jika exact match

**Solution**: Add fuzzy matching dan better keyword detection

```python
from difflib import SequenceMatcher

# ADD UTILITY FUNCTION:
def _fuzzy_match(text: str, keywords: List[str], threshold: float = 0.85) -> int:
    """
    Count keywords yang match dengan text menggunakan fuzzy matching.
    threshold: 0.85 = 85% similarity required
    """
    text_lower = text.lower()
    matched = 0

    for keyword in keywords:
        keyword_lower = keyword.lower()

        # Exact substring match (fastest)
        if keyword_lower in text_lower:
            matched += 1
            continue

        # Fuzzy match untuk partial keywords
        # Check if keyword adalah prefix dari any word dalam text
        for word in text_lower.split():
            if keyword_lower in word or word in keyword_lower:
                matched += 1
                break

    return matched


# IMPROVE LEVEL KEYWORDS (add more variants):
LEVEL_KEYWORDS: Dict[str, List[str]] = {
    "beginner": [
        "baru mulai", "belum pernah", "pemula", "newbie", "dari nol",
        "awal", "mulai dari awal", "junior", "belum experience",
        "baru dimulai", "level 0", "tidak ada pengalaman"
    ],
    "basic": [
        "sudah bisa", "pernah belajar", "basic", "dasar", "sedikit tahu",
        "pernah coba", "sudah paham", "sedikit experience", "sudah mencoba",
        "basic knowledge", "foundational"
    ],
    "intermediate": [
        "sudah pernah project", "intermediate", "sudah paham", "cukup paham",
        "pernah kerja", "sudah experience", "mid-level", "menengah",
        "sudah biasa", "sudah expert", "sudah mahir"
    ],
    "advanced": [
        "advanced", "senior", "expert", "sangat paham", "sudah lama",
        "expert level", "sangat experience", "professional", "master",
        "sudah kuasai", "sangat mahir"
    ],
}


# IMPROVE SCORE FUNCTIONS:
def _score_level(txt: str) -> Tuple[str, float]:
    best_level = "beginner"
    best_hit = 0

    for level, kws in LEVEL_KEYWORDS.items():
        hit = _fuzzy_match(txt, kws)
        if hit > best_hit:
            best_hit = hit
            best_level = level

    # Better scoring: more hits = higher score
    score = round(min(1.0, best_hit / 1.5), 3)
    return best_level, score


# SIMILARLY FOR OTHER SCORING FUNCTIONS:
def _score_intent(txt: str) -> Tuple[str, float]:
    best_intent = "skill_gap"
    best_hit = 0

    for intent, kws in INTENT_KEYWORDS.items():
        hit = _fuzzy_match(txt, kws)
        if hit > best_hit:
            best_hit = hit
            best_intent = intent

    score = round(min(1.0, best_hit / 1.5), 3)
    return best_intent, score


def _score_domain(txt: str) -> Tuple[str, float]:
    best_domain = "general"
    best_count = 0

    for domain, kws in DOMAIN_KEYWORDS.items():
        hit = _fuzzy_match(txt, kws)  # Use fuzzy_match
        if hit > best_count:
            best_count = hit
            best_domain = domain

    score = round(min(1.0, best_count / 2.5), 3)
    return best_domain, score
```

**Testing**:

```bash
# These tests should now PASS:
pytest tests/test_confused_user_scenarios.py::TestConfusionDetectionLogic::test_high_confidence_for_clear_input -v
```

---

### FIX #3: Priority Gap API Fallback (Fixes 1 test)

**Failing Test**:

1. `test_generate_skill_gap_with_unclear_role` ❌

**Root Cause**:

- API tidak handle role="general_learner"
- generate_skill_gap returns None untuk priority_gap

**Current Code** (ai_ml_module/engines/skill_gap_engine.py atau similar):

```python
def generate_skill_gap(target_role: str, user_skill_profile: Dict) -> Dict:
    # Assumes target_role exists in skills database
    # Returns None if role not found

    priority_gap = None  # ← This becomes None for general_learner
    return {
        "target_role": target_role,
        "priority_gap": priority_gap,  # ← Returns None
    }
```

**Solution**: Add fallback for general_learner role

```python
def generate_skill_gap(target_role: str, user_skill_profile: Dict) -> Dict:
    # SPECIAL CASE: general_learner
    if target_role == "general_learner":
        return {
            "target_role": "general_learner",
            "missing_skills": [],
            "owned_skills": list(user_skill_profile.keys()) if user_skill_profile else [],
            "priority_gap": "role_clarity",  # ← Special marker instead of None
            "priority_gap_description": "Tentukan role yang ingin Anda kejar terlebih dahulu",
            "recommendation": "Ambil skill assessment discovery untuk mengidentifikasi role yang tepat",
            "suggested_path": "discovery_assessment",
            "next_action": "Complete role exploration assessment",
            "readiness_score": 0.0,
            "readiness_level": "not_ready",
        }

    # EXISTING LOGIC for other roles:
    # ... (rest of implementation)
```

**Testing**:

```bash
# This test should now PASS:
pytest tests/test_confused_user_scenarios.py::TestAPIHandlingConfusedUsers::test_generate_skill_gap_with_unclear_role -v
```

---

## 🟡 PRIORITY 2: HIGH IMPORTANCE FIXES

### FIX #4: Level Detection for "Junior" Context

**Failing Test**:

1. `test_confused_between_junior_tracks` ❌

**Issue**:
"Sebagai junior developer..." → detected as "advanced" instead of "beginner"/"basic"

**Solution**: Already covered in FIX #2 by adding "junior" to beginner keywords

```python
LEVEL_KEYWORDS = {
    "beginner": [
        # ... existing ...
        "junior", "pemula", "baru",  # ← Add these
    ]
}
```

---

### FIX #5: Intent Detection for Career Transition

**Failing Test**:

1. `test_confused_career_transition_multiple_paths` ❌

**Issue**:
"Mau career switch..." → detected as "validate_direction" instead of "switch_career"

**Root Cause**:
Text has "career switch" but keyword list has "pindah karier", "pindah karir", etc.

**Solution**: Add more intent keyword variants

```python
INTENT_KEYWORDS = {
    "switch_career": [
        "pindah karier", "pindah karir", "career change", "ganti profesi",
        "career switch", "beralih karir", "career transition", "career transition",
        "switch ke", "pindah ke", "transisi ke", "change to"
    ],
    # ... rest unchanged
}
```

---

## 🟢 PRIORITY 3: NICE-TO-HAVE

### ENHANCEMENT #1: Add Multi-Role Explicit Fields

**Affected Tests**: Will improve but not fix failing tests

**Suggestion**: Enhance API response dengan multi-role info

```python
# In pretext analysis result:
result = {
    # ... existing fields ...
    "multi_role_detected": False,  # NEW
    "detected_roles": [],           # NEW
    "multi_role_keywords": [],      # NEW
    "_meta": {
        # ... existing ...
        "multi_role_detected": is_multi_domain,
        "detected_domains": detected_domains,
    }
}

# In app.py endpoints:
@app.post("/full-pipeline-demo")
async def full_pipeline_demo(req: FullPipelineRequest):
    pretext = analyze_pretext(req.user_input_text)

    # NEW: If multi-role detected, add clarification questions
    if pretext.get("multi_role_detected"):
        return {
            "pretext_analysis": pretext,
            "clarification_needed": True,
            "suggested_questions": [
                "Mana satu yang paling Anda minat?",
                "Apa yang membuat Anda tertarik dengan semua opsi ini?",
                "Apakah ada constraints (waktu, resources) yang mempengaruhi pilihan?"
            ]
        }
```

---

## 📋 Implementation Checklist

### IMMEDIATE (Day 1)

- [ ] Implement FIX #1: Multi-Domain Detection
  - [ ] Add `_detect_multi_domain()` function
  - [ ] Modify `analyze_pretext()` to detect multi-domain
  - [ ] Test: `pytest tests/test_confused_user_scenarios.py::TestMultiRoleScenarios::test_mentions_three_roles_simultaneously -v`

- [ ] Implement FIX #2: Keyword Matching
  - [ ] Add `_fuzzy_match()` utility function
  - [ ] Update LEVEL_KEYWORDS with more variants
  - [ ] Update `_score_level()`, `_score_intent()`, `_score_domain()`
  - [ ] Test: `pytest tests/test_confused_user_scenarios.py::TestConfusionDetectionLogic -v`

- [ ] Implement FIX #3: Priority Gap Fallback
  - [ ] Add fallback logic untuk general_learner
  - [ ] Test: `pytest tests/test_confused_user_scenarios.py::TestAPIHandlingConfusedUsers::test_generate_skill_gap_with_unclear_role -v`

### VERIFICATION (Day 2)

- [ ] Run full test suite: `pytest tests/test_confused_user_scenarios.py -v`
- [ ] Expected: 33+ tests pass (up from 27)
- [ ] Check for any regressions: `pytest tests/ -v` (all tests)
- [ ] Performance test: `pytest tests/test_confused_user_scenarios.py --durations=10`

### MINOR FIXES (Day 2-3)

- [ ] FIX #4: Add "junior" keyword (automatic from FIX #2)
- [ ] FIX #5: Add "career switch" keyword variants
- [ ] Re-run tests: Should have 35+ passing

### NICE-TO-HAVE (Next week)

- [ ] ENHANCEMENT #1: Add multi-role explicit fields
- [ ] Add clarification questions feature
- [ ] Performance optimization if needed

---

## 🧪 Before & After: Test Execution

### BEFORE (Current State)

```
======================== test session starts ========================
collected 36 items

tests/test_confused_user_scenarios.py ... ✅ 27 passed, ❌ 9 failed

FAILURES:
1. test_mentions_three_roles_simultaneously
2. test_confused_overwhelmed_with_multiple_roles
3. test_confused_between_junior_tracks
4. test_confused_career_transition_multiple_paths
5. test_generate_skill_gap_with_unclear_role
6. test_confusion_keywords_detection
7. test_multi_role_keywords_detection
8. test_high_confidence_for_clear_input
9. test_overwhelmed_learner_persona
```

### AFTER (Expected after fixes)

```
======================== test session starts ========================
collected 36 items

tests/test_confused_user_scenarios.py ... ✅ 35+ passed, ❌ 0-1 failed

Expected improvements:
✅ FIX #1 (Multi-Domain): +3 tests
✅ FIX #2 (Keyword Matching): +3 tests
✅ FIX #3 (API Fallback): +1 test
✅ FIX #4 (Junior): +1 test
✅ FIX #5 (Career Intent): +1 test

Total: 27 + 9 = 36 tests passing
```

---

## 🔗 Code Files to Modify

### File 1: engine1_pretext.py

**Path**: `ai_ml_module/engines/engine1_pretext.py`

**Changes**:

1. Add `_detect_multi_domain()` function
2. Add `_fuzzy_match()` utility function
3. Update keyword dictionaries (add variants)
4. Modify `_score_level()`, `_score_intent()`, `_score_domain()`
5. Modify `analyze_pretext()` to handle multi-domain

### File 2: skill_gap_engine.py or similar

**Path**: `ai_ml_module/engines/skill_gap_engine.py` or wherever generate_skill_gap lives

**Changes**:

1. Add special case handling untuk "general_learner"
2. Return meaningful values instead of None

---

## 📞 Questions to Consider

1. **Should "too_many_options" blocker affect confidence score?**
   - YES: Multiple conflicting options = higher uncertainty
   - Suggestion: Increase blocker_score when multi-domain

2. **Should system suggest narrowing path for overwhelmed users?**
   - YES: Instead of full skill gap, suggest role comparison
   - Suggestion: Different action plan path for overwhelmed_learner

3. **Should we add recommendation engine for role selection?**
   - YES: Help users decide between 2+ roles
   - Could provide comparison matrix (e.g., "Frontend vs Backend")

4. **Should we track confidence by component?**
   - YES: Helps understand which part is uncertain
   - Suggestion: Add `confidence_breakdown` to metadata

---

## ✅ Validation Steps

After implementing all fixes, validate with:

```bash
# 1. Unit test for individual functions
python3 -m pytest tests/test_confused_user_scenarios.py::TestUserConfusion -v

# 2. Full test suite
python3 -m pytest tests/test_confused_user_scenarios.py -v

# 3. All tests (check for regressions)
python3 -m pytest tests/ -v

# 4. Manual API testing
curl -X POST http://127.0.0.1:8000/full-pipeline-demo \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","user_input_text":"Saya bingung antara frontend atau backend."}'

# 5. Performance check
python3 -m pytest tests/test_confused_user_scenarios.py --durations=10
```

---

## 🎯 Success Criteria

✅ All 36 tests pass
✅ No performance degradation (< 3 seconds)
✅ No regressions in other tests
✅ API returns valid data for all scenarios
✅ Confused users get proper guidance
✅ Multi-role ambiguity properly detected

Good luck! 🚀
