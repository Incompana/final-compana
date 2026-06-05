"""
Test cases untuk edge scenarios:
1. Pengguna yang benar-benar bingung (confusion)
2. Pengguna yang menyebutkan 2 roles sekaligus (multi-role ambiguity)
3. Pengguna dengan kombinasi bingung + multi-role
4. Deteksi dan handling yang tepat untuk edge cases tersebut
"""

import pytest
from fastapi.testclient import TestClient

from ai_ml_module.app import app
from ai_ml_module.engines.engine1_pretext import analyze_pretext


class TestUserConfusion:
    """Test cases untuk pengguna yang benar-benar bingung."""

    def test_extremely_confused_no_direction(self):
        """Skenario: Pengguna sangat bingung dan tidak tahu arah."""
        text = "Bingung banget mau jadi apa. Tertarik banyak hal tapi ga tahu mulai dari mana."
        result = analyze_pretext(text)

        # Harus terdeteksi sebagai confusion/validation_seeker
        assert result["blocker_type"] in ["none", "confusion", "overwhelm"]
        assert result["confidence_score"] < 0.7
        assert result["needs_assessment"] is True
        assert "bingung" in result["problem_category"].lower() or result["confidence_score"] < 0.6

    def test_confused_about_career_path(self):
        """Skenario: Pengguna ragu tentang pilihan karir mereka."""
        text = "Saya takut memilih jalur yang salah. Belum yakin ini benar-benar cocok untuk saya."
        result = analyze_pretext(text)

        # Harus terdeteksi sebagai fear/validation_seeker
        assert "validation_seeker" in result["persona_type"] or result["confidence_score"] < 0.7
        assert result["needs_assessment"] is True
        assert result["current_level"] in ["beginner", "basic"]

    def test_confused_minimal_input(self):
        """Skenario: Input minimal tapi bingung."""
        text = "Ga tahu apa yang mau saya lakukan"
        result = analyze_pretext(text)

        assert result["confidence_score"] < 0.7
        assert result["needs_assessment"] is True
        assert result["target_role"] == "general_learner"

    def test_confused_with_too_many_interests(self):
        """Skenario: Terlalu banyak minat menyebabkan kebingungan."""
        text = "Saya tertarik sama AI, web development, mobile, dan data science. Tapi karena banyak jadi ga tahu fokus kemana."
        result = analyze_pretext(text)

        # Banyak keyword domain tapi persona harus overwhelmed_learner
        assert result["persona_type"] == "overwhelmed_learner" or result["confidence_score"] < 0.7
        assert result["needs_assessment"] is True

    def test_confused_overthinking(self):
        """Skenario: Overthinking dan ragu-ragu."""
        text = "Aku overthinking banget, takut ga cocok, takut gagal terus, takut salah jalan."
        result = analyze_pretext(text)

        assert result["confidence_score"] < 0.7
        assert result["blocker_type"] in ["none", "fear", "doubt"]
        assert result["needs_assessment"] is True

    def test_confused_imposter_syndrome(self):
        """Skenario: Imposter syndrome dan self-doubt."""
        text = "Saya tidak yakin kemampuan saya cukup untuk karir ini. Mungkin saya tidak cocok."
        result = analyze_pretext(text)

        assert result["confidence_score"] <= 0.7
        assert result["needs_assessment"] is True

    def test_confused_needs_counseling(self):
        """Skenario: Pengguna butuh guidance yang lebih dalam."""
        text = "Saya bingung dengan arah karir saya. Ada banyak pilihan tapi semua terasa mendekat. Bagaimana ya?"
        result = analyze_pretext(text)

        assert result["needs_assessment"] is True
        assert "bingung" in text.lower()


