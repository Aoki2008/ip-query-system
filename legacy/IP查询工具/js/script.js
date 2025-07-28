// IP查询工具的交互逻辑

// 下拉菜单处理
function initializeDropdownMenus() {
    const dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');

        // 移动端点击处理
        if (window.innerWidth <= 768) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();

                // 关闭其他下拉菜单
                dropdowns.forEach(otherDropdown => {
                    if (otherDropdown !== dropdown) {
                        const otherMenu = otherDropdown.querySelector('.dropdown-menu');
                        if (otherMenu) {
                            otherMenu.style.display = 'none';
                        }
                    }
                });

                // 切换当前菜单
                if (menu) {
                    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
                }
            });
        }
    });

    // 点击外部关闭菜单
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!e.target.closest('.dropdown')) {
                dropdowns.forEach(dropdown => {
                    const menu = dropdown.querySelector('.dropdown-menu');
                    if (menu) {
                        menu.style.display = 'none';
                    }
                });
            }
        }
    });

    // 窗口大小改变时重置菜单状态
    window.addEventListener('resize', function() {
        dropdowns.forEach(dropdown => {
            const menu = dropdown.querySelector('.dropdown-menu');
            if (menu) {
                if (window.innerWidth > 768) {
                    menu.style.display = '';
                } else {
                    menu.style.display = 'none';
                }
            }
        });
    });
}

// API配置
const API_CONFIG = {
    baseURL: 'http://localhost:5000/api',
    endpoints: {
        queryIP: '/query-ip',
        queryBatch: '/query-batch',
        health: '/health'
    }
};

// API健康检查
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.health}`);
        if (response.ok) {
            console.log('API服务连接正常');
            return true;
        }
    } catch (error) {
        console.warn('API服务连接失败，请确保后端服务已启动:', error.message);
        showNotification('后端服务连接失败，请检查服务是否启动', 'error');
        return false;
    }
}

// 获取DOM元素
const ipInput = document.getElementById('ip-input');
const queryBtn = document.getElementById('query-btn');
const resultSection = document.getElementById('result-section');
const resultList = document.getElementById('result-list');
const loading = document.getElementById('loading');
const error = document.getElementById('error');

// 批量查询相关元素
const batchIpInput = document.getElementById('batch-ip-input');
const batchQueryBtn = document.getElementById('batch-query-btn');
const clearBatchBtn = document.getElementById('clear-batch');
const ipCountSpan = document.getElementById('ip-count');
const batchProgress = document.getElementById('batch-progress');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const batchResults = document.getElementById('batch-results');

// 导入导出相关元素
const importFileInput = document.getElementById('import-file');
const importBtn = document.getElementById('import-btn');
const fileDropZone = document.getElementById('file-drop-zone');
const resultsHeader = document.getElementById('results-header');
const resultsCount = document.getElementById('results-count');
const exportCsvBtn = document.getElementById('export-csv');
const exportJsonBtn = document.getElementById('export-json');
const exportExcelBtn = document.getElementById('export-excel');

// 存储批量查询结果数据
let batchQueryResults = [];

// 标签页和导航相关元素
const queryTabs = document.querySelectorAll('.query-tab');
const queryContents = document.querySelectorAll('.query-content');
const subNavItems = document.querySelectorAll('.sub-nav-item');

// IP地址验证函数
function isValidIp(ip) {
    // 简单的IP地址格式验证
    const ipRegex = /^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$/;
    return ipRegex.test(ip);
}

// 清空结果显示 - 添加元素存在性检查
function clearResults() {
    // 显示结果区域
    if (resultSection) resultSection.style.display = 'block';

    if (resultList) {
        resultList.style.display = 'none';
        resultList.classList.remove('grid');
    }
    if (error) error.style.display = 'none';
    if (loading) loading.style.display = 'block';
}

// 显示错误信息
function showError(message) {
    loading.style.display = 'none';
    error.style.display = 'block';
    error.textContent = message;
    resultList.style.display = 'none';
    resultList.classList.remove('grid');
}

// 显示查询结果
function displayResults(data) {
    // 清空现有列表项
    resultList.innerHTML = '';
    loading.style.display = 'none';
    resultList.style.display = 'block';
    resultList.classList.add('grid');

    // 创建结果列表项，包含图标和更好的格式化
    const resultItems = [
        { label: 'IP地址', value: data.ip, icon: '🌐' },
        { label: '国家', value: data.country, icon: '🏳️' },
        { label: '地区', value: data.region, icon: '🗺️' },
        { label: '城市', value: data.city, icon: '🏙️' },
        { label: '邮政编码', value: data.postal, icon: '📮' },
        { label: '纬度', value: data.lat ? `${data.lat}°` : null, icon: '📍' },
        { label: '经度', value: data.lon ? `${data.lon}°` : null, icon: '📍' },
        { label: '时区', value: data.timezone, icon: '🕐' },
        { label: 'ISP', value: data.isp, icon: '🏢' }
    ];

    // 添加列表项到页面
    resultItems.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `
            <strong>${item.icon} ${item.label}</strong>
            <div class="value">${item.value || '未知'}</div>
        `;
        resultList.appendChild(li);
    });

    // 显示结果区域
    resultSection.style.display = 'block';

    // 添加动画效果
    resultList.querySelectorAll('li').forEach((li, index) => {
        li.style.opacity = '0';
        li.style.transform = 'translateY(20px)';
        setTimeout(() => {
            li.style.transition = 'all 0.3s ease';
            li.style.opacity = '1';
            li.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// 标签页切换功能
function initTabs() {
    queryTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.dataset.tab;

            // 更新标签页状态
            queryTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // 更新内容显示
            queryContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabId}-query`) {
                    content.classList.add('active');
                }
            });

            // 如果切换到单个查询，隐藏结果区域
            if (tabId === 'single') {
                if (resultSection) resultSection.style.display = 'none';
            }
        });
    });
}

