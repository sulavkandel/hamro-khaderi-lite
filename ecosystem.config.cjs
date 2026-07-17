module.exports = {
  apps: [
    {
      name: 'khaderi-api',
      cwd: '/home/user/webapp/backend',
      script: 'gunicorn',
      args: 'config.wsgi:application --bind 0.0.0.0:8000 --workers 2',
      interpreter: 'none',
      watch: false
    },
    {
      name: 'khaderi-web',
      cwd: '/home/user/webapp/frontend',
      script: 'npm',
      args: 'start',
      interpreter: 'none',
      env: { PORT: '3000' },
      watch: false
    }
  ]
}
