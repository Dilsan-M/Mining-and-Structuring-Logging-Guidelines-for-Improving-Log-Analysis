# Fly.io Deployment Guide

This guide covers deploying the Lista da regulação Laravel application to Fly.io with global edge deployment capabilities.

Made with ❤️ by [Gustavo M.](https://github.com/guztaver)

## What is Fly.io?

Fly.io is a platform for running applications globally with:
- **Global edge deployment** - Deploy close to users worldwide
- **Automatic scaling** - Scale up/down based on demand
- **Built-in load balancing** - Distribute traffic across regions
- **Persistent volumes** - Store files and data
- **Database hosting** - MySQL, PostgreSQL, Redis
- **Zero-downtime deployments** - Rolling updates

## Prerequisites

- Fly.io account (sign up at [fly.io](https://fly.io))
- Docker installed locally
- flyctl CLI tool
- Git repository with your application

## Installation

### Install flyctl

**macOS:**
```bash
brew install flyctl
```

**Linux/WSL:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows:**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

### Login to Fly.io

```bash
flyctl auth login
```

## Quick Deploy

### Automated Deployment

Use the included deployment script:

```bash
# Make the script executable
chmod +x fly-deploy.sh

# Run complete deployment
./fly-deploy.sh

# Or run specific steps
./fly-deploy.sh init    # Initialize only
./fly-deploy.sh deploy  # Deploy only
./fly-deploy.sh status  # Check status
./fly-deploy.sh logs    # View logs
```

### Manual Deployment

1. **Initialize the app:**
   ```bash
   flyctl apps create regulacao-list
   ```

2. **Create storage volume:**
   ```bash
   flyctl volumes create storage_volume --size 1
   ```

3. **Set up database:**
   ```bash
   flyctl mysql create --name regulacao-list-db
   flyctl mysql attach regulacao-list-db
   ```

4. **Configure environment:**
   ```bash
   flyctl secrets set APP_KEY=$(php artisan key:generate --show)
   flyctl secrets set APP_ENV=production
   flyctl secrets set APP_DEBUG=false
   ```

5. **Deploy:**
   ```bash
   flyctl deploy
   ```

## Database Setup

### MySQL (Recommended)

Fly.io provides managed MySQL with automatic backups:

```bash
# Create MySQL instance
flyctl mysql create --name regulacao-list-db

# Attach to your app
flyctl mysql attach regulacao-list-db

# Connect to database console
flyctl mysql connect regulacao-list-db
```

Environment variables are automatically set:
- `DATABASE_HOST`
- `DATABASE_PORT`
- `DATABASE_NAME`
- `DATABASE_USERNAME`
- `DATABASE_PASSWORD`
- `DATABASE_URL`

### PostgreSQL Alternative

```bash
# Create PostgreSQL instance
flyctl postgres create --name regulacao-list-pg

# Attach to your app
flyctl postgres attach regulacao-list-pg

# Connect to database
flyctl postgres connect regulacao-list-pg
```

## Redis Setup

Redis improves performance for caching, sessions, and queues:

```bash
# Create Redis instance
flyctl redis create --name regulacao-list-redis

# Attach to your app
flyctl redis attach regulacao-list-redis
```

Environment variables automatically set:
- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_PASSWORD`
- `REDIS_URL`

## Environment Configuration

### Required Variables

Set these via flyctl or the dashboard:

```bash
# Application basics
flyctl secrets set APP_NAME="Lista da regulação"
flyctl secrets set APP_ENV=production
flyctl secrets set APP_DEBUG=false
flyctl secrets set APP_KEY=$(openssl rand -base64 32 | base64)

# Security
flyctl secrets set SESSION_SECURE_COOKIE=true
flyctl secrets set TRUSTED_PROXIES="*"

# Database (automatically set when attaching)
flyctl secrets set DB_CONNECTION=mysql

# Cache and sessions
flyctl secrets set CACHE_DRIVER=redis
flyctl secrets set SESSION_DRIVER=redis
flyctl secrets set QUEUE_CONNECTION=redis
```

### Optional Variables

```bash
# Mail configuration
flyctl secrets set MAIL_MAILER=smtp
flyctl secrets set MAIL_HOST=your-smtp-host
flyctl secrets set MAIL_PORT=587
flyctl secrets set MAIL_USERNAME=your-username
flyctl secrets set MAIL_PASSWORD=your-password
flyctl secrets set MAIL_FROM_ADDRESS=noreply@yourdomain.com

# File storage (S3 compatible)
flyctl secrets set FILESYSTEM_DISK=s3
flyctl secrets set AWS_ACCESS_KEY_ID=your-access-key
flyctl secrets set AWS_SECRET_ACCESS_KEY=your-secret-key
flyctl secrets set AWS_DEFAULT_REGION=us-east-1
flyctl secrets set AWS_BUCKET=your-bucket-name
```

### Bulk Environment Setup

Use the provided template:

```bash
# Copy and edit the template
cp .env.fly .env.production
nano .env.production

# Set all variables at once
flyctl secrets import < .env.production
```

## Scaling and Performance

### Vertical Scaling

Configure VM resources:

```bash
# View current scaling
flyctl scale show

# Scale to different VM sizes
flyctl scale vm shared-cpu-1x --memory 512    # Small
flyctl scale vm shared-cpu-2x --memory 1024   # Medium
flyctl scale vm performance-1x --memory 2048  # Large

# Custom memory allocation
flyctl scale memory 512
```

### Horizontal Scaling

Scale across multiple instances:

```bash
# Scale to multiple instances
flyctl scale count 2

# Scale specific process groups
flyctl scale count app=2 worker=1

# Auto-scaling based on metrics
flyctl autoscale set min=1 max=3
flyctl autoscale set --metric=cpu --target=70
```

### Global Deployment

Deploy to multiple regions:

```bash
# List available regions
flyctl platform regions

# Add regions
flyctl regions add lhr    # London
flyctl regions add nrt    # Tokyo
flyctl regions add syd    # Sydney

# Remove regions
flyctl regions remove iad

# Backup regions (standby instances)
flyctl regions backup lhr
```

## Process Groups

The application supports multiple process types:

### Web Server (Default)

```bash
# Handles HTTP requests
# Runs nginx + php-fpm
flyctl scale count app=2
```

### Background Workers

```bash
# Processes queued jobs
flyctl scale count worker=1

# Multiple workers for high load
flyctl scale count worker=3
```

### Task Scheduler

```bash
# Runs Laravel scheduled tasks
flyctl scale count scheduler=1
```

### High-Performance Server

```bash
# Uses Laravel Octane with Swoole
flyctl scale count octane=2
```

## Storage and Volumes

### Persistent Storage

```bash
# Create volume for file uploads
flyctl volumes create storage_volume --size 1

# Larger volume for more storage
flyctl volumes create storage_volume --size 10

# List volumes
flyctl volumes list

# Extend volume size
flyctl volumes extend storage_volume --size 5
```

### File Storage Options

1. **Local Volume** (included)
   - Fast access
   - Persistent across deployments
   - Single region only

2. **S3 Compatible Storage** (recommended for production)
   - Global access
   - Automatic backups
   - CDN integration

3. **Fly.io Object Storage** (beta)
   - Native Fly.io solution
   - Global replication

## Monitoring and Logging

### Application Logs

```bash
# View recent logs
flyctl logs

# Follow logs in real-time
flyctl logs -f

# Filter logs by instance
flyctl logs -i instance-id

# Search logs
flyctl logs | grep ERROR
```

### Metrics and Monitoring

```bash
# View app status
flyctl status

# Check resource usage
flyctl vm status

# Monitor deployments
flyctl deploy --strategy=immediate --wait-timeout=300
```

### Health Checks

The application includes multiple health check endpoints:

- `GET /health` - Basic application health
- `GET /metrics` - Nginx metrics (internal only)
- Database connectivity checks
- Redis connectivity checks

### Custom Monitoring

Integration options:
- **New Relic** - Application performance monitoring
- **Sentry** - Error tracking and performance
- **Honeycomb** - Observability and debugging
- **Grafana** - Custom dashboards

## Database Management

### Running Migrations

Migrations run automatically on deployment, but can be run manually:

```bash
# SSH into the container
flyctl ssh console

# Run migrations
php artisan migrate --force

# Rollback migrations
php artisan migrate:rollback

# Check migration status
php artisan migrate:status
```

### Database Backups

Fly.io databases include automatic backups:

```bash
# List backups
flyctl mysql list-backups regulacao-list-db

# Create manual backup
flyctl mysql backup regulacao-list-db

# Restore from backup
flyctl mysql restore regulacao-list-db backup-id
```

### Database Console Access

```bash
# MySQL console
flyctl mysql connect regulacao-list-db

# PostgreSQL console (if using PostgreSQL)
flyctl postgres connect regulacao-list-pg
```

## SSL and Custom Domains

### Automatic SSL

Fly.io provides automatic SSL for:
- Default `.fly.dev` domains
- Custom domains

### Custom Domains

```bash
# Add custom domain
flyctl certs create yourdomain.com

# Add subdomain
flyctl certs create app.yourdomain.com

# Wildcard certificate
flyctl certs create *.yourdomain.com

# Check certificate status
flyctl certs show yourdomain.com

# List all certificates
flyctl certs list
```

### DNS Configuration

Point your domain to Fly.io:

```dns
# A record
yourdomain.com.     300    IN    A       66.241.124.200

# AAAA record (IPv6)
yourdomain.com.     300    IN    AAAA    2a09:8280:1::200

# CNAME for subdomains
app.yourdomain.com. 300    IN    CNAME   regulacao-list.fly.dev.
```

## Deployment Strategies

### Rolling Deployments (Default)

```bash
# Deploy with rolling updates
flyctl deploy

# Faster rolling deployment
flyctl deploy --strategy=rolling
```

### Blue-Green Deployments

```bash
# Deploy to new instances, then switch
flyctl deploy --strategy=bluegreen
```

### Immediate Deployment

```bash
# Deploy immediately (faster, brief downtime)
flyctl deploy --strategy=immediate
```

### Canary Deployments

```bash
# Deploy to subset of instances
flyctl deploy --strategy=canary
```

## Secrets Management

### Setting Secrets

```bash
# Individual secrets
flyctl secrets set SECRET_NAME=value

# Multiple secrets
flyctl secrets set SECRET1=value1 SECRET2=value2

# From file
flyctl secrets import < .env.production

# Interactive secret entry
flyctl secrets set API_KEY -
```

### Managing Secrets

```bash
# List secrets (names only)
flyctl secrets list

# Remove secret
flyctl secrets unset SECRET_NAME

# Update secret
flyctl secrets set SECRET_NAME=new_value
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/fly.yml`:

```yaml
name: Fly.io Deploy

on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  deploy:
    name: Deploy app
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: superfly/flyctl-actions/setup-flyctl@master
      
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

### GitLab CI

```yaml
deploy:
  image: flyio/flyctl:latest
  stage: deploy
  script:
    - flyctl deploy --remote-only
  only:
    - main
  variables:
    FLY_API_TOKEN: $CI_FLY_API_TOKEN
```

## Troubleshooting

### Common Issues

1. **Build failures:**
   ```bash
   # Check build logs
   flyctl logs --app regulacao-list
   
   # Build locally to test
   docker build --target production .
   ```

2. **Database connection issues:**
   ```bash
   # Check database status
   flyctl mysql status regulacao-list-db
   
   # Test connection
   flyctl ssh console -C "php artisan migrate:status"
   ```

3. **Memory issues:**
   ```bash
   # Check memory usage
   flyctl vm status
   
   # Scale memory up
   flyctl scale memory 1024
   ```

4. **Volume issues:**
   ```bash
   # Check volume status
   flyctl volumes list
   
   # Create new volume if needed
   flyctl volumes create storage_volume --size 2
   ```

### Debug Mode

**Never enable in production**, but for troubleshooting:

```bash
# Temporary debug enable
flyctl secrets set APP_DEBUG=true

# Check logs immediately
flyctl logs -f

# Disable debug
flyctl secrets set APP_DEBUG=false
```

### SSH Access

```bash
# SSH into running container
flyctl ssh console

# Run specific commands
flyctl ssh console -C "php artisan --version"

# Access specific instance
flyctl ssh console -s instance-id
```

## Cost Optimization

### Resource Management

1. **Right-size instances:**
   ```bash
   # Monitor usage
   flyctl vm status
   
   # Scale down if underutilized
   flyctl scale vm shared-cpu-1x --memory 256
   ```

2. **Auto-scaling:**
   ```bash
   # Set minimum instances
   flyctl autoscale set min=0 max=3
   
   # Scale to zero when idle
   flyctl autoscale balanced
   ```

3. **Regional optimization:**
   ```bash
   # Remove unused regions
   flyctl regions remove region-code
   
   # Use backup regions for failover only
   flyctl regions backup lhr
   ```

### Usage Monitoring

```bash
# Check current usage
flyctl billing

# View detailed metrics
flyctl dashboard
```

## Security Best Practices

### Application Security

1. **Environment variables:**
   - Use `flyctl secrets` for sensitive data
   - Never commit secrets to Git
   - Rotate keys regularly

2. **Network security:**
   - Use internal networking for service communication
   - Configure proper firewall rules
   - Enable HTTPS everywhere

3. **Container security:**
   - Keep base images updated
   - Use non-root users when possible
   - Scan for vulnerabilities

### Database Security

```bash
# Use strong passwords
flyctl secrets set DB_PASSWORD=$(openssl rand -base64 32)

# Enable SSL connections
flyctl secrets set DB_SSLMODE=require

# Restrict database access
flyctl mysql users create readonly_user --read-only
```

## Backup and Disaster Recovery

### Application Backup

1. **Configuration backup:**
   ```bash
   # Export app configuration
   flyctl config save > backup-config.toml
   
   # Export secrets list
   flyctl secrets list > backup-secrets.txt
   ```

2. **Volume backup:**
   ```bash
   # Create volume snapshot
   flyctl volumes snapshot storage_volume
   
   # List snapshots
   flyctl volumes snapshots list
   ```

### Disaster Recovery

```bash
# Clone app to new region
flyctl apps create regulacao-list-backup --copy-config regulacao-list

# Restore from volume snapshot
flyctl volumes create storage_volume --snapshot snapshot-id

# Point DNS to backup
# Update DNS records to point to backup app
```

## Advanced Configuration

### Custom Dockerfile

The consolidated `Dockerfile` is optimized for both local development and Fly.io with:
- Multi-stage builds for smaller images
- Proper PHP/Nginx configuration
- Health checks and monitoring
- Production-ready optimizations for Fly.io deployment

### Process Configuration

Configure different process types in `fly.toml`:

```toml
[processes]
app = "php artisan octane:start --server=frankenphp --host=0.0.0.0 --port=8080"
worker = "php artisan queue:work --sleep=3 --tries=3 --max-time=3600"
scheduler = "php artisan schedule:work"
```

### Load Balancing

```bash
# Configure load balancing
flyctl config save
# Edit fly.toml [services] section
flyctl deploy
```

### Custom Health Checks

Configure in `fly.toml`:

```toml
[[services.http_checks]]
interval = "10s"
grace_period = "5s"
method = "get"
path = "/health"
protocol = "http"
timeout = "2s"
```

## Migration from Other Platforms

### From Heroku

```bash
# Import Heroku configuration
flyctl launch --copy-config --from-heroku your-heroku-app

# Migrate database
# Export from Heroku, import to Fly.io MySQL
```

### From Railway

```bash
# Similar configuration structure
# Manual migration of environment variables
flyctl secrets import < railway-env-export.txt
```

### From DigitalOcean/AWS

```bash
# Create new app
flyctl apps create

# Import database backup
flyctl mysql restore regulacao-list-db backup.sql

# Deploy application
flyctl deploy
```

## Support and Resources

### Fly.io Documentation

- [Fly.io Docs](https://fly.io/docs/)
- [Laravel on Fly.io Guide](https://fly.io/docs/laravel/)
- [flyctl Reference](https://fly.io/docs/flyctl/)

### Community Support

- [Fly.io Community Forum](https://community.fly.io/)
- [Discord Server](https://discord.gg/fly)
- [GitHub Discussions](https://github.com/superfly/flyctl/discussions)

### Getting Help

1. **Check status:** [status.fly.io](https://status.fly.io)
2. **Community forum:** Get help from other developers
3. **Support tickets:** Available for paid plans
4. **Documentation:** Comprehensive guides and tutorials

## Example Complete Deployment

Here's a complete deployment workflow:

```bash
# 1. Install and login
curl -L https://fly.io/install.sh | sh
flyctl auth login

# 2. Clone your repository
git clone https://github.com/your-username/regulacao-list.git
cd regulacao-list

# 3. Run automated deployment
./fly-deploy.sh

# 4. Configure custom domain (optional)
flyctl certs create yourdomain.com

# 5. Set up monitoring
flyctl dashboard

# 6. Test deployment
curl https://regulacao-list.fly.dev/health
```

Your Laravel application will be running globally on Fly.io with automatic scaling, load balancing, and monitoring!

## Performance Optimization

### Application Performance

1. **Enable OPcache:** Already configured in the production Dockerfile
2. **Use Redis:** For caching, sessions, and queues
3. **Optimize queries:** Use Laravel's query optimization tools
4. **Asset optimization:** Use CDN for static assets

### Database Performance

```bash
# Monitor database performance
flyctl mysql metrics regulacao-list-db

# Optimize queries
flyctl ssh console -C "php artisan db:monitor"

# Use read replicas for scaling
flyctl mysql read-replica create regulacao-list-db
```

### Caching Strategy

```bash
# Configure multi-layer caching
flyctl secrets set CACHE_DRIVER=redis
flyctl secrets set VIEW_CACHE_PATH=/tmp/views

# Enable query caching
flyctl secrets set DB_CACHE_TTL=3600
```

This Fly.io setup provides a robust, globally distributed deployment solution for your Laravel application with excellent performance and scalability characteristics.