// 二级导航功能
function initSubNav() {
    subNavItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;

            // 更新导航状态
            subNavItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // 根据选择的section执行相应操作
            switch(section) {
                case 'single':
                    // 显示单个查询内容
                    queryContents.forEach(content => {
                        content.classList.remove('active');
                        if (content.id === 'single-query') {
                            content.classList.add('active');
                        }
                    });
                    // 如果没有查询结果，隐藏结果区域
                    if (resultSection && (!resultList || resultList.children.length === 0)) {
                        resultSection.style.display = 'none';
                    }
                    break;
                case 'batch':
                    // 显示批量查询内容
                    queryContents.forEach(content => {
                        content.classList.remove('active');
                        if (content.id === 'batch-query') {
                            content.classList.add('active');
                        }
                    });
                    break;
                case 'history':
                    // 显示查询历史内容
                    queryContents.forEach(content => {
                        content.classList.remove('active');
                        if (content.id === 'history-query') {
                            content.classList.add('active');
                        }
                    });
                    break;
                case 'tools':
                    // 显示工具箱内容
                    queryContents.forEach(content => {
                        content.classList.remove('active');
                        if (content.id === 'tools-query') {
                            content.classList.add('active');
                        }
                    });
                    break;
            }
        });
    });
}

// 批量查询IP计数更新
function updateIpCount() {
    if (!batchIpInput) return;

    const text = batchIpInput.value.trim();
    const ips = text ? text.split('\n').filter(line => line.trim()) : [];
    const validIps = ips.filter(ip => isValidIp(ip.trim()));

    if (ipCountSpan) {
        ipCountSpan.textContent = validIps.length;
    }

    if (batchQueryBtn) {
        batchQueryBtn.disabled = validIps.length === 0;
    }

    return validIps;
}

