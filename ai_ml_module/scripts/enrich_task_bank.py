"""Generate enriched task and rubric banks for Compana.

The app reads CSV data at runtime, so this script keeps task/rubric content
auditable while avoiding hand-editing large CSV files.
"""
from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_DATA = ROOT / "ai_ml_module" / "data"
CANONICAL_DATA = ROOT / "data"
LEGACY_PROCESSED_DATA = ROOT / "ai_engines_5_8" / "data" / "processed"


TASK_FIELDS = [
    "task_id",
    "domain_interest",
    "target_role",
    "target_skill_id",
    "current_level",
    "task_title",
    "task_description",
    "duration_estimate",
    "output_format",
    "difficulty",
    "prerequisite_skill_id",
    "learning_focus",
    "task_steps",
    "assessment_checklist",
    "reference_keywords",
]

RUBRIC_FIELDS = [
    "rubric_id",
    "task_id",
    "criteria",
    "weight",
    "required",
    "keyword_signal",
    "feedback_if_missing",
]

LEGACY_TASK_FIELDS = ["id_tugas", "judul", "deskripsi", "keahlian_terkait", "sumber"]
LEGACY_RUBRIC_FIELDS = ["id_rubrik", "keahlian", "kriteria", "skor_min", "skor_max"]


SKILL_LABELS = {
    "html_basic": "HTML dasar",
    "css_basic": "CSS dasar",
    "javascript_basic": "JavaScript dasar",
    "rest_api": "REST API",
    "sql_basic": "SQL dasar",
    "git": "Git dan GitHub",
    "typescript": "TypeScript",
    "python_basic": "Python dasar",
    "java": "Java",
    "php": "PHP",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "docker": "Docker",
    "wireframing": "wireframe",
    "ui_principles": "prinsip UI",
    "ui_ux": "UI/UX",
    "prototyping": "prototype",
    "figma": "Figma",
    "spreadsheet_basic": "spreadsheet",
    "excel": "Excel",
    "problem_solving": "problem solving",
    "tableau": "Tableau",
    "power_bi": "Power BI",
    "machine_learning": "machine learning",
    "etl": "ETL",
    "data_modeling": "data modeling",
    "bigquery": "BigQuery",
    "log_analysis": "log analysis",
    "networking_fundamental": "networking fundamental",
    "linux_basic": "Linux dasar",
    "mlops": "MLOps",
    "model_training": "model training",
}


ROLE_DOMAIN = {
    "frontend_developer": "frontend",
    "backend_developer": "backend",
    "ui_ux_designer": "ui_ux",
    "soc_analyst": "cyber_security",
    "machine_learning_engineer": "ai_ml",
    "data_analyst": "data",
}


