# Project Alignment Progress

Tanggal audit: 2026-05-31

## Status Singkat

Project saat ini berada di tahap MVP Engine 1-8 yang sudah bisa berjalan end-to-end dengan dataset capstone yang digabung ke data canonical project.

Status teknis terakhir:

- Alignment validation: PASS, 0 error, 0 warning.
- Test suite: PASS, 56 tests.
- FastAPI MVP: endpoint utama dapat berjalan.
- Dataset capstone: sudah diekstrak, dinormalisasi, dan digabung.
- Demo deployment config tersedia: env-based CORS, `/health`, `/readiness`, `Procfile`, dan frontend API config.

## Data Yang Sudah Align

Dataset dari `data/dataset_capstone-20260531T010643Z-3-001.zip` sudah masuk ke struktur project:

- Raw extract: `data/dataset_capstone/`
- Canonical app data: `ai_ml_module/data/`
- Root shared data: `data/`
- Pretext label data: `data/labels/dataset_pretext.csv`

Jumlah data canonical setelah merge:

- `role_skill_mapping.csv`: 69 data mapping role-skill canonical
- `task_bank.csv`: 28 task
- `question_bank.csv`: 1.002 pertanyaan
- `answer_skill_mapping.csv`: 3.000 answer-skill mapping
- `dataset_pretext.csv`: 2.062 contoh pretext

Normalisasi yang sudah dilakukan:

- `web_development` -> `frontend`
- `data_science` -> `data`
- `html` -> `html_basic`
- `css` -> `css_basic`
- `javascript` / `js` -> `javascript_basic`
- `python` -> `python_basic`
- `sql` -> `sql_basic`
- `spreadsheet` -> `spreadsheet_basic`
- `networking` -> `networking_fundamental`

## Engine Yang Sudah Align

### Engine 1 - Pretext Analyzer

Sudah mendukung domain dari dataset capstone:

- `frontend` -> `frontend_developer`
- `ai_ml` -> `machine_learning_engineer`
- `cyber_security` -> `soc_analyst`
- `ui_ux` -> `ui_ux_designer`
- `data` -> `data_analyst`

Catatan penting: model capstone sudah dipakai untuk prediksi `problem_category` seperti `direction_confused`, `beginner_lost`, dan `overwhelmed`. Guard Engine 1 tetap mencegah prediksi format lama seperti `frontend_task` dipakai pada domain yang salah.

### Engine 2 - Question Selector

Sudah membaca `question_bank.csv` hasil merge. Pertanyaan capstone dinormalisasi agar tetap kompatibel dengan kontrak lama:

- `question` dipakai sebagai `prompt`
- `current_level` dipakai sebagai `difficulty`
- `skill_id` diinfer dari `answer_skill_mapping.csv`
- `options` dipakai sebagai keyword fallback

### Engine 5-8

Sudah lolos validasi kontrak:

- role-skill mapping valid terhadap taxonomy
- task-bank role valid terhadap taxonomy
- rubric task id valid terhadap task bank
- output contract Engine 5, 6, 7, 8 valid

## Progress Project Saat Ini

Perkiraan progres MVP AI/ML module:

- Data integration: 80%
- Engine 1-8 deterministic pipeline: 85%
- API MVP: 80%
- Dataset alignment validation: 90%
- ML classifier integration: 60%
- Production readiness: 45%

Kesimpulan: project sudah masuk fase MVP terintegrasi dan bisa didemokan end-to-end, tetapi belum siap production penuh karena kualitas rubric masih generic, model masih perlu data balance, dan real-user feedback loop belum selesai.

## Yang Masih Perlu Dikerjakan

Selesai setelah audit lanjutan:

- Tambahkan rubric untuk semua task baru di `task_bank.csv`.
- Latih ulang model problem category memakai `data/labels/dataset_pretext.csv`.
- Tambahkan tests untuk domain baru: `ai_ml`, `cyber_security`, `ui_ux`, dan `data`.
- Rapikan taxonomy role agar hanya memakai role canonical product.

Catatan hasil:

- `rubric_feedback_bank.csv` sekarang cover 28/28 task dengan 84 rubric row.
- Semua task punya 3 rubric criteria berbasis manual/template skill; criteria fallback generic lama sudah dihapus.
- `role_skill_mapping.csv` dirapikan dari ribuan role mentah menjadi role canonical product.
- Model capstone tersimpan di `evaluation/outputs/problem_category_capstone/` dan artifact aktif disalin ke `ai_ml_module/models/problem_category_logreg.joblib`.
- Hasil training capstone: accuracy `0.8378`, macro F1 `0.2279`. Macro F1 rendah karena dataset sangat imbalanced: mayoritas `direction_confused`, sementara `confidence_issue` hanya 4 row.

Prioritas tinggi berikutnya:

- Tambahkan atau rebalance data untuk kelas minoritas `confidence_issue`, `overwhelmed`, dan `beginner_lost`.
- Validasi kualitas label `dataset_pretext.csv`, karena target_role masih berasal dari job-title mentah sementara product memakai role canonical.
- Buat rubric yang lebih spesifik per domain, bukan hanya rubric auto-generated generic.

Selesai setelah audit ini:

- Ubah assessment flow agar jawaban `single_choice` dari capstone dinilai via `answer_skill_mapping.csv`, bukan keyword scoring saja.
- Tambahkan endpoint real assessment submission: `POST /submit-assessment`.
- Tambahkan data quality report untuk duplikat role, skill alias, dan task tanpa rubric melalui `scripts/generate_data_quality_report.py`.

Selesai setelah audit UI:

- UI `mvp_app/` sekarang memakai flow real: `/analyze-pretext` -> `/select-questions` -> user jawab -> `/submit-assessment`.
- Pertanyaan `single_choice` dirender sebagai radio option dari `options`; pertanyaan non-choice dirender sebagai textarea.
- UI sekarang bisa submit project task ke `/evaluate-task` dari recommended task yang dipilih.

Prioritas sedang berikutnya:

- Lanjutkan review copy/deskripsi task capstone yang masih placeholder seperti `Deskripsi tugas mendalam di sini`.
- Tambahkan UI progress update setelah project evaluation memakai `/update-progress`.

Selesai untuk demo production:

- Backend CORS sekarang dikontrol lewat `CORS_ORIGINS`; wildcard ditolak saat `APP_ENV=production`.
- Backend punya `/health` untuk uptime check dan `/readiness` untuk cek dataset/model.
- Frontend `mvp_app/` memakai `config.js` untuk API base URL, bukan hardcode di source logic.
- Deployment notes tersedia di `DEPLOYMENT.md`.

## Command Verifikasi

```bash
python3 ai_ml_module/validate_alignment.py
python3 -m pytest -q
python3 scripts/generate_data_quality_report.py
PYTHONPATH=. python3 -m uvicorn ai_ml_module.app:app --reload
```
