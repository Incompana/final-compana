# Test Case Analysis: Confused Users & Multi-Role Scenarios

## Ringkasan Eksekusi Test

**Total Tests**: 36  
**Passed**: 27 ✅  
**Failed**: 9 ❌  
**Success Rate**: 75%

---

## Test Results Summary

### ✅ Tests yang PASS (27/36)

#### 1. **TestUserConfusion** (7/7 PASS)

Sistem berhasil mendeteksi berbagai kondisi kebingungan pengguna:

- ✅ Extremely confused (sangat bingung) dengan confidence rendah
- ✅ Confusion tentang career path → persona sebagai validation_seeker
- ✅ Minimal input → needs_assessment = True
- ✅ Overthinking dan self-doubt → low confidence
- ✅ Imposter syndrome → low confidence
- ✅ Multiple interests overwhelming → overwhelmed detection
- ✅ Generic confusion → assessment needed

**Kesimpulan**: Sistem BAIK dalam mendeteksi confusion signals.

---

#### 2. **TestMultiRoleScenarios** (7/8 PASS)

✅ Sistem berhasil mendeteksi:

- Frontend vs Backend ambiguity
- Data Analyst vs AI/ML Engineer confusion
- Frontend Web vs Mobile ambiguity
- Backend vs DevOps decision making
- First role then questioning second role
- Multi-role with different skill levels
- Direct role comparison (UI/UX vs Frontend)

❌ **GAGAL**: Three roles simultaneously

- Expected: `overwhelmed_learner`
- Actual: `learner`
- **Issue**: Persona rule hanya melihat blocker_type, tidak mempertimbangkan jumlah domain keywords

---

#### 3. **TestConfusedMultiRoleCombinations** (3/5 PASS)

✅ Berhasil:

- Confused + mentions 2 roles
- Skills don't match roles

❌ **GAGAL**:

1. **test_confused_overwhelmed_with_multiple_roles**
   - Expected persona: `overwhelmed_learner`
   - Actual: `learner`
2. **test_confused_between_junior_tracks**
   - Expected level: `beginner` atau `basic`
   - Actual: `advanced`
   - **Issue**: "senior frontend" → detected sebagai advanced, bukan junior
3. **test_confused_career_transition_multiple_paths**
   - Expected intent: `learn_new` atau `switch_career`
   - Actual: `validate_direction`
   - **Issue**: Keyword "career switch" tidak cukup dominan

---

#### 4. **TestAPIHandlingConfusedUsers** (3/4 PASS)

✅ Berhasil:

- Full pipeline with confused user
- Full pipeline with overthinking user
- Full pipeline with multi-role user

❌ **GAGAL**: test_generate_skill_gap_with_unclear_role

- Expected: `priority_gap` != None
- Actual: `priority_gap` = None
- **Issue**: API tidak memberikan priority_gap untuk role "general_learner"

---

#### 5. **TestConfusionDetectionLogic** (1/4 PASS)

✅ Berhasil:

- Low confidence threshold behavior

❌ **GAGAL**:

1. **test_confusion_keywords_detection**
   - "Saya jelas mau jadi frontend" → confidence rendah (should be high)
   - Issue: Keyword "jelas" tidak overwrite "bingung" signals
2. **test_multi_role_keywords_detection**
   - "Saya mau jadi frontend developer" → confidence tinggi (should be?)
   - Issue: Multi-role detection bukan hanya dari keywords "atau"
3. **test_high_confidence_for_clear_input**
   - "Saya ingin jadi frontend developer dan sudah bisa HTML CSS..." → confidence 0.47
   - Should be >= 0.7
   - **Issue**: Keyword matching logic tidak optimal (tidak case-sensitive enough?)

---

#### 6. **TestConfusedUserPersonas** (3/4 PASS)

✅ Berhasil:

- Validation seeker persona
- Beginner explorer persona
- Project seeker with confusion

❌ **GAGAL**: test_overwhelmed_learner_persona

- Expected: `overwhelmed_learner`
- Actual: `learner`
- **Issue**: Persona rule tidak detect overwhelming dari too many keywords

---

#### 7. **TestEdgeCasesAndBoundaries** (4/4 PASS) ✅

Semua edge cases berhasil:

- Empty input
- Very long confused input
- Mixed languages
- All confusion signals combined

---

## 🔴 Identified Issues & Root Causes

### Issue #1: Overwhelmed Learner Persona Not Detected

**Symptom**: Multiple domain keywords tidak trigger `overwhelmed_learner` persona  
**Root Cause**:

```python
PERSONA_RULES = [
    ("no_starting_point", "beginner", "beginner_explorer"),
    ("no_portfolio", "*", "project_seeker"),
    ("fear_wrong_path", "*", "validation_seeker"),
    ("too_many_options", "*", "overwhelmed_learner"),  # ← blocker_type harus "too_many_options"
    ("no_time", "*", "busy_learner"),
]
```

Blocker_type hanya di-set dari keyword mapping, tidak dari jumlah domain keywords.

**Fix**: Tambahkan logic untuk detect multi-domain keywords → set blocker_type = "too_many_options"

---

### Issue #2: Confidence Score Calculation Sub-optimal

**Symptom**: Clear inputs mendapat low confidence  
**Examples**:

- "Saya ingin jadi frontend developer dan sudah bisa HTML CSS JavaScript React" → 0.47 (should be > 0.7)
- "Saya jelas mau jadi frontend" → low confidence (should be high)

**Root Cause**:

- Keyword matching case-sensitive dan partial match only
- Level keywords tidak match "sudah bisa" pattern
- Intent keywords tidak properly weight multiple occurrences

**Fix**:

- Improve keyword matching algorithm
- Add fuzzy matching atau regex patterns
- Weight level keywords better