class TestMultiRoleScenarios:
    """Test cases untuk pengguna yang menyebutkan 2 atau lebih roles sekaligus."""

    def test_explicitly_mentions_two_roles_frontend_backend(self):
        """Skenario: Pengguna menyebutkan frontend dan backend secara bersamaan."""
        text = "Saya bingung antara frontend developer atau backend developer. Mana yang lebih cocok?"
        result = analyze_pretext(text)

        # System harus terdeteksi ada ambiguity
        assert result["confidence_score"] < 0.8
        assert result["needs_assessment"] is True
        # Bisa terdeteksi sebagai frontend atau backend tapi confidence rendah
        assert result["target_role"] in ["frontend_developer", "backend_developer", "general_learner"]

    def test_explicitly_mentions_two_roles_data_ai(self):
        """Skenario: Pengguna antara data analyst dan AI/ML engineer."""
        text = "Aku tertarik antara data analysis atau machine learning. Sulit memilih."
        result = analyze_pretext(text)

        assert result["confidence_score"] < 0.8
        assert result["needs_assessment"] is True
        assert result["target_role"] in ["data_analyst", "machine_learning_engineer", "general_learner"]

    def test_explicitly_mentions_two_roles_frontend_mobile(self):
        """Skenario: Pengguna antara frontend web dan mobile development."""
        text = "Saya suka JavaScript dan bisa design responsive. Tapi tertarik juga dengan mobile React Native. Mana dulu?"
        result = analyze_pretext(text)

        assert result["domain_interest"] in ["frontend", "mobile"]
        assert result["confidence_score"] <= 0.8
        assert result["needs_assessment"] is True

    def test_explicitly_mentions_two_roles_backend_devops(self):
        """Skenario: Pengguna antara backend development dan devops."""
        text = "Tertarik backend API dan juga interested dengan infrastructure/devops. Mana starting point?"
        result = analyze_pretext(text)

        assert result["confidence_score"] < 0.8
        assert result["needs_assessment"] is True
        assert result["target_role"] in ["backend_developer", "devops_engineer", "general_learner"]

    def test_mentions_three_roles_simultaneously(self):
        """Skenario: Pengguna menyebutkan 3 roles sekaligus."""
        text = "Saya bingung antara frontend, backend, atau data science. Semua menarik tapi bingung mulai dari mana."
        result = analyze_pretext(text)

        # Confidence harus sangat rendah untuk 3 pilihan
        assert result["confidence_score"] < 0.7
        assert result["needs_assessment"] is True
        assert result["persona_type"] == "overwhelmed_learner"

    def test_first_role_then_questioning_second_role(self):
        """Skenario: Pengguna pertama ngomong role A, kemudian ragu dengan role B."""
        text = "Awalnya saya mau jadi frontend developer. Tapi sekarang saya pertanyakan apakah backend lebih cocok?"
        result = analyze_pretext(text)

        # Bisa terdeteksi frontend atau backend, tapi confidence rendah karena ada questioning
        assert result["confidence_score"] < 0.8
        assert result["needs_assessment"] is True

    def test_multi_role_with_skill_levels(self):
        """Skenario: Bingung antara 2 roles dengan berbagai skill level."""
        text = "Sudah bisa HTML/CSS (intermediate) tapi juga tertarik backend Python (beginner). Mana yang harus diperdalam dulu?"
        result = analyze_pretext(text)

        assert result["domain_interest"] in ["frontend", "backend"]
        assert result["confidence_score"] < 0.75
        assert result["needs_assessment"] is True

    def test_multi_role_comparison(self):
        """Skenario: Pengguna membandingkan 2 roles secara langsung."""
        text = "UI/UX Designer vs Frontend Developer? Mana yang lebih sesuai untuk saya yang suka design tapi juga coding?"
        result = analyze_pretext(text)

        assert result["domain_interest"] in ["ui_ux", "frontend"]
        assert result["confidence_score"] < 0.75
        assert result["needs_assessment"] is True


class TestConfusedMultiRoleCombinations:
    """Test cases untuk kombinasi confusion + multi-role."""

    def test_confused_and_mentions_two_roles(self):
        """Skenario: Pengguna bingung DAN menyebutkan 2 roles."""
        text = "Saya benar-benar bingung antara frontend developer atau backend developer. Keduanya menarik tapi saya tidak yakin cocok."
        result = analyze_pretext(text)

        assert result["confidence_score"] < 0.7
        assert result["needs_assessment"] is True
        assert result["blocker_type"] != "none" or result["confidence_score"] < 0.65

    def test_confused_overwhelmed_with_multiple_roles(self):
        """Skenario: Pengguna overwhelmed dengan multiple roles."""
        text = "Banyak banget pilihan: frontend, backend, mobile, AI. Aku jadi overthinking dan ga tahu mau mulai dari mana. Takut juga salah pilih."
        result = analyze_pretext(text)

        assert result["confidence_score"] < 0.65
        assert result["persona_type"] == "overwhelmed_learner"
        assert result["needs_assessment"] is True

    def test_confused_skills_dont_match_roles(self):
        """Skenario: Pengguna bingung karena skills tidak sesuai dengan roles yang diinginkan."""
        text = "Saya bagus di Python tapi tertarik frontend design. Tapi juga pengen jadi backend. Ga tahu skill mana yang mau diperkuat."
        result = analyze_pretext(text)

        assert result["confidence_score"] < 0.75
        assert result["needs_assessment"] is True

    def test_confused_between_junior_tracks(self):
        """Skenario: Pengguna junior bingung antara 2 junior tracks."""
        text = "Sebagai junior developer, saya bingung antara fokus jadi senior frontend atau pivot ke backend. Kedua menarik tapi butuh guidance."
        result = analyze_pretext(text)

        assert result["current_level"] in ["beginner", "basic"]
        assert result["confidence_score"] < 0.75
        assert result["needs_assessment"] is True

    def test_confused_career_transition_multiple_paths(self):
        """Skenario: Career transition dengan multiple paths."""
        text = "Saya mau career switch dari non-tech. Tertarik dengan data science atau web development tapi bingung jalur mana lebih feasible."
        result = analyze_pretext(text)

        assert result["intent"] in ["learn_new", "switch_career"]
        assert result["confidence_score"] < 0.75
        assert result["needs_assessment"] is True


