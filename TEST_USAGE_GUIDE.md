# Test Cases: Usage Guide & Implementation Roadmap

## 📋 Quick Start

### Running All Tests

```bash
cd /Users/macbookpro/testing/Vscode/Compana-AI:ML/ai-ml
source venv/bin/activate

# Run all confused user tests
python3 -m pytest tests/test_confused_user_scenarios.py -v

# Run specific test class
python3 -m pytest tests/test_confused_user_scenarios.py::TestUserConfusion -v

# Run specific test
python3 -m pytest tests/test_confused_user_scenarios.py::TestUserConfusion::test_extremely_confused_no_direction -v

# Run with detailed output
python3 -m pytest tests/test_confused_user_scenarios.py -vv --tb=long

# Run with print statements
python3 -m pytest tests/test_confused_user_scenarios.py -v -s
```

### Running Individual Scenarios

```bash
# Test only confusion detection
python3 -m pytest tests/test_confused_user_scenarios.py::TestUserConfusion -v

# Test only multi-role scenarios
python3 -m pytest tests/test_confused_user_scenarios.py::TestMultiRoleScenarios -v

# Test only API integration
python3 -m pytest tests/test_confused_user_scenarios.py::TestAPIHandlingConfusedUsers -v
```

---

## 📊 Understanding Test Output

### Example Test Output Breakdown

```
tests/test_confused_user_scenarios.py::TestUserConfusion::test_extremely_confused_no_direction PASSED [  2%]
```

**Components**:

- `tests/test_confused_user_scenarios.py` → Test file location
- `TestUserConfusion` → Test class (groups related tests)
- `test_extremely_confused_no_direction` → Test method name
- `PASSED` → Test result ✅ or FAILED ❌
- `[  2%]` → Progress (2 tests done, moving through all)

### Full Test Report

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /Users/macbookpro/testing/Vscode/Compana-AI:ML/ai-ml
configfile: pyproject.toml
plugins: anyio-4.11.0
collected 36 items

tests/test_confused_user_scenarios.py ... ✅ 27 passed, ❌ 9 failed in 2.47s
```

---

## 🧪 Test Structure

Each test follows this pattern:

```python
class TestUserConfusion:
    """Group of related tests for confusion detection."""

    def test_extremely_confused_no_direction(self):
        """
        Test name = descriptive action being tested

        Docstring = what scenario this tests
        """
        # 1. ARRANGE: Setup input data
        text = "Bingung banget mau jadi apa..."

        # 2. ACT: Call the function
        result = analyze_pretext(text)

        # 3. ASSERT: Verify expected behavior
        assert result["confidence_score"] < 0.7
        assert result["needs_assessment"] is True
```

### Understanding Each Component

**1. Input (What we're testing)**

- Raw user text
- Simulates real user input
- Various Indonesian phrases

**2. Current Output (What system returns)**

- `analyze_pretext()` returns a dictionary
- Contains confidence_score, target_role, blocker_type, etc.

**3. Assertions (What we expect)**

- `assert`: Python's way to verify truth
- `assert x < 0.7` → x must be less than 0.7
- `assert x is True` → x must be exactly True

**4. Test Result**

- ✅ PASS: All assertions passed
- ❌ FAIL: At least one assertion failed

---

## 📈 Test Execution Flow

```
Test Suite Execution
│
├─ Test Class 1: TestUserConfusion
│  ├─ test_1 → PASS ✅
│  ├─ test_2 → PASS ✅
│  └─ test_N → PASS ✅
│
├─ Test Class 2: TestMultiRoleScenarios
│  ├─ test_1 → PASS ✅
│  ├─ test_2 → FAIL ❌ (assertion error)
│  └─ test_N → PASS ✅
│
└─ Summary
   └─ 27 passed, 9 failed
```

---

## 🔍 Analyzing Failures

When a test fails, look for:

1. **Error Type**

```python
AssertionError: assert 'learner' == 'overwhelmed_learner'
                       ↑ actual value
                                   ↑ expected value