TASKS = [
    # Frontend
    ("T_FRONT_1", "frontend_developer", "html_basic", "beginner", "Bangun Landing Page Portfolio Pertamamu", "Buat halaman portfolio satu layar yang menampilkan nama, ringkasan diri, daftar skill, dan satu tombol call-to-action.", "45m", "html_file/screenshot", "practice", "", "HTML semantic, struktur heading, section, link, dan tombol yang mudah dicek", "Buat file index.html|Tambahkan header berisi nama dan role target|Buat section ringkasan profil dan daftar 3 skill|Tambahkan satu tombol call-to-action|Buka di browser dan screenshot hasilnya", "Ada struktur HTML semantic|Ada heading dan section profil|Ada tombol call-to-action|Ada screenshot hasil browser", "MDN HTML semantic|HTML button basics|portfolio landing page"),
    ("T_FRONT_2", "frontend_developer", "css_basic", "basic", "Rapikan Portfolio dengan Layout Responsif", "Tambahkan CSS agar halaman portfolio memiliki spacing rapi, warna konsisten, dan tetap nyaman dilihat di mobile.", "60m", "html_css_files/screenshot", "practice", "html_basic", "CSS selector, spacing, warna, responsive layout, dan visual hierarchy dasar", "Buat file style.css dan hubungkan ke HTML|Atur font, warna, margin, dan padding utama|Buat layout card/profile yang rapi|Tambahkan media query sederhana untuk mobile|Screenshot tampilan desktop atau mobile", "CSS terhubung ke HTML|Spacing dan warna konsisten|Layout tidak pecah di mobile|Ada screenshot hasil", "MDN CSS basics|CSS media queries|responsive layout"),
    ("T_FRONT_3", "frontend_developer", "javascript_basic", "basic", "Buat Tombol Interaktif dengan JavaScript", "Tambahkan interaksi tombol yang mengubah teks/status halaman saat diklik menggunakan JavaScript dasar.", "45m", "html_js_files/screenshot", "practice", "html_basic", "DOM query, event listener, function, dan update teks sederhana", "Buat file script.js dan hubungkan ke HTML|Pilih tombol memakai querySelector|get atau buat elemen status hasil|Tambahkan addEventListener click|Saat tombol diklik, ubah teks status dan screenshot hasilnya", "JavaScript terhubung ke HTML|Ada querySelector|Ada addEventListener|Ada perubahan tampilan setelah klik", "MDN querySelector|MDN addEventListener|JavaScript DOM"),
    ("T_FRONT_4", "frontend_developer", "css_basic", "beginner", "Buat Komponen Card Responsif", "Buat 3 card sederhana untuk menampilkan project/skill dengan layout yang menyesuaikan lebar layar.", "60m", "html_css_files/screenshot", "practice", "html_basic", "Card component, grid/flex layout, responsive spacing, dan reusable class", "Buat section daftar card|Isi minimal 3 card dengan title dan deskripsi|Gunakan flex atau grid untuk menyusun card|Tambahkan style hover sederhana|Uji tampilan saat layar dipersempit", "Ada minimal 3 card|Layout memakai flex/grid|Card tetap terbaca di mobile|Ada screenshot hasil", "CSS flexbox|CSS grid cards|responsive card component"),
    ("T_FRONT_5", "frontend_developer", "javascript_basic", "intermediate", "Hubungkan Form ke API Dummy dengan Fetch", "Buat form kecil yang mengirim data ke API dummy atau endpoint simulasi lalu menampilkan response JSON.", "1-2 hari", "github_link/screenshot", "practice", "javascript_basic", "Form handling, fetch, async flow, error state, dan rendering response", "Buat form berisi input title dan body|Tangkap submit event tanpa reload halaman|Kirim data memakai fetch POST ke API dummy|Tampilkan loading, success, dan error sederhana|Screenshot response yang berhasil tampil", "Ada form input|Ada fetch POST|Ada handling loading/error|Response JSON tampil di UI", "MDN fetch|JSONPlaceholder API|JavaScript form submit"),
    ("T_FRONT_6", "frontend_developer", "git", "basic", "Dokumentasikan Project Frontend di GitHub", "Susun repository kecil berisi project frontend, README, cara menjalankan, dan screenshot hasil.", "1 hari", "github_link", "portfolio", "html_basic", "GitHub repository, README, screenshot, dan dokumentasi project sederhana", "Buat repository GitHub|Upload file HTML/CSS/JS project|Tulis README berisi tujuan dan cara membuka project|Tambahkan screenshot tampilan|Lampirkan link repository", "Ada link GitHub|README menjelaskan tujuan|Ada cara menjalankan/membuka|Ada screenshot hasil", "GitHub README|frontend portfolio documentation|git basics"),
    ("T_FRONT_7", "frontend_developer", "typescript", "intermediate", "Ubah Data Card menjadi Typed Object", "Buat contoh kecil TypeScript untuk mendefinisikan tipe data card dan merender daftar data secara aman.", "1 hari", "ts_file/screenshot", "practice", "javascript_basic", "Type definition, array object, function parameter, dan data rendering", "Buat type atau interface ProjectCard|Buat array minimal 3 data card|Buat function renderCard yang menerima data typed|Jalankan compile atau tampilkan output|Lampirkan file dan screenshot/error-free output", "Ada type/interface|Ada array data typed|Ada function memakai tipe|Ada bukti compile/output", "TypeScript interface|TypeScript array object|typed JavaScript"),
    ("T_FRONT_8", "frontend_developer", "javascript_basic", "advanced", "Audit dan Perbaiki State UI Sederhana", "Buat mini UI yang memiliki state kosong, loading, sukses, dan error agar user flow lebih jelas.", "1-2 hari", "github_link/screenshot", "practice", "javascript_basic", "UI state, conditional rendering, error handling, dan user feedback", "Buat daftar item atau simulasi request data|Tampilkan state kosong sebelum data ada|Tambahkan tombol load data dengan loading state|Tampilkan success dan error state simulasi|Dokumentasikan alur state di README", "Ada empty state|Ada loading state|Ada success/error state|Ada dokumentasi alur", "frontend UI states|conditional rendering JavaScript|error state UX"),

    # Backend
    ("T_BACK_1", "backend_developer", "javascript_basic", "basic", "Buat Fungsi Validasi Payload API", "Buat script JavaScript yang memvalidasi payload todo sebelum disimpan: title wajib, status hanya pending/done, dan error ditampilkan jelas.", "45m", "js_file/screenshot", "practice", "", "JavaScript object, function, conditional, dan validasi payload API", "Buat file validateTodo.js|Buat function validateTodo(payload)|Validasi title wajib dan minimal 3 karakter|Validasi status hanya pending atau done|Tampilkan contoh payload valid dan invalid di console", "Ada function validasi|Ada minimal 2 contoh test payload|Error message jelas|Ada screenshot/link hasil run", "MDN JavaScript functions|JavaScript object validation|Node.js console run"),
    ("T_BACK_2", "backend_developer", "sql_basic", "basic", "Buat Query SQL untuk Laporan Todo", "Buat skema tabel todo dan query untuk menampilkan todo berdasarkan status, jumlah todo per status, serta update status.", "60m", "sql_file/screenshot", "practice", "javascript_basic", "SQL DDL, SELECT, INSERT, UPDATE, WHERE, GROUP BY, dan filter data", "Buat tabel todos dengan id, title, status, created_at|Masukkan minimal 5 data todo|Tulis SELECT filter status pending|Tulis query GROUP BY status|Tulis UPDATE status dan jelaskan hasilnya", "Ada CREATE TABLE|Ada INSERT minimal 5 data|Ada SELECT WHERE|Ada GROUP BY atau summary|Ada screenshot/file SQL", "SQL CREATE TABLE|SQL SELECT WHERE|SQLite GROUP BY"),
    ("T_BACK_3", "backend_developer", "rest_api", "intermediate", "Buat REST API Todo dengan Validasi Input", "Implementasikan endpoint GET dan POST untuk resource todo. Jelaskan request body, response JSON, dan error handling minimal.", "1-2 hari", "github_link/api_screenshot", "practice", "sql_basic", "REST API, HTTP method, request body, response JSON, status code, error handling", "Buat endpoint GET /todos|Buat endpoint POST /todos|Validasi title dan status sebelum menyimpan|Return response JSON dengan status code sesuai|Test endpoint memakai Postman, curl, atau browser", "Ada endpoint GET dan POST|Response berbentuk JSON|Ada validasi input|Ada error response saat payload salah|Ada bukti test API", "REST API basics|HTTP status code|Express.js REST API"),
    ("T_BACK_4", "backend_developer", "git", "basic", "Buat Repository Portfolio Backend", "Susun repository GitHub untuk mini API backend: README, struktur folder, contoh request, dan screenshot hasil endpoint.", "1 hari", "github_link/readme_screenshot", "portfolio", "javascript_basic", "Portfolio backend, dokumentasi API, README, struktur folder, dan bukti endpoint", "Buat repository GitHub untuk mini backend|Rapikan struktur folder minimal src atau app|Tulis README berisi tujuan dan cara menjalankan|Tambahkan contoh endpoint dan request response|Lampirkan screenshot endpoint berjalan", "Ada link GitHub|README menjelaskan project|Ada contoh endpoint/request response|Ada screenshot endpoint|Struktur folder mudah dipahami", "GitHub backend portfolio|API README example|backend project documentation"),
    ("T_BACK_5", "backend_developer", "python_basic", "basic", "Buat Script Python Ringkasan Todo", "Buat script Python yang memvalidasi list todo dan menghitung ringkasan pending/done.", "60m", "python_file/screenshot", "practice", "sql_basic", "Python function, dictionary, list, conditional, dan ringkasan data", "Buat list minimal 5 todo dictionary|Buat function validate_todo|Buat function count_by_status|Cetak hasil validasi dan summary|Lampirkan file dan screenshot output", "Ada list/dictionary todo|Ada function validasi|Ada summary status|Ada handling data invalid|Ada bukti output", "Python dictionary list|Python function basics|Python data validation"),
    ("T_BACK_6", "backend_developer", "java", "basic", "Buat Program Java CRUD Todo Console", "Buat program Java console untuk tambah todo, lihat daftar todo, ubah status, dan menampilkan output yang jelas.", "1 hari", "github_link/terminal_screenshot", "practice", "sql_basic", "Java class, method, list, conditional, loop, dan CRUD sederhana", "Buat class Todo dengan id, title, status|Buat menu tambah, lihat, dan ubah status|Simpan data memakai ArrayList|Tampilkan minimal 3 contoh todo|Jalankan program dan screenshot terminal", "Ada class Todo|Ada ArrayList atau struktur data sejenis|Ada fitur tambah dan lihat|Ada fitur ubah status|Ada screenshot terminal", "Java class object|Java ArrayList|Java console application"),
    ("T_BACK_7", "backend_developer", "docker", "advanced", "Containerize Mini API Backend", "Buat Dockerfile untuk menjalankan mini API backend dan dokumentasikan cara build/run container.", "1-2 hari", "github_link/terminal_screenshot", "practice", "rest_api", "Dockerfile, image build, container run, port mapping, dan dokumentasi deployment awal", "Tambahkan Dockerfile ke project backend|Pastikan app bisa jalan dari container|Build image dengan nama jelas|Run container dan test endpoint|Tulis perintah build/run di README", "Ada Dockerfile|Container berhasil run|Endpoint bisa ditest|README berisi command build/run|Ada screenshot terminal/API", "Dockerfile Node.js|docker build run|containerized REST API"),
    ("T_BACK_8", "backend_developer", "ci_cd", "advanced", "Buat Checklist CI/CD untuk API Backend", "Susun workflow sederhana untuk menjalankan test/build backend otomatis dan catat status sukses/gagal.", "1-2 hari", "github_link/workflow_screenshot", "practice", "git", "CI/CD basics, automated check, test command, build command, dan workflow documentation", "Tentukan command test atau build backend|Buat file workflow GitHub Actions sederhana|Jalankan workflow di repository|Catat error jika workflow gagal|Lampirkan screenshot workflow", "Ada workflow file|Ada command test/build|Workflow pernah dijalankan|Ada screenshot status|Ada catatan perbaikan jika gagal", "GitHub Actions Node.js|CI CD basics|backend build workflow"),

    # UI/UX
    ("T_UIUX_1", "ui_ux_designer", "ui_principles", "beginner", "Audit UI Satu Halaman dengan Prinsip Dasar", "Pilih satu halaman aplikasi dan nilai hierarki visual, konsistensi, spacing, dan readability.", "45m", "doc_link/screenshot", "practice", "", "Visual hierarchy, consistency, spacing, contrast, dan readability", "Pilih satu halaman aplikasi atau screenshot|Tandai 3 bagian yang sudah baik|Tandai 3 bagian yang perlu diperbaiki|Tulis alasan berdasarkan prinsip UI|Buat rekomendasi perbaikan singkat", "Ada screenshot halaman|Ada minimal 3 temuan baik|Ada minimal 3 temuan perbaikan|Alasan memakai prinsip UI", "UI design principles|visual hierarchy|heuristic UI review"),
    ("T_UIUX_2", "ui_ux_designer", "wireframing", "basic", "Rancang Wireframe Low-Fidelity Dashboard", "Buat wireframe sederhana untuk dashboard career companion berisi ringkasan status, task aktif, dan progress.", "1 hari", "figma_link/image", "practice", "ui_principles", "Low-fidelity wireframe, layout priority, sectioning, dan user flow dashboard", "Tentukan 3 informasi utama di dashboard|Buat wireframe low-fidelity di Figma/kertas|Label setiap area penting|Tambahkan alur klik ke task aktif|Lampirkan gambar atau link Figma", "Ada wireframe dashboard|Ada label area penting|Ada task aktif/progress|Ada link/gambar hasil", "low fidelity wireframe|dashboard UX layout|Figma wireframe"),
    ("T_UIUX_3", "ui_ux_designer", "figma", "intermediate", "Buat Component Button dan Card di Figma", "Buat component button dan card dengan variant sederhana agar desain lebih konsisten.", "1 hari", "figma_link/screenshot", "practice", "wireframing", "Figma component, variant, spacing, naming, dan consistency", "Buat frame UI kecil|Buat component button primary/secondary|Buat component card informasi|Atur auto layout atau spacing konsisten|Screenshot panel component/variant", "Ada component button|Ada component card|Naming rapi|Spacing konsisten|Ada screenshot/link Figma", "Figma components|Figma variants|auto layout basics"),
    ("T_UIUX_4", "ui_ux_designer", "prototyping", "intermediate", "Buat Prototype Flow Submit Task", "Buat prototype sederhana dari halaman action plan ke detail task lalu feedback setelah submit.", "1-2 hari", "figma_link/prototype", "practice", "figma", "Interactive prototype, task flow, state transition, dan user feedback", "Buat minimal 3 screen: action plan, detail task, feedback|Hubungkan screen dengan prototype interaction|Tambahkan state submit sukses/revisi|Uji alur klik dari awal sampai feedback|Lampirkan link prototype", "Ada minimal 3 screen|Prototype bisa diklik|Ada state feedback|Flow mudah diikuti|Ada link Figma", "Figma prototype|UX flow task submission|interactive prototype"),
    ("T_UIUX_5", "ui_ux_designer", "ui_ux", "intermediate", "Buat User Flow Onboarding Aplikasi Karir", "Petakan alur user dari input kebingungan sampai mendapat action plan pertama.", "60m", "diagram_link/screenshot", "practice", "ui_principles", "User flow, decision point, empty state, dan outcome action plan", "Tulis tujuan user dalam 1 kalimat|Buat step user dari input sampai action plan|Tandai decision point atau klarifikasi|Tentukan output setiap step|Lampirkan diagram flow", "Ada tujuan user|Ada flow step-by-step|Ada decision point|Ada output per step|Ada screenshot/diagram", "user flow UX|onboarding flow|career app UX"),
    ("T_UIUX_6", "ui_ux_designer", "css_basic", "basic", "Terjemahkan Wireframe ke Layout HTML CSS", "Buat versi HTML/CSS sederhana dari wireframe dashboard agar struktur visual bisa diuji di browser.", "1 hari", "html_css_files/screenshot", "practice", "wireframing", "Layout implementation, CSS spacing, section hierarchy, dan browser preview", "Pilih wireframe yang sudah dibuat|Buat struktur HTML section dashboard|Tambahkan CSS spacing dan card sederhana|Preview di browser|Bandingkan hasil dengan wireframe dalam catatan singkat", "Ada HTML/CSS|Layout mengikuti wireframe|Spacing rapi|Ada screenshot browser|Ada catatan perbandingan", "HTML CSS from wireframe|dashboard layout CSS|UI implementation basics"),
    ("T_UIUX_7", "ui_ux_designer", "javascript_basic", "basic", "Buat Interaksi Prototype Ringan di Browser", "Tambahkan interaksi sederhana seperti tab/filter pada layout HTML agar flow terasa hidup.", "1 hari", "html_js_files/screenshot", "practice", "css_basic", "DOM interaction, simple tabs/filter, feedback state, dan usability check", "Buat dua tab atau filter sederhana|Tambahkan JavaScript click handler|Pastikan tampilan berubah saat diklik|Tambahkan active state visual|Screenshot sebelum dan sesudah klik", "Ada interaksi klik|Ada perubahan tampilan|Ada active state|Ada screenshot hasil|Kode mudah dicek", "JavaScript tabs|DOM click interaction|interactive UI prototype"),
    ("T_UIUX_8", "ui_ux_designer", "agile_scrum", "basic", "Susun Backlog Perbaikan UX Prioritas", "Ubah hasil audit UI menjadi backlog kecil berisi masalah, dampak user, dan prioritas pengerjaan.", "45m", "doc_link/screenshot", "practice", "ui_principles", "UX issue backlog, prioritization, user impact, dan acceptance criteria", "Pilih 5 temuan dari audit UI|Tulis impact user untuk tiap temuan|Beri prioritas high/medium/low|Tulis acceptance criteria singkat|Lampirkan backlog dalam doc/screenshot", "Ada minimal 5 item backlog|Ada impact user|Ada prioritas|Ada acceptance criteria|Output bisa dicek reviewer", "UX backlog|prioritization UX|acceptance criteria design"),

    # SOC
    ("T_CYBE_1", "soc_analyst", "networking_fundamental", "beginner", "Petakan Alur Koneksi HTTP Sederhana", "Buat catatan visual tentang perjalanan request HTTP dari browser ke server dan kembali ke user.", "45m", "doc_link/diagram", "practice", "", "IP, DNS, port, HTTP request/response, dan client-server flow", "Gambar alur browser ke DNS ke server|Label IP, domain, port, request, response|Jelaskan fungsi tiap bagian dalam 1 kalimat|Tambahkan contoh URL dan port|Lampirkan diagram/catatan", "Ada diagram alur|Ada label IP/domain/port|Ada penjelasan request response|Ada contoh URL|Output bisa dicek", "HTTP request flow|DNS basics|networking fundamentals"),
    ("T_CYBE_2", "soc_analyst", "linux_basic", "basic", "Jalankan Perintah Linux untuk Investigasi Awal", "Gunakan perintah Linux dasar untuk melihat file log simulasi, mencari keyword, dan menghitung temuan sederhana.", "60m", "terminal_screenshot/notes", "practice", "networking_fundamental", "Linux ls, cat, grep, wc, tail, dan pencarian log awal", "Buat file sample.log berisi minimal 10 baris event|Gunakan cat atau tail untuk membaca log|Gunakan grep untuk mencari failed/login/error|Gunakan wc untuk menghitung hasil|Screenshot terminal dan tulis catatan temuan", "Ada sample log|Ada penggunaan grep|Ada hitungan dengan wc atau sejenis|Ada screenshot terminal|Ada catatan temuan", "Linux grep logs|Linux command line basics|SOC Linux basics"),
    ("T_CYBE_3", "soc_analyst", "log_analysis", "intermediate", "Analisis Pola Login Mencurigakan dari Sample Log", "Analisis sample authentication log untuk menemukan IP/user dengan pola failed login berulang dan tulis rekomendasi tindak lanjut.", "1-2 hari", "log_notes/screenshot", "practice", "linux_basic", "Log parsing, failed login count, source IP, threshold, findings, dan recommendation", "Buat atau gunakan sample auth log minimal 12 baris|Identifikasi field timestamp, user, source IP, dan status|Hitung failed login per IP atau user|Tandai IP/user mencurigakan jika gagal login berulang|Tulis 3 findings dan 2 rekomendasi mitigasi", "Ada sample log|Ada hitungan failed login|Ada identifikasi IP/user mencurigakan|Ada findings dan rekomendasi|Ada screenshot/catatan hasil", "auth log analysis|failed login detection|SOC log analysis"),
    ("T_CYBE_4", "soc_analyst", "log_analysis", "intermediate", "Buat Ringkasan Alert SOC dari 10 Event", "Kelompokkan 10 event keamanan simulasi menjadi alert prioritas rendah/sedang/tinggi dengan alasan singkat.", "1 hari", "doc_link/table_screenshot", "practice", "log_analysis", "Alert triage, severity, event grouping, and SOC summary writing", "Buat tabel 10 event berisi timestamp, source, event, severity awal|Kelompokkan event serupa|Tentukan prioritas low/medium/high|Tulis alasan prioritas tiap alert|Buat ringkasan 3 alert paling penting", "Ada tabel 10 event|Ada grouping event|Ada prioritas alert|Ada alasan severity|Ada ringkasan alert", "SOC alert triage|security event severity|alert summary"),
    ("T_CYBE_5", "soc_analyst", "log_analysis", "advanced", "Petakan Alur Investigasi Phishing Sederhana", "Buat checklist investigasi phishing dari email mencurigakan sampai rekomendasi containment.", "1-2 hari", "doc_link/checklist", "practice", "log_analysis", "Phishing indicator, investigation checklist, evidence, containment, dan reporting", "Buat contoh email phishing simulasi|Tandai indikator seperti domain, link, sender, urgency|Tulis langkah investigasi awal|Tentukan bukti yang perlu dikumpulkan|Tulis rekomendasi containment dan edukasi user", "Ada contoh email simulasi|Ada indikator phishing|Ada langkah investigasi|Ada daftar bukti|Ada rekomendasi containment", "phishing investigation checklist|SOC phishing analysis|email security indicators"),
    ("T_CYBE_6", "soc_analyst", "networking_fundamental", "basic", "Baca Output Nmap Simulasi dan Tentukan Risiko", "Analisis output nmap simulasi untuk mengidentifikasi port terbuka dan risiko dasar yang perlu ditindaklanjuti.", "60m", "notes/screenshot", "practice", "networking_fundamental", "Open port, service detection, basic risk, and next action recommendation", "Gunakan output nmap simulasi minimal 5 port|Catat port yang terbuka dan service-nya|Kelompokkan risiko low/medium/high|Tulis alasan risiko untuk 3 port|Berikan rekomendasi follow-up", "Ada daftar port/service|Ada klasifikasi risiko|Ada alasan risiko|Ada rekomendasi follow-up|Ada screenshot/catatan", "nmap output basics|open ports risk|network service enumeration"),
    ("T_CYBE_7", "soc_analyst", "linux_basic", "intermediate", "Buat Script Filter Log Sederhana", "Buat command atau script kecil untuk memfilter event failed login dan menyimpan hasilnya ke file output.", "1 hari", "script_or_command/screenshot", "practice", "linux_basic", "Shell command, grep/awk, output redirection, and repeatable log filtering", "Siapkan sample log minimal 15 baris|Tulis command grep/awk untuk failed login|Simpan hasil filter ke file baru|Hitung jumlah baris hasil filter|Lampirkan command dan screenshot output", "Ada sample log|Ada command filter|Ada file output hasil filter|Ada jumlah event|Ada screenshot terminal", "grep awk log filter|Linux redirection|SOC shell scripting"),
    ("T_CYBE_8", "soc_analyst", "log_analysis", "advanced", "Tulis Mini Incident Report dari Temuan Log", "Ubah hasil analisis log menjadi incident report pendek berisi summary, evidence, impact, dan next action.", "1-2 hari", "doc_link/report", "portfolio", "log_analysis", "Incident summary, evidence table, impact assessment, recommendation, and report clarity", "Ambil satu hasil temuan log sebelumnya|Tulis executive summary 2-3 kalimat|Buat tabel evidence berisi waktu, indikator, dan sumber|Tentukan impact dan severity|Tulis next action yang bisa dilakukan tim", "Ada executive summary|Ada tabel evidence|Ada impact/severity|Ada next action|Report mudah dibaca", "SOC incident report|security evidence table|incident response basics"),

    # AI/ML
    ("T_AIML_1", "machine_learning_engineer", "python_basic", "beginner", "Buat Script Python untuk Membersihkan Teks", "Buat script Python kecil yang membersihkan teks user menjadi lowercase, trim spasi, dan menghapus karakter kosong berlebih.", "45m", "python_file/screenshot", "practice", "", "Python function, string processing, list example, and reproducible output", "Buat function clean_text(text)|Uji minimal 5 contoh teks|Tampilkan input dan output|Tambahkan handling text kosong|Screenshot hasil run", "Ada function Python|Ada minimal 5 contoh|Ada output sebelum/sesudah|Ada handling text kosong|Ada screenshot", "Python string methods|text preprocessing Python|Python function basics"),
    ("T_AIML_2", "machine_learning_engineer", "model_training", "basic", "Latih Classifier Baseline untuk Problem Category", "Buat notebook/script baseline sederhana untuk memprediksi problem category dari teks memakai data kecil.", "1-2 hari", "notebook_or_script/report", "practice", "python_basic", "Train/test split, vectorization, classifier, metrics, and error examples", "Siapkan dataset kecil berisi text dan label|Bagi data train/test|Latih model baseline sederhana|Tampilkan accuracy atau classification report|Catat 3 contoh prediksi salah", "Ada dataset text-label|Ada train/test split|Ada model baseline|Ada metric/report|Ada error examples", "scikit learn text classification|classification report|baseline ML model"),
    ("T_AIML_3", "machine_learning_engineer", "model_training", "intermediate", "Buat Script Inference Model Sederhana", "Buat script inference yang menerima teks input dan mengembalikan label, confidence, dan top prediction.", "1 hari", "python_file/json_output", "practice", "model_training", "Model loading, inference function, JSON output, confidence, and example prediction", "Load model atau buat model simulasi sederhana|Buat function predict(text)|Return label dan confidence|Tambahkan minimal 3 contoh input|Cetak output JSON", "Ada script inference|Ada function predict|Output punya label/confidence|Ada 3 contoh input|Output JSON valid", "ML inference script|Python JSON output|model predict function"),
    ("T_AIML_4", "machine_learning_engineer", "mlops", "basic", "Catat Error Analysis dari Prediksi Model", "Buat dokumen error analysis berisi prediksi salah, pola penyebab, dan rencana perbaikan dataset/model.", "1 hari", "doc_link/csv", "practice", "model_training", "Error analysis, misclassification pattern, dataset improvement, and model iteration", "Kumpulkan minimal 5 prediksi model|Tandai mana yang salah|Kelompokkan pola error|Tulis kemungkinan penyebab|Tulis 3 rencana perbaikan", "Ada daftar prediksi|Ada label salah/benar|Ada pola error|Ada penyebab|Ada rencana perbaikan", "ML error analysis|model evaluation mistakes|dataset improvement"),
    ("T_AIML_5", "machine_learning_engineer", "mlops", "intermediate", "Buat Format Logging Prediksi Model", "Susun format JSONL untuk logging input, label prediksi, confidence, fallback trigger, dan timestamp.", "60m", "jsonl_example/doc", "practice", "mlops", "Prediction logging, JSONL format, confidence threshold, and fallback monitoring", "Tentukan field log yang dibutuhkan|Buat 5 contoh baris JSONL|Tambahkan field confidence dan fallback_trigger|Tentukan threshold confidence rendah|Tulis cara review log mingguan", "Ada format JSONL|Ada minimal 5 contoh|Ada confidence/fallback|Ada threshold|Ada rencana review", "JSONL logging|ML monitoring basics|confidence threshold"),
    ("T_AIML_6", "machine_learning_engineer", "python_basic", "advanced", "Buat Pipeline Preprocessing Reusable", "Buat module preprocessing yang bisa dipakai ulang untuk training dan inference agar transformasi teks konsisten.", "1-2 hari", "python_module/tests_screenshot", "practice", "python_basic", "Reusable module, preprocessing consistency, simple tests, and documentation", "Buat file preprocessing.py|Implementasikan clean_text dan tokenize sederhana|Gunakan fungsi di contoh train/inference|Tambahkan minimal 3 test input-output|Dokumentasikan cara pakai", "Ada module preprocessing|Ada fungsi reusable|Dipakai di contoh lain|Ada test input-output|Ada dokumentasi", "Python module preprocessing|text preprocessing pipeline|reusable ML code"),
    ("T_AIML_7", "machine_learning_engineer", "model_training", "advanced", "Bandingkan Dua Baseline Model", "Bandingkan dua pendekatan model sederhana dan pilih yang paling stabil berdasarkan metric dan error analysis.", "1-2 hari", "notebook/report", "practice", "model_training", "Model comparison, metric table, confusion examples, and decision rationale", "Latih dua baseline sederhana|Buat tabel metric per model|Bandingkan minimal 3 prediksi berbeda|Catat tradeoff tiap model|Tulis pilihan model dan alasannya", "Ada dua model baseline|Ada tabel metric|Ada contoh prediksi|Ada tradeoff|Ada keputusan model", "model comparison sklearn|ML baseline comparison|classification metrics"),
    ("T_AIML_8", "machine_learning_engineer", "mlops", "advanced", "Buat Checklist Deploy Model Siap Produksi", "Susun checklist deployment model berisi artifact, inference script, env config, logging, dan fallback.", "1 hari", "doc_link/checklist", "portfolio", "mlops", "Model artifact, deployment readiness, env config, logging, fallback, and validation", "Daftar artifact model yang harus tersedia|Tulis env/config yang dibutuhkan|Tulis cara menjalankan inference|Tambahkan logging dan fallback requirement|Buat checklist validasi sebelum deploy", "Ada artifact checklist|Ada env/config|Ada command inference|Ada logging/fallback|Ada checklist validasi", "ML deployment checklist|model artifact production|MLOps readiness"),

    # Data Analyst
    ("T_DATA_1", "data_analyst", "spreadsheet_basic", "beginner", "Bersihkan Dataset Spreadsheet Kecil", "Bersihkan data penjualan sederhana dari duplikasi, kolom kosong, dan format angka/tanggal yang tidak konsisten.", "60m", "spreadsheet_link/screenshot", "practice", "", "Data cleaning, duplicate removal, empty cell handling, number/date formatting", "Siapkan tabel minimal 20 baris|Cari duplikasi dan baris kosong|Rapikan format tanggal dan angka|Buat sheet before-after atau catatan perubahan|Screenshot hasil data bersih", "Ada dataset minimal 20 baris|Ada pembersihan duplikasi/kosong|Format tanggal/angka rapi|Ada bukti before-after|Ada screenshot/link", "spreadsheet data cleaning|Excel remove duplicates|Google Sheets cleaning"),
    ("T_DATA_2", "data_analyst", "sql_basic", "basic", "Tulis Insight dari Query SQL Sederhana", "Gunakan SQL untuk menjawab 3 pertanyaan bisnis kecil dari tabel transaksi simulasi.", "1 hari", "sql_file/report", "practice", "spreadsheet_basic", "SQL SELECT, WHERE, GROUP BY, aggregate, and business insight writing", "Buat tabel transaksi minimal 20 baris|Tulis 3 pertanyaan bisnis|Buat query untuk menjawab tiap pertanyaan|Tulis hasil angka utama|Ubah hasil query menjadi 3 insight singkat", "Ada tabel transaksi|Ada 3 query|Ada aggregate/filter|Ada 3 insight|Ada file SQL/screenshot", "SQL aggregate|SQL GROUP BY|data analyst insight"),
    ("T_DATA_3", "data_analyst", "excel", "basic", "Buat Pivot Summary Penjualan", "Buat ringkasan penjualan per kategori atau bulan memakai pivot table dan tulis insight utama.", "60m", "spreadsheet_link/screenshot", "practice", "spreadsheet_basic", "Pivot table, grouping, totals, category comparison, and insight summary", "Siapkan data penjualan minimal 30 baris|Buat pivot per kategori atau bulan|Tambahkan total atau average|Tandai kategori tertinggi/terendah|Tulis 3 insight dari pivot", "Ada pivot table|Ada total/average|Ada perbandingan kategori/bulan|Ada 3 insight|Ada screenshot/link", "Excel pivot table|Google Sheets pivot|sales summary analysis"),
    ("T_DATA_4", "data_analyst", "python_basic", "basic", "Buat Ringkasan Data dengan Python", "Gunakan Python untuk membaca dataset kecil, menghitung summary, dan menampilkan insight sederhana.", "1 hari", "python_file/screenshot", "practice", "spreadsheet_basic", "Python data structures, pandas basics, summary stats, and insight writing", "Siapkan CSV kecil minimal 20 baris|Baca data dengan Python atau pandas|Hitung jumlah baris, missing value, dan summary numeric|Tampilkan top category|Tulis 3 insight", "Ada CSV data|Ada script Python|Ada summary stats|Ada top category|Ada insight dan screenshot", "pandas read csv|Python data summary|data analysis basics"),
    ("T_DATA_5", "data_analyst", "power_bi", "intermediate", "Buat Dashboard Ringkas dari Data Penjualan", "Buat dashboard sederhana berisi KPI total penjualan, kategori teratas, dan tren waktu.", "1-2 hari", "dashboard_screenshot/link", "practice", "excel", "Dashboard KPI, chart selection, trend, category ranking, and visual clarity", "Import dataset penjualan|Buat KPI total penjualan|Buat chart tren per bulan|Buat chart kategori teratas|Tulis 3 insight di dashboard atau catatan", "Ada KPI utama|Ada chart tren|Ada chart kategori|Ada insight|Dashboard bisa dicek", "Power BI beginner dashboard|sales dashboard KPI|dashboard design basics"),
    ("T_DATA_6", "data_analyst", "tableau", "intermediate", "Visualisasikan Tren dan Outlier Data", "Buat visual sederhana untuk menemukan tren dan outlier lalu jelaskan apa yang perlu ditindaklanjuti.", "1-2 hari", "dashboard_screenshot/link", "practice", "excel", "Trend chart, outlier detection, visual annotation, and analytical explanation", "Import dataset kecil|Buat line chart atau bar chart tren|Cari 1-2 outlier atau nilai ekstrem|Tambahkan annotation atau catatan|Tulis rekomendasi tindak lanjut", "Ada visual tren|Ada identifikasi outlier|Ada annotation/catatan|Ada rekomendasi|Ada screenshot/link", "Tableau trend chart|data outlier analysis|visual analytics"),
    ("T_DATA_7", "data_analyst", "problem_solving", "basic", "Ubah Pertanyaan Bisnis menjadi Analisis Data", "Ambil satu masalah bisnis sederhana lalu turunkan menjadi metric, data yang dibutuhkan, dan analisis yang harus dilakukan.", "45m", "doc_link/screenshot", "practice", "spreadsheet_basic", "Problem framing, metric definition, data requirement, and analysis plan", "Tulis satu masalah bisnis sederhana|Tentukan metric utama|Tentukan data/kolom yang dibutuhkan|Tulis langkah analisis|Tentukan output akhir yang akan dibuat", "Ada masalah bisnis|Ada metric utama|Ada data requirement|Ada langkah analisis|Ada output akhir", "data analysis problem framing|business metrics|analytics plan"),
    ("T_DATA_8", "data_analyst", "etl", "advanced", "Rancang Alur ETL Mini untuk Dataset Harian", "Buat rancangan ETL sederhana dari source CSV harian ke tabel bersih dan laporan mingguan.", "1-2 hari", "diagram_doc/screenshot", "portfolio", "sql_basic", "ETL flow, source-target mapping, validation, schedule, and data quality checks", "Gambar source CSV ke staging ke clean table|Tentukan mapping kolom utama|Tambahkan validasi data quality|Tentukan jadwal proses harian/mingguan|Tulis contoh output laporan", "Ada diagram ETL|Ada mapping kolom|Ada data quality check|Ada jadwal proses|Ada contoh output", "ETL pipeline basics|data quality checks|source target mapping"),
]


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _task_row(item: tuple[str, ...]) -> dict[str, object]:
    (
        task_id,
        role,
        skill,
        level,
        title,
        description,
        duration,
        output_format,
        difficulty,
        prerequisite,
        focus,
        steps,
        checklist,
        references,
    ) = item
    return {
        "task_id": task_id,
        "domain_interest": ROLE_DOMAIN[role],
        "target_role": role,
        "target_skill_id": skill,
        "current_level": level,
        "task_title": title,
        "task_description": description,
        "duration_estimate": duration,
        "output_format": output_format,
        "difficulty": difficulty,
        "prerequisite_skill_id": prerequisite,
        "learning_focus": focus,
        "task_steps": steps,
        "assessment_checklist": checklist,
        "reference_keywords": references,
    }