class TestAPIHandlingConfusedUsers:
    """Test API endpoints dengan confused user inputs."""

    def test_full_pipeline_demo_with_confused_user(self):
        """Test full pipeline dengan confused user input."""
        client = TestClient(app)

        response = client.post(
            "/full-pipeline-demo",
            json={
                "user_id": "confused_user_001",
                "user_input_text": "Saya bingung antara frontend developer atau backend developer. Keduanya menarik tapi ga tahu mana yang cocok.",
            },
        )

        assert response.status_code == 200
        body = response.json()

        # Pretext analysis harus detect confusion
        assert body["pretext_analysis"]["confidence_score"] < 0.8
        assert body["pretext_analysis"]["needs_assessment"] is True

        # Action plan harus memberikan recommendations untuk membantu clarification
        assert body["action_plan"]["recommended_tasks"] is not None

    def test_full_pipeline_demo_with_overthinking_user(self):
        """Test full pipeline dengan overthinking user."""
        client = TestClient(app)

        response = client.post(
            "/full-pipeline-demo",
            json={
                "user_id": "overthinking_user_001",
                "user_input_text": "Saya overthinking banget. Takut salah jalan, takut ga cocok, takut gagal. Tidak yakin dengan kemampuan saya.",
            },
        )

        assert response.status_code == 200
        body = response.json()

        # Harus terdeteksi persona type yang tepat
        persona = body["pretext_analysis"]["persona_type"]
        assert persona in ["validation_seeker", "learner", "overwhelmed_learner"]
        assert body["pretext_analysis"]["needs_assessment"] is True

    def test_full_pipeline_demo_with_multi_role_user(self):
        """Test full pipeline dengan multi-role user."""
        client = TestClient(app)

        response = client.post(
            "/full-pipeline-demo",
            json={
                "user_id": "multi_role_user_001",
                "user_input_text": "Tertarik jadi data scientist atau machine learning engineer. Dua-duanya tentang data dan model tapi bingung pilih.",
            },
        )

        assert response.status_code == 200
        body = response.json()

        # Confidence harus lower karena ada ambiguity
        assert body["pretext_analysis"]["confidence_score"] < 0.8
        assert body["pretext_analysis"]["needs_assessment"] is True

    def test_generate_skill_gap_with_unclear_role(self):
        """Test skill gap generation dengan role yang unclear."""
        client = TestClient(app)

        response = client.post(
            "/generate-skill-gap",
            json={
                "target_role": "general_learner",  # unclear role
                "user_skill_profile": {"general_knowledge": 1},
            },
        )

        assert response.status_code == 200
        body = response.json()

        # Harus memberikan gap recommendations
        assert body["target_role"] == "general_learner"
        assert body.get("priority_gap") is not None


