'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MagnifyingGlassIcon, GlobeAltIcon, ChartBarIcon, UserGroupIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

import IPQueryWidget from '@/components/IPQueryWidget';
import StatsCard from '@/components/StatsCard';
import FeatureCard from '@/components/FeatureCard';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function HomePage() {
  const [stats, setStats] = useState({
    totalQueries: 0,
    activeUsers: 0,
    successRate: 0,
    avgResponseTime: 0
  });

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // 获取统计数据
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats/public');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    {
      icon: <MagnifyingGlassIcon className="h-8 w-8" />,
      title: '精准查询',
      description: '基于MaxMind数据库，提供准确的IP地理位置信息',
      color: 'blue'
    },
    {
      icon: <GlobeAltIcon className="h-8 w-8" />,
      title: '全球覆盖',
      description: '支持全球IPv4和IPv6地址查询，覆盖范围广泛',
      color: 'green'
    },
    {
      icon: <ChartBarIcon className="h-8 w-8" />,
      title: '批量处理',
      description: '支持批量IP查询，最多可同时查询100个IP地址',
      color: 'purple'
    },
    {
      icon: <UserGroupIcon className="h-8 w-8" />,
      title: 'API接口',
      description: '提供RESTful API，支持开发者集成到自己的应用中',
      color: 'orange'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-slate-800">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              IP查询工具
            </span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
            专业的IP地址查询服务，快速获取IP地理位置、ISP信息等详细数据。
            支持单个查询、批量查询，提供完整的API接口。
          </p>
        </motion.section>

        {/* Stats Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16"
        >
          <StatsCard
            title="总查询次数"
            value={stats.totalQueries}
            icon={<MagnifyingGlassIcon className="h-6 w-6" />}
            color="blue"
            isLoading={isLoading}
          />
          <StatsCard
            title="活跃用户"
            value={stats.activeUsers}
            icon={<UserGroupIcon className="h-6 w-6" />}
            color="green"
            isLoading={isLoading}
          />
          <StatsCard
            title="成功率"
            value={`${stats.successRate}%`}
            icon={<ChartBarIcon className="h-6 w-6" />}
            color="purple"
            isLoading={isLoading}
          />
          <StatsCard
            title="平均响应时间"
            value={`${stats.avgResponseTime}ms`}
            icon={<GlobeAltIcon className="h-6 w-6" />}
            color="orange"
            isLoading={isLoading}
          />
        </motion.section>

        {/* IP Query Widget */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-16"
        >
          <IPQueryWidget />
        </motion.section>

        {/* Features Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mb-16"
        >
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              功能特性
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              我们提供专业、可靠、高效的IP查询服务，满足各种使用场景的需求
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.8 + index * 0.1 }}
              >
                <FeatureCard {...feature} />
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* CTA Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.2 }}
          className="text-center bg-white dark:bg-slate-800 rounded-2xl p-12 shadow-xl"
        >
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            开始使用API服务
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
            注册账号获取API密钥，享受更高的查询限额和专业的技术支持
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              onClick={() => window.location.href = '/auth/register'}
            >
              免费注册
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-semibold hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors"
              onClick={() => window.location.href = '/docs'}
            >
              查看文档
            </motion.button>
          </div>
        </motion.section>
      </main>

      <Footer />
    </div>
  );
}
