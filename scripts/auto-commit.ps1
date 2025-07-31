# 🔄 自动Git提交脚本 (PowerShell版本)
# 用法: .\scripts\auto-commit.ps1 [提交信息] [-Push]

param(
    [string]$Message = "",
    [switch]$Push = $false,
    [switch]$Help = $false
)

# 颜色函数
function Write-ColorOutput {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

function Write-Info {
    param([string]$Text)
    Write-ColorOutput "ℹ️  [INFO] $Text" "Cyan"
}

function Write-Success {
    param([string]$Text)
    Write-ColorOutput "✅ [SUCCESS] $Text" "Green"
}

function Write-Warning {
    param([string]$Text)
    Write-ColorOutput "⚠️  [WARNING] $Text" "Yellow"
}

function Write-Error {
    param([string]$Text)
    Write-ColorOutput "❌ [ERROR] $Text" "Red"
}

# 显示帮助信息
function Show-Help {
    Write-Host ""
    Write-ColorOutput "🔄 自动Git提交脚本 (PowerShell版本)" "Cyan"
    Write-Host ""
    Write-Host "用法:"
    Write-Host "  .\scripts\auto-commit.ps1 [参数]"
    Write-Host ""
    Write-Host "参数:"
    Write-Host "  -Message <string>    自定义提交信息"
    Write-Host "  -Push               自动推送到远程仓库"
    Write-Host "  -Help               显示此帮助信息"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\scripts\auto-commit.ps1                      # 自动生成提交信息"
    Write-Host "  .\scripts\auto-commit.ps1 -Message '修复bug'    # 使用自定义提交信息"
    Write-Host "  .\scripts\auto-commit.ps1 -Message '更新' -Push # 提交并自动推送"
    Write-Host ""
}

# 检查是否在Git仓库中
function Test-GitRepository {
    try {
        git rev-parse --git-dir | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# 检查是否有未提交的更改
function Test-GitChanges {
    try {
        git diff-index --quiet HEAD --
        return $LASTEXITCODE -ne 0
    }
    catch {
        return $false
    }
}

# 生成自动提交信息
function Get-AutoCommitMessage {
    param([string]$CustomMessage)
    
    if ($CustomMessage) {
        return $CustomMessage
    }
    
    # 获取更改的文件
    $changedFiles = git diff --name-only HEAD
    $stagedFiles = git diff --cached --name-only
    $allFiles = @($changedFiles) + @($stagedFiles) | Sort-Object -Unique
    $fileCount = $allFiles.Count
    
    # 根据文件类型确定提交类型
    $commitType = "📝"
    $commitScope = "general"
    
    if ($allFiles -match "\.md$") {
        $commitType = "📝"
        $commitScope = "docs"
    }
    elseif ($allFiles -match "\.py$") {
        $commitType = "🐍"
        $commitScope = "backend"
    }
    elseif ($allFiles -match "\.(vue|ts|js)$") {
        $commitType = "🌐"
        $commitScope = "frontend"
    }
    elseif ($allFiles -match "(docker|\.ya?ml)$") {
        $commitType = "🐳"
        $commitScope = "deploy"
    }
    elseif ($allFiles -match "\.(json|package)") {
        $commitType = "📦"
        $commitScope = "deps"
    }
    
    # 生成时间戳
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    
    return "$commitType 自动提交 - $commitScope ($fileCount 个文件) - $timestamp"
}

# 执行自动提交
function Invoke-AutoCommit {
    param(
        [string]$CommitMessage,
        [bool]$AutoPush
    )
    
    Write-Info "开始自动Git提交流程..."
    
    # 检查Git仓库
    if (-not (Test-GitRepository)) {
        Write-Error "当前目录不是Git仓库"
        return $false
    }
    
    # 检查是否有更改
    if (-not (Test-GitChanges)) {
        Write-Warning "没有检测到未提交的更改"
        return $true
    }
    
    # 显示当前状态
    Write-Info "当前Git状态:"
    git status --short
    
    # 添加所有更改
    Write-Info "添加所有更改到暂存区..."
    git add .
    
    # 生成提交信息
    $finalMessage = Get-AutoCommitMessage -CustomMessage $CommitMessage
    Write-Info "提交信息: $finalMessage"
    
    # 执行提交
    Write-Info "执行提交..."
    try {
        git commit -m $finalMessage
        Write-Success "提交完成!"
    }
    catch {
        Write-Error "提交失败: $_"
        return $false
    }
    
    # 推送到远程
    if ($AutoPush) {
        Write-Info "自动推送到远程仓库..."
        try {
            git push origin main
            Write-Success "推送完成!"
        }
        catch {
            Write-Error "推送失败: $_"
            return $false
        }
    }
    else {
        $pushChoice = Read-Host "是否推送到远程仓库? (y/N)"
        if ($pushChoice -eq "y" -or $pushChoice -eq "Y") {
            Write-Info "推送到远程仓库..."
            try {
                git push origin main
                Write-Success "推送完成!"
            }
            catch {
                Write-Error "推送失败: $_"
                return $false
            }
        }
        else {
            Write-Info "跳过推送，可以稍后手动执行: git push origin main"
        }
    }
    
    return $true
}

# 主函数
function Main {
    Write-Host ""
    Write-ColorOutput "🔄 自动Git提交脚本" "Cyan"
    Write-Host "===================="
    
    if ($Help) {
        Show-Help
        return
    }
    
    $result = Invoke-AutoCommit -CommitMessage $Message -AutoPush $Push
    
    if ($result) {
        Write-Host ""
        Write-Success "🎉 自动提交流程完成!"
    }
    else {
        Write-Host ""
        Write-Error "❌ 自动提交流程失败!"
        exit 1
    }
}

# 运行主函数
Main
