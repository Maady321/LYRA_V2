const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const backendPath = 'c:\\sabari\\Lyra\\frontend\\dist\\packaged\\Lyra AI-win32-x64\\resources\\backend';
const pythonExe = path.join(backendPath, 'venv', 'Scripts', 'python.exe');

console.log('pythonExe exists:', fs.existsSync(pythonExe));
console.log('backendPath exists:', fs.existsSync(backendPath));

try {
  const backendProcess = spawn(pythonExe, ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'], {
    cwd: backendPath,
    shell: false
  });

  console.log('Spawned process with PID:', backendProcess.pid);

  backendProcess.stdout.on('data', (data) => {
    console.log('STDOUT:', data.toString().trim());
  });

  backendProcess.stderr.on('data', (data) => {
    console.log('STDERR:', data.toString().trim());
  });

  backendProcess.on('error', (err) => {
    console.error('ERROR event:', err);
  });

  backendProcess.on('close', (code) => {
    console.log('CLOSE event: exited with code', code);
  });
} catch (err) {
  console.error('CATCH block error:', err);
}
