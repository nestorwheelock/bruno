# Bruno Health Tracker - Project Configuration

## Production Environment

- **Domain**: https://helpbruno.com
- **Server IP**: 108.61.224.251
- **Port**: 1080 (mapped to container 8000)
- **Deploy Path**: /home/nwheelo/bruno

## URL Structure

| Path | Description |
|------|-------------|
| `/` | Fundraiser landing page |
| `/tracker/` | Health tracker app (login required) |
| `/tracker/login/` | Login page |
| `/tracker/dashboard/` | Main dashboard |
| `/tracker/timeline/` | Case journal |
| `/tracker/providers/` | Provider management |
| `/admin/` | Django admin |

## Deployment

### Deploy Command
```bash
sshpass -p 't*A6n=aPpoSoQnmp' ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new root@108.61.224.251 "cd /home/nwheelo/bruno && git pull origin master && docker compose down && docker compose up -d --build"
```

### Post-Deploy Verification
```bash
# Check site is responding
curl -sL -o /dev/null -w "%{http_code}" https://helpbruno.com/
curl -sL -o /dev/null -w "%{http_code}" https://helpbruno.com/tracker/login/

# Check container logs
docker logs bruno-web-1 --tail 30
```

## Development

### Run Tests
```bash
python manage.py test health
```

### Check Coverage
```bash
coverage run --source=health manage.py test health
coverage report
```

### Local Development
```bash
python manage.py runserver
```

## Docker Containers

| Container | Purpose |
|-----------|---------|
| bruno-web-1 | Django/Gunicorn app |
| bruno-db-1 | PostgreSQL database |