// 清空批量输入
function clearBatchInput() {
    if (batchIpInput) {
        batchIpInput.value = '';
        updateIpCount();
    }
    if (batchResults) {
        batchResults.innerHTML = '';
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--space-lg);
        box-shadow: var(--shadow-lg);
        z-index: 1000;
        max-width: 300px;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// 绑定查询事件
function bindQueryEvents() {
    // 单个查询按钮点击事件
    if (queryBtn) {
        queryBtn.addEventListener('click', () => {
            const ip = ipInput.value.trim();
            if (ip) {
                queryIpInfo(ip);
            } else {
                showError('请输入IP地址');
            }
        });
    }

    // 单个查询回车键事件
    if (ipInput) {
        ipInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                queryBtn.click();
            }
        });
    }

    // 批量查询相关事件
    if (batchIpInput) {
        batchIpInput.addEventListener('input', updateIpCount);
        batchIpInput.addEventListener('paste', () => {
            setTimeout(updateIpCount, 100); // 延迟执行以确保粘贴内容已处理
        });
    }

    if (batchQueryBtn) {
        batchQueryBtn.addEventListener('click', startBatchQuery);
    }

    if (clearBatchBtn) {
        clearBatchBtn.addEventListener('click', clearBatchInput);
    }
}

// 页面加载完成后绑定事件
document.addEventListener('DOMContentLoaded', () => {
    initializeDropdownMenus();
    initSubNav();
    bindQueryEvents();
    updateIpCount();
    // 初始化导入导出功能
    initImportFeature();
    initExportFeature();
    // 初始化快速操作按钮
    initQuickActions();
    // 检查API服务健康状态
    checkAPIHealth();
});

// 初始化快速操作按钮
function initQuickActions() {
    const sampleIpsBtn = document.getElementById('sample-ips-btn');
    const clearAllBtn = document.getElementById('clear-all-btn');
    const batchInput = document.getElementById('batch-ip-input');

    if (sampleIpsBtn && batchInput) {
        sampleIpsBtn.addEventListener('click', () => {
            const sampleIps = [
                '8.8.8.8',
                '1.1.1.1',
                '114.114.114.114',
                '208.67.222.222',
                '223.5.5.5'
            ];

            const currentValue = batchInput.value.trim();
            const newValue = currentValue ?
                currentValue + '\n' + sampleIps.join('\n') :
                sampleIps.join('\n');

            batchInput.value = newValue;
            updateIpCount();

            // 添加视觉反馈
            sampleIpsBtn.style.transform = 'scale(0.95)';
            setTimeout(() => {
                sampleIpsBtn.style.transform = '';
            }, 150);

            showNotification('已插入示例IP地址', 'success');
        });
    }

    if (clearAllBtn && batchInput) {
        clearAllBtn.addEventListener('click', () => {
            if (batchInput.value.trim()) {
                batchInput.value = '';
                updateIpCount();

                // 添加视觉反馈
                clearAllBtn.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    clearAllBtn.style.transform = '';
                }, 150);

                showNotification('已清空所有内容', 'info');
            }
        });
    }
}

// 批量查询功能
async function startBatchQuery() {
    const validIps = updateIpCount();
    if (validIps.length === 0) {
        showNotification('请输入有效的IP地址', 'error');
        return;
    }

    if (validIps.length > 100) {
        showNotification('最多支持100个IP地址同时查询', 'error');
        return;
    }

    // 显示进度条
    batchProgress.style.display = 'block';
    batchQueryBtn.disabled = true;
    batchResults.innerHTML = '';

    let completed = 0;
    const total = validIps.length;

    // 更新进度
    function updateProgress() {
        const percentage = (completed / total) * 100;
        progressFill.style.width = `${percentage}%`;
        progressText.textContent = `正在查询... ${completed}/${total}`;
    }

    updateProgress();

    try {
        // 使用批量查询API
        const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.queryBatch}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ips: validIps })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `请求失败: ${response.status}`);
        }

        const data = await response.json();
        const results = data.results || [];

        // 保存查询结果数据用于导出
        updateResultsDisplay(results);

        // 逐个显示结果（模拟进度）
        for (let i = 0; i < results.length; i++) {
            const result = results[i];
            completed++;
            updateProgress();

            // 格式化结果以匹配原有的显示逻辑
            const formattedResult = {
                ip: result.ip,
                data: result,
                success: !result.error
            };

            displayBatchResult(formattedResult);

            // 添加小延迟以显示进度效果
            if (i < results.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 50));
            }
        }
    } catch (error) {
        showNotification(`批量查询失败: ${error.message}`, 'error');
        batchQueryBtn.disabled = false;
        batchProgress.style.display = 'none';
        return;
    }

    // 查询完成
    progressText.textContent = `查询完成！ ${total}/${total}`;
    batchQueryBtn.disabled = false;

    // 3秒后隐藏进度条
    setTimeout(() => {
        batchProgress.style.display = 'none';
    }, 3000);

    showNotification(`批量查询完成，共查询 ${total} 个IP地址`, 'success');
}

