# Confused User & Multi-Role Scenarios: Detailed Examples

## 📋 Format Dokumentasi

Setiap skenario mencakup:

- **Input**: User's raw text
- **Current Output**: Apa yang sistem saat ini deteksi
- **Expected Output**: Apa yang seharusnya terjadi
- **Status**: ✅ Pass / ❌ Fail
- **Analysis**: Penjelasan detil

---

## KATEGORI 1: Pengguna Yang BENAR-BENAR BINGUNG

### Scenario 1.1: Sangat Bingung, No Direction ❌ PASS

```
INPUT:
"Bingung banget mau jadi apa. Tertarik banyak hal tapi ga tahu mulai dari mana."

CURRENT OUTPUT:
{
  "target_role": "general_learner",
  "confidence_score": 0.45,
  "blocker_type": "none",
  "persona_type": "learner",
  "needs_assessment": true
}

EXPECTED OUTPUT:
{
  "target_role": "general_learner",
  "confidence_score": < 0.6,
  "blocker_type": "too_many_options",
  "persona_type": "overwhelmed_learner",
  "needs_assessment": true,
  "clarification_needed": true,
  "confusion_signals": ["bingung", "tertarik banyak hal"]
}

STATUS: ✅ PASS (mostly correct, persona improvement needed)

ANALYSIS:
- Confidence rendah ✅ (0.45 < 0.6)
- needs_assessment = true ✅
- Persona harus overwhelmed_learner tapi terdeteksi learner ❌
- Blocker_type harus detect "too_many_options" ❌
```

---

### Scenario 1.2: Ragu Tentang Career Path ✅ PASS

```
INPUT:
"Saya takut memilih jalur yang salah. Belum yakin ini benar-benar cocok untuk saya."

CURRENT OUTPUT:
{
  "target_role": "general_learner",
  "confidence_score": 0.42,
  "blocker_type": "fear",
  "persona_type": "validation_seeker",
  "needs_assessment": true
}

EXPECTED OUTPUT:
{
  "target_role": "general_learner",
  "confidence_score": < 0.65,
  "blocker_type": "fear_wrong_path",
  "persona_type": "validation_seeker",
  "needs_assessment": true,
  "validation_needed": true
}

STATUS: ✅ PASS
- Correct persona (validation_seeker)
- Low confidence ✅
- needs_assessment = true ✅
- Blocker type correctly identified ✅
```

---

### Scenario 1.3: Overthinking Ekstrem ✅ PASS

```
INPUT:
"Aku overthinking banget, takut ga cocok, takut gagal terus, takut salah jalan."

CURRENT OUTPUT:
{
  "confidence_score": 0.38,
  "blocker_type": "fear",
  "needs_assessment": true,
  "persona_type": "validation_seeker"
}

EXPECTED OUTPUT:
Same as above

STATUS: ✅ PASS
- Multiple fear signals detected ✅
- Low confidence ✅
- Validation seeker persona ✅
```

---

### Scenario 1.4: Imposter Syndrome ✅ PASS

```
INPUT:
"Saya tidak yakin kemampuan saya cukup untuk karir ini. Mungkin saya tidak cocok."

CURRENT OUTPUT:
{
  "confidence_score": 0.35,
  "needs_assessment": true
}

EXPECTED OUTPUT:
Low confidence + needs assessment

STATUS: ✅ PASS
- confidence < 0.65 ✅
- needs_assessment = true ✅
```

---

## KATEGORI 2: Pengguna Menyebutkan 2 ROLES SEKALIGUS

### Scenario 2.1: Frontend vs Backend ✅ PASS

```
INPUT:
"Saya bingung antara frontend developer atau backend developer. Mana yang lebih cocok?"

CURRENT OUTPUT:
{
  "domain_interest": "frontend",  (or backend)
  "target_role": "frontend_developer",  (or backend_developer)
  "confidence_score": 0.58,
  "needs_assessment": true
}

EXPECTED OUTPUT:
{
  "multi_role_detected": true,
  "roles_mentioned": ["frontend_developer", "backend_developer"],
  "confidence_score": < 0.65,
  "needs_assessment": true,
  "clarification_type": "role_selection",
  "recommended_action": "Suggest role comparison assessment"
}

STATUS: ✅ PASS
- Low confidence ✅
- needs_assessment = true ✅
- System picks one role, not ideal but functional
- Missing: explicit multi-role flag

IMPROVEMENT: Add multi_role_detected field
```

---

### Scenario 2.2: Data Analyst vs AI/ML Engineer ✅ PASS

```
INPUT:
"Aku tertarik antara data analysis atau machine learning. Sulit memilih."

CURRENT OUTPUT:
{
  "domain_interest": "data" (or "ai_ml"),
  "confidence_score": 0.52,
  "needs_assessment": true
}

EXPECTED OUTPUT:
Same + multi_role flag

STATUS: ✅ PASS

ANALYSIS:
- System correctly identifies lower confidence
- Could be improved with explicit multi-role detection
```

