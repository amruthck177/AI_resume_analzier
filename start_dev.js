const { spawn } = require('child_process');
const path = require('path');

const rootDir = __dirname;
const pythonPath = path.join(rootDir, 'backend', '.venv', 'Scripts', 'python.exe');

console.log('[DevRunner] Starting FastAPI Backend on http://127.0.0.1:8000 ...');
const backend = spawn(pythonPath, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], {
  cwd: path.join(rootDir, 'backend'),
  stdio: 'inherit',
  shell: true,
});

console.log('[DevRunner] Starting Vite Frontend on http://localhost:5173 ...');
const npmCmd = process.platform === 'win32' ? 'npm.cmd' : 'npm';
const frontend = spawn(npmCmd, ['run', 'dev'], {
  cwd: path.join(rootDir, 'frontend'),
  stdio: 'inherit',
  shell: true,
});

function cleanup() {
  console.log('\n[DevRunner] Shutting down dev servers...');
  backend.kill();
  frontend.kill();
  process.exit();
}

process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);
