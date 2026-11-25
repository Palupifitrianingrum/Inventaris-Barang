# Track A - EC2 + RDS MySQL

Nama resource: `inv-sg-web`, `inv-sg-db`, `inv-ec2-a`, `inv-rds-mysql`, database `inventory`. Region us-east-1.

## 1. Security group
1. EC2 > Security Groups > buat `inv-sg-web`: inbound SSH (22) dan Custom TCP 5000, source **My IP**.
2. Buat `inv-sg-db`: inbound MySQL/Aurora (3306), source **inv-sg-web** (pilih SG, bukan IP).

## 2. RDS
1. RDS > Create database > Standard create > MySQL, template **Free tier/Dev**, `db.t3.micro`.
2. Identifier `inv-rds-mysql`, master user `admin`, password catat sendiri.
3. Public access **No**, security group `inv-sg-db`. Initial database name: `inventory`.

## 3. EC2
1. Launch `inv-ec2-a`: Amazon Linux 2023, `t3.micro`, key pair `vockey` (Learner Lab), SG `inv-sg-web`.
2. SSH ke instance, lalu:
```bash
sudo dnf install -y git python3-pip mariadb105
git clone https://github.com/davingabalyarochmadi/aws.git
cd aws/track-a-vm
pip3 install -r requirements.txt
cp .env.example .env && nano .env      # isi endpoint RDS + password
set -a; source .env; set +a
```

## 4. Tes koneksi (screenshot sebagai bukti)
```bash
mysql -h $DB_HOST -u $DB_USER -p < schema.sql
mysql -h $DB_HOST -u $DB_USER -p -e "SHOW DATABASES;"
python3 test_connection.py
```

## 5. Jalankan API
```bash
python3 app.py            # atau: gunicorn -b 0.0.0.0:5000 app:app
curl http://<EC2_PUBLIC_IP>:5000/health
curl -X POST http://<EC2_PUBLIC_IP>:5000/items -H "Content-Type: application/json" \
     -d '{"name":"Laptop","quantity":3,"location":"Rak A"}'
curl http://<EC2_PUBLIC_IP>:5000/items
```

## 6. Selesai
**Stop/hapus RDS dan EC2.** Catat sisa budget Learner Lab.