```

2. **Assertion Line**

```python
tests/test_confused_user_scenarios.py:133: in test_mentions_three_roles_simultaneously
    assert result["persona_type"] == "overwhelmed_learner"
    ↑ File      ↑ Line number  ↑ Which assertion failed
```

3. **Root Cause**: Debug by checking

```python
# Add debug print before assertion
print(f"Persona detected: {result['persona_type']}")
print(f"Confidence: {result['confidence_score']}")
print(f"Blocker: {result['blocker_type']}")
```

---

## 🎯 Test Categories Explained

### 1. TestUserConfusion (7 tests)

**Purpose**: Verify system detects various confusion signals  
**Key Checks**:

- `confidence_score < 0.7` → Low confidence when confused
- `needs_assessment is True` → Trigger assessment
- `persona_type` matches confusion pattern

**Example**:

```python
def test_confused_about_career_path(self):
    # Input: User unsure about career
    # Check: System detects validation need
    result = analyze_pretext("Takut memilih jalur yang salah...")
    assert result["persona_type"] == "validation_seeker"
```

### 2. TestMultiRoleScenarios (8 tests)

**Purpose**: Test when users mention multiple roles  
**Key Checks**:

- `confidence_score < 0.8` → Ambiguity lowers confidence
- System picks one role (picks dominant one)
- `needs_assessment is True` → Needs clarification

**Example**:

```python
def test_explicitly_mentions_two_roles_frontend_backend(self):
    # Input: "Saya bingung antara frontend atau backend..."
    # Check: Confidence lower due to ambiguity
    result = analyze_pretext(text)
    assert result["confidence_score"] < 0.8
    assert result["target_role"] in ["frontend_developer", "backend_developer"]
```

### 3. TestConfusedMultiRoleCombinations (5 tests)

**Purpose**: Confused + Multi-role together (worst case)  
**Key Checks**:

- Even lower confidence
- Assessment definitely needed
- Proper persona for overwhelming situations

### 4. TestAPIHandlingConfusedUsers (4 tests)

**Purpose**: Test full pipeline with confused users  
**Key Checks**:

- API returns correct structure
- All downstream components handle confusion
- Action plan generated despite uncertainty

### 5. TestConfusionDetectionLogic (4 tests)

**Purpose**: Unit test the keyword detection  
**Key Checks**:

- Confusion keywords properly identified
- Multi-role keywords detected
- Confidence thresholds correct

### 6. TestConfusedUserPersonas (4 tests)

**Purpose**: Persona assignment for confused users  
**Key Checks**:

- `validation_seeker` for validation-seeking confusion
- `overwhelmed_learner` for too-many-options
- `beginner_explorer` for completely lost beginners

### 7. TestEdgeCasesAndBoundaries (4 tests)

**Purpose**: Handle edge cases gracefully  
**Key Checks**:

- Empty input → doesn't crash
- Very long text → handled
- Mixed languages → works
- All signals combined → extreme case handled

---

## 🚀 Running Tests in Different Modes

### Mode 1: Quick Check (Fast)

```bash
pytest tests/test_confused_user_scenarios.py --tb=no -q
# Output:
# 27 passed, 9 failed
```

### Mode 2: Verbose with Details (Informative)

```bash
pytest tests/test_confused_user_scenarios.py -vv --tb=short
# Shows each test name + short error description
```

### Mode 3: Full Debug (Detailed)

```bash
pytest tests/test_confused_user_scenarios.py -vv --tb=long -s
# Shows everything + print statements
```

### Mode 4: Stop on First Failure (Development)

```bash
pytest tests/test_confused_user_scenarios.py -x
# Stops at first failure (helpful when fixing issues)
```

### Mode 5: Show Slowest Tests (Performance)

```bash
pytest tests/test_confused_user_scenarios.py --durations=10
# Shows slowest 10 tests
```

---

## 📝 Adding New Test Cases

### Template for New Test

```python
class TestNewScenario:
    """Test description."""

    def test_specific_scenario_name(self):
        """
        Describe what this tests.

        Skenario: [Real world scenario]
        Expected: [What should happen]
        """
        # ARRANGE
        text = "User input text here"

        # ACT
        result = analyze_pretext(text)

        # ASSERT
        assert result["confidence_score"] < 0.7, \
            f"Expected low confidence, got {result['confidence_score']}"
        assert result["needs_assessment"] is True
        assert result["target_role"] in ["role1", "role2", "general_learner"]
