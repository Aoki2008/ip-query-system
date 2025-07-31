/**
 * 前端SEO服务 - 用于动态更新页面SEO信息
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface SeoConfig {
  id: number
  title: string
  description: string
  keywords: string[]
  created_at: string
  updated_at: string
}

class FrontendSeoService {
  private baseURL = `${API_BASE_URL}/api/admin/seo`

  /**
   * 获取公开的SEO配置
   */
  async getPublicSeoConfig(): Promise<SeoConfig> {
    try {
      const response = await axios.get(`${this.baseURL}/public/config`)
      return response.data
    } catch (error) {
      console.error('获取SEO配置失败:', error)
      // 返回默认配置
      return {
        id: 0,
        title: 'IP查询工具 - 专业的IP地址查询服务',
        description: '专业的IP地址查询工具，支持单个和批量查询，提供准确的地理位置信息、ISP信息和网络分析功能。',
        keywords: ['IP查询', 'IP地址查询', '地理位置', '网络工具'],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    }
  }

  /**
   * 更新页面标题
   */
  updatePageTitle(title: string): void {
    document.title = title
  }

  /**
   * 更新Meta描述
   */
  updateMetaDescription(description: string): void {
    let metaDesc = document.querySelector('meta[name="description"]') as HTMLMetaElement
    if (!metaDesc) {
      metaDesc = document.createElement('meta')
      metaDesc.name = 'description'
      document.head.appendChild(metaDesc)
    }
    metaDesc.content = description
  }

  /**
   * 更新Meta关键词
   */
  updateMetaKeywords(keywords: string[]): void {
    let metaKeywords = document.querySelector('meta[name="keywords"]') as HTMLMetaElement
    if (!metaKeywords) {
      metaKeywords = document.createElement('meta')
      metaKeywords.name = 'keywords'
      document.head.appendChild(metaKeywords)
    }
    metaKeywords.content = keywords.join(', ')
  }

  /**
   * 更新Open Graph标签
   */
  updateOpenGraphTags(config: SeoConfig): void {
    // OG Title
    this.updateOrCreateMetaTag('property', 'og:title', config.title)
    
    // OG Description
    this.updateOrCreateMetaTag('property', 'og:description', config.description)
    
    // OG Type
    this.updateOrCreateMetaTag('property', 'og:type', 'website')
    
    // OG URL
    this.updateOrCreateMetaTag('property', 'og:url', window.location.href)
  }

  /**
   * 更新Twitter Card标签
   */
  updateTwitterCardTags(config: SeoConfig): void {
    // Twitter Card
    this.updateOrCreateMetaTag('name', 'twitter:card', 'summary')
    
    // Twitter Title
    this.updateOrCreateMetaTag('name', 'twitter:title', config.title)
    
    // Twitter Description
    this.updateOrCreateMetaTag('name', 'twitter:description', config.description)
  }

  /**
   * 更新或创建Meta标签
   */
  private updateOrCreateMetaTag(attribute: string, value: string, content: string): void {
    let meta = document.querySelector(`meta[${attribute}="${value}"]`) as HTMLMetaElement
    if (!meta) {
      meta = document.createElement('meta')
      meta.setAttribute(attribute, value)
      document.head.appendChild(meta)
    }
    meta.content = content
  }

  /**
   * 应用SEO配置到页面
   */
  async applySeoConfig(): Promise<void> {
    try {
      const config = await this.getPublicSeoConfig()
      
      // 更新页面标题
      this.updatePageTitle(config.title)
      
      // 更新Meta标签
      this.updateMetaDescription(config.description)
      this.updateMetaKeywords(config.keywords)
      
      // 更新社交媒体标签
      this.updateOpenGraphTags(config)
      this.updateTwitterCardTags(config)
      
      console.log('SEO配置已应用:', config)
    } catch (error) {
      console.error('应用SEO配置失败:', error)
    }
  }

  /**
   * 为特定页面设置SEO信息
   */
  setPageSeo(title: string, description?: string, keywords?: string[]): void {
    // 更新标题
    this.updatePageTitle(title)
    
    // 更新描述
    if (description) {
      this.updateMetaDescription(description)
    }
    
    // 更新关键词
    if (keywords) {
      this.updateMetaKeywords(keywords)
    }
    
    // 更新OG标签
    this.updateOrCreateMetaTag('property', 'og:title', title)
    if (description) {
      this.updateOrCreateMetaTag('property', 'og:description', description)
    }
    
    // 更新Twitter标签
    this.updateOrCreateMetaTag('name', 'twitter:title', title)
    if (description) {
      this.updateOrCreateMetaTag('name', 'twitter:description', description)
    }
  }

  /**
   * 生成结构化数据 (JSON-LD)
   */
  generateStructuredData(config: SeoConfig): string {
    const structuredData = {
      "@context": "https://schema.org",
      "@type": "WebApplication",
      "name": config.title,
      "description": config.description,
      "url": window.location.origin,
      "applicationCategory": "NetworkingApplication",
      "operatingSystem": "Web Browser",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
      },
      "creator": {
        "@type": "Organization",
        "name": "IP查询工具"
      }
    }
    
    return JSON.stringify(structuredData, null, 2)
  }

  /**
   * 添加结构化数据到页面
   */
  addStructuredData(config: SeoConfig): void {
    // 移除现有的结构化数据
    const existingScript = document.querySelector('script[type="application/ld+json"]')
    if (existingScript) {
      existingScript.remove()
    }
    
    // 添加新的结构化数据
    const script = document.createElement('script')
    script.type = 'application/ld+json'
    script.textContent = this.generateStructuredData(config)
    document.head.appendChild(script)
  }

  /**
   * 完整的SEO初始化
   */
  async initializeSeo(): Promise<void> {
    try {
      const config = await this.getPublicSeoConfig()
      
      // 应用基本SEO配置
      await this.applySeoConfig()
      
      // 添加结构化数据
      this.addStructuredData(config)
      
      console.log('SEO初始化完成')
    } catch (error) {
      console.error('SEO初始化失败:', error)
    }
  }
}

export const frontendSeoService = new FrontendSeoService()
export default frontendSeoService
