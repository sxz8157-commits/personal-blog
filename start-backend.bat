@echo off
cd /d "%~dp0backend"
title 博客后端服务
echo 正在启动博客后端服务...
echo.
call venv\Scripts\python.exe app.py