```

### Example: Add Test for Career Pivot

```python
def test_career_pivot_with_skill_gap(self):
    """
    Skenario: User switching career with skill gaps.

    Input: "Saya developer 5 tahun tapi mau pivot ke data science.
            Takut skills ga cukup."
    Expected: Detect career switch + skill concern
    """
    text = "Saya developer 5 tahun tapi mau pivot ke data science. Takut skills ga cukup."
    result = analyze_pretext(text)

    assert result["intent"] == "switch_career"
    assert "data" in result["domain_interest"]
    assert result["blocker_type"] in ["fear", "skill_gap"]
    assert result["needs_assessment"] is True

    # Can add custom assertion message
    assert result["confidence_score"] < 0.75, \
        f"Career pivot should have uncertainty, got {result['confidence_score']}"
```

---

## 🔧 Debugging Failed Tests

### Step 1: Run Single Failing Test

```bash
pytest tests/test_confused_user_scenarios.py::TestMultiRoleScenarios::test_mentions_three_roles_simultaneously -vv
```

### Step 2: Add Debug Output

```python
def test_mentions_three_roles_simultaneously(self):
    text = "Saya bingung antara frontend, backend, atau data science..."
    result = analyze_pretext(text)

    # Add these for debugging
    print(f"\nFull result: {result}")
    print(f"Persona type: {result['persona_type']}")
    print(f"Confidence: {result['confidence_score']}")
    print(f"Blocker type: {result['blocker_type']}")
    print(f"Domain interest: {result['domain_interest']}")

    # Then your assertions
    assert result["persona_type"] == "overwhelmed_learner"
```

### Step 3: Run with Print Output

```bash
pytest tests/test_confused_user_scenarios.py::TestMultiRoleScenarios::test_mentions_three_roles_simultaneously -vv -s
# -s flag shows print() statements
```

### Step 4: Analyze the Output

```
Full result: {
  'persona_type': 'learner',  ❌ Expected: overwhelmed_learner
  'confidence': 0.45,
  'blocker_type': 'none',  ❌ Expected: too_many_options
  'domain_interest': 'data'
}
```

### Step 5: Identify Root Cause

- Blocker type not "too_many_options" → Multi-domain detection issue
- Persona not "overwhelmed_learner" → Persona rule not triggered

---

## 🔗 Integration Points

### Where These Test Results Feed Into

```
Test Cases (this file)
    ↓
Engine 1: Pretext Analysis
    ↓
Downstream Engines (2-8)
    ├─ Engine 2: Question Selection
    ├─ Engine 3: Assessment Scoring
    ├─ Engine 4: Profile Building
    ├─ Engine 5: Skill Gap Mapping
    ├─ Engine 6: Action Planning
    ├─ Engine 7: Task Evaluation
    └─ Engine 8: Progress Tracking
    ↓
API Responses
    ↓
Frontend/User Experience
```

**Key Connection Points**:

1. **Pretext Analysis Output** → Used by all downstream engines
2. **Confidence Score** → Affects assessment difficulty/complexity
3. **Persona Type** → Determines recommendation strategy
4. **Needs Assessment** → Triggers assessment path
5. **Blocker Type** → Affects action plan recommendations

---

## 🎯 Performance Metrics

### Current Test Performance

```
Test Suite Runtime: ~2.5 seconds
Tests Per Second: ~14 tests/sec
Memory Usage: < 50MB

