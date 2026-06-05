# Compana Role-Skill-Task Knowledge Base (v1)

Folder ini menyimpan knowledge base terstruktur untuk rekomendasi tugas awal Compana.

## Tujuan

Menyediakan sumber data sederhana dan konsisten untuk:

- pemetaan gap skill per role,
- pemilihan tugas beginner-friendly,
- evaluasi output task dengan rubric ringan.

## Struktur File

- `index.json`: daftar role yang tersedia dan path file role.
- `<role>.json`: definisi lengkap satu role.

Role yang tersedia:

- `cybersecurity`
- `frontend`
- `backend`
- `data_analyst`
- `uiux`

## Struktur Setiap Role JSON

Setiap file role memiliki 4 bagian utama:

1. `required_skills`
- Daftar skill inti untuk role.
- Setiap skill punya `priority`: `high`, `medium`, `low`.

2. `beginner_tasks`
- 3 tugas awal yang realistis untuk pemula.
- Setiap tugas memuat:
  - `focus_skills`: skill yang dilatih,
  - `expected_artifacts`: output konkret untuk evaluasi.

3. `task_rubric`
- Rubrik evaluasi ringan (skala 0-2 per kriteria).
- Dipakai untuk feedback cepat dan konsisten.

## Prinsip Desain

- Tidak membuat skill tree terlalu dalam.
- Fokus pada tugas yang bisa dieksekusi 1-7 hari.
- Rubrik sederhana agar mudah digunakan reviewer manusia maupun rule engine.
- Struktur dibuat untuk early-stage product: jelas, kecil, dan mudah di-maintain.

## Cara Pakai (Contoh)

1. Ambil role user (misal `frontend`).
2. Load `frontend.json`.
3. Bandingkan skill user vs `required_skills`.
4. Pilih task dari `beginner_tasks` sesuai gap prioritas tertinggi.
5. Nilai output user dengan `task_rubric`.
