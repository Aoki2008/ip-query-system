/**
 * SEO配置服务
 */
import api from '@/utils/api'

// SEO配置接口类型
export interface SeoConfig {
  id: number
  title: string
  description: string
  keywords: string[]
  created_at: string
  updated_at: string
}

export interface SeoConfigCreate {
  title: string
  description: string
  keywords: string[]
}

export interface SeoConfigUpdate {
  title?: string
  description?: string
  keywords?: string[]
}

export interface SeoPreview {
  title: string
  description: string
  keywords: string[]
  meta_tags: string
}

export interface SeoStats {
  title_length: number
  description_length: number
  keywords_count: number
  title_status: string
  description_status: string
  keywords_status: string
  overall_score: number
}

class SeoService {
  private baseURL = `/admin/seo`

  /**
   * 获取SEO配置
   */
  async getSeoConfig(): Promise<SeoConfig> {
    const response = await api.get(`${this.baseURL}/config`)
    return response.data
  }

  /**
   * 创建SEO配置
   */
  async createSeoConfig(config: SeoConfigCreate): Promise<SeoConfig> {
    const response = await api.post(`${this.baseURL}/config`, config)
    return response.data
  }

  /**
   * 更新SEO配置
   */
  async updateSeoConfig(config: SeoConfigUpdate): Promise<SeoConfig> {
    const response = await api.put(`${this.baseURL}/config`, config)
    return response.data
  }

  /**
   * 删除SEO配置
   */
  async deleteSeoConfig(): Promise<void> {
    await api.delete(`${this.baseURL}/config`)
  }

  /**
   * 获取SEO预览
   */
  async getSeoPreview(): Promise<SeoPreview> {
    const response = await api.get(`${this.baseURL}/preview`)
    return response.data
  }

  /**
   * 获取SEO统计
   */
  async getSeoStats(): Promise<SeoStats> {
    const response = await api.get(`${this.baseURL}/stats`)
    return response.data
  }

  /**
   * 获取关键词建议
   */
  async getKeywordSuggestions(): Promise<string[]> {
    const response = await api.get(`${this.baseURL}/keywords/suggestions`)
    return response.data
  }

  /**
   * 获取公开SEO配置（用于前端页面）
   */
  async getPublicSeoConfig(): Promise<SeoConfig> {
    const response = await api.get(`${this.baseURL}/public/config`)
    return response.data
  }

  /**
   * 保存SEO配置（智能判断创建或更新）
   */
  async saveSeoConfig(config: SeoConfigCreate): Promise<SeoConfig> {
    try {
      // 先尝试获取现有配置
      await this.getSeoConfig()
      // 如果存在，则更新
      return await this.updateSeoConfig(config)
    } catch (error: any) {
      if (error.response?.status === 404) {
        // 如果不存在，则创建
        return await this.createSeoConfig(config)
      }
      throw error
    }
  }

  /**
   * 验证SEO配置
   */
  validateSeoConfig(config: SeoConfigCreate): string[] {
    const errors: string[] = []

    // 验证标题
    if (!config.title || config.title.trim().length === 0) {
      errors.push('网站标题不能为空')
    } else if (config.title.length < 10) {
      errors.push('网站标题长度不能少于10个字符')
    } else if (config.title.length > 60) {
      errors.push('网站标题长度不能超过60个字符')
    }

    // 验证描述
    if (!config.description || config.description.trim().length === 0) {
      errors.push('网站描述不能为空')
    } else if (config.description.length < 50) {
      errors.push('网站描述长度不能少于50个字符')
    } else if (config.description.length > 160) {
      errors.push('网站描述长度不能超过160个字符')
    }

    // 验证关键词
    if (config.keywords.length > 10) {
      errors.push('关键词数量不能超过10个')
    }

    // 验证关键词唯一性
    const uniqueKeywords = new Set(config.keywords)
    if (uniqueKeywords.size !== config.keywords.length) {
      errors.push('关键词不能重复')
    }

    return errors
  }

  /**
   * 生成Meta标签
   */
  generateMetaTags(config: SeoConfig): string {
    const keywords = config.keywords.join(', ')
    return `<title>${config.title}</title>
<meta name="description" content="${config.description}" />
<meta name="keywords" content="${keywords}" />
<meta property="og:title" content="${config.title}" />
<meta property="og:description" content="${config.description}" />
<meta property="og:type" content="website" />
<meta name="twitter:card" content="summary" />
<meta name="twitter:title" content="${config.title}" />
<meta name="twitter:description" content="${config.description}" />`
  }

  /**
   * 获取SEO评分
   */
  calculateSeoScore(config: SeoConfig): number {
    let score = 0

    // 标题评分 (40%)
    const titleLength = config.title.length
    if (titleLength >= 10 && titleLength <= 60) {
      score += 40
    } else if (titleLength < 10) {
      score += 20
    } else {
      score += 30
    }

    // 描述评分 (40%)
    const descLength = config.description.length
    if (descLength >= 50 && descLength <= 160) {
      score += 40
    } else if (descLength < 50) {
      score += 20
    } else {
      score += 30
    }

    // 关键词评分 (20%)
    const keywordCount = config.keywords.length
    if (keywordCount >= 5 && keywordCount <= 10) {
      score += 20
    } else if (keywordCount > 0 && keywordCount < 5) {
      score += 15
    } else if (keywordCount === 0) {
      score += 0
    } else {
      score += 10
    }

    return score
  }
}

export const seoService = new SeoService()
export default seoService