Breakdown by Category:
- TestUserConfusion: 100ms (7 tests)
- TestMultiRoleScenarios: 400ms (8 tests)
- TestConfusedMultiRoleCombinations: 300ms (5 tests)
- TestAPIHandlingConfusedUsers: 1200ms (4 tests) ← Slowest (API calls)
- TestConfusionDetectionLogic: 200ms (4 tests)
- TestConfusedUserPersonas: 150ms (4 tests)
- TestEdgeCasesAndBoundaries: 150ms (4 tests)
```

**Note**: API integration tests are slower due to FastAPI server startup

---

## 📋 Checklist: After Adding New Tests

- [ ] Test has clear docstring explaining scenario
- [ ] Uses `ARRANGE → ACT → ASSERT` pattern
- [ ] Assertions have helpful failure messages
- [ ] Test is independent (doesn't depend on other tests)
- [ ] Test data is realistic (actual Indonesian text)
- [ ] Test covers happy path AND edge cases
- [ ] Run test individually to verify it passes/fails as expected
- [ ] Run full suite to ensure no regression
- [ ] Update documentation if adding new category

---

## 🚨 Common Test Issues & Fixes

### Issue 1: Test Passes Locally But Fails in CI

**Solution**:

- Check for hardcoded paths
- Ensure test data is committed to repo
- Mock external dependencies

### Issue 2: Flaky Test (Sometimes Pass, Sometimes Fail)

**Solution**:

- Don't rely on timing
- Don't use random data without seed
- Mock datetime if using current time

### Issue 3: Test Too Slow

**Solution**:

- Avoid API calls in unit tests (mock instead)
- Cache expensive operations
- Use fixtures for setup

### Issue 4: Test Passes But Doesn't Test Anything

**Red Flags**:

- Assertion is always true (e.g., `assert 1 < 10`)
- Test doesn't call the function
- Uses wrong data

**Solution**: Review assertion logic

---

## 📞 Test Organization

### Files Structure

```
tests/
├─ test_confused_user_scenarios.py     ← Confused user tests (THIS FILE)
├─ test_ai_ml_module_pipeline.py       ← End-to-end pipeline tests
├─ test_baseline_pretext_engine.py     ← Older rule-engine tests
├─ test_api.py                         ← API endpoint tests
├─ test_*.py                           ← Other engine tests
```

### Documentation

```
docs/
├─ TEST_ANALYSIS_CONFUSED_USERS.md     ← Analysis of test results
├─ CONFUSED_USER_SCENARIOS.md          ← Detailed scenario examples
└─ [THIS FILE]                         ← Usage guide
```

---

## 🔄 Continuous Improvement Cycle

```
1. Write Test Cases
   ↓
2. Run Tests Against Current Code
   ↓
3. Analyze Failures
   ↓
4. Identify Root Causes
   ↓
5. Implement Fixes in Engine
   ↓
6. Re-run Tests
   ↓
7. Verify All Pass
   ↓
8. Add More Edge Cases
   ↓
[Repeat from step 2]
```

---

## 🎓 Key Learnings from Test Suite

### What Works Well ✅

1. Confusion detection via low confidence score
2. Multi-role ambiguity via confidence thresholds
3. Assessment triggering mechanism
4. Edge case handling (empty inputs, etc.)

### What Needs Improvement ❌

1. Persona assignment for extreme cases
2. Keyword matching precision
3. Level detection for junior/senior context
4. Multi-role explicit detection
5. API fallback for unclear roles

### Next Steps 📈

1. Implement multi-domain detection
2. Enhance keyword matching algorithm
3. Add explicit multi-role field to API
4. Fix persona rules for overwhelmed case
5. Add clarification questions feature

---

## 📞 Support & Troubleshooting

### If Tests Fail:

1. Check if venv is activated
2. Ensure requirements.txt is installed
3. Check if FastAPI server can start
4. Look at error message carefully

### Common Error Messages:

```
ModuleNotFoundError: No module named 'ai_ml_module'
→ Solution: Run from correct directory, PYTHONPATH set

AssertionError: assert 'x' == 'y'
→ Solution: Check assertion logic, print actual values

ConnectionError: Cannot connect to 127.0.0.1:8000
→ Solution: API tests need app.py accessible
```
