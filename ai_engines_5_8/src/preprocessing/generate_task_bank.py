"""Generate a simple task bank and rubric bank from role-skill mappings.

Input: data/processed/role_skill_mapping.csv
Output:
- data/processed/task_bank.csv
- data/processed/rubric_bank.csv

Creates minimal, non-complex learning tasks and rubrics (Indonesian).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

logging.basicConfig(level=logging.INFO)

ROOT = Path(__file__).resolve().parents[2]
ROLE_SKILL_CSV = ROOT / "data" / "processed" / "role_skill_mapping.csv"
TASK_BANK_CSV = ROOT / "data" / "processed" / "task_bank.csv"
RUBRIC_BANK_CSV = ROOT / "data" / "processed" / "rubric_bank.csv"


DEFAULT_TASKS: Dict[str, List[Dict]] = {
    "frontend_developer": [
        {
            "judul": "Buat halaman sederhana dengan tombol interaktif",
            "deskripsi": "Buat halaman HTML dengan tombol yang men-trigger event JavaScript sederhana. Sertakan file HTML, CSS, dan JS.",
            "keahlian_terkait": ["JavaScript", "HTML", "CSS"],
            "rubric": [
                "Ada struktur HTML yang jelas",
                "Ada styling CSS dasar",
                "Ada event JavaScript yang berfungsi",
                "Ada penjelasan singkat cara kerja (README)"
            ]
        },
        {
            "judul": "Bangun komponen UI menggunakan React (komponen kecil)",
            "deskripsi": "Implementasikan komponen React yang menerima props dan menangani state sederhana.",
            "keahlian_terkait": ["React", "JavaScript"],
            "rubric": [
                "Komponen menggunakan props dan state",
                "Rendering kondisional jika diperlukan",
                "Styling sederhana (CSS atau styled-components)",
                "Dokumentasi penggunaan komponen"
            ]
        },
        {
            "judul": "Buat halaman responsif sederhana",
            "deskripsi": "Desain layout yang responsif untuk desktop dan mobile menggunakan CSS.",
            "keahlian_terkait": ["HTML", "CSS"],
            "rubric": [
                "Layout responsif untuk 2 breakpoints",
                "Menggunakan Flexbox atau Grid",
                "Konten tidak overflow pada mobile",
                "Penjelasan pendek tentang pendekatan responsif"
            ]
        },
        {
            "judul": "Integrasi API sederhana pada UI",
            "deskripsi": "Panggil sebuah API publik dari frontend dan tampilkan hasilnya di halaman.",
            "keahlian_terkait": ["JavaScript", "API"],
            "rubric": [
                "Panggilan API berhasil (fetch/axios)",
                "Menangani loading dan error",
                "Menampilkan data dengan format yang rapi",
                "Dokumentasi endpoint yang dipakai"
            ]
        },
        {
            "judul": "Optimisasi performa frontend sederhana",
            "deskripsi": "Identifikasi dan terapkan 2 optimisasi dasar pada halaman web sederhana.",
            "keahlian_terkait": ["JavaScript", "HTML", "CSS"],
            "rubric": [
                "Identifikasi minimal 2 masalah performa",
                "Terapkan perbaikan (mis. minify, lazy load)",
                "Ukur sebelum dan sesudah perubahan",
                "Jelaskan hasil dan rekomendasi selanjutnya"
            ]
        }
    ],
    "backend_developer": [
        {
            "judul": "Buat REST API sederhana untuk data todo",
            "deskripsi": "Implementasikan REST API dengan endpoint GET/POST untuk resource todo (in-memory atau file).",
            "keahlian_terkait": ["REST API", "Python", "Database"],
            "rubric": [
                "Ada endpoint GET untuk daftar",
                "Ada endpoint POST untuk menambah",
                "Ada validasi input sederhana",
                "Ada dokumentasi request/response"
            ]
        },
        {
            "judul": "Autentikasi sederhana pada API",
            "deskripsi": "Tambahkan mekanisme autentikasi token sederhana untuk API yang dibuat.",
            "keahlian_terkait": ["API", "Security"],
            "rubric": [
                "Endpoint dilindungi oleh token",
                "Token sederhana diissue dan diverifikasi",
                "Dokumentasi cara mendapatkan token",
                "Menangani error autentikasi"
            ]
        },
        {
            "judul": "Menyimpan data ke database sederhana",
            "deskripsi": "Sambungkan API ke database ringan (SQLite) untuk persistensi todo.",
            "keahlian_terkait": ["SQL", "Database", "Python"],
            "rubric": [
                "Schema tabel untuk todo",
                "Operasi CRUD dasar tersedia",
                "Transaksi/commit sederhana dipastikan",
                "Dokumentasi skema dan contoh query"
            ]
        },
        {
            "judul": "Deploy lokal dengan Docker (task sederhana)",
            "deskripsi": "Buat Dockerfile untuk menjalankan aplikasi backend secara lokal.",
            "keahlian_terkait": ["Docker"],
            "rubric": [
                "Ada Dockerfile yang dapat build image",
                "Container menjalankan service",
                "Instruksi run pada README",
                "Tidak menyertakan credential sensitif"
            ]
        },
        {
            "judul": "Logging dan error handling dasar",
            "deskripsi": "Tambahkan logging dan penanganan error yang baik pada API.",
            "keahlian_terkait": ["Python", "API"],
            "rubric": [
                "Menangkap dan mencatat error penting",
                "Menyediakan response dengan status code sesuai",
                "Log cukup informatif untuk debugging",
                "Dokumentasi singkat mengenai format log"
            ]
        }
    ],
    "cyber_security_analyst": [
        {
            "judul": "Analisis log autentikasi dan identifikasi percobaan brute force",
            "deskripsi": "Analisis dataset log sederhana untuk menemukan pola gagal login dan IP mencurigakan.",
            "keahlian_terkait": ["SIEM", "Linux"],
            "rubric": [
                "Menemukan IP sumber serangan",
                "Menjelaskan pola gagal login",
                "Menentukan severity untuk insiden",
                "Memberikan rekomendasi mitigasi"
            ]
        },
        {
            "judul": "Simulasi analisis malware statis sederhana",
            "deskripsi": "Lakukan analisis statis pada binari atau skrip contoh dan catat indikasi berbahaya.",
            "keahlian_terkait": ["Forensic"],
            "rubric": [
                "Mencatat indikator kompromi (IOC)",
                "Menjelaskan alasan indikasi berbahaya",
                "Dokumentasi langkah analisis",
                "Rekomendasi mitigasi dasar"
            ]
        },
        {
            "judul": "Dasar-dasar penetration testing (lab sederhana)",
            "deskripsi": "Jalankan serangkaian pemeriksaan dasar pada aplikasi uji untuk menemukan kerentanan sederhana.",
            "keahlian_terkait": ["Penetration Testing"],
            "rubric": [
                "Menemukan minimal 1 issue",
                "Menjelaskan metode eksploitasi",
                "Menyarankan perbaikan",
                "Mendokumentasikan bukti (screenshot/log)"
            ]
        },
        {
            "judul": "Analisis log jaringan untuk anomali sederhana",
            "deskripsi": "Cari pola trafik yang tidak biasa pada sample pcap atau log jaringan.",
            "keahlian_terkait": ["SIEM", "Linux"],
            "rubric": [
                "Identifikasi pola anomali",
                "Menghubungkan pola ke kemungkinan ancaman",
                "Menentukan langkah investigasi berikutnya",
                "Membuat ringkasan temuan"
            ]
        },
        {
            "judul": "Menetapkan prosedur tanggap insiden sederhana",
            "deskripsi": "Buat checklist tanggap insiden untuk skenario kompromi akun.",
            "keahlian_terkait": ["Incident Response"],
            "rubric": [
                "Checklist langkah-langkah awal (containment)",
                "Penanggung jawab tindakan tercantum",
                "Kriteria eskalasi jelas",
                "Rekomendasi mitigasi jangka panjang"
            ]
        }
    ],
    "data_analyst": [
        {
            "judul": "Bersihkan dataset CSV sederhana dan buat insight awal",
            "deskripsi": "Hapus duplikasi, tangani missing value, dan buat ringkasan statistik untuk dataset contoh.",
            "keahlian_terkait": ["Data Cleaning", "Pandas", "SQL"],
            "rubric": [
                "Menghapus duplikasi dengan benar",
                "Menangani missing value dengan metode yang sesuai",
                "Membuat summary statistik",
                "Menulis insight singkat dan rekomendasi"
            ]
        },
        {
            "judul": "Visualisasi data sederhana untuk insight",
            "deskripsi": "Buat 2 visualisasi yang menjelaskan insight dari dataset.",
            "keahlian_terkait": ["Visualization", "Tableau", "Power BI"],
            "rubric": [
                "Visualisasi relevan untuk insight",
                "Label/legend jelas",
                "Interpretasi hasil disediakan",
                "File/tautan hasil disertakan"
            ]
        },
        {
            "judul": "Query SQL untuk menjawab pertanyaan bisnis sederhana",
            "deskripsi": "Tulis beberapa query SQL untuk menjawab 3 pertanyaan bisnis pada dataset sample.",
            "keahlian_terkait": ["SQL"],
            "rubric": [
                "Query benar dan efisien untuk dataset kecil",
                "Menggunakan agregasi/grouping bila perlu",
                "Memberikan hasil yang terverifikasi",
                "Dokumentasi pertanyaan dan query"
            ]
        },
        {
            "judul": "Membangun pipeline ETL sederhana (lokal)",
            "deskripsi": "Susun script yang mengekstrak CSV, transform dan simpan hasil bersih.",
            "keahlian_terkait": ["Pandas", "Data Cleaning"],
            "rubric": [
                "Pipeline memproses data end-to-end",
                "Transformasi terdokumentasi",
                "Hasil bersih disimpan untuk analisis",
                "Instruksi run disediakan"
            ]
        },
        {
            "judul": "Eksplorasi data dan hipotesis awal",
            "deskripsi": "Lakukan EDA singkat dan ajukan 2 hipotesis yang bisa diuji.",
            "keahlian_terkait": ["Data Analysis", "Pandas"],
            "rubric": [
                "EDA dasar lengkap (missing, distribusi)",
                "Visualisasi pendukung hipotesis",
                "Formulasi hipotesis yang jelas",
                "Saran langkah analisis selanjutnya"
            ]
        }
    ]
}


def generate_tasks_from_role(role: str, entries: List[Dict], start_id: int) -> (List[Dict], List[Dict], int):
    tasks = []
    rubrics = []
    idx = start_id
    role_tasks = DEFAULT_TASKS.get(role, [])
    for t in role_tasks:
        task_id = f"T{idx:04d}"
        tasks.append({
            "id_tugas": task_id,
            "judul": t["judul"],
            "deskripsi": t["deskripsi"],
            "keahlian_terkait": ";".join(t["keahlian_terkait"]),
            "sumber": "generated"
        })
        # create rubric row per task
        rubric_id = f"R{idx:04d}"
        rubrics.append({
            "id_rubrik": rubric_id,
            "keahlian": ";".join(t["keahlian_terkait"]),
            "kriteria": ";".join(t["rubric"]),
            "skor_min": 0,
            "skor_max": 100
        })
        idx += 1
    return tasks, rubrics, idx


def main():
    # read role_skill_mapping if exists to discover roles
    roles = ["frontend_developer", "backend_developer", "cyber_security_analyst", "data_analyst"]
    out_tasks: List[Dict] = []
    out_rubrics: List[Dict] = []
    seq = 1
    for role in roles:
        tasks, rubrics, seq = generate_tasks_from_role(role, [], seq)
        out_tasks.extend(tasks)
        out_rubrics.extend(rubrics)

    TASK_BANK_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_tasks = pd.DataFrame(out_tasks)
    df_tasks.to_csv(TASK_BANK_CSV, index=False)
    logging.info(f"Tersimpan {len(df_tasks)} tugas ke {TASK_BANK_CSV}")

    df_rub = pd.DataFrame(out_rubrics)
    df_rub.to_csv(RUBRIC_BANK_CSV, index=False)
    logging.info(f"Tersimpan {len(df_rub)} rubrik ke {RUBRIC_BANK_CSV}")


if __name__ == "__main__":
    main()
