# Railway Deployment Guide for Factum Humanum

This guide covers deploying the Factum Humanum application to Railway.

## What is Railway?

Railway is a modern deployment platform that automatically detects your Django app and deploys it with minimal configuration. It's perfect for small to medium projects and has a generous free tier.

## Prerequisites

- A GitHub account
- A Railway account (free tier available at https://railway.app)
- This repository pushed to GitHub

## Step-by-Step Deployment

### 1. Connect Your GitHub Repository to Railway

1. Go to https://railway.app and sign in with GitHub
2. Create a new project → "Deploy from GitHub repo"
3. Select your repository (jamesth1978/grumble)
4. Authorize Railway to access your GitHub account

### 2. Railway Will Auto-Detect Your App

Railway automatically detects:
- ✅ `Procfile` - knows how to run your app
- ✅ `requirements.txt` - installs Python dependencies
- ✅ Django application

### 3. Create a PostgreSQL Database

1. In Railway dashboard, click "+ Add Service"
2. Select "PostgreSQL"
3. Railway will automatically create `DATABASE_URL` environment variable
4. This replaces the SQLite database

### 4. Configure Environment Variables

In Railway dashboard, go to your project → Variables:

**Essential Variables:**
```
SECRET_KEY=<generate-a-strong-random-key>
DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app,yourdomain.com,www.yourdomain.com
SITE_URL=https://your-domain.railway.app
```

**Optional Email Variables** (for certificate emails):
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

**To generate SECRET_KEY in terminal:**
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 5. Deploy

Click the "Deploy" button. Railway will:
1. ✅ Install dependencies from requirements.txt
2. ✅ Run migrations (`python manage.py migrate`)
3. ✅ Collect static files (`python manage.py collectstatic --noinput`)
4. ✅ Start your application with Gunicorn

Monitor the deployment in the Deployments tab. Look for a green "Success" status.

### 6. View Your App

Once deployed, Railway provides a URL like: `https://factum-humanum-production-abc123.railway.app`

You can:
- View it live at this URL
- Add a custom domain in settings

## Custom Domain Setup

1. In Railway dashboard → Project Settings
2. Add your domain (e.g., factuhumanum.com)
3. Point your domain registrar DNS to Railway's nameservers
4. DNS settings are shown in Railway dashboard

## Database Migrations

Migrations run automatically on first deploy. For future migrations:

1. Commit and push your changes to GitHub
2. Railway auto-detects and redeploys
3. Migrations run automatically before the app starts

**Manual migrations** (if needed):
- Use Railway's integrated terminal in the dashboard
- Run: `python manage.py migrate`
- Run: `python manage.py createsuperuser` (for admin access)

## Admin Panel

After first deploy:

1. SSH into Railway or use the terminal feature
2. Run: `python manage.py createsuperuser`
3. Access admin at: `https://yourdomain.com/admin`

## Static Files

- WhiteNoise is configured in `settings.py`
- Static files are collected automatically on deploy
- CSS, images, and JS served efficiently by WhiteNoise

## Environment Variables Reference

| Variable | Required | Notes |
|----------|----------|-------|
| `SECRET_KEY` | Yes | Generate a strong random key |
| `DEBUG` | Yes | Set to `False` in production |
| `ALLOWED_HOSTS` | Yes | Your domain and Railway URL |
| `DATABASE_URL` | Auto | Created by PostgreSQL addon |
| `SITE_URL` | Yes | Your full domain URL with https:// |
| `EMAIL_HOST` | No | Only if sending emails |
| `STRIPE_*` | No | Only if using Stripe payments |

## Troubleshooting

### 502 Bad Gateway Error
- Check Railway logs in Dashboard
- Ensure all required environment variables are set
- Verify `SECRET_KEY` is set

### Static files not loading
- Static files are cached. Hard refresh browser (Ctrl+Shift+R)
- Check Railway logs for collection errors
- Ensure `STATIC_ROOT` is configured

### Database connection errors
- Confirm PostgreSQL service is deployed
- Check `DATABASE_URL` environment variable exists
- Run migrations: Railway should do this automatically

### Email not sending
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- Gmail requires "App Passwords" not regular password
- Check spam folder

## Logs & Monitoring

In Railway Dashboard:
- **Logs Tab** - View real-time application logs
- **Metrics Tab** - CPU, memory, and bandwidth usage
- **Deployments Tab** - History of deployments

## Backup Database

Railway includes automatic backups. To export data:

1. Download backup from Railway dashboard
2. Or access PostgreSQL directly via provided credentials
3. Use `pg_dump` command with provided connection string

## Scaling

Railway supports automatic scaling. For future growth:
- Free tier: Limited to shared resources
- Paid tier: More CPU/memory, custom domains included

## Next Steps

1. Set up monitoring notifications
2. Configure error tracking (Sentry optional)
3. Set up custom domain
4. Test registration and certificate generation
5. Monitor logs for first few days

---

**For more Railway documentation:** https://docs.railway.app
**Railway Community:** https://community.railway.app
