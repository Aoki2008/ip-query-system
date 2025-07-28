/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // 环境变量
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },

  // 图片优化配置
  images: {
    domains: ['localhost', 'api.example.com'],
    formats: ['image/webp', 'image/avif'],
  },

  // 国际化配置
  i18n: {
    locales: ['zh-CN', 'en'],
    defaultLocale: 'zh-CN',
  },

  // 重定向配置
  async redirects() {
    return [
      {
        source: '/admin',
        destination: '/admin/dashboard',
        permanent: true,
      },
    ];
  },

  // 重写配置
  async rewrites() {
    return [
      {
        source: '/api/proxy/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },

  // 头部配置
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },

  // Webpack配置
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // 自定义webpack配置
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });

    return config;
  },

  // 实验性功能
  experimental: {
    appDir: true,
    serverComponentsExternalPackages: ['prisma'],
  },

  // 输出配置
  output: 'standalone',

  // 压缩配置
  compress: true,

  // 电源配置
  poweredByHeader: false,

  // 生成ETag
  generateEtags: true,

  // 页面扩展名
  pageExtensions: ['ts', 'tsx', 'js', 'jsx'],

  // 跟踪配置
  trailingSlash: false,

  // 构建指示器
  devIndicators: {
    buildActivity: true,
    buildActivityPosition: 'bottom-right',
  },
};

module.exports = nextConfig;