def _keyword_signal(criteria: str, skill: str, output_format: str) -> str:
    words = [
        token.strip(".,:;()").lower()
        for token in f"{criteria} {SKILL_LABELS.get(skill, skill)} {output_format}".split()
    ]
    selected = []
    for word in words:
        if len(word) >= 4 and word not in selected:
            selected.append(word)
        if len(selected) >= 8:
            break
    return "|".join(selected)


def _rubric_rows(task: dict[str, object]) -> list[dict[str, object]]:
    checklist = [part.strip() for part in str(task["assessment_checklist"]).split("|") if part.strip()]
    base = [
        ("Output utama sesuai instruksi task dan bisa dicek reviewer", 35, "Lengkapi output utama task agar reviewer bisa menilai hasilnya."),
        ("Akurasi teknis sesuai skill target dan level task", 30, "Perbaiki bagian teknis agar sesuai skill yang sedang dilatih."),
        ("Bukti hasil disertakan melalui file, link, screenshot, atau catatan proses", 20, "Lampirkan bukti hasil yang bisa dibuka atau diverifikasi."),
        ("Penjelasan proses singkat menyebut keputusan, kendala, dan langkah berikutnya", 15, "Tambahkan catatan proses, kendala, dan langkah perbaikan berikutnya."),
    ]
    if checklist:
        base[0] = (checklist[0], 35, f"Lengkapi bagian ini: {checklist[0]}")
    if len(checklist) > 1:
        base[1] = (checklist[1], 30, f"Lengkapi bagian ini: {checklist[1]}")
    if len(checklist) > 2:
        base[2] = (checklist[2], 20, f"Lengkapi bagian ini: {checklist[2]}")
    if len(checklist) > 3:
        base[3] = (checklist[3], 15, f"Lengkapi bagian ini: {checklist[3]}")

    rows = []
    for index, (criteria, weight, feedback) in enumerate(base, start=1):
        rows.append({
            "rubric_id": f"R_{task['task_id']}_{index}",
            "task_id": task["task_id"],
            "criteria": criteria,
            "weight": weight,
            "required": True if index <= 3 else False,
            "keyword_signal": _keyword_signal(criteria, str(task["target_skill_id"]), str(task["output_format"])),
            "feedback_if_missing": feedback,
        })
    return rows


