# Track C - API Gateway + Lambda + DynamoDB

Semua lewat AWS Console (us-east-1). Learner Lab tidak mengizinkan membuat IAM role baru, jadi Lambda memakai **LabRole**.

## 1. DynamoDB
DynamoDB > Create table: name `items`, partition key `id` (String), capacity **On-demand**.

## 2. Lambda
1. Lambda > Create function: name `inventory-api`, runtime **Python 3.12**.
2. Permissions > Use an existing role > **LabRole**.
3. Tempel isi `lambda_function.py` ke editor, klik **Deploy**.
4. Configuration > Environment variables: `TABLE_NAME` = `items` (opsional, default sudah `items`).

## 3. Tes fungsi (screenshot sebagai bukti)
Tab Test > buat event dari file di folder `events/`. Urutan: `create-item.json` (catat `id` di respons), `list-items.json`, lalu `update-item.json` / `delete-item.json` setelah `id`-nya diganti. Status 201/200 dan item muncul di DynamoDB > Explore items.

## 4. API Gateway
1. Create API > **HTTP API** > Build. Name `inventory-http-api`.
2. Integrations: Lambda `inventory-api`. Payload format 2.0 (default).
3. Routes: `POST /items`, `GET /items`, `PUT /items/{id}`, `DELETE /items/{id}`, `GET /health`, semuanya ke integrasi Lambda tadi.
4. Stage `$default` dengan auto-deploy. Salin **Invoke URL**.

## 5. Tes dari terminal
```bash
API=https://xxxxxxxx.execute-api.us-east-1.amazonaws.com
curl $API/health
curl -X POST $API/items -H "Content-Type: application/json" \
     -d '{"name":"Laptop","quantity":3,"location":"Rak A"}'
curl $API/items
```

## 6. Selesai
Biaya hampir nol, boleh dibiarkan. Log ada di CloudWatch > `/aws/lambda/inventory-api`.
