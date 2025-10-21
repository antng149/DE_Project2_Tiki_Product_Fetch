```ENGLISH 

Project Overview

Project Name: Tiki Product Fetcher – Data Engineering Mini Project
This project automates the extraction of product data from the Tiki.vn API using Python. It supports parallel fetching (4 workers) for performance, auto-restart & checkpoint recovery, and Discord notifications for error alerts or process interruption.

⸻

Main Features
	•	Parallel Workers (A1, A2, B1, B2): Each handles ¼ of the total 200,000 product IDs.
	•	Auto Checkpoint: Saves progress every 1,000 items to prevent data loss.
	•	Auto Restart: Resumes safely after interruption.
	•	Error Logging: Failed fetches (404, timeout, etc.) recorded in errors_tiki_total.log.
	•	Discord Webhook: Notifies on crash or manual stop.
	•	Final Merge Script: Combines and deduplicates all fetched JSONs into one clean dataset.


DE_Project2_Tiki_Product_Fetch/
│
├── tiki_A1.py ... B2.py       # Worker scripts (parallel runs)
├── tiki_IDs_prep.ipynb        # ID cleaning + splitting (4 txt files)
│
├── ids_A1.txt                 # Product ID subset 1
├── ids_A2.txt                 # Product ID subset 2
├── ids_B1.txt                 # Product ID subset 3
├── ids_B2.txt                 # Product ID subset 4
│
├── errors_tiki_total.log      # 1058 failed fetches (mostly 404)
├── product_ids.txt            # Full cleaned 200,000 product IDs
│
└── README.md



Output Data

The total extracted data includes:
	•	198,942 valid products
	•	1,058 failed (mainly HTTP 404 errors)
	•	Each batch JSON (~1,000 per file) saved in output_json_A1...B2.


Download Full Dataset

Due to GitHub’s file size limit (25 MB), full results are hosted on Google Drive:

Google Drive Folder:
[Click here to access all outputs and final dataset
](https://drive.google.com/drive/folders/1dkvPjuk56mEelXZhGILrZ1y0D5B4Xk38?usp=drive_link)

Includes:
	•	output_json_A1.zip, output_json_A2.zip, output_json_B1.zip, output_json_B2.zip
	•	products_all_dedup.json (final merged dataset, 198,942 products)
	•	errors_tiki_total.log (list of failed product IDs and reasons)

Step 1 — Prepare IDs
Open and run the tiki_IDs_prep.ipynb

Step 2 — Run Fetch Scripts

Use caffeinate (if on macOS) to keep your computer awake during long runs: 
caffeinate python3 tiki_A1.py
caffeinate python3 tiki_A2.py
caffeinate python3 tiki_B1.py
caffeinate python3 tiki_B2.py

Step 3 — Merge & Deduplicate JSON Outputs

After all workers finish, merge and clean the outputs
	•	Combine them into one list
	•	Remove duplicate product IDs
	•	Save to products_all_dedup.json


Final Summary (Results Overview)
Data Overview:
	•	Total input product IDs: 200,000
	•	Successfully fetched: 198,942 (≈ 99.47%)
	•	Failed fetches (404, timeout, etc.): 1,058 (≈ 0.53%)
	•	Valid records after deduplication: 198,942



🇻🇳 README (Tiếng Việt)

Giới thiệu dự án

Tên dự án: Tiki Product Fetcher – Dự án mini về Data Engineering
Dự án này tự động thu thập dữ liệu sản phẩm từ API Tiki.vn bằng Python.
Hệ thống hỗ trợ chạy song song (4 tiến trình) để tăng tốc độ, tự động lưu checkpoint, tự động khôi phục, và gửi thông báo Discord khi lỗi hoặc bị dừng.

Tính năng chính
	•	Chạy song song: 4 tiến trình (A1, A2, B1, B2) xử lý 200.000 sản phẩm chia đều.
	•	Tự động lưu checkpoint mỗi 1.000 sản phẩm.
	•	Tự động khôi phục sau khi dừng đột ngột.
	•	Ghi log lỗi vào errors_tiki_total.log.
	•	Thông báo Discord khi bị crash hoặc dừng bằng tay.
	•	Hợp nhất dữ liệu thành file cuối cùng products_all_dedup.json.


DE_Project2_Tiki_Product_Fetch/
│
├── tiki_fetch.py              # File chính (script gốc)
├── tiki_A1.py ... B2.py       # 4 file chạy song song
├── tiki_IDs_prep.ipynb        # Làm sạch và chia ID thành 4 phần
│
├── ids_A1.txt ... ids_B2.txt  # 4 file ID chia sẵn
├── product_ids.txt            # Danh sách đầy đủ 200.000 ID
├── errors_tiki_total.log      # 1058 lỗi (chủ yếu 404)
│
└── README.md



Kết quả thu thập
	•	198.942 sản phẩm hợp lệ
	•	1.058 sản phẩm lỗi (hầu hết 404)
	•	Mỗi file JSON chứa khoảng 1.000 sản phẩm (trong 4 thư mục output_json_A1...B2)

Tải dữ liệu đầy đủ

Do giới hạn 25MB của GitHub, toàn bộ kết quả được lưu trên Google Drive:

Google Drive:
[Nhấn vào đây để truy cập toàn bộ dữ liệu
](https://drive.google.com/drive/folders/1dkvPjuk56mEelXZhGILrZ1y0D5B4Xk38?usp=drive_link)

Bao gồm:
	•	output_json_A1.zip, output_json_A2.zip, output_json_B1.zip, output_json_B2.zip
	•	products_all_dedup.json (dữ liệu cuối cùng – 198.942 sản phẩm)
	•	errors_tiki_total.log (danh sách ID lỗi và lý do)

Bước 1 — Chuẩn bị ID
Chạy jupyter notebook tiki_IDs_prep.ipynb

Bước 2 — Thu thập dữ liệu
Sử dụng caffeinate để giữ máy không ngủ trong quá trình chạy:
caffeinate python3 tiki_A1.py 
caffeinate python3 tiki_A2.py 
caffeinate python3 tiki_B1.py 
caffeinate python3 tiki_B2.py 

Bước 3 — Hợp nhất & loại trùng

Sau khi cả 4 tiến trình hoàn tất, chạy:
	•	Đọc toàn bộ file JSON từ 4 thư mục output_json_*
	•	Gộp tất cả sản phẩm lại
	•	Loại bỏ ID trùng
	•	Xuất ra products_all_dedup.json

	
Final Summary (Results Overview)

Tổng quan dữ liệu:
	•	Tổng số ID đầu vào: 200,000
	•	Lấy dữ liệu thành công: 198,942  (≈ 99.47%)
	•	Lỗi (404, timeout, v.v.): 1,058  (≈ 0.53%)
	•	Dữ liệu hợp lệ sau loại trùng: 198,942
```



  