// 显示批量查询结果
function displayBatchResult(result) {
    const resultDiv = document.createElement('div');
    resultDiv.className = 'batch-result-item';

    if (result.success && result.data) {
        resultDiv.innerHTML = `
            <div class="batch-result-header">
                <div class="batch-result-ip">${result.ip}</div>
                <div class="batch-result-status success">成功</div>
            </div>
            <div class="batch-result-data">
                <div class="batch-result-field">
                    <strong>🏳️ 国家</strong>
                    <span>${result.data.country || '未知'}</span>
                </div>
                <div class="batch-result-field">
                    <strong>🗺️ 地区</strong>
                    <span>${result.data.region || '未知'}</span>
                </div>
                <div class="batch-result-field">
                    <strong>🏙️ 城市</strong>
                    <span>${result.data.city || '未知'}</span>
                </div>
                <div class="batch-result-field">
                    <strong>🏢 ISP</strong>
                    <span>${result.data.isp || '未知'}</span>
                </div>
                <div class="batch-result-field">
                    <strong>📍 坐标</strong>
                    <span>${result.data.lat && result.data.lon ? `${result.data.lat}°, ${result.data.lon}°` : '未知'}</span>
                </div>
                <div class="batch-result-field">
                    <strong>🕐 时区</strong>
                    <span>${result.data.timezone || '未知'}</span>
                </div>
            </div>
        `;
    } else {
        resultDiv.innerHTML = `
            <div class="batch-result-header">
                <div class="batch-result-ip">${result.ip}</div>
                <div class="batch-result-status error">失败</div>
            </div>
            <div class="batch-result-data">
                <div class="batch-result-field">
                    <strong>❌ 错误信息</strong>
                    <span>${result.error || result.data?.error || '查询失败'}</span>
                </div>
            </div>
        `;
    }

    batchResults.appendChild(resultDiv);

    // 添加动画效果
    resultDiv.style.opacity = '0';
    resultDiv.style.transform = 'translateY(20px)';
    setTimeout(() => {
        resultDiv.style.transition = 'all 0.3s ease';
        resultDiv.style.opacity = '1';
        resultDiv.style.transform = 'translateY(0)';
    }, 100);
}

