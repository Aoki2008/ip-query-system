// IP查询工具的交互逻辑

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
    initSubNav();
    bindQueryEvents();
    updateIpCount();
});

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

    // 并发查询（限制并发数为5）
    const concurrency = 5;
    const results = [];

    for (let i = 0; i < validIps.length; i += concurrency) {
        const batch = validIps.slice(i, i + concurrency);
        const promises = batch.map(async (ip) => {
            try {
                const response = await fetch(`/query-ip?ip=${ip}`);
                const data = await response.json();
                completed++;
                updateProgress();
                return { ip, data, success: !data.error };
            } catch (error) {
                completed++;
                updateProgress();
                return { ip, error: error.message, success: false };
            }
        });

        const batchResults = await Promise.all(promises);
        results.push(...batchResults);

        // 实时显示结果
        batchResults.forEach(result => {
            displayBatchResult(result);
        });

        // 添加小延迟避免过于频繁的请求
        if (i + concurrency < validIps.length) {
            await new Promise(resolve => setTimeout(resolve, 200));
        }
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
        // 使用ipinfo.io的API查询IP信息（更可靠）
        const response = await fetch(`/query-ip?ip=${ip}`);

        // 检查HTTP响应状态
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            showError(errorData.error || `请求失败: ${response.status} ${response.statusText}`);
            return;
        }

        const data = await response.json();

        // 检查查询是否成功
        if (data.error) {
            showError('无法查询该IP信息，请尝试其他IP');
            return;
        }

        // 显示结果
        displayResults(data);
    } catch (err) {
        showError(`网络错误: ${err.message}`);
        console.error('查询错误:', err);
    }
}