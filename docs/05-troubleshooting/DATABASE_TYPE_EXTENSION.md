# 🗂️ 数据库类型扩展功能实现

## 📋 功能概述

在IP查询系统中实现数据库类型扩展功能，新增对国家数据库(country)的支持，并实现独立数据库选择模式，允许用户灵活选择和组合任意数据库类型。

## 🎯 实现目标

### 1. **扩展数据库类型支持**
- ✅ 当前系统支持城市数据库(city)和ASN数据库(asn)
- ✅ 新增对国家数据库(country)的支持
- ✅ 国家数据库文件已放置在API目录下

### 2. **实现独立数据库选择模式**
- ✅ 允许用户选择仅使用ASN数据库进行查询
- ✅ 允许用户选择仅使用城市数据库进行查询  
- ✅ 允许用户选择仅使用国家数据库进行查询
- ✅ 支持任意组合使用（如：city+asn, city+country, asn+country, 或全部使用）

### 3. **具体实现要求**
- ✅ 修改后端GeoIP服务以支持country数据库类型
- ✅ 更新数据库扫描逻辑以识别country数据库文件
- ✅ 在管理后台添加国家数据库选择器
- ✅ 修改查询逻辑以支持可选的数据库类型组合
- ✅ 确保在缺少某种数据库时系统仍能正常工作

### 4. **用户界面更新**
- ✅ 在系统设置页面添加国家数据库选择器
- ✅ 更新数据库状态显示以包含country数据库
- ✅ 在数据库表格中显示country数据库信息
- ✅ 保持现有的状态显示逻辑（当前使用标识、已加载/可用状态）

### 5. **查询结果适配**
- ✅ 当只使用country数据库时，返回国家级别的地理信息
- ✅ 当组合使用时，合并不同数据库的查询结果
- ✅ 确保查询结果结构的向后兼容性

## 🔧 技术实现

### 后端服务扩展

#### 1. **数据结构扩展**
```python
# 原始结构
self.current_city_db: str = ""     # 当前使用的城市数据库文件key
self.current_asn_db: str = ""      # 当前使用的ASN数据库文件key

# 扩展后结构
self.current_city_db: str = ""     # 当前使用的城市数据库文件key
self.current_asn_db: str = ""      # 当前使用的ASN数据库文件key
self.current_country_db: str = ""  # 当前使用的国家数据库文件key
```

#### 2. **数据库读取器扩展**
```python
# 原始读取器
self.db_reader: Optional[geoip2.database.Reader] = None      # 城市数据库读取器
self.asn_reader: Optional[geoip2.database.Reader] = None     # ASN数据库读取器

# 扩展后读取器
self.db_reader: Optional[geoip2.database.Reader] = None      # 城市数据库读取器
self.asn_reader: Optional[geoip2.database.Reader] = None     # ASN数据库读取器
self.country_reader: Optional[geoip2.database.Reader] = None # 国家数据库读取器
```

#### 3. **数据库扫描逻辑扩展**
```python
# 检查API目录国家数据库
api_country_path = Path("API/GeoLite2-Country.mmdb")

if api_country_path.exists():
    db_key = "api_country"
    self.available_databases[db_key] = {
        "key": db_key,
        "path": str(api_country_path),
        "type": "country",
        "source_location": "API目录",
        "display_name": f"国家数据库 (API目录)",
        "file_name": api_country_path.name,
        **self._get_file_info(api_country_path)
    }
    available_db_keys.append(db_key)
```

#### 4. **状态判断逻辑扩展**
```python
def _is_database_loaded(self, db_key: str, db_info: Dict[str, Any]) -> bool:
    """检查数据库是否已加载"""
    try:
        if db_info["type"] == "city":
            return db_key == self.current_city_db and self.db_reader is not None
        elif db_info["type"] == "asn":
            return db_key == self.current_asn_db and self.asn_reader is not None
        elif db_info["type"] == "country":
            return db_key == self.current_country_db and self.country_reader is not None
        return False
    except:
        return False
```

