@echo off
cd /d %~dp0
title 博客前端服务
echo 正在启动博客前端服务...
echo.
cd ..\src
call npm run dev
