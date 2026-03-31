# Railway Deployment

This repo includes a Dockerfile, so Railway will build and run the container using the Dockerfile defaults. The Dockerfile is already set up to bind Gunicorn to the runtime PORT and run migrations + collectstatic at container start.

## Steps

1. Create a new Railway project and connect this repository.
2. (Optional) Add a PostgreSQL database service and copy its `DATABASE_URL` into the web service variables.
3. Set service variables (Railway exposes these as environment variables at build and runtime):
   - DJANGO_SECRET_KEY
   - DJANGO_DEBUG=false
   - DJANGO_ALLOWED_HOSTS=<your-railway-domain>
   - DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-railway-domain>
   - DATABASE_URL=postgres://...
   - Optional: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME, AWS_S3_CUSTOM_DOMAIN
   - Optional: EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL
   - Optional: GEN_API_KEY
4. Deploy.

## Notes

- If you attach a custom domain, update `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` to include it.
- If you prefer a non-Docker Railpack build, remove/rename the Dockerfile and define a start command that binds Gunicorn to `0.0.0.0:$PORT`.
