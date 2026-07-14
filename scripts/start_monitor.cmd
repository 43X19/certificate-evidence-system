@echo off
cd /d "%~dp0.."
"D:\Anaconda3\envs\datacompenv\python.exe" "scripts\monitor_remote.py" --interval-minutes 30