// 查询IP信息
async function queryIpInfo(ip) {
    clearResults();

    try {
        // 调用后端API查询IP信息
        const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.queryIP}?ip=${ip}`);

        // 检查HTTP响应状态
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            showError(errorData.error || `请求失败: ${response.status} ${response.statusText}`);
            return;
        }

        const data = await response.json();

        // 检查查询是否成功
        if (data.error) {
            showError(data.error || '无法查询该IP信息，请尝试其他IP');
            return;
        }

        // 显示结果
        displayResults(data);
    } catch (err) {
        showError(`网络错误: ${err.message}`);
        console.error('查询错误:', err);
    }
}

// ==================== 导入导出功能 ====================

// 文件导入功能
function initImportFeature() {
    if (!importBtn || !importFileInput || !fileDropZone) return;

    // 导入按钮点击事件
    importBtn.addEventListener('click', () => {
        importFileInput.click();
    });

    // 文件选择事件
    importFileInput.addEventListener('change', handleFileSelect);

    // 拖拽区域点击事件
    fileDropZone.addEventListener('click', () => {
        importFileInput.click();
    });

    // 拖拽功能
    fileDropZone.addEventListener('dragover', handleDragOver);
    fileDropZone.addEventListener('dragleave', handleDragLeave);
    fileDropZone.addEventListener('drop', handleFileDrop);
}

// 处理拖拽悬停
function handleDragOver(e) {
    e.preventDefault();
    fileDropZone.classList.add('dragover');
}

// 处理拖拽离开
function handleDragLeave(e) {
    e.preventDefault();
    fileDropZone.classList.remove('dragover');
}

// 处理文件拖拽放置
function handleFileDrop(e) {
    e.preventDefault();
    fileDropZone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processImportFile(files[0]);
    }
}

// 处理文件选择
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        processImportFile(file);
    }
}

// 处理导入文件
async function processImportFile(file) {
    // 添加加载状态
    if (importBtn) {
        importBtn.classList.add('loading');
        importBtn.disabled = true;
    }

    // 验证文件类型
    const allowedTypes = ['.txt', '.csv'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowedTypes.includes(fileExtension)) {
        showNotification('不支持的文件格式，请选择 .txt 或 .csv 文件', 'error');
        resetImportButton('error');
        return;
    }

    // 验证文件大小 (最大5MB)
    if (file.size > 5 * 1024 * 1024) {
        showNotification('文件大小不能超过5MB', 'error');
        resetImportButton('error');
        return;
    }

    try {
        const text = await readFileAsText(file);
        const ips = parseImportedText(text, fileExtension);

        if (ips.length === 0) {
            showNotification('文件中没有找到有效的IP地址', 'warning');
            resetImportButton('error');
            return;
        }

        if (ips.length > 100) {
            showNotification(`文件包含${ips.length}个IP地址，已截取前100个`, 'warning');
            ips.splice(100);
        }

        // 填充到文本框
        batchIpInput.value = ips.join('\n');
        updateIpCount();

        showNotification(`成功导入${ips.length}个IP地址`, 'success');
        resetImportButton('success');

    } catch (error) {
        console.error('文件处理错误:', error);
        showNotification('文件读取失败，请检查文件格式', 'error');
        resetImportButton('error');
    }
}

// 重置导入按钮状态
function resetImportButton(state = 'normal') {
    if (!importBtn) return;

    // 移除所有状态类
    importBtn.classList.remove('loading', 'success', 'error');
    importBtn.disabled = false;

    // 添加相应状态
    if (state !== 'normal') {
        importBtn.classList.add(state);

        // 2秒后恢复正常状态
        setTimeout(() => {
            importBtn.classList.remove(state);
        }, 2000);
    }
}

// 读取文件内容
function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.onerror = e => reject(e);
        reader.readAsText(file, 'UTF-8');
    });
}

// 解析导入的文本内容
function parseImportedText(text, fileExtension) {
    const ips = [];
    const lines = text.split(/\r?\n/).map(line => line.trim()).filter(line => line);

    if (fileExtension === '.csv') {
        // CSV格式：假设第一列是IP地址
        for (const line of lines) {
            const columns = line.split(',').map(col => col.trim().replace(/['"]/g, ''));
            if (columns.length > 0 && isValidIp(columns[0])) {
                ips.push(columns[0]);
            }
        }
    } else {
        // TXT格式：每行一个IP
        for (const line of lines) {
            if (isValidIp(line)) {
                ips.push(line);
            }
        }
    }

    // 去重
    return [...new Set(ips)];
}

// 导出功能初始化
function initExportFeature() {
    if (!exportCsvBtn || !exportJsonBtn || !exportExcelBtn) return;

    exportCsvBtn.addEventListener('click', () => exportResults('csv'));
    exportJsonBtn.addEventListener('click', () => exportResults('json'));
    exportExcelBtn.addEventListener('click', () => exportResults('excel'));
}

// 导出结果
function exportResults(format) {
    if (batchQueryResults.length === 0) {
        showNotification('没有可导出的查询结果', 'warning');
        return;
    }

    // 获取对应的导出按钮
    const exportBtn = document.getElementById(`export-${format}`);

    // 添加导出状态
    if (exportBtn) {
        exportBtn.classList.add('exporting');
        exportBtn.disabled = true;
    }

    try {
        // 添加小延迟以显示加载状态
        setTimeout(() => {
            try {
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
                const filename = `IP查询结果_${timestamp}`;

                switch (format) {
                    case 'csv':
                        exportToCSV(batchQueryResults, filename);
                        break;
                    case 'json':
                        exportToJSON(batchQueryResults, filename);
                        break;
                    case 'excel':
                        exportToExcel(batchQueryResults, filename);
                        break;
                }

                showNotification(`${format.toUpperCase()}文件导出成功`, 'success');
                resetExportButton(exportBtn, 'success');
            } catch (error) {
                console.error('导出错误:', error);
                showNotification('导出失败，请重试', 'error');
                resetExportButton(exportBtn, 'error');
            }
        }, 500);

    } catch (error) {
        console.error('导出错误:', error);
        showNotification('导出失败，请重试', 'error');
        resetExportButton(exportBtn, 'error');
    }
}

// 重置导出按钮状态
function resetExportButton(button, state = 'normal') {
    if (!button) return;

    // 移除加载状态
    button.classList.remove('exporting');
    button.disabled = false;

    // 添加相应状态
    if (state !== 'normal') {
        button.classList.add(state);

        // 2秒后恢复正常状态
        setTimeout(() => {
            button.classList.remove(state);
        }, 2000);
    }
}

// 导出为CSV格式
function exportToCSV(data, filename) {
    const headers = ['IP地址', '国家', '国家代码', '地区', '地区代码', '城市', '邮编', '纬度', '经度', '时区', 'ISP', '组织', '精度半径'];
    const csvContent = [
        headers.join(','),
        ...data.map(item => [
            item.ip || '',
            `"${item.country || ''}"`,
            item.country_code || '',
            `"${item.region || ''}"`,
            item.region_code || '',
            `"${item.city || ''}"`,
            item.postal || '',
            item.latitude || '',
            item.longitude || '',
            `"${item.timezone || ''}"`,
            `"${item.isp || ''}"`,
            `"${item.organization || ''}"`,
            item.accuracy_radius || ''
        ].join(','))
    ].join('\n');

    downloadFile(csvContent, `${filename}.csv`, 'text/csv;charset=utf-8;');
}

// 导出为JSON格式
function exportToJSON(data, filename) {
    const jsonContent = JSON.stringify({
        exportTime: new Date().toISOString(),
        totalCount: data.length,
        results: data
    }, null, 2);

    downloadFile(jsonContent, `${filename}.json`, 'application/json;charset=utf-8;');
}

// 导出为Excel格式 (使用CSV格式，Excel可以打开)
function exportToExcel(data, filename) {
    // 创建带有BOM的CSV内容，确保Excel正确显示中文
    const BOM = '\uFEFF';
    const headers = ['IP地址', '国家', '国家代码', '地区', '地区代码', '城市', '邮编', '纬度', '经度', '时区', 'ISP', '组织', '精度半径'];
    const csvContent = BOM + [
        headers.join(','),
        ...data.map(item => [
            item.ip || '',
            `"${item.country || ''}"`,
            item.country_code || '',
            `"${item.region || ''}"`,
            item.region_code || '',
            `"${item.city || ''}"`,
            item.postal || '',
            item.latitude || '',
            item.longitude || '',
            `"${item.timezone || ''}"`,
            `"${item.isp || ''}"`,
            `"${item.organization || ''}"`,
            item.accuracy_radius || ''
        ].join(','))
    ].join('\n');

    downloadFile(csvContent, `${filename}.xlsx`, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8;');
}

// 下载文件
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // 清理URL对象
    setTimeout(() => URL.revokeObjectURL(url), 100);
}

// 更新结果显示和导出按钮状态
function updateResultsDisplay(results) {
    batchQueryResults = results;

    if (results.length > 0 && resultsHeader) {
        resultsHeader.style.display = 'flex';
        if (resultsCount) {
            resultsCount.textContent = `${results.length} 条结果`;
        }
    } else if (resultsHeader) {
        resultsHeader.style.display = 'none';
    }
}