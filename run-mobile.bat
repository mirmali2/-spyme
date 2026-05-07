@echo off
cd /d "%~dp0mobile"
if not exist node_modules ( call npm install )
call npx expo start
