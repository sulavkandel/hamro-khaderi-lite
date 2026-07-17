/**
 * PM2 process file — runs both services on a single VM.
 *   pm2 start deploy/ecosystem.config.js
 */
module.exports = {
  apps: [
    {
      name: "khaderi-api",
      cwd: "./backend",
      script: "gunicorn",
      args: "config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60",
      interpreter: "none",
      env: {
        DJANGO_DEBUG: "0",
        SCHEDULER_AUTOSTART: "1",
      },
      watch: false,
    },
    {
      name: "khaderi-web",
      cwd: "./frontend",
      script: "npm",
      args: "start",
      interpreter: "none",
      env: {
        NODE_ENV: "production",
        PORT: "3000",
      },
      watch: false,
    },
  ],
};