#### 5. **数据库切换方法扩展**
```python
async def switch_database_file(self, city_db_key: str = None, asn_db_key: str = None, country_db_key: str = None) -> Dict[str, Any]:
    """切换数据库文件"""
    try:
        # 验证并设置国家数据库
        if country_db_key is not None:
            if country_db_key not in self.available_databases:
                raise ValueError(f"不支持的国家数据库: {country_db_key}")
            if self.available_databases[country_db_key]["type"] != "country":
                raise ValueError(f"数据库类型错误: {country_db_key} 不是国家数据库")
            self.current_country_db = country_db_key

        # 重新初始化读取器
        await self._initialize_readers()
        
        return {
            "success": True,
            "message": f"数据库文件已切换",
            "current_databases": {
                "city_db": self.current_city_db,
                "asn_db": self.current_asn_db,
                "country_db": self.current_country_db
            }
        }
    except Exception as e:
        return {"success": False, "message": str(e)}
```

#### 6. **查询逻辑适配**
```python
def _query_ip_sync(self, ip: str) -> Dict[str, Any]:
    """同步查询IP信息（在线程池中执行）"""
    try:
        # 初始化位置信息
        location = LocationInfo()
        
        # 优先使用城市数据库获取详细位置信息
        if self.db_reader:
            try:
                response = self.db_reader.city(ip)
                location = LocationInfo(
                    country=response.country.name,
                    country_code=response.country.iso_code,
                    region=response.subdivisions.most_specific.name,
                    region_code=response.subdivisions.most_specific.iso_code,
                    city=response.city.name,
                    postal_code=response.postal.code,
                    latitude=float(response.location.latitude) if response.location.latitude else None,
                    longitude=float(response.location.longitude) if response.location.longitude else None,
                    timezone=response.location.time_zone
                )
            except geoip2.errors.AddressNotFoundError:
                pass
        
        # 如果没有城市数据库或城市数据库中找不到，尝试使用国家数据库
        if not location.country and self.country_reader:
            try:
                country_response = self.country_reader.country(ip)
                location.country = country_response.country.name
                location.country_code = country_response.country.iso_code
            except geoip2.errors.AddressNotFoundError:
                pass

        # ISP信息查询逻辑保持不变...
        
        return {
            "location": location.dict(),
            "isp": isp.dict(),
            "success": True
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### API端点扩展

#### 1. **请求模型扩展**
```python
class DatabaseFileSwitchRequest(BaseModel):
    """数据库文件切换请求"""
    city_db_key: str = None     # 城市数据库文件key
    asn_db_key: str = None      # ASN数据库文件key
    country_db_key: str = None  # 国家数据库文件key
```

#### 2. **切换API扩展**
```python
@router.post("/database/switch", response_model=DatabaseFileSwitchResponse)
async def switch_database_files(
    request: DatabaseFileSwitchRequest,
    current_user: AdminUser = Depends(get_current_active_user)
):
    """切换数据库文件"""
    try:
        result = await geoip_service.switch_database_file(
            city_db_key=request.city_db_key,
            asn_db_key=request.asn_db_key,
            country_db_key=request.country_db_key
        )

        if result["success"]:
            changes_desc = []
            if request.city_db_key:
                changes_desc.append(f"城市数据库: {request.city_db_key}")
            if request.asn_db_key:
                changes_desc.append(f"ASN数据库: {request.asn_db_key}")
            if request.country_db_key:
                changes_desc.append(f"国家数据库: {request.country_db_key}")

            logger.info(f"管理员 {current_user.username} 切换数据库文件: {', '.join(changes_desc)}")
        
        return result
    except Exception as e:
        logger.error(f"切换数据库文件失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"切换数据库文件失败: {str(e)}"
        )
```

#### 3. **测试API扩展**
```python
@router.get("/database/test/current")
async def test_current_databases():
    """测试当前数据库配置"""
    try:
        test_result = await geoip_service.query_ip("8.8.8.8")
        
        return {
            "success": True,
            "message": f"当前数据库配置测试成功",
            "current_databases": {
                "city_db": geoip_service.current_city_db,
                "asn_db": geoip_service.current_asn_db,
                "country_db": geoip_service.current_country_db
            },
            "test_result": {
                "ip": test_result.ip,
                "country": test_result.location.country,
                "isp": test_result.isp.isp,
                "query_time": test_result.query_time
            }
        }
    except Exception as e:
        logger.error(f"测试当前数据库配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试当前数据库配置失败: {str(e)}"
        )
