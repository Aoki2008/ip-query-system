<template>
  <div class="seo-container">
    <el-card class="page-header">
      <template #header>
        <div class="header-content">
          <h2>SEO设置</h2>
          <p>管理网站的搜索引擎优化配置，包括标题、关键词和描述</p>
        </div>
      </template>
    </el-card>

    <el-row :gutter="20">
      <!-- 左侧配置表单 -->
      <el-col :span="16">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><Edit /></el-icon>
              <span>SEO配置</span>
            </div>
          </template>

          <el-form
            ref="seoFormRef"
            :model="seoForm"
            :rules="seoRules"
            label-width="120px"
            label-position="left"
          >
            <!-- 网站标题 -->
            <el-form-item label="网站标题" prop="title">
              <el-input
                v-model="seoForm.title"
                placeholder="请输入网站标题"
                maxlength="60"
                show-word-limit
                clearable
              />
              <div class="form-tip">
                建议长度：50-60字符，将显示在浏览器标签页和搜索结果中
              </div>
            </el-form-item>

            <!-- 网站描述 -->
            <el-form-item label="网站描述" prop="description">
              <el-input
                v-model="seoForm.description"
                type="textarea"
                :rows="4"
                placeholder="请输入网站描述"
                maxlength="160"
                show-word-limit
                clearable
              />
              <div class="form-tip">
                建议长度：150-160字符，将显示在搜索引擎结果页面的摘要中
              </div>
            </el-form-item>

            <!-- 关键词管理 -->
            <el-form-item label="SEO关键词" prop="keywords">
              <div class="keywords-container">
                <div class="keywords-input">
                  <el-input
                    v-model="newKeyword"
                    placeholder="输入关键词后按回车添加"
                    @keyup.enter="addKeyword"
                    clearable
                  >
                    <template #append>
                      <el-button @click="addKeyword" :disabled="!newKeyword.trim()">
                        添加
                      </el-button>
                    </template>
                  </el-input>
                </div>
                
                <div class="keywords-tags" v-if="seoForm.keywords.length > 0">
                  <el-tag
                    v-for="(keyword, index) in seoForm.keywords"
                    :key="index"
                    closable
                    @close="removeKeyword(index)"
                    class="keyword-tag"
                  >
                    {{ keyword }}
                  </el-tag>
                </div>
                
                <div class="keywords-suggestions">
                  <div class="suggestions-label">建议关键词：</div>
                  <el-tag
                    v-for="suggestion in keywordSuggestions"
                    :key="suggestion"
                    @click="addSuggestedKeyword(suggestion)"
                    class="suggestion-tag"
                    effect="plain"
                  >
                    {{ suggestion }}
                  </el-tag>
                </div>
                
                <div class="form-tip">
                  建议添加5-10个核心关键词，当前已添加：{{ seoForm.keywords.length }}/10
                </div>
              </div>
            </el-form-item>

            <!-- 操作按钮 -->
            <el-form-item>
              <el-button type="primary" @click="saveSeoConfig" :loading="saving">
                保存配置
              </el-button>
              <el-button @click="resetForm">重置</el-button>
              <el-button @click="previewSeo" type="info">预览效果</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧预览面板 -->
      <el-col :span="8">
        <el-card class="preview-card">
          <template #header>
            <div class="card-header">
              <el-icon><View /></el-icon>
              <span>预览效果</span>
            </div>
          </template>

          <!-- 浏览器标签页预览 -->
          <div class="preview-section">
            <h4>浏览器标签页</h4>
            <div class="browser-tab-preview">
              <div class="tab-icon">🌐</div>
              <div class="tab-title">{{ seoForm.title || '网站标题' }}</div>
            </div>
          </div>

          <!-- 搜索结果预览 -->
          <div class="preview-section">
            <h4>搜索引擎结果</h4>
            <div class="search-result-preview">
              <div class="result-title">{{ seoForm.title || '网站标题' }}</div>
              <div class="result-url">https://your-domain.com</div>
              <div class="result-description">
                {{ seoForm.description || '网站描述将显示在这里...' }}
              </div>
            </div>
          </div>

          <!-- 关键词统计 -->
          <div class="preview-section">
            <h4>关键词统计</h4>
            <div class="keywords-stats">
              <div class="stat-item">
                <span class="stat-label">总数量：</span>
                <span class="stat-value">{{ seoForm.keywords.length }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">建议范围：</span>
                <span class="stat-value">5-10个</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">状态：</span>
                <el-tag 
                  :type="getKeywordsStatus().type" 
                  size="small"
                >
                  {{ getKeywordsStatus().text }}
                </el-tag>
              </div>
            </div>
          </div>

          <!-- 配置状态 -->
          <div class="preview-section">
            <h4>配置状态</h4>
            <div class="config-status">
              <div class="status-item">
                <el-icon :color="seoForm.title ? '#67c23a' : '#f56c6c'">
                  <CircleCheck v-if="seoForm.title" />
                  <CircleClose v-else />
                </el-icon>
                <span>网站标题</span>
              </div>
              <div class="status-item">
                <el-icon :color="seoForm.description ? '#67c23a' : '#f56c6c'">
                  <CircleCheck v-if="seoForm.description" />
                  <CircleClose v-else />
                </el-icon>
                <span>网站描述</span>
              </div>
              <div class="status-item">
                <el-icon :color="seoForm.keywords.length > 0 ? '#67c23a' : '#f56c6c'">
                  <CircleCheck v-if="seoForm.keywords.length > 0" />
                  <CircleClose v-else />
                </el-icon>
                <span>SEO关键词</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="SEO效果预览"
      width="600px"
    >
      <div class="preview-dialog-content">
        <h3>HTML Meta标签预览</h3>
        <el-input
          type="textarea"
          :rows="8"
          :value="generateMetaTags()"
          readonly
          class="meta-preview"
        />
        
        <h3>搜索引擎结果预览</h3>
        <div class="search-engine-preview">
          <div class="search-result">
            <div class="result-title-large">{{ seoForm.title }}</div>
            <div class="result-url-large">https://your-domain.com</div>
            <div class="result-description-large">{{ seoForm.description }}</div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, View, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import seoService, { type SeoConfigCreate } from '@/services/seoService'

// 表单引用
const seoFormRef = ref<FormInstance>()

// 表单数据
const seoForm = reactive({
  title: '',
  description: '',
  keywords: [] as string[]
})

// 新关键词输入
const newKeyword = ref('')

// 关键词建议
const keywordSuggestions = ref<string[]>([])

// 加载关键词建议
const loadKeywordSuggestions = async () => {
  try {
    keywordSuggestions.value = await seoService.getKeywordSuggestions()
  } catch (error: any) {
    console.error('加载关键词建议失败:', error)
    // 使用默认建议
    keywordSuggestions.value = [
      'IP查询', 'IP地址查询', '地理位置查询', '网络工具',
      'IP定位', '批量IP查询', 'IP地址定位', '网络分析',
      'ISP查询', 'IP归属地', '网络诊断', 'IP工具'
    ]

    // 只有在非认证错误时才显示错误消息
    if (error.response?.status !== 401) {
      ElMessage.warning('使用默认关键词建议')
    }
  }
}

// 状态
const saving = ref(false)
const previewDialogVisible = ref(false)

// 表单验证规则
const seoRules: FormRules = {
  title: [
    { required: true, message: '请输入网站标题', trigger: 'blur' },
    { min: 10, max: 60, message: '标题长度应在10-60字符之间', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入网站描述', trigger: 'blur' },
    { min: 50, max: 160, message: '描述长度应在50-160字符之间', trigger: 'blur' }
  ]
}

// 方法
const addKeyword = () => {
  const keyword = newKeyword.value.trim()
  if (!keyword) return

  if (seoForm.keywords.length >= 10) {
    ElMessage.warning('最多只能添加10个关键词')
    return
  }

  if (seoForm.keywords.includes(keyword)) {
    ElMessage.warning('关键词已存在')
    return
  }

  seoForm.keywords.push(keyword)
  newKeyword.value = ''
  ElMessage.success('关键词添加成功')
}

const removeKeyword = (index: number) => {
  seoForm.keywords.splice(index, 1)
}

const addSuggestedKeyword = (keyword: string) => {
  if (seoForm.keywords.includes(keyword)) {
    ElMessage.warning('关键词已存在')
    return
  }

  if (seoForm.keywords.length >= 10) {
    ElMessage.warning('最多只能添加10个关键词')
    return
  }

  seoForm.keywords.push(keyword)
  ElMessage.success('关键词添加成功')
}

const getKeywordsStatus = () => {
  const count = seoForm.keywords.length
  if (count === 0) {
    return { type: 'danger', text: '未设置' }
  } else if (count < 5) {
    return { type: 'warning', text: '偏少' }
  } else if (count <= 10) {
    return { type: 'success', text: '合适' }
  } else {
    return { type: 'danger', text: '过多' }
  }
}

const generateMetaTags = () => {
  const keywords = seoForm.keywords.join(', ')
  return `<title>${seoForm.title}</title>
<meta name="description" content="${seoForm.description}" />
<meta name="keywords" content="${keywords}" />
<meta property="og:title" content="${seoForm.title}" />
<meta property="og:description" content="${seoForm.description}" />
<meta property="og:type" content="website" />
<meta name="twitter:card" content="summary" />
<meta name="twitter:title" content="${seoForm.title}" />
<meta name="twitter:description" content="${seoForm.description}" />`
}

const saveSeoConfig = async () => {
  if (!seoFormRef.value) return

  try {
    await seoFormRef.value.validate()
    saving.value = true

    // 验证配置
    const errors = seoService.validateSeoConfig(seoForm as SeoConfigCreate)
    if (errors.length > 0) {
      ElMessage.error(errors[0])
      return
    }

    // 调用API保存配置
    await seoService.saveSeoConfig(seoForm as SeoConfigCreate)

    ElMessage.success('SEO配置保存成功')
  } catch (error: any) {
    console.error('保存SEO配置失败:', error)
    const message = error.response?.data?.detail || '保存失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  ElMessageBox.confirm('确定要重置所有配置吗？', '确认重置', {
    type: 'warning'
  }).then(() => {
    seoFormRef.value?.resetFields()
    seoForm.keywords = []
    newKeyword.value = ''
    ElMessage.success('配置已重置')
  }).catch(() => {
    // 用户取消
  })
}

const previewSeo = () => {
  previewDialogVisible.value = true
}

const loadSeoConfig = async () => {
  try {
    const config = await seoService.getSeoConfig()
    Object.assign(seoForm, {
      title: config.title,
      description: config.description,
      keywords: config.keywords
    })
  } catch (error: any) {
    console.error('加载SEO配置失败:', error)
    if (error.response?.status === 404) {
      // 404错误表示还没有配置，使用默认值
      console.log('SEO配置不存在，使用默认配置')
    } else if (error.response?.status === 401) {
      // 401错误表示认证失败，不显示错误消息（由拦截器处理）
      console.log('SEO配置加载需要认证')
    } else {
      ElMessage.error('加载SEO配置失败')
    }
  }
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadSeoConfig(),
    loadKeywordSuggestions()
  ])
})
</script>

