@echo off
cd /d %~dp0
title 博客后端服务
echo 正在启动博客后端服务...
echo.
venv\Scripts\python.exe app.py
