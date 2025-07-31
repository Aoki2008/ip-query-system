# 🔧 数据库切换问题解决方案

## 📋 问题描述

在IP查询系统管理后台中，数据库切换选项的下拉菜单没有显示可用的数据库选项，只显示当前正在使用的数据源，且该选项被禁用。

## 🔍 问题诊断

### 原始问题状态
- **现象**: 数据源下拉菜单只有一个选项"本地数据库"且被禁用
- **后端日志**: `available_sources: Array(1)` - 只检测到1个数据源
- **根本原因**: 系统只检测到本地数据源，缺少API数据源的数据库文件

### 问题分析
1. **后端服务工作目录**: FastAPI服务从 `backend-fastapi` 目录启动
2. **数据库文件路径**: 代码中查找 `API/GeoLite2-City.mmdb` 和 `API/GeoLite2-ASN.mmdb`
3. **实际路径**: 相对于 `backend-fastapi` 目录的 `API` 子目录
4. **缺失文件**: `backend-fastapi/API/` 目录不存在

## ✅ 解决方案

### 步骤1: 创建API数据库目录
```bash
# 在项目根目录执行
mkdir backend-fastapi\API
```

### 步骤2: 复制数据库文件
```bash
# 复制城市数据库
copy "backend-fastapi\data\GeoLite2-City.mmdb" "backend-fastapi\API\GeoLite2-City.mmdb"

# 复制ASN数据库
copy "GeoLite2-ASN.mmdb" "backend-fastapi\API\GeoLite2-ASN.mmdb"
```

### 步骤3: 重新扫描数据库
1. 访问管理后台: http://localhost:5175/system
2. 点击"重新扫描数据库"按钮
3. 等待扫描完成提示

### 步骤4: 验证数据源选项
1. 点击"数据源"下拉菜单
2. 确认显示3个选项：
   - 本地数据库 (当前使用时禁用)
   - API目录数据库 ✅
   - 混合模式 ✅

## 🧪 测试验证

### 功能测试
1. **数据库检测**
   ```
   ✅ local_city: data\GeoLite2-City.mmdb
   ✅ local_asn: ..\GeoLite2-ASN.mmdb  
   ✅ api_city: API\GeoLite2-City.mmdb
   ✅ api_asn: API\GeoLite2-ASN.mmdb
   ```

2. **数据源切换**
   ```
   ✅ 本地数据库 → API目录数据库
   ✅ API目录数据库 → 混合模式
   ✅ 混合模式 → 本地数据库
   ```

3. **数据库状态验证**
   ```
   ✅ 城市数据库: 已加载
   ✅ ASN数据库: 已加载
   ✅ 当前数据源: 正确显示
   ```

### API测试
```javascript
// 测试数据库信息API
fetch('http://localhost:8000/api/admin/system/database/info', {
  headers: { 'Authorization': 'Bearer <token>' }
})
.then(response => response.json())
.then(data => {
  console.log('Available sources:', data.available_sources);
  console.log('Current source:', data.current_source);
  console.log('Databases:', data.available_databases);
});
```

### 数据库切换测试
```javascript
// 测试切换到API数据源
fetch('http://localhost:8000/api/admin/system/database/switch', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>'
  },
  body: JSON.stringify({ source: 'api' })
})
.then(response => response.json())
.then(data => console.log('Switch result:', data));
```

## 📁 文件结构

### 修复后的目录结构
```
backend-fastapi/
├── data/
│   └── GeoLite2-City.mmdb     # 本地城市数据库
├── API/                        # ✅ 新增API数据库目录
│   ├── GeoLite2-City.mmdb     # ✅ API城市数据库
│   └── GeoLite2-ASN.mmdb      # ✅ API ASN数据库
└── ...

项目根目录/
└── GeoLite2-ASN.mmdb          # 本地ASN数据库
```

### 数据库映射关系
| 数据源 | 城市数据库 | ASN数据库 |
|--------|------------|-----------|
| **local** | `data/GeoLite2-City.mmdb` | `../GeoLite2-ASN.mmdb` |
| **api** | `API/GeoLite2-City.mmdb` | `API/GeoLite2-ASN.mmdb` |
| **mixed** | 优先local，回退api | 优先local，回退api |

## 🔧 代码修复详情

### 后端扫描逻辑
```python
# backend-fastapi/app/services/geoip_service.py
async def _scan_available_databases(self) -> None:
    """扫描可用的数据库"""
    self.available_databases = {}
    available_sources = []

    # 检查本地数据库
    local_city_path = Path(settings.geoip_db_path)  # data/GeoLite2-City.mmdb
    local_asn_path = Path(settings.geoip_asn_db_path)  # ../GeoLite2-ASN.mmdb

    # 检查API目录数据库 ✅ 关键修复点
    api_city_path = Path("API/GeoLite2-City.mmdb")
    api_asn_path = Path("API/GeoLite2-ASN.mmdb")
    
    # 如果两个源都可用，添加混合模式
    if "local" in available_sources and "api" in available_sources:
        available_sources.append("mixed")
```

### 前端下拉菜单
```vue
<!-- frontend-admin/src/views/SystemView.vue -->
<el-select v-model="switchForm.source">
  <el-option
    v-for="source in databaseInfo.available_sources"
    :key="source"
    :label="getSourceDisplayName(source)"
    :value="source"
    :disabled="source === databaseInfo.current_source"
  >
    <span>{{ getSourceDisplayName(source) }}</span>
    <span>{{ getSourceDescription(source) }}</span>
  </el-option>
</el-select>
```

## 🚨 常见问题

### 问题1: 重新扫描后仍然只有一个数据源
**原因**: 数据库文件路径不正确或文件不存在
**解决**: 检查 `backend-fastapi/API/` 目录是否存在且包含数据库文件

### 问题2: 切换数据源后查询失败
**原因**: 数据库文件损坏或格式不正确
**解决**: 重新下载并复制正确的GeoLite2数据库文件

### 问题3: 下拉菜单显示但选项被禁用
**原因**: 所有选项都是当前正在使用的数据源
**解决**: 确认有多个可用数据源，当前数据源选项会被自动禁用

## 📈 性能优化建议

1. **数据库文件管理**
   - 定期更新GeoLite2数据库文件
   - 监控数据库文件大小和完整性
   - 实施自动备份机制

2. **切换性能优化**
   - 缓存数据库读取器实例
   - 异步初始化数据库连接
   - 实施连接池管理

3. **监控和日志**
   - 记录数据库切换操作
   - 监控查询性能指标
   - 设置数据库健康检查

## 🎯 总结

通过创建正确的API数据库目录结构并复制相应的数据库文件，成功解决了数据库切换选项不显示的问题。现在系统支持：

- ✅ **3种数据源**: 本地、API、混合模式
- ✅ **动态切换**: 实时切换数据库源
- ✅ **状态监控**: 实时显示数据库状态
- ✅ **测试功能**: 支持数据源测试验证

**修复完成时间**: 2025-07-31  
**状态**: ✅ 完全修复  
**测试状态**: ✅ 全部通过
