'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MagnifyingGlassIcon, ClipboardDocumentIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import clsx from 'clsx';

interface IPResult {
  ip: string;
  country: string;
  country_code: string;
  region: string;
  city: string;
  postal_code: string;
  latitude: number;
  longitude: number;
  timezone: string;
  isp: string;
  organization: string;
  asn: number;
  asn_organization: string;
}

export default function IPQueryWidget() {
  const [ip, setIp] = useState('');
  const [result, setResult] = useState<IPResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [queryMode, setQueryMode] = useState<'single' | 'batch'>('single');
  const [batchIps, setBatchIps] = useState('');
  const [batchResults, setBatchResults] = useState<any[]>([]);

  const validateIP = (ip: string): boolean => {
    const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    const ipv6Regex = /^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$/;
    return ipv4Regex.test(ip) || ipv6Regex.test(ip);
  };

  const handleSingleQuery = async () => {
    if (!ip.trim()) {
      setError('请输入IP地址');
      return;
    }

    if (!validateIP(ip.trim())) {
      setError('请输入有效的IP地址');
      return;
    }

    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch(`/api/ip/query?ip=${encodeURIComponent(ip.trim())}`);
      const data = await response.json();

      if (data.success) {
        setResult(data.data);
        toast.success('查询成功');
      } else {
        setError(data.message || '查询失败');
        toast.error(data.message || '查询失败');
      }
    } catch (err) {
      const errorMessage = '网络错误，请稍后重试';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBatchQuery = async () => {
    const ips = batchIps
      .split('\n')
      .map(ip => ip.trim())
      .filter(ip => ip.length > 0);

    if (ips.length === 0) {
      setError('请输入至少一个IP地址');
      return;
    }

    if (ips.length > 100) {
      setError('最多支持100个IP地址');
      return;
    }

    const invalidIps = ips.filter(ip => !validateIP(ip));
    if (invalidIps.length > 0) {
      setError(`以下IP地址格式无效: ${invalidIps.join(', ')}`);
      return;
    }

    setIsLoading(true);
    setError('');
    setBatchResults([]);

    try {
      const response = await fetch('/api/ip/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ips }),
      });

      const data = await response.json();

      if (data.success) {
        setBatchResults(data.data);
        toast.success(`批量查询完成，成功查询 ${data.summary.success} 个IP`);
      } else {
        setError(data.message || '批量查询失败');
        toast.error(data.message || '批量查询失败');
      }
    } catch (err) {
      const errorMessage = '网络错误，请稍后重试';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      toast.success('已复制到剪贴板');
    });
  };

  const getMyIP = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      setIp(data.ip);
      toast.success('已获取您的IP地址');
    } catch (err) {
      toast.error('获取IP地址失败');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8">
      {/* 查询模式切换 */}
      <div className="flex justify-center mb-8">
        <div className="bg-gray-100 dark:bg-slate-700 rounded-lg p-1">
          <button
            onClick={() => setQueryMode('single')}
            className={clsx(
              'px-6 py-2 rounded-md font-medium transition-all',
              queryMode === 'single'
                ? 'bg-white dark:bg-slate-600 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            )}
          >
            单个查询
          </button>
          <button
            onClick={() => setQueryMode('batch')}
            className={clsx(
              'px-6 py-2 rounded-md font-medium transition-all',
              queryMode === 'batch'
                ? 'bg-white dark:bg-slate-600 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
            )}
          >
            批量查询
          </button>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {queryMode === 'single' ? (
          <motion.div
            key="single"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            {/* 单个查询界面 */}
            <div className="space-y-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <input
                    type="text"
                    value={ip}
                    onChange={(e) => setIp(e.target.value)}
                    placeholder="输入IP地址，例如：8.8.8.8"
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
                    onKeyPress={(e) => e.key === 'Enter' && handleSingleQuery()}
                  />
                </div>
                <div className="flex gap-2">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={getMyIP}
                    disabled={isLoading}
                    className="px-4 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    我的IP
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleSingleQuery}
                    disabled={isLoading}
                    className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                  >
                    {isLoading ? (
                      <ArrowPathIcon className="h-5 w-5 animate-spin" />
                    ) : (
                      <MagnifyingGlassIcon className="h-5 w-5" />
                    )}
                    查询
                  </motion.button>
                </div>
              </div>

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400"
                >
                  {error}
                </motion.div>
              )}

              {result && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-gray-50 dark:bg-slate-700 rounded-lg p-6"
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      查询结果
                    </h3>
                    <button
                      onClick={() => copyToClipboard(JSON.stringify(result, null, 2))}
                      className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                    >
                      <ClipboardDocumentIcon className="h-5 w-5" />
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-3">
                      <div>
                        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">IP地址</span>
                        <p className="text-gray-900 dark:text-white font-mono">{result.ip}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">国家</span>
                        <p className="text-gray-900 dark:text-white">{result.country || '未知'}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">地区</span>
                        <p className="text-gray-900 dark:text-white">{result.region || '未知'}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">城市</span>
                        <p className="text-gray-900 dark:text-white">{result.city || '未知'}</p>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div>
                        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">ISP</span>
                        <p className="text-gray-900 dark:text-white">{result.isp || '未知'}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">时区</span>
                        <p className="text-gray-900 dark:text-white">{result.timezone || '未知'}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">坐标</span>
                        <p className="text-gray-900 dark:text-white">
                          {result.latitude && result.longitude 
                            ? `${result.latitude}, ${result.longitude}`
                            : '未知'
                          }
                        </p>
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">ASN</span>
                        <p className="text-gray-900 dark:text-white">
                          {result.asn ? `AS${result.asn}` : '未知'}
                        </p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="batch"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {/* 批量查询界面 */}
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  IP地址列表（每行一个，最多100个）
                </label>
                <textarea
                  value={batchIps}
                  onChange={(e) => setBatchIps(e.target.value)}
                  placeholder={`8.8.8.8\n114.114.114.114\n1.1.1.1`}
                  rows={8}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-slate-700 dark:text-white font-mono"
                />
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {batchIps.split('\n').filter(ip => ip.trim()).length} 个IP地址
                </span>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleBatchQuery}
                  disabled={isLoading}
                  className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                  {isLoading ? (
                    <ArrowPathIcon className="h-5 w-5 animate-spin" />
                  ) : (
                    <MagnifyingGlassIcon className="h-5 w-5" />
                  )}
                  批量查询
                </motion.button>
              </div>

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400"
                >
                  {error}
                </motion.div>
              )}

              {batchResults.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-gray-50 dark:bg-slate-700 rounded-lg p-6"
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      批量查询结果
                    </h3>
                    <button
                      onClick={() => copyToClipboard(JSON.stringify(batchResults, null, 2))}
                      className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                    >
                      <ClipboardDocumentIcon className="h-5 w-5" />
                    </button>
                  </div>
                  
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {batchResults.map((result, index) => (
                      <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-mono text-sm font-medium">{result.ip}</span>
                          <span className={clsx(
                            'px-2 py-1 rounded text-xs font-medium',
                            result.success 
                              ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                              : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                          )}>
                            {result.success ? '成功' : '失败'}
                          </span>
                        </div>
                        
                        {result.success ? (
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">国家:</span>
                              <span className="ml-1 text-gray-900 dark:text-white">{result.data.country || '未知'}</span>
                            </div>
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">城市:</span>
                              <span className="ml-1 text-gray-900 dark:text-white">{result.data.city || '未知'}</span>
                            </div>
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">ISP:</span>
                              <span className="ml-1 text-gray-900 dark:text-white">{result.data.isp || '未知'}</span>
                            </div>
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">时区:</span>
                              <span className="ml-1 text-gray-900 dark:text-white">{result.data.timezone || '未知'}</span>
                            </div>
                          </div>
                        ) : (
                          <p className="text-sm text-red-600 dark:text-red-400">{result.error}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