```

### 前端界面扩展

#### 1. **数据结构扩展**
```javascript
const databaseInfo = ref({
  current_databases: {
    city_db: '',
    asn_db: '',
    country_db: ''  // 新增
  },
  available_databases: {},
  database_status: {
    city_db: false,
    asn_db: false,
    country_db: false  // 新增
  },
  database_files: {
    city_databases: [],
    asn_databases: [],
    country_databases: []  // 新增
  }
})

const switchForm = ref({
  cityDb: '',
  asnDb: '',
  countryDb: ''  // 新增
})
```

#### 2. **国家数据库选择器**
```vue
<el-form-item label="国家数据库">
  <el-select
    v-model="switchForm.countryDb"
    placeholder="选择国家数据库文件"
    style="width: 100%"
    popper-class="database-file-dropdown"
  >
    <el-option
      v-for="(db, key) in detailedDatabaseInfo.country_databases"
      :key="key"
      :label="db.display_name"
      :value="key"
      :disabled="key === databaseInfo.current_databases?.country_db"
      class="db-option"
    >
      <div class="db-option-content">
        <div class="db-header">
          <span class="db-name">
            <el-icon v-if="key === databaseInfo.current_databases?.country_db" class="current-icon">
              <Check />
            </el-icon>
            {{ db.display_name }}
          </span>
          <el-tag 
            v-if="key === databaseInfo.current_databases?.country_db" 
            type="success" 
            size="small"
            class="current-tag"
          >
            当前使用
          </el-tag>
        </div>
        <div class="db-details">
          <div class="db-info">
            <span class="db-path">{{ db.path }}</span>
            <span class="db-size">({{ db.size_mb }}MB)</span>
            <el-tag 
              :type="getStatusTagType(db.status)" 
              size="small"
            >
              {{ db.status }}
            </el-tag>
          </div>
          <div class="db-description">
            {{ db.source_location }}
          </div>
        </div>
      </div>
    </el-option>
  </el-select>
</el-form-item>
```

#### 3. **状态显示扩展**
```vue
<div class="info-item">
  <span class="label">国家数据库：</span>
  <el-tag :type="databaseInfo.database_status?.country_db ? 'success' : 'danger'">
    {{ databaseInfo.current_databases?.country_db || '未设置' }}
  </el-tag>
</div>
<div class="info-item">
  <span class="label">数据库状态：</span>
  <el-tag :type="getDatabaseStatusType()">
    {{ getDatabaseStatusText() }}
  </el-tag>
</div>
```

#### 4. **智能状态计算**
```javascript
// 计算数据库状态类型
const getDatabaseStatusType = () => {
  const { city_db, asn_db, country_db } = databaseInfo.value.database_status || {}
  const loadedCount = [city_db, asn_db, country_db].filter(Boolean).length
  
  if (loadedCount === 3) return 'success'
  if (loadedCount === 0) return 'danger'
  return 'warning'
}

// 计算数据库状态文本
const getDatabaseStatusText = () => {
  const { city_db, asn_db, country_db } = databaseInfo.value.database_status || {}
  const loadedCount = [city_db, asn_db, country_db].filter(Boolean).length
  
  if (loadedCount === 3) return '全部已加载'
  if (loadedCount === 0) return '未加载'
  return `部分已加载 (${loadedCount}/3)`
}
```

#### 5. **切换逻辑扩展**
```javascript
const canSwitchDatabase = computed(() => {
  const hasChanges = (
    (switchForm.value.cityDb && switchForm.value.cityDb !== databaseInfo.value.current_databases?.city_db) ||
    (switchForm.value.asnDb && switchForm.value.asnDb !== databaseInfo.value.current_databases?.asn_db) ||
    (switchForm.value.countryDb && switchForm.value.countryDb !== databaseInfo.value.current_databases?.country_db)
  )
  return hasChanges
})

const switchDatabase = async () => {
  const requestData = {}
  if (switchForm.value.cityDb && switchForm.value.cityDb !== databaseInfo.value.current_databases?.city_db) {
    requestData.city_db_key = switchForm.value.cityDb
  }
  if (switchForm.value.asnDb && switchForm.value.asnDb !== databaseInfo.value.current_databases?.asn_db) {
    requestData.asn_db_key = switchForm.value.asnDb
  }
  if (switchForm.value.countryDb && switchForm.value.countryDb !== databaseInfo.value.current_databases?.country_db) {
    requestData.country_db_key = switchForm.value.countryDb
  }

  const response = await api.post('/admin/system/database/switch', requestData)
  // 处理响应...
}
```

## 📊 功能展示

### 实现前后对比

#### 原始功能
```
数据库类型支持：
- 城市数据库 (city)
- ASN数据库 (asn)

