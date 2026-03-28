# EC2 Deployment (Ubuntu 22.04)

1. Launch an EC2 instance (Ubuntu 22.04), and open inbound ports 22, 80, and 443.
2. SSH in and install system packages.

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip nginx
```

3. Clone the repo and create a virtualenv.

```bash
git clone <your-repo-url> /home/ubuntu/siyasi_news
cd /home/ubuntu/siyasi_news/SIYASI_NEWS
python3 -m venv /home/ubuntu/siyasi_news/venv
source /home/ubuntu/siyasi_news/venv/bin/activate
pip install -r requirements.txt
```

4. Create the environment file.

```bash
sudo cp /home/ubuntu/siyasi_news/SIYASI_NEWS/deploy/ec2/siyasi_news.env.example /etc/siyasi_news.env
sudo nano /etc/siyasi_news.env
```

5. Run migrations and collect static files.

```bash
source /home/ubuntu/siyasi_news/venv/bin/activate
python manage.py migrate
python manage.py collectstatic
```

6. Install systemd service and socket.

```bash
sudo cp /home/ubuntu/siyasi_news/SIYASI_NEWS/deploy/ec2/gunicorn.service /etc/systemd/system/
sudo cp /home/ubuntu/siyasi_news/SIYASI_NEWS/deploy/ec2/gunicorn.socket /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn.socket
sudo systemctl enable --now gunicorn.service
```

7. Configure Nginx.

```bash
sudo cp /home/ubuntu/siyasi_news/SIYASI_NEWS/deploy/ec2/nginx.conf /etc/nginx/sites-available/siyasi_news
sudo ln -s /etc/nginx/sites-available/siyasi_news /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

8. (Optional) Add HTTPS with Certbot.

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

Notes:
- If you are using S3 for static/media, leave the /static and /media Nginx locations commented.
- Ensure your RDS security group allows inbound from the EC2 instance security group on port 5432.
- If using a domain, add it to `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS`.

---

# Docker (EC2)

If you prefer running the app as a container on EC2:

1. Install Docker + Compose:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
newgrp docker
```

2. Add your environment file:

```bash
sudo cp /home/ubuntu/siyasi_news/SIYASI_NEWS/deploy/ec2/siyasi_news.env.example /etc/siyasi_news.env
sudo nano /etc/siyasi_news.env
```

3. Build and run:

```bash
cd /home/ubuntu/siyasi_news/SIYASI_NEWS
sudo docker compose --env-file /etc/siyasi_news.env up -d --build
```

4. (Optional) Put Nginx in front for HTTPS and domain routing.

Notes:
- RDS must allow inbound from the EC2 security group on port 5432.
- If using S3, ensure the IAM user/role has access to the bucket.
