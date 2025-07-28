<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Redis;
use Carbon\Carbon;

class DashboardController extends Controller
{
    /**
     * 显示仪表板
     */
    public function index()
    {
        $stats = $this->getDashboardStats();
        $charts = $this->getChartData();
        
        return view('dashboard.index', compact('stats', 'charts'));
    }

    /**
     * 获取仪表板统计数据
     */
    private function getDashboardStats()
    {
        // 今日统计
        $today = Carbon::today();
        $todayStats = DB::table('api_logs')
            ->whereDate('created_at', $today)
            ->selectRaw('
                COUNT(*) as total_requests,
                COUNT(CASE WHEN status_code = 200 THEN 1 END) as success_requests,
                COUNT(CASE WHEN status_code != 200 THEN 1 END) as error_requests,
                AVG(response_time) as avg_response_time
            ')
            ->first();

        // 昨日统计（用于计算增长率）
        $yesterday = Carbon::yesterday();
        $yesterdayStats = DB::table('api_logs')
            ->whereDate('created_at', $yesterday)
            ->selectRaw('COUNT(*) as total_requests')
            ->first();

        // 用户统计
        $userStats = DB::table('users')
            ->selectRaw('
                COUNT(*) as total_users,
                COUNT(CASE WHEN status = "active" THEN 1 END) as active_users,
                COUNT(CASE WHEN DATE(created_at) = CURDATE() THEN 1 END) as new_users_today
            ')
            ->first();

        // API密钥统计
        $apiKeyStats = DB::table('api_keys')
            ->selectRaw('
                COUNT(*) as total_keys,
                COUNT(CASE WHEN status = "active" THEN 1 END) as active_keys
            ')
            ->first();

        // 计算增长率
        $growthRate = 0;
        if ($yesterdayStats->total_requests > 0) {
            $growthRate = (($todayStats->total_requests - $yesterdayStats->total_requests) / $yesterdayStats->total_requests) * 100;
        }

        // 获取实时在线用户数（从Redis）
        $onlineUsers = $this->getOnlineUsersCount();

        // 获取当前QPS
        $currentQps = $this->getCurrentQps();

        return [
            'today_requests' => $todayStats->total_requests ?? 0,
            'success_rate' => $todayStats->total_requests > 0 ? 
                round(($todayStats->success_requests / $todayStats->total_requests) * 100, 2) : 0,
            'avg_response_time' => round($todayStats->avg_response_time ?? 0, 2),
            'growth_rate' => round($growthRate, 2),
            'total_users' => $userStats->total_users ?? 0,
            'active_users' => $userStats->active_users ?? 0,
            'new_users_today' => $userStats->new_users_today ?? 0,
            'total_api_keys' => $apiKeyStats->total_keys ?? 0,
            'active_api_keys' => $apiKeyStats->active_keys ?? 0,
            'online_users' => $onlineUsers,
            'current_qps' => $currentQps
        ];
    }

    /**
     * 获取图表数据
     */
    private function getChartData()
    {
        // 最近7天的请求量统计
        $requestsChart = DB::table('api_logs')
            ->selectRaw('DATE(created_at) as date, COUNT(*) as requests')
            ->where('created_at', '>=', Carbon::now()->subDays(7))
            ->groupBy('date')
            ->orderBy('date')
            ->get();

        // 最近24小时的QPS统计
        $qpsChart = DB::table('api_logs')
            ->selectRaw('HOUR(created_at) as hour, COUNT(*) as requests')
            ->where('created_at', '>=', Carbon::now()->subHours(24))
            ->groupBy('hour')
            ->orderBy('hour')
            ->get();

        // 状态码分布
        $statusChart = DB::table('api_logs')
            ->selectRaw('
                CASE 
                    WHEN status_code = 200 THEN "成功"
                    WHEN status_code >= 400 AND status_code < 500 THEN "客户端错误"
                    WHEN status_code >= 500 THEN "服务器错误"
                    ELSE "其他"
                END as status_type,
                COUNT(*) as count
            ')
            ->where('created_at', '>=', Carbon::now()->subDays(7))
            ->groupBy('status_type')
            ->get();

        // 热门查询IP
        $topIps = DB::table('api_logs')
            ->select('query_ip', DB::raw('COUNT(*) as count'))
            ->where('created_at', '>=', Carbon::now()->subDays(7))
            ->where('status_code', 200)
            ->groupBy('query_ip')
            ->orderByDesc('count')
            ->limit(10)
            ->get();

        return [
            'requests' => $requestsChart,
            'qps' => $qpsChart,
            'status' => $statusChart,
            'top_ips' => $topIps
        ];
    }

    /**
     * 获取在线用户数
     */
    private function getOnlineUsersCount()
    {
        try {
            // 从Redis获取在线用户数
            $onlineKeys = Redis::keys('online:user:*');
            return count($onlineKeys);
        } catch (\Exception $e) {
            return 0;
        }
    }

    /**
     * 获取当前QPS
     */
    private function getCurrentQps()
    {
        try {
            // 获取最近1分钟的请求数
            $requests = DB::table('api_logs')
                ->where('created_at', '>=', Carbon::now()->subMinute())
                ->count();
            
            return round($requests / 60, 2);
        } catch (\Exception $e) {
            return 0;
        }
    }

    /**
     * 获取实时统计数据（AJAX接口）
     */
    public function realTimeStats()
    {
        $stats = [
            'current_qps' => $this->getCurrentQps(),
            'online_users' => $this->getOnlineUsersCount(),
            'today_requests' => DB::table('api_logs')
                ->whereDate('created_at', Carbon::today())
                ->count(),
            'active_users' => DB::table('users')
                ->where('status', 'active')
                ->count()
        ];

        return response()->json($stats);
    }

    /**
     * 获取系统状态
     */
    public function systemStatus()
    {
        $status = [
            'database' => $this->checkDatabaseStatus(),
            'redis' => $this->checkRedisStatus(),
            'api_service' => $this->checkApiServiceStatus(),
            'disk_usage' => $this->getDiskUsage(),
            'memory_usage' => $this->getMemoryUsage()
        ];

        return response()->json($status);
    }

    /**
     * 检查数据库状态
     */
    private function checkDatabaseStatus()
    {
        try {
            DB::connection()->getPdo();
            return ['status' => 'healthy', 'message' => '数据库连接正常'];
        } catch (\Exception $e) {
            return ['status' => 'error', 'message' => '数据库连接失败: ' . $e->getMessage()];
        }
    }

    /**
     * 检查Redis状态
     */
    private function checkRedisStatus()
    {
        try {
            Redis::ping();
            return ['status' => 'healthy', 'message' => 'Redis连接正常'];
        } catch (\Exception $e) {
            return ['status' => 'error', 'message' => 'Redis连接失败: ' . $e->getMessage()];
        }
    }

    /**
     * 检查API服务状态
     */
    private function checkApiServiceStatus()
    {
        try {
            $response = \Http::timeout(5)->get(config('app.api_service_url') . '/health');
            if ($response->successful()) {
                return ['status' => 'healthy', 'message' => 'API服务正常'];
            } else {
                return ['status' => 'warning', 'message' => 'API服务响应异常'];
            }
        } catch (\Exception $e) {
            return ['status' => 'error', 'message' => 'API服务连接失败'];
        }
    }

    /**
     * 获取磁盘使用率
     */
    private function getDiskUsage()
    {
        $bytes = disk_free_space(".");
        $total = disk_total_space(".");
        $used = $total - $bytes;
        $percentage = round(($used / $total) * 100, 2);
        
        return [
            'used' => $this->formatBytes($used),
            'total' => $this->formatBytes($total),
            'percentage' => $percentage
        ];
    }

    /**
     * 获取内存使用率
     */
    private function getMemoryUsage()
    {
        $used = memory_get_usage(true);
        $peak = memory_get_peak_usage(true);
        
        return [
            'used' => $this->formatBytes($used),
            'peak' => $this->formatBytes($peak)
        ];
    }

    /**
     * 格式化字节数
     */
    private function formatBytes($bytes, $precision = 2)
    {
        $units = array('B', 'KB', 'MB', 'GB', 'TB');
        
        for ($i = 0; $bytes > 1024 && $i < count($units) - 1; $i++) {
            $bytes /= 1024;
        }
        
        return round($bytes, $precision) . ' ' . $units[$i];
    }
}