<style scoped>
.seo-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.header-content p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.config-card,
.preview-card {
  height: fit-content;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

/* 关键词管理样式 */
.keywords-container {
  width: 100%;
}

.keywords-input {
  margin-bottom: 12px;
}

.keywords-tags {
  margin-bottom: 12px;
  min-height: 32px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  cursor: default;
}

.keywords-suggestions {
  margin-bottom: 8px;
}

.suggestions-label {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
}

.suggestion-tag {
  margin-right: 8px;
  margin-bottom: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-tag:hover {
  background-color: #409eff;
  color: white;
}

/* 预览样式 */
.preview-section {
  margin-bottom: 24px;
}

.preview-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.browser-tab-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  font-size: 13px;
}

.tab-icon {
  font-size: 14px;
}

.tab-title {
  color: #303133;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.search-result-preview {
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.result-title {
  color: #1a0dab;
  font-size: 18px;
  font-weight: 400;
  margin-bottom: 4px;
  cursor: pointer;
  text-decoration: underline;
}

.result-url {
  color: #006621;
  font-size: 14px;
  margin-bottom: 4px;
}

.result-description {
  color: #545454;
  font-size: 13px;
  line-height: 1.4;
}

.keywords-stats {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
}

.stat-item:last-child {
  margin-bottom: 0;
}

.stat-label {
  color: #606266;
}

.stat-value {
  color: #303133;
  font-weight: 500;
}

.config-status {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

.status-item:last-child {
  margin-bottom: 0;
}

/* 预览对话框样式 */
.preview-dialog-content h3 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.meta-preview {
  margin-bottom: 24px;
}

.search-engine-preview {
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.search-result {
  max-width: 600px;
}

.result-title-large {
  color: #1a0dab;
  font-size: 20px;
  font-weight: 400;
  margin-bottom: 6px;
  cursor: pointer;
  text-decoration: underline;
  line-height: 1.3;
}

.result-url-large {
  color: #006621;
  font-size: 14px;
  margin-bottom: 6px;
}

.result-description-large {
  color: #545454;
  font-size: 14px;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .seo-container :deep(.el-col-16) {
    width: 100%;
    margin-bottom: 20px;
  }

  .seo-container :deep(.el-col-8) {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .seo-container {
    padding: 10px;
  }

  .keywords-tags {
    flex-direction: column;
    align-items: flex-start;
  }

  .suggestion-tag {
    margin-right: 4px;
    margin-bottom: 8px;
  }
}
</style>