---

### Issue #3: Priority Gap for "general_learner" Role

**Symptom**: API returns None for priority_gap when role is "general_learner"  
**Root Cause**: Role "general_learner" tidak ada di priority mapping

**Fix**: Add default priority recommendations untuk general_learner

---

### Issue #4: Multi-Role Detection Needs Improvement

**Symptom**: "Saya mau jadi frontend developer" flagged sebagai multi-role (confidence < 0.75)  
**Root Cause**: Confidence calculation terlalu konservatif, bukan hanya dari "atau"/"vs" keywords

**Fix**: Need explicit multi-role keyword detection

---

## Recommendations

### Priority 1 (Critical)

1. ✅ **Add Multi-Domain Blocker Detection**
   - Hitung jumlah domain keywords
   - If > 1 unique domains → blocker_type = "too_many_options"
   - Set persona → overwhelmed_learner

2. ✅ **Improve Keyword Matching**
   - Use fuzzy matching (fuzzywuzzy atau difflib)
   - Case-insensitive, better partial matching
   - Regex patterns untuk level keywords

3. ✅ **Fix Priority Gap API**
   - Add fallback recommendations untuk general_learner
   - Base on detected intent/blocker types

### Priority 2 (Important)

4. **Enhance Multi-Role Detection Logic**
   - Explicit multi-role keyword detection (e.g., "atau", "vs", "dibanding")
   - Count domain keywords, not just presence
   - Better scoring when multiple roles detected

5. **Improve Persona Resolution**
   - Consider multiple signals, not just blocker_type
   - Context-aware persona selection
   - Persona confidence score

### Priority 3 (Nice-to-Have)

6. **Add Confusion Confidence Metric**
   - Return confusion_confidence separately from overall confidence_score
   - Help downstream engines understand type of uncertainty

7. **Better Multi-Language Support**
   - Currently relies on keyword matching
   - Could benefit from better Indonesian language processing

---

## Test Coverage Summary

| Category              | Tests  | Pass   | Coverage |
| --------------------- | ------ | ------ | -------- |
| Confusion Detection   | 7      | 7      | 100%     |
| Multi-Role Detection  | 8      | 7      | 87.5%    |
| Combination Scenarios | 5      | 3      | 60%      |
| API Integration       | 4      | 3      | 75%      |
| Detection Logic       | 4      | 1      | 25%      |
| Persona Types         | 4      | 3      | 75%      |
| Edge Cases            | 4      | 4      | 100%     |
| **Total**             | **36** | **27** | **75%**  |

---

## Skenario Bisnis yang Tercakup

### ✅ Well Covered

1. User sangat bingung → System triggers assessment
2. User menyebutkan 2 roles → Low confidence, needs clarification
3. User overwhelmed dengan banyak pilihan → Detected (mostly)
4. User dengan imposter syndrome → Detected
5. User career switcher → Detected
6. Empty/minimal input → Handled gracefully

### ⚠️ Partially Covered

1. 3+ roles simultaneously → Not properly detected
2. Clear inputs dengan many skills → Sometimes mis-scored
3. Junior vs Senior confusion → Level detection imperfect

### ❌ Not Fully Covered

1. Priority gap recommendations for unclear roles
2. Explicit multi-domain overwhelm persona
3. Career transition with multi-role paths

---

## Implementasi Next Steps

1. **Update Engine 1 Pretext Analyzer**
   - Add multi-domain detection logic
   - Improve keyword scoring algorithm
   - Better level detection

2. **Add Multi-Role Handler Component**
   - Explicit module untuk handle multi-role scenarios
   - Return clarification questions
   - Suggest role comparison framework

3. **Enhance Assessment Generator**
   - Add special assessment paths untuk confused users
   - Multi-role scenarios → role-specific assessments

4. **Improve API Contracts**
   - Add `clarification_questions` field
   - Add `multi_role_detected` flag
   - Add `confusion_level` metric

---

## Contoh Implementasi Improvements

### Fix #1: Multi-Domain Detection

```python
def _detect_multi_domain(txt: str) -> Tuple[List[str], bool]:
    """
    Detect multiple domains in text.
    Returns: (list of detected domains, is_multi_domain)
    """
    detected = []
    for domain, kws in DOMAIN_KEYWORDS.items():
        if any(kw in txt for kw in kws):
            detected.append(domain)
    return detected, len(detected) > 1

# In analyze_pretext():
domains, is_multi = _detect_multi_domain(txt)
if is_multi:
    blocker_type = "too_many_options"
```

### Fix #2: Better Keyword Matching

```python
from difflib import SequenceMatcher

def _fuzzy_match_keywords(txt: str, keywords: List[str], threshold=0.8) -> int:
    """Count fuzzy-matched keywords."""
    txt_lower = txt.lower()
    count = 0
    for keyword in keywords:
        if keyword in txt_lower:  # Exact match first
            count += 1
        else:
            # Fuzzy match untuk partial keywords
            ratio = SequenceMatcher(None, txt_lower, keyword).ratio()
            if ratio >= threshold:
                count += 1
    return count
```

### Fix #3: Priority Gap for General Learner

```python
def generate_skill_gap(target_role: str, user_skill_profile: Dict) -> Dict:
    if target_role == "general_learner":
        # Return default recommendations based on context
        return {
            "target_role": "general_learner",
            "priority_gap": "role_clarity",  # Help them clarify role first
            "recommendation": "Ambil skill assessment untuk explore options"
        }
```

---

## Next Meeting Agenda

1. Review test results dan discuss prioritas improvements
2. Implement Fix #1: Multi-Domain Detection
3. Implement Fix #2: Keyword Matching Enhancement
4. Add Multi-Role Clarification Questions Feature
5. Update API contracts dengan new fields