def main() -> None:
    tasks = [_task_row(item) for item in TASKS]
    rubrics: list[dict[str, object]] = []
    for task in tasks:
        rubrics.extend(_rubric_rows(task))

    for data_dir in (MODULE_DATA, CANONICAL_DATA):
        _write_csv(data_dir / "task_bank.csv", TASK_FIELDS, tasks)
        _write_csv(data_dir / "rubric_feedback_bank.csv", RUBRIC_FIELDS, rubrics)

    legacy_tasks = [
        {
            "id_tugas": task["task_id"],
            "judul": task["task_title"],
            "deskripsi": task["task_description"],
            "keahlian_terkait": SKILL_LABELS.get(str(task["target_skill_id"]), str(task["target_skill_id"])),
            "sumber": "compana_enriched_synthetic",
        }
        for task in tasks
    ]
    legacy_rubrics = [
        {
            "id_rubrik": row["rubric_id"],
            "keahlian": SKILL_LABELS.get(
                str(next((task["target_skill_id"] for task in tasks if task["task_id"] == row["task_id"]), "")),
                "",
            ),
            "kriteria": row["criteria"],
            "skor_min": 0,
            "skor_max": row["weight"],
        }
        for row in rubrics
    ]
    _write_csv(LEGACY_PROCESSED_DATA / "task_bank.csv", LEGACY_TASK_FIELDS, legacy_tasks)
    _write_csv(LEGACY_PROCESSED_DATA / "rubric_bank.csv", LEGACY_RUBRIC_FIELDS, legacy_rubrics)

    print(f"Generated {len(tasks)} tasks and {len(rubrics)} rubric rows.")


if __name__ == "__main__":
    main()
