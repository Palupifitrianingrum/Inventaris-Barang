# Track C (versi S3) - API Gateway + Lambda + S3

Pengganti DynamoDB karena `dynamodb:CreateTable` ditolak. Satu item = satu file JSON di bucket S3 (`items/<id>.json`).

## 1. Bucket S3
S3 > Create bucket: nama unik global, misalnya `inv-items-<nim>-<angka>`, region sama dengan Lambda. Biarkan **Block all public access** aktif.

## 2. Lambda
1. Create function: `inventory-api`, runtime **Python 3.12**.
2. Execution role: role yang tersedia di sandbox (di Learner Lab: LabRole). Role harus punya izin `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket` pada bucket tadi.
3. Tempel isi `lambda_function_s3.py`, klik **Deploy**.
4. Configuration > Environment variables: `BUCKET_NAME` = nama bucketmu.

## 3. Tes fungsi
Pakai event di folder `events/` (sama seperti versi DynamoDB). Setelah `create-item`, cek bucket: harus ada objek `items/<id>.json`. Screenshot hasil tes dan isi bucket.

## 4. API Gateway
Sama seperti `DEPLOY.md` Track C langkah 4 dan 5: HTTP API `inventory-http-api`, lima route ke integrasi Lambda, stage `$default`, lalu tes dengan curl.