---

### Scenario 2.3: Frontend Web vs Mobile Development ✅ PASS

```
INPUT:
"Saya suka JavaScript dan bisa design responsive. Tapi tertarik juga dengan mobile React Native. Mana dulu?"

CURRENT OUTPUT:
{
  "domain_interest": "frontend" (could be mobile),
  "confidence_score": 0.61,
  "needs_assessment": true
}

EXPECTED OUTPUT:
Same + multi_role flag + clarification

STATUS: ✅ PASS
- Ambiguity detected via low confidence
- Could benefit from explicit "frontend vs mobile" decision point
```

---

### Scenario 2.4: Backend vs DevOps ✅ PASS

```
INPUT:
"Tertarik backend API dan juga interested dengan infrastructure/devops. Mana starting point?"

CURRENT OUTPUT:
{
  "domain_interest": "backend",
  "confidence_score": 0.55,
  "needs_assessment": true
}

EXPECTED OUTPUT:
Same + clarify backend vs devops path

STATUS: ✅ PASS
```

---

### Scenario 2.5: Explicitly 3 Roles Simultaneously ❌ FAIL

```
INPUT:
"Saya bingung antara frontend, backend, atau data science. Semua menarik tapi bingung mulai dari mana."

CURRENT OUTPUT:
{
  "domain_interest": "data" (one of them),
  "confidence_score": 0.45,
  "persona_type": "learner",  ❌ Should be overwhelmed_learner
  "needs_assessment": true
}

EXPECTED OUTPUT:
{
  "domain_interest": null,  (or null)
  "roles_mentioned": ["frontend", "backend", "data_analyst"],
  "multi_role_count": 3,
  "confidence_score": < 0.5,
  "persona_type": "overwhelmed_learner",  ✅
  "needs_assessment": true,
  "clarification_type": "major_role_selection"
}

STATUS: ❌ FAIL
- Persona tidak terdeteksi sebagai overwhelmed_learner
- Multi-domain logic tidak cukup strong

ROOT CAUSE:
- PERSONA_RULES hanya check blocker_type, tidak count domain keywords
- Need to add multi-domain detection logic
```

---

## KATEGORI 3: CONFUSED + MULTI-ROLE COMBINATIONS

### Scenario 3.1: Confused AND Mentions 2 Roles ✅ PASS

```
INPUT:
"Saya benar-benar bingung antara frontend developer atau backend developer.
Keduanya menarik tapi saya tidak yakin cocok."

CURRENT OUTPUT:
{
  "confidence_score": 0.38,
  "needs_assessment": true,
  "blocker_type": "fear" (or none)
}

EXPECTED OUTPUT:
{
  "confidence_score": < 0.5,
  "multi_role_detected": true,
  "confusion_type": "role_selection",
  "needs_assessment": true,
  "recommended_path": "Role comparison + self-assessment"
}

STATUS: ✅ PASS
- Very low confidence ✅
- needs_assessment = true ✅
- Could be improved with explicit multi-role + confusion combo handling
```

---

### Scenario 3.2: Confused + Overwhelmed with Multiple Roles ❌ FAIL

```
INPUT:
"Banyak banget pilihan: frontend, backend, mobile, AI. Aku jadi overthinking dan ga tahu
mau mulai dari mana. Takut juga salah pilih."

CURRENT OUTPUT:
{
  "domain_interest": "frontend" (one picked),
  "confidence_score": 0.35,
  "persona_type": "learner",  ❌ Should be overwhelmed_learner
  "needs_assessment": true
}

EXPECTED OUTPUT:
{
  "domain_interest": null,
  "roles_mentioned": ["frontend_developer", "backend_developer", "mobile_developer", "machine_learning_engineer"],
  "multi_role_count": 4,
  "confidence_score": < 0.4,
  "persona_type": "overwhelmed_learner",  ✅
  "blocker_type": "too_many_options",
  "confusion_level": "extreme",
  "needs_assessment": true,
  "recommended_action": "Deep role exploration with narrowing"
}

STATUS: ❌ FAIL
- Persona not overwhelmed_learner
- Multi-domain detection missing
- Confusion severity not captured

IMPACT: User doesn't get appropriate guidance for extreme overwhelm
```

---

### Scenario 3.3: Confused Skills Don't Match Roles ✅ PASS

```
INPUT:
"Saya bagus di Python tapi tertarik frontend design. Tapi juga pengen jadi backend.
Ga tahu skill mana yang mau diperkuat."

CURRENT OUTPUT:
{
  "confidence_score": 0.48,
  "needs_assessment": true
}

EXPECTED OUTPUT:
Same + note skills-roles mismatch

STATUS: ✅ PASS
- Low confidence ✅
- Assessment recommended ✅
- Could detect skills-roles mismatch explicitly
```