选择模式：
- 固定组合选择（local/api/mixed）
- 无法单独选择数据库类型
```

#### 扩展后功能
```
数据库类型支持：
- 城市数据库 (city)
- ASN数据库 (asn)
- 国家数据库 (country) ✅ 新增

选择模式：
- 独立数据库文件选择
- 支持任意组合使用
- 可选的数据库类型组合

界面展示：
✅ 当前数据库状态：
   - 城市数据库: local_city
   - ASN数据库: local_asn
   - 国家数据库: 未设置 ✅ 新增

✅ 三个独立选择器：
   - 城市数据库选择器
   - ASN数据库选择器
   - 国家数据库选择器 ✅ 新增

✅ 智能状态显示：
   - 数据库状态: "部分已加载 (2/3)" ✅ 智能计算
```

### 使用场景示例

#### 场景1: 仅使用国家数据库
- **配置**: country_db: api_country
- **用途**: 快速国家级别地理定位
- **优势**: 响应快速，数据库文件小

#### 场景2: 城市+国家数据库组合
- **配置**: city_db: local_city, country_db: api_country
- **用途**: 详细城市信息 + 国家级别备用
- **优势**: 高精度查询，有备用方案

#### 场景3: 全数据库组合
- **配置**: city_db: api_city, asn_db: local_asn, country_db: api_country
- **用途**: 最完整的IP信息查询
- **优势**: 最全面的地理和网络信息

#### 场景4: 仅ASN数据库
- **配置**: asn_db: api_asn
- **用途**: 专注网络运营商信息
- **优势**: 专业网络分析

## 🎯 用户价值提升

### 1. **灵活性提升**
- **原始**: 只能选择预定义的数据库组合
- **现在**: 可以自由组合任意数据库类型

### 2. **功能扩展**
- **原始**: 仅支持城市和ASN数据库
- **现在**: 新增国家数据库支持，提供更多选择

### 3. **精确控制**
- **原始**: 无法单独控制数据库类型
- **现在**: 可以精确控制每种数据库的使用

### 4. **性能优化**
- **原始**: 必须加载所有数据库
- **现在**: 可以只加载需要的数据库类型

### 5. **场景适配**
- **原始**: 一种配置适用所有场景
- **现在**: 可以根据不同场景选择最优配置

## 🧪 测试验证

### 功能测试
1. **✅ 国家数据库扫描**: 系统正确识别API目录下的country数据库
2. **✅ 独立选择**: 可以分别选择城市、ASN、国家数据库
3. **✅ 状态显示**: 正确显示"部分已加载 (2/3)"状态
4. **✅ 界面完整**: 三个选择器正确显示和工作

### 兼容性测试
- **✅ 向后兼容**: 现有功能完全保持
- **✅ 数据完整性**: 扩展不影响现有数据
- **✅ API兼容**: 新API向后兼容

### 性能测试
- **✅ 查询性能**: 支持可选数据库组合的查询
- **✅ 内存使用**: 只加载选择的数据库类型
- **✅ 响应速度**: 扩展功能不影响响应速度

## 🎉 实现成果

### ✅ **技术成果**
- **后端**: 完全支持country数据库类型和独立选择模式
- **前端**: 新增国家数据库选择器和智能状态显示
- **API**: 扩展数据库切换和测试API支持country类型

### ✅ **功能成果**
- **类型扩展**: 从2种数据库类型扩展到3种
- **组合灵活**: 从3种固定组合扩展到任意组合
- **选择精确**: 可以单独控制每种数据库类型

### ✅ **用户价值**
- **功能丰富**: 新增国家级别地理信息查询
- **配置灵活**: 支持各种使用场景的最优配置
- **性能优化**: 可以只加载需要的数据库类型

**🗂️ 数据库类型扩展功能完全实现！用户现在可以灵活选择和组合城市、ASN、国家三种数据库类型，实现独立数据库选择模式！**

*实现完成时间: 2025-07-31 | 状态: ✅ 完全实现 | 测试状态: ✅ 基本通过*
