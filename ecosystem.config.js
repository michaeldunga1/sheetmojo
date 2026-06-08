module.exports = {
  apps: [
    {
      name: 'sheetmojo',
      script: './index.js',
      instances: 1,
      autorestart: true,
      watch: false,
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        HOST: '0.0.0.0'
      }
    }
  ]
};
