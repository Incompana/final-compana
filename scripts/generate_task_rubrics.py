"""Generate rubric rows for every task in task_bank.csv."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODULE_DATA = ROOT / "ai_ml_module" / "data"
ROOT_DATA = ROOT / "data"

MANUAL_RUBRICS = [
    {
        "rubric_id": "R_T1_1",
        "task_id": "T1",
        "criteria": "HTML memuat struktur halaman dan tombol utama",
        "weight": 40,
        "required": True,
        "keyword_signal": "html|button|tombol",
        "feedback_if_missing": "Tambahkan struktur HTML dan tombol utama yang terlihat.",
    },
    {
        "rubric_id": "R_T1_2",
        "task_id": "T1",
        "criteria": "Tombol memiliki event handler sederhana",
        "weight": 40,
        "required": True,
        "keyword_signal": "onclick|addeventlistener|queryselector",
        "feedback_if_missing": "Tambahkan event handler untuk tombol, misalnya onclick atau addEventListener.",
    },
    {
        "rubric_id": "R_T1_3",
        "task_id": "T1",
        "criteria": "Submission menyertakan link atau file hasil",
        "weight": 20,
        "required": True,
        "keyword_signal": "github|link|html|screenshot",
        "feedback_if_missing": "Lampirkan link repository, file HTML, atau screenshot hasil.",
    },
    {
        "rubric_id": "R_T2_1",
        "task_id": "T2",
        "criteria": "CSS mengatur layout dan visual tombol",
        "weight": 50,
        "required": True,
        "keyword_signal": "css|style|layout|button|tombol",
        "feedback_if_missing": "Tambahkan CSS untuk layout halaman dan visual tombol.",
    },
    {
        "rubric_id": "R_T2_2",
        "task_id": "T2",
        "criteria": "Style dipisahkan atau ditulis jelas",
        "weight": 30,
        "required": True,
        "keyword_signal": "class|stylesheet|style.css|selector",
        "feedback_if_missing": "Gunakan selector/class atau file stylesheet agar style mudah diperiksa.",
    },
    {
        "rubric_id": "R_T2_3",
        "task_id": "T2",
        "criteria": "Submission menyertakan output HTML atau GitHub",
        "weight": 20,
        "required": True,
        "keyword_signal": "html|github|link|screenshot",
        "feedback_if_missing": "Lampirkan output HTML, screenshot, atau link GitHub.",
    },
    {
        "rubric_id": "R_T3_1",
        "task_id": "T3",
        "criteria": "JavaScript memakai addEventListener atau onclick",
        "weight": 40,
        "required": True,
        "keyword_signal": "addeventlistener|onclick|event",
        "feedback_if_missing": "Tambahkan event handler JavaScript untuk aksi klik.",
    },
    {
        "rubric_id": "R_T3_2",
        "task_id": "T3",
        "criteria": "DOM dipilih dan dimanipulasi dengan jelas",
        "weight": 40,
        "required": True,
        "keyword_signal": "queryselector|getelementbyid|innertext|textcontent|classlist",
        "feedback_if_missing": "Tunjukkan pemilihan elemen DOM dan perubahan teks/style/class.",
    },
    {
        "rubric_id": "R_T3_3",
        "task_id": "T3",
        "criteria": "Submission dapat dijalankan atau diperiksa",
        "weight": 20,
        "required": True,
        "keyword_signal": "github|link|html|screenshot",
        "feedback_if_missing": "Lampirkan link, file, atau screenshot hasil interaksi.",
    },
    {
        "rubric_id": "R_T_AI_M_21_1",
        "task_id": "T_AI_M_21",
        "criteria": "Training pipeline memuat data, fitur, model, dan evaluasi",
        "weight": 45,
        "required": True,
        "keyword_signal": "train|training|dataset|model|fit|evaluate|accuracy|f1",
        "feedback_if_missing": "Jelaskan pipeline training dari data sampai evaluasi model.",
    },
    {
        "rubric_id": "R_T_AI_M_21_2",
        "task_id": "T_AI_M_21",
        "criteria": "Hasil evaluasi model dilaporkan dengan metrik",
        "weight": 35,
        "required": True,
        "keyword_signal": "accuracy|f1|precision|recall|confusion|metric",
        "feedback_if_missing": "Tambahkan metrik evaluasi seperti accuracy, F1, precision, atau recall.",
    },
    {
        "rubric_id": "R_T_AI_M_21_3",
        "task_id": "T_AI_M_21",
        "criteria": "Submission menyertakan notebook, script, atau link repository",
        "weight": 20,
        "required": True,
        "keyword_signal": "notebook|script|github|repository|link",
        "feedback_if_missing": "Lampirkan notebook, script, atau link repository training.",
    },
    {
        "rubric_id": "R_T_DATA_24_1",
        "task_id": "T_DATA_24",
        "criteria": "Query SQL mengambil data dengan SELECT dan filter/agregasi",
        "weight": 45,
        "required": True,
        "keyword_signal": "select|where|group by|join|count|sum|avg",
        "feedback_if_missing": "Tulis query SQL yang memakai SELECT dan minimal satu filter, join, atau agregasi.",
    },
    {
        "rubric_id": "R_T_DATA_24_2",
        "task_id": "T_DATA_24",
        "criteria": "Insight atau interpretasi hasil query dijelaskan",
        "weight": 35,
        "required": True,
        "keyword_signal": "insight|analisis|hasil|interpretasi|temuan",
        "feedback_if_missing": "Tambahkan interpretasi singkat dari hasil query.",
    },
    {
        "rubric_id": "R_T_DATA_24_3",
        "task_id": "T_DATA_24",
        "criteria": "Submission menyertakan screenshot atau link",
        "weight": 20,
        "required": True,
        "keyword_signal": "screenshot|link|github|sql",
        "feedback_if_missing": "Lampirkan screenshot hasil query atau link file SQL.",
    },
    {
        "rubric_id": "R_T_CYBE_25_1",
        "task_id": "T_CYBE_25",
        "criteria": "Perintah Linux dasar digunakan dengan tujuan yang jelas",
        "weight": 45,
        "required": True,
        "keyword_signal": "ls|cd|cat|grep|chmod|ps|systemctl|journalctl",
        "feedback_if_missing": "Gunakan dan jelaskan beberapa perintah Linux dasar yang relevan.",
    },
    {
        "rubric_id": "R_T_CYBE_25_2",
        "task_id": "T_CYBE_25",
        "criteria": "Konteks keamanan atau SOC dijelaskan",
        "weight": 35,
        "required": True,
        "keyword_signal": "log|permission|process|service|security|soc",
        "feedback_if_missing": "Hubungkan perintah Linux dengan konteks keamanan, log, proses, atau service.",
    },
    {
        "rubric_id": "R_T_CYBE_25_3",
        "task_id": "T_CYBE_25",
        "criteria": "Submission menyertakan bukti terminal atau link",
        "weight": 20,
        "required": True,
        "keyword_signal": "screenshot|terminal|link|github",
        "feedback_if_missing": "Lampirkan screenshot terminal atau link catatan praktik.",
    },
    {
        "rubric_id": "R_T_UI_U_13_1",
        "task_id": "T_UI_U_13",
        "criteria": "Desain Figma memuat frame dan komponen utama",
        "weight": 45,
        "required": True,
        "keyword_signal": "figma|frame|component|layout|screen",
        "feedback_if_missing": "Buat frame dan komponen utama di Figma.",
    },
    {
        "rubric_id": "R_T_UI_U_13_2",
        "task_id": "T_UI_U_13",
        "criteria": "Alur pengguna atau prototype dijelaskan",
        "weight": 35,
        "required": True,
        "keyword_signal": "prototype|flow|user flow|wireframe|interaction",
        "feedback_if_missing": "Jelaskan flow/prototype dan interaksi utama pengguna.",
    },
    {
        "rubric_id": "R_T_UI_U_13_3",
        "task_id": "T_UI_U_13",
        "criteria": "Submission menyertakan link Figma atau screenshot",
        "weight": 20,
        "required": True,
        "keyword_signal": "figma|link|screenshot",
        "feedback_if_missing": "Lampirkan link Figma atau screenshot desain.",
    },
]

SKILL_RUBRIC_TEMPLATES = {
    "html_basic": [
        ("HTML memakai struktur dokumen dan elemen semantik dasar", 40, "html|doctype|body|section|main|button|form", "Tambahkan struktur HTML dasar dan elemen yang relevan."),
        ("Konten halaman sesuai tujuan task", 35, "heading|title|text|content|label|tombol", "Pastikan konten halaman menjawab tujuan task."),
        ("Submission menyertakan bukti hasil", 25, "screenshot|link|github|html", "Lampirkan screenshot, link, atau file HTML."),
    ],
    "javascript_basic": [
        ("JavaScript menangani interaksi pengguna", 40, "javascript|addeventlistener|onclick|event|click", "Tambahkan interaksi JavaScript berbasis event."),
        ("DOM dipilih dan diperbarui dengan jelas", 35, "queryselector|getelementbyid|textcontent|innertext|classlist", "Tunjukkan pemilihan dan pembaruan elemen DOM."),
        ("Submission menyertakan bukti interaksi berjalan", 25, "screenshot|link|github|html", "Lampirkan bukti hasil interaksi berjalan."),
    ],
    "ui_principles": [
        ("Desain menerapkan hierarki visual dan spacing", 40, "hierarki|spacing|alignment|kontras|layout", "Jelaskan hierarki visual, spacing, alignment, atau kontras yang dipakai."),
        ("Keputusan UI dikaitkan dengan kebutuhan pengguna", 35, "user|pengguna|persona|kebutuhan|tujuan", "Hubungkan keputusan UI dengan kebutuhan pengguna."),
        ("Submission menyertakan artefak desain", 25, "screenshot|link|figma|wireframe", "Lampirkan screenshot atau link artefak desain."),
    ],
    "figma": [
        ("File Figma memuat frame dan komponen utama", 40, "figma|frame|component|layout|screen", "Buat frame dan komponen utama di Figma."),
        ("Desain menunjukkan konsistensi warna, teks, dan spacing", 35, "color|warna|typography|spacing|style", "Rapikan konsistensi visual desain."),
        ("Submission menyertakan link Figma atau screenshot", 25, "figma|link|screenshot", "Lampirkan link Figma atau screenshot."),
    ],
    "wireframing": [
        ("Wireframe menampilkan struktur layar utama", 40, "wireframe|layout|screen|section|navigation", "Tampilkan struktur layar utama secara jelas."),
        ("Flow pengguna dari awal sampai aksi utama dijelaskan", 35, "flow|user flow|alur|interaction|prototype", "Jelaskan alur pengguna dan aksi utama."),
        ("Submission menyertakan artefak wireframe", 25, "screenshot|link|figma|wireframe", "Lampirkan artefak wireframe."),
    ],
    "sql_basic": [
        ("Query SQL memakai SELECT dengan filter atau agregasi", 40, "select|where|group by|count|sum|avg", "Tulis query SELECT dengan filter atau agregasi."),
        ("Hasil query diinterpretasikan menjadi insight", 35, "hasil|insight|analisis|interpretasi|temuan", "Tambahkan interpretasi hasil query."),
        ("Submission menyertakan query dan bukti output", 25, "sql|screenshot|link|output", "Lampirkan query dan bukti output."),
    ],
    "spreadsheet_basic": [
        ("Spreadsheet memakai formula atau fungsi dasar", 40, "formula|sum|average|countif|vlookup|pivot", "Gunakan formula atau fungsi spreadsheet yang relevan."),
        ("Data dirapikan dan dianalisis menjadi ringkasan", 35, "cleaning|sort|filter|summary|chart|pivot", "Rapikan data dan buat ringkasan analisis."),
        ("Submission menyertakan file, screenshot, atau link sheet", 25, "spreadsheet|sheet|screenshot|link|csv", "Lampirkan file, screenshot, atau link sheet."),
    ],
    "python_basic": [
        ("Kode Python memuat input, proses, dan output yang jelas", 40, "python|def|print|return|input|pandas", "Tunjukkan alur input, proses, dan output dalam kode Python."),
        ("Kode memakai struktur yang mudah dibaca", 35, "function|variable|loop|condition|comment", "Rapikan struktur kode dengan nama variabel/fungsi yang jelas."),
        ("Submission menyertakan script/notebook dan hasil run", 25, "script|notebook|output|github|screenshot", "Lampirkan script/notebook dan hasil eksekusi."),
    ],
    "model_training": [
        ("Pipeline training memuat data, fitur, model, dan evaluasi", 45, "train|training|dataset|model|fit|evaluate|accuracy|f1", "Jelaskan pipeline training dari data sampai evaluasi model."),
        ("Metrik evaluasi model dilaporkan", 35, "accuracy|f1|precision|recall|confusion|metric", "Tambahkan metrik evaluasi model."),
        ("Submission menyertakan notebook, script, atau repository", 20, "notebook|script|github|repository|link", "Lampirkan notebook, script, atau repository."),
    ],
    "mlops": [
        ("Workflow MLOps menjelaskan training, versioning, dan deployment", 40, "mlops|pipeline|versioning|deployment|monitoring", "Jelaskan workflow MLOps dari training sampai deployment/monitoring."),
        ("Artifact model atau eksperimen dapat dilacak", 35, "model|artifact|experiment|metrics|registry|log", "Tambahkan bukti tracking artifact atau eksperimen."),
        ("Submission menyertakan diagram, script, atau link repository", 25, "diagram|script|github|repository|link", "Lampirkan diagram, script, atau repository."),
    ],
    "log_analysis": [
        ("Analisis log menemukan event atau pola penting", 40, "log|event|error|warning|pattern|timestamp", "Identifikasi event, error, atau pola penting dari log."),
        ("Temuan dikaitkan dengan risiko atau tindakan SOC", 35, "incident|risk|soc|alert|investigation|mitigation", "Hubungkan temuan log dengan risiko atau tindakan SOC."),
        ("Submission menyertakan potongan log atau screenshot", 25, "screenshot|log|terminal|link", "Lampirkan potongan log, screenshot, atau link catatan."),
    ],
    "networking_fundamental": [
        ("Konsep jaringan dasar dijelaskan dengan contoh", 40, "ip|dns|tcp|udp|port|subnet|http", "Jelaskan konsep jaringan dasar dengan contoh."),
        ("Analisis memakai command atau bukti praktikum", 35, "ping|traceroute|nslookup|netstat|nmap|wireshark", "Gunakan command/tool jaringan dan jelaskan hasilnya."),
        ("Submission menyertakan screenshot terminal atau link", 25, "screenshot|terminal|link|github", "Lampirkan screenshot terminal atau link catatan."),
    ],
    "linux_basic": [
        ("Perintah Linux dasar digunakan dengan tujuan jelas", 40, "ls|cd|cat|grep|chmod|ps|systemctl|journalctl", "Gunakan perintah Linux dasar yang relevan."),
        ("Output command dijelaskan dalam konteks task", 35, "output|permission|process|service|log|security", "Jelaskan output command dalam konteks task."),
        ("Submission menyertakan bukti terminal atau link", 25, "screenshot|terminal|link|github", "Lampirkan screenshot terminal atau link catatan."),
    ],
}


def clean_token(value: object) -> str:
    return str(value or "").strip()


def skill_keywords(skill_id: str, title: str, description: str) -> str:
    tokens = [t for t in clean_token(skill_id).split("_") if t]
    words = []
    for text in (title, description):
        words.extend([w.strip(".,:;!?()[]{}").lower() for w in clean_token(text).split()])
    selected = []
    for token in tokens + words:
        if len(token) < 3:
            continue
        if token not in selected:
            selected.append(token)
        if len(selected) >= 6:
            break
    return "|".join(selected or [skill_id])


def generate_rubrics(task_df: pd.DataFrame, existing_df: pd.DataFrame) -> pd.DataFrame:
    existing_task_ids = set(existing_df["task_id"].astype(str)) if not existing_df.empty else set()
    rows = []
    for _, task in task_df.iterrows():
        task_id = clean_token(task.get("task_id"))
        if not task_id or task_id in existing_task_ids:
            continue

        skill_id = clean_token(task.get("target_skill_id"))
        template = SKILL_RUBRIC_TEMPLATES.get(skill_id)
        if template:
            for idx, (criteria, weight, keyword_signal, feedback) in enumerate(template, start=1):
                rows.append({
                    "rubric_id": f"R_{task_id}_{idx}",
                    "task_id": task_id,
                    "criteria": criteria,
                    "weight": weight,
                    "required": True,
                    "keyword_signal": keyword_signal,
                    "feedback_if_missing": feedback,
                })
        else:
            title = clean_token(task.get("task_title"))
            description = clean_token(task.get("task_description"))
            output_format = clean_token(task.get("output_format")) or "submission"
            keywords = skill_keywords(skill_id, title, description)

            rows.extend([
                {
                    "rubric_id": f"R_{task_id}_1",
                    "task_id": task_id,
                    "criteria": f"Submission menunjukkan penerapan {skill_id}",
                    "weight": 60,
                    "required": True,
                    "keyword_signal": keywords,
                    "feedback_if_missing": f"Tunjukkan bukti penerapan {skill_id} secara eksplisit dalam submission.",
                },
                {
                    "rubric_id": f"R_{task_id}_2",
                    "task_id": task_id,
                    "criteria": f"Output sesuai format {output_format}",
                    "weight": 40,
                    "required": True,
                    "keyword_signal": output_format.replace("/", "|").replace(",", "|").replace(" ", "|"),
                    "feedback_if_missing": f"Lampirkan output sesuai format yang diminta: {output_format}.",
                },
            ])

    if not rows:
        return existing_df
    return pd.concat([existing_df, pd.DataFrame(rows)], ignore_index=True, sort=False)


def main() -> None:
    task_df = pd.read_csv(MODULE_DATA / "task_bank.csv")
    manual_df = pd.DataFrame(MANUAL_RUBRICS)
    manual_task_ids = set(manual_df["task_id"].astype(str))
    generated_task_df = task_df[~task_df["task_id"].astype(str).isin(manual_task_ids)]
    generated_df = generate_rubrics(generated_task_df, pd.DataFrame())
    rubric_df = pd.concat([manual_df, generated_df], ignore_index=True, sort=False)
    rubric_df = rubric_df.drop_duplicates(subset=["rubric_id"], keep="first")

    for path in (MODULE_DATA / "rubric_feedback_bank.csv", ROOT_DATA / "rubric_feedback_bank.csv"):
        path.parent.mkdir(parents=True, exist_ok=True)
        rubric_df.to_csv(path, index=False)

    covered = rubric_df["task_id"].astype(str).nunique()
    print(f"Wrote rubric_feedback_bank.csv with {len(rubric_df)} rows covering {covered}/{len(task_df)} tasks")


if __name__ == "__main__":
    main()
