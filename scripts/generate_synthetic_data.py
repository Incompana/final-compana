#!/usr/bin/env python3
"""Generate expanded synthetic data for AI/ML pipeline training.

Generates diverse pretext examples, problem categories, roles, and levels
to expand the training dataset beyond the minimal 120 rows.
"""
import csv
import json
import random
from pathlib import Path


def load_taxonomy(taxonomy_path: str) -> dict:
    """Load label taxonomy."""
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_pretext_variants(problem_category: str, target_role: str, current_level: str) -> list[str]:
    """Generate diverse pretext text variants for a given category."""
    
    variants = {
        "frontend_task": [
            "Saya baru mulai {role}, tidak tahu harus mulai dari mana.",
            "Saya mengalami kesulitan dengan HTML/CSS untuk {role}.",
            "Bagaimana cara memulai karir sebagai {role}? Saya sangat bingung.",
            "Saya tidak mengerti JavaScript fundamentals untuk {role}.",
            "Saya merasa hilang, tidak ada roadmap yang jelas untuk menjadi {role}.",
            "Saya stuck di awal belajar React sebagai {role}.",
            "Apa aja yang perlu saya pelajari untuk menjadi {role} yang bagus?",
            "Saya kebingungan, mulai dari CSS atau JavaScript ya untuk {role}?",
            "Saya ragu-ragu apakah bisa jadi {role} yang bagus.",
            "Saya takut tidak cukup smart untuk UI/UX di {role}.",
            "Ada banyak framework frontend, saya tidak tahu yang mana untuk {role}.",
            "Saya bingung harus specialisasi di mana sebagai {role}.",
            "Terlalu banyak tools CSS untuk {role}, saya pusing.",
            "Saya tahu skill apa yang perlu, tapi gap di beberapa area {role}.",
            "Saya sudah {current_level} tapi masih ada gap signifikan di responsive design.",
        ],
        "backend_task": [
            "Saya baru mulai backend development sebagai {role}, tidak tahu caranya.",
            "Saya mengalami kesulitan memahami database concepts untuk {role}.",
            "Bagaimana cara memulai backend sebagai {role}? Saya sangat bingung.",
            "Saya tidak mengerti REST API fundamentals untuk {role}.",
            "Saya merasa hilang dengan microservices sebagai {role}.",
            "Saya stuck dengan server-side concepts sebagai {role}.",
            "Apa aja yang perlu saya pelajari untuk menjadi {role} yang solid?",
            "Saya kebingungan, mulai dari SQL atau Python ya untuk {role}?",
            "Saya ragu-ragu apakah bisa jadi {role} yang competent.",
            "Saya takut tidak cukup smart untuk database design di {role}.",
            "Ada banyak backend framework, saya tidak tahu yang mana untuk {role}.",
            "Saya bingung apakah harus focus di DevOps atau coding sebagai {role}.",
            "Terlalu banyak tools backend untuk {role}, overwhelming.",
            "Saya tahu skill apa yang perlu, tapi gap di API design untuk {role}.",
            "Saya sudah {current_level} tapi masih ada gap di performance tuning.",
        ],
    }
    
    # Default variants if category not found
    default_variants = [
        "Saya perlu bantuan dengan {role}, tidak tahu bagaimana cara maju.",
        "Saya tertarik dengan {role}, tapi ada hambatan.",
        "Saya {current_level} di {role}, tapi perlu guidance lebih.",
        "Ada yang perlu saya perbaiki di {role}.",
        "Saya perlu develop lebih lanjut di {role}.",
    ]
    
    category_variants = variants.get(problem_category, default_variants)
    if not category_variants:
        category_variants = default_variants
    
    return [
        v.format(role=target_role, current_level=current_level, skill="technical_skills")
        for v in category_variants
    ]


def generate_dataset(
    output_path: str,
    taxonomy_path: str = "ai_ml_module/data/label_taxonomy.json",
    num_samples: int = 500,
    seed: int = 42
) -> None:
    """Generate synthetic dataset with diverse examples."""
    random.seed(seed)
    
    # Load taxonomy
    taxonomy = load_taxonomy(taxonomy_path)
    
    target_roles = taxonomy.get("target_role", [])
    problem_categories = taxonomy.get("problem_category", [])
    current_levels = taxonomy.get("current_level", [])
    blocker_types = taxonomy.get("blocker_type", [])
    
    rows = []
    
    # Generate samples across all combinations
    total_combinations = len(problem_categories) * len(target_roles) * len(current_levels)
    samples_per_combination = max(1, num_samples // total_combinations)
    
    for problem_cat in problem_categories:
        for role in target_roles:
            for level in current_levels:
                # Generate variants for this combination
                pretext_variants = generate_pretext_variants(problem_cat, role, level)
                
                for _ in range(samples_per_combination):
                    pretext = random.choice(pretext_variants)
                    blocker = random.choice(blocker_types)
                    
                    rows.append({
                        "pretext_text": pretext,
                        "target_role": role,
                        "problem_category": problem_cat,
                        "current_level": level,
                        "blocker_type": blocker,
                    })
    
    # Limit to requested number
    rows = rows[:num_samples]
    
    # Write to CSV
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["pretext_text", "target_role", "problem_category", "current_level", "blocker_type"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Generated {len(rows)} synthetic samples")
    print(f"✓ Saved to: {output_file}")
    print(f"\nDataset breakdown:")
    print(f"  - Problem categories: {len(set(r['problem_category'] for r in rows))}")
    print(f"  - Target roles: {len(set(r['target_role'] for r in rows))}")
    print(f"  - Current levels: {len(set(r['current_level'] for r in rows))}")
    print(f"  - Blocker types: {len(set(r['blocker_type'] for r in rows))}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate synthetic data for AI/ML pipeline")
    parser.add_argument(
        "--output",
        default="data/labels/compana_synthetic_expanded_v1.csv",
        help="Output CSV path"
    )
    parser.add_argument(
        "--taxonomy",
        default="ai_ml_module/data/label_taxonomy.json",
        help="Taxonomy JSON path"
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=500,
        help="Number of synthetic samples to generate"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed"
    )
    
    args = parser.parse_args()
    
    generate_dataset(
        output_path=args.output,
        taxonomy_path=args.taxonomy,
        num_samples=args.num_samples,
        seed=args.seed
    )
