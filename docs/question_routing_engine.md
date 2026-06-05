# Question Routing Engine (Rule-Based v1)

Engine ini merutekan 3-5 pertanyaan follow-up assessment berdasarkan:

- `pretext_analysis` result
- `problem_category`
- `target_role`
- `current_level`
- `blocker_type`

Fokus utama pertanyaan:

1. apakah target role sudah jelas,
2. apakah fondasi user sudah cukup,
3. blocker utama yang benar-benar dominan.

## Output JSON (Frontend-Ready)

```json
{
  "router_version": "question_router_rule_v1",
  "input_snapshot": {
    "problem_category": "skill_gap",
    "target_role": "frontend",
    "current_level": "basic",
    "blocker_type": "no_portfolio",
    "pretext_confidence": 0.84
  },
  "clarification_needed": false,
  "decision_path": [
    "core.role_clarity",
    "core.foundation_check",
    "core.blocker_identification",
    "extra.weakest_foundation_area",
    "extra.portfolio_evidence_state"
  ],
  "question_count": 5,
  "questions": [
    {
      "id": "role_commitment_4_weeks",
      "prompt": "Untuk 4 minggu ke depan, apakah kamu mau fokus di role frontend?",
      "answer_type": "single_choice",
      "options": [
        "Ya, fokus di frontend",
        "Masih ingin bandingkan dengan role lain",
        "Belum yakin sama sekali"
      ],
      "required": true,
      "goal": "role_clarity",
      "why_asked": "Konfirmasi komitmen role agar action plan tidak melebar."
    }
  ]
}
```

## Decision Tree Ringkas

Core (selalu ditanyakan):

- `role_clarity` question
- `foundation_check` question
- `blocker_identification` question

Branch (maks 2 pertanyaan tambahan):

- jika `direction_confused` atau role `unclear` -> tanyakan anchor keputusan role
- jika `beginner_lost` / `skill_gap` -> tanyakan area fondasi terlemah
- jika `no_portfolio` -> tanyakan status bukti portfolio
- jika `no_time` / `overwhelmed` -> tanyakan kapasitas waktu realistis
- jika `no_confidence` / `confidence_issue` -> tanyakan trigger kurang percaya diri
- jika `no_roadmap` -> tanyakan bagian roadmap paling kabur
- jika `too_many_options` -> tanyakan sumber distraksi opsi

## Example 1 — Cybersecurity Beginner

Input:

```json
{
  "pretext_analysis": {"confidence": 0.71, "clarification_needed": false},
  "problem_category": "beginner_lost",
  "target_role": "cybersecurity",
  "current_level": "zero",
  "blocker_type": "no_foundation"
}
```

Expected routing behavior:

- `clarification_needed`: `false`
- 3-5 pertanyaan
- pertanyaan fondasi berisi opsi cybersecurity (misal CIA triad / Linux / log dasar)

## Example 2 — Confused Multi-Interest User

Input:

```json
{
  "pretext_analysis": {
    "confidence": 0.38,
    "clarification_needed": true,
    "matched_signals": {
      "roles": {
        "frontend": ["\\bfrontend\\b"],
        "data_analyst": ["\\bdata\\s?analyst\\b"]
      }
    }
  },
  "problem_category": "direction_confused",
  "target_role": "unclear",
  "current_level": "unclear",
  "blocker_type": "too_many_options"
}
```

Expected routing behavior:

- `clarification_needed`: `true`
- ada `role_pick_primary`
- ada `role_decision_anchor`

## Example 3 — Frontend User with Basic Skills

Input:

```json
{
  "pretext_analysis": {"confidence": 0.84, "clarification_needed": false},
  "problem_category": "skill_gap",
  "target_role": "frontend",
  "current_level": "basic",
  "blocker_type": "no_portfolio"
}
```

Expected routing behavior:

- `clarification_needed`: `false`
- ada konfirmasi role frontend
- ada check fondasi frontend
- ada pertanyaan status evidence portfolio
