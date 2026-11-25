# Track B - EC2 + Docker + ECR

Dua service: `api` (Flask) dan `db` (MySQL 8.0). Image disimpan di ECR repo `inventory-api`.

## 1. EC2
Launch `inv-ec2-b`: Amazon Linux 2023, `t3.micro`, key pair `vockey`, SG `inv-sg-ec2-b` (22 dan 5000 dari **My IP**, 3306 tidak dibuka). Di Advanced details pilih IAM instance profile **LabInstanceProfile**.

## 2. Install Docker
```bash
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user && newgrp docker
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
     -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
docker --version && docker compose version
```

## 3. Build image (screenshot sebagai bukti)
```bash
git clone https://github.com/davingabalyarochmadi/aws.git
cd aws/track-b-containers
docker build -t inventory-api:latest ./api
docker images
```

## 4. ECR
```bash
REGION=us-east-1
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
aws ecr create-repository --repository-name inventory-api --region $REGION
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $ACCOUNT.dkr.ecr.$REGION.amazonaws.com
docker tag inventory-api:latest $ACCOUNT.dkr.ecr.$REGION.amazonaws.com/inventory-api:latest
docker push $ACCOUNT.dkr.ecr.$REGION.amazonaws.com/inventory-api:latest
```
Screenshot repo `inventory-api` di konsol ECR.

## 5. Jalankan dua service
```bash
cp .env.example .env && nano .env
docker compose up -d --build
docker compose ps
curl http://localhost:5000/health
```

## 6. Selesai
`docker compose down`, lalu **stop EC2**. Catat sisa budget.