class TestConfusionDetectionLogic:
    """Test logic untuk deteksi confusion dalam pretext analysis."""

    def test_confusion_keywords_detection(self):
        """Test deteksi keywords yang menunjukkan confusion."""
        confusion_keywords = ["bingung", "ragu", "ga tahu", "tidak tahu", "tidak yakin", "takut"]

        test_cases = [
            ("Saya bingung", True),
            ("Saya ragu-ragu", True),
            ("Saya tidak tahu harus ngapain", True),
            ("Saya jelas mau jadi frontend", False),
        ]

        for text, should_be_confused in test_cases:
            result = analyze_pretext(text)
            has_confusion_signal = result["confidence_score"] < 0.7
            assert has_confusion_signal == should_be_confused, f"Failed for: {text}"

    def test_multi_role_keywords_detection(self):
        """Test deteksi keywords yang menunjukkan multiple roles."""
        multi_role_keywords = ["atau", "atau", "ataukah", "vs", "dibanding", "dibandingkan"]

        test_cases = [
            ("Frontend atau backend?", True),
            ("Frontend vs backend", True),
            ("Saya mau jadi frontend developer", False),
        ]

        for text, should_be_multi_role in test_cases:
            result = analyze_pretext(text)
            # Multi-role biasanya lower confidence
            is_multi_role_signal = result["confidence_score"] < 0.75
            assert is_multi_role_signal == should_be_multi_role, f"Failed for: {text}"

    def test_low_confidence_threshold_behavior(self):
        """Test behavior saat confidence score rendah."""
        low_confidence_texts = [
            "Bingung banget",
            "Tidak tahu",
            "Ragu-ragu",
            "Frontend atau backend?",
            "Apa ya",
        ]

        for text in low_confidence_texts:
            result = analyze_pretext(text)
            # Low confidence harus set needs_assessment ke True
            if result["confidence_score"] < 0.6:
                assert result["needs_assessment"] is True

    def test_high_confidence_for_clear_input(self):
        """Test high confidence untuk clear input."""
        clear_texts = [
            "Saya ingin jadi frontend developer dan sudah bisa HTML CSS JavaScript React.",
            "Target saya backend API development dengan Python Flask, sudah punya pengalaman 2 tahun.",
            "Saya data scientist sudah advance dan mau fokus deep learning.",
        ]

        for text in clear_texts:
            result = analyze_pretext(text)
            # Clear input harus high confidence
            assert result["confidence_score"] >= 0.7, f"Failed for: {text}"
            assert result["needs_assessment"] is False


class TestConfusedUserPersonas:
    """Test persona types untuk confused users."""

    def test_validation_seeker_persona(self):
        """Test validation_seeker persona detection."""
        text = "Saya takut salah memilih jalur karir. Butuh validasi bahwa pilihan saya benar."
        result = analyze_pretext(text)

        assert result["persona_type"] in ["validation_seeker", "learner"]
        assert result["needs_assessment"] is True

    def test_overwhelmed_learner_persona(self):
        """Test overwhelmed_learner persona detection."""
        text = "Terlalu banyak yang ingin saya pelajari. Frontend, backend, mobile, AI. Kewalahan dan tidak tahu prioritas."
        result = analyze_pretext(text)

        assert result["persona_type"] == "overwhelmed_learner"

    def test_beginner_explorer_persona(self):
        """Test beginner_explorer persona detection."""
        text = "Saya pemula dan tidak tahu harus mulai dari mana untuk jadi developer."
        result = analyze_pretext(text)

        assert result["persona_type"] in ["beginner_explorer", "learner"]
        assert result["current_level"] == "beginner"

    def test_project_seeker_with_confusion(self):
        """Test project_seeker persona yang juga confused."""
        text = "Saya sudah belajar tapi belum pernah project. Bingung project apa yang cocok untuk portfolio."
        result = analyze_pretext(text)

        assert result["persona_type"] in ["project_seeker", "learner"]


class TestEdgeCasesAndBoundaries:
    """Test edge cases dan boundary conditions."""

    def test_empty_input(self):
        """Test dengan input kosong."""
        result = analyze_pretext("")

        assert result["confidence_score"] < 0.5
        assert result["needs_assessment"] is True
        assert result["target_role"] == "general_learner"

    def test_very_long_confused_input(self):
        """Test dengan input yang panjang dan confused."""
        long_text = " ".join(
            [
                "Saya bingung antara" for _ in range(20)
            ]
        )
        result = analyze_pretext(long_text)

        assert result["confidence_score"] < 0.7
        assert result["needs_assessment"] is True

    def test_mixed_languages_confused_input(self):
        """Test dengan input campuran bahasa."""
        text = "I'm confused antara frontend and backend development. Mana starting point?"
        result = analyze_pretext(text)

        # System should still handle it
        assert result["confidence_score"] < 0.75
        assert result["needs_assessment"] is True

    def test_all_confusion_signals_combined(self):
        """Test dengan semua confusion signals."""
        text = (
            "Saya benar-benar bingung. Ragu-ragu memilih antara frontend, backend, atau mobile. "
            "Takut salah jalan dan tidak yakin kemampuan saya. Kewalahan dengan banyaknya pilihan."
        )
        result = analyze_pretext(text)

        assert result["confidence_score"] < 0.6
        assert result["needs_assessment"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
