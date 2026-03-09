/**
 * PM2 Configuration for Personal AI Employee - Bronze Tier
 *
 * This configuration sets up the file system watcher to monitor for new files
 * and route them through the AI employee workflow.
 */
module.exports = {
  apps: [{
    name: 'personal-ai-employee',
    script: './automated_orchestrator.py',
    interpreter: 'python',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'development',
      DRY_RUN: 'true',
      PYTHONPATH: '.'
    },
    log_file: './AI_Employee_Vault/Logs/pm2-ai-employee.log',
    out_file: './AI_Employee_Vault/Logs/pm2-ai-employee-out.log',
    error_file: './AI_Employee_Vault/Logs/pm2-ai-employee-error.log'
  }]
};