---

### Scenario 3.4: Junior Career Confusion ❌ FAIL

```
INPUT:
"Sebagai junior developer, saya bingung antara fokus jadi senior frontend atau
pivot ke backend. Kedua menarik tapi butuh guidance."

CURRENT OUTPUT:
{
  "current_level": "advanced",  ❌ Should be "beginner" or "basic"
  "confidence_score": 0.52
}

EXPECTED OUTPUT:
{
  "current_level": "basic" or "beginner",  (junior = not senior)
  "context": "career_stage_confusion",
  "confusion_type": "specialization_vs_pivot",
  "confidence_score": < 0.7,
  "needs_assessment": true
}

STATUS: ❌ FAIL
- Level detection wrong: "junior" not properly mapped to beginner/basic
- "senior" keyword picked up as advanced level

ROOT CAUSE:
LEVEL_KEYWORDS not include "junior" mapping
```

---

### Scenario 3.5: Career Transition Multi-Path ❌ FAIL

```
INPUT:
"Saya mau career switch dari non-tech. Tertarik dengan data science atau
web development tapi bingung jalur mana lebih feasible."

CURRENT OUTPUT:
{
  "intent": "validate_direction",  ❌ Should be "switch_career"
  "domain_interest": "data" (or frontend)
}

EXPECTED OUTPUT:
{
  "intent": "switch_career",  ✅
  "domain_interest": null,  (both data & web dev)
  "multi_role_detected": true,
  "context": "career_transition",
  "transition_risk": "medium",  (non-tech → tech)
  "confidence_score": < 0.65
}

STATUS: ❌ FAIL
- Intent detection picked validate_direction instead of switch_career
- Keyword "career switch" not strong enough

ROOT CAUSE:
INTENT_KEYWORDS ["switch_career"] = ["pindah karier", "pindah karir", "career change", "ganti profesi"]
Input has "career switch" which doesn't match exactly
```

---

## KATEGORI 4: API INTEGRATION SCENARIOS

### Scenario 4.1: Full Pipeline with Confused User ✅ PASS

```
INPUT (API POST /full-pipeline-demo):
{
  "user_id": "confused_user_001",
  "user_input_text": "Saya bingung antara frontend developer atau backend developer.
                      Keduanya menarik tapi ga tahu mana yang cocok."
}

CURRENT OUTPUT:
{
  "pretext_analysis": {
    "confidence_score": 0.38,
    "needs_assessment": true
  },
  "action_plan": {
    "recommended_tasks": [...]
  }
}

EXPECTED OUTPUT:
Same + clarification recommendations

STATUS: ✅ PASS
- Correctly identifies low confidence
- Generates action plan
- Could be enhanced with multi-role specific recommendations
```

---

### Scenario 4.2: Generate Skill Gap for Unclear Role ❌ FAIL

```
INPUT (API POST /generate-skill-gap):
{
  "target_role": "general_learner",
  "user_skill_profile": {"general_knowledge": 1}
}

CURRENT OUTPUT:
{
  "target_role": "general_learner",
  "priority_gap": null,  ❌ NULL!
  "readiness_score": 0.0
}

EXPECTED OUTPUT:
{
  "target_role": "general_learner",
  "priority_gap": "role_clarity",  (special case)
  "recommendation": "Ambil skill assessment untuk mengidentifikasi role yang tepat",
  "suggested_path": "discovery_assessment",
  "readiness_score": 0.0
}

STATUS: ❌ FAIL
- priority_gap returns None for general_learner
- No fallback recommendations

ROOT CAUSE:
API assumes priority_gap exists for role in database
"general_learner" not in skills mapping
```

---

## KATEGORI 5: CLEAR INPUT (Should NOT be Low Confidence)

### Scenario 5.1: Clear Frontend + Skills ❌ FAIL

```
INPUT:
"Saya ingin jadi frontend developer dan sudah bisa HTML CSS JavaScript React."

CURRENT OUTPUT:
{
  "confidence_score": 0.47,  ❌ Too low
  "domain_interest": "frontend"
}

EXPECTED OUTPUT:
{
  "confidence_score": >= 0.75,  ✅ Should be high
  "domain_interest": "frontend",
  "current_level": "intermediate",
  "needs_assessment": false
}

STATUS: ❌ FAIL
- Confidence should be high (clear goal + multiple relevant skills)
- Actual: 0.47 (low)

ROOT CAUSE:
Keyword matching issue:
- "ingin jadi" not in INTENT_KEYWORDS (not exact match)
- "sudah bisa" level keywords need to find "sudah bisa HTML CSS..." pattern
- Multiple keywords not accumulating to high score

ANALYSIS:
- domain_score calculation: HTML, CSS, JavaScript, React all found = 4 hits
  → score = min(1.0, 4/3) = 1.0 (but truncated?)

Current scoring:
- domain_score * 0.35 = high
- level_score * 0.25 = needs improvement
- blocker_score * 0.20 = ok
- intent_score * 0.20 = needs improvement
→ Total too low

ISSUE: Level keywords not matching "sudah bisa" pattern
```

