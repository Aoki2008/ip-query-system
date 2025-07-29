@echo off
echo 🚀 开始推送到GitHub...

echo 📊 检查Git状态...
git status

echo 📤 尝试推送到远程仓库...
git push origin main

if %ERRORLEVEL% neq 0 (
    echo ❌ 推送失败，尝试强制推送...
    echo ⚠️ 注意：强制推送会覆盖远程历史
    set /p confirm="确认强制推送? (y/N): "
    if /i "%confirm%"=="y" (
        git push -f origin main
    ) else (
        echo 取消强制推送
    )
) else (
    echo ✅ 推送成功！
)

echo 🔍 检查推送结果...
git log --oneline -3

pause