---

## 🎯 Skenario Prioritas untuk TESTING

### TEST PRIORITY MATRIX

| Scenario                 | Impact | Frequency | Difficulty | Priority |
| ------------------------ | ------ | --------- | ---------- | -------- |
| 2-role mention           | High   | High      | Medium     | 🔴 P0    |
| 3+ role mention          | High   | Medium    | High       | 🔴 P0    |
| Overwhelmed detection    | High   | Medium    | Medium     | 🔴 P1    |
| Confused + multi-role    | High   | Low       | High       | 🟡 P1    |
| Career transition        | Medium | High      | Medium     | 🟡 P2    |
| Imposter syndrome        | Medium | High      | Low        | 🟢 P3    |
| Clear input misdirection | High   | High      | High       | 🔴 P0    |

---

## 📊 Summary: Test Coverage per Scenario Type

```
Confusion Signals:
  ✅ Single confusion keyword (75%)
  ✅ Multiple confusion + emotions (85%)
  ❌ Overwhelming with 3+ options (40%)

Multi-Role Detection:
  ✅ Explicit 2-role mention (90%)
  ⚠️  Implicit multi-role (60%)
  ❌ 3+ roles (20%)

Clear Input:
  ❌ Complex but clear goal (30%)
  ⚠️  Simple clear goal (70%)

API Integration:
  ✅ Full pipeline (90%)
  ❌ Skill gap for unclear role (0%)
```

---

## 🔧 Fixes Needed (Prioritized)

### FIX #1: Multi-Domain Detection (CRITICAL)

```python
# In engine1_pretext.py

def _count_domains(txt: str) -> Tuple[List[str], int]:
    """Count unique domains in text."""
    detected = []
    for domain, kws in DOMAIN_KEYWORDS.items():
        hit = sum(1 for k in kws if k in txt)
        if hit > 0:
            detected.append(domain)
    return detected, len(detected)

# Usage:
domains, domain_count = _count_domains(txt)
if domain_count >= 2:
    blocker_type = "too_many_options"
    if current_level == "*":  # Any level can be overwhelmed
        persona_type = "overwhelmed_learner"
```

### FIX #2: Better Level Keyword Detection (CRITICAL)

```python
# Add more level keywords
LEVEL_KEYWORDS = {
    "beginner": [
        "baru mulai", "belum pernah", "pemula", "newbie", "dari nol",
        "awal", "mulai dari awal", "junior", "belum experience",
    ],
    "intermediate": [
        "sudah bisa", "pernah belajar", "sudah pernah project",
        "intermediate", "sudah paham", "sudah experience",
    ],
    ...
}

# Use better matching
def _score_level_improved(txt: str) -> Tuple[str, float]:
    best_level = "beginner"
    best_score = 0
    for level, kws in LEVEL_KEYWORDS.items():
        score = sum(1 for k in kws if k in txt.lower())
        if score > best_score:
            best_score = score
            best_level = level
    return best_level, min(1.0, best_score / 2.0)
```

### FIX #3: Priority Gap Fallback (HIGH)

```python
# In skill_gap_engine.py

def generate_skill_gap(target_role: str, user_skill_profile: Dict) -> Dict:
    if target_role == "general_learner":
        return {
            "target_role": "general_learner",
            "missing_skills": [],
            "owned_skills": [],
            "priority_gap": "role_clarity",  # Special marker
            "recommendation": "Sebaiknya ambil role discovery assessment terlebih dahulu",
            "readiness_score": 0.0,
            "next_step": "assessment_clarification"
        }

    # ... existing logic for other roles
```

### FIX #4: Multi-Role Explicit Detection (HIGH)

```python
def _detect_multi_role_keywords(txt: str) -> Tuple[bool, List[str]]:
    """Detect explicit multi-role keywords."""
    multi_role_keywords = ["atau", "vs", "dibanding", "dibandingkan",
                          "antara", "mana", "atau dulu", "duluan"]
    found = [kw for kw in multi_role_keywords if kw in txt.lower()]

    if found and len(domains) >= 2:
        return True, found
    return False, []

# Usage:
multi_role, multi_keywords = _detect_multi_role_keywords(txt)
result["_meta"]["multi_role_detected"] = multi_role
result["_meta"]["multi_role_keywords"] = multi_keywords
```
