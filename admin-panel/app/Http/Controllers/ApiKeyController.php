<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Str;
use Carbon\Carbon;
use Yajra\DataTables\Facades\DataTables;

class ApiKeyController extends Controller
{
    /**
     * 显示API密钥列表
     */
    public function index()
    {
        return view('api-keys.index');
    }

    /**
     * 获取API密钥数据表格
     */
    public function getData(Request $request)
    {
        $query = DB::table('api_keys as ak')
            ->join('users as u', 'ak.user_id', '=', 'u.id')
            ->select([
                'ak.id',
                'ak.key_name',
                'ak.api_key',
                'u.username',
                'u.email',
                'ak.rate_limit_per_minute',
                'ak.rate_limit_per_day',
                'ak.status',
                'ak.last_used_at',
                'ak.created_at'
            ]);

        return DataTables::of($query)
            ->addColumn('action', function ($row) {
                $actions = '<div class="btn-group" role="group">';
                $actions .= '<button type="button" class="btn btn-sm btn-info" onclick="viewApiKey(\'' . $row->id . '\')">查看</button>';
                $actions .= '<button type="button" class="btn btn-sm btn-warning" onclick="editApiKey(\'' . $row->id . '\')">编辑</button>';
                
                if ($row->status === 'active') {
                    $actions .= '<button type="button" class="btn btn-sm btn-secondary" onclick="toggleApiKey(\'' . $row->id . '\', \'disabled\')">禁用</button>';
                } else {
                    $actions .= '<button type="button" class="btn btn-sm btn-success" onclick="toggleApiKey(\'' . $row->id . '\', \'active\')">启用</button>';
                }
                
                $actions .= '<button type="button" class="btn btn-sm btn-danger" onclick="deleteApiKey(\'' . $row->id . '\')">删除</button>';
                $actions .= '</div>';
                
                return $actions;
            })
            ->addColumn('status_badge', function ($row) {
                $class = $row->status === 'active' ? 'success' : 'secondary';
                $text = $row->status === 'active' ? '启用' : '禁用';
                return '<span class="badge badge-' . $class . '">' . $text . '</span>';
            })
            ->addColumn('masked_key', function ($row) {
                return substr($row->api_key, 0, 8) . '...' . substr($row->api_key, -8);
            })
            ->addColumn('usage_stats', function ($row) {
                // 获取今日使用统计
                $todayUsage = DB::table('api_logs')
                    ->where('api_key_id', $row->id)
                    ->whereDate('created_at', Carbon::today())
                    ->count();
                
                return $todayUsage . ' / ' . $row->rate_limit_per_day;
            })
            ->editColumn('last_used_at', function ($row) {
                return $row->last_used_at ? Carbon::parse($row->last_used_at)->diffForHumans() : '从未使用';
            })
            ->editColumn('created_at', function ($row) {
                return Carbon::parse($row->created_at)->format('Y-m-d H:i:s');
            })
            ->rawColumns(['action', 'status_badge'])
            ->make(true);
    }

    /**
     * 显示创建API密钥表单
     */
    public function create()
    {
        $users = DB::table('users')
            ->where('status', 'active')
            ->select('id', 'username', 'email')
            ->get();
            
        return view('api-keys.create', compact('users'));
    }

    /**
     * 存储新的API密钥
     */
    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'user_id' => 'required|exists:users,id',
            'key_name' => 'required|string|max:64',
            'rate_limit_per_minute' => 'required|integer|min:1|max:1000',
            'rate_limit_per_day' => 'required|integer|min:1|max:100000',
            'allowed_origins' => 'nullable|string',
            'expires_at' => 'nullable|date|after:now'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => '验证失败',
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            // 生成API密钥
            $apiKey = 'ak_' . Str::random(32);
            $secretKey = 'sk_' . Str::random(48);

            // 处理允许的域名
            $allowedOrigins = null;
            if ($request->allowed_origins) {
                $origins = array_map('trim', explode(',', $request->allowed_origins));
                $allowedOrigins = json_encode($origins);
            }

            // 插入数据库
            $id = DB::table('api_keys')->insertGetId([
                'id' => Str::uuid(),
                'user_id' => $request->user_id,
                'key_name' => $request->key_name,
                'api_key' => $apiKey,
                'secret_key' => $secretKey,
                'allowed_origins' => $allowedOrigins,
                'rate_limit_per_minute' => $request->rate_limit_per_minute,
                'rate_limit_per_day' => $request->rate_limit_per_day,
                'expires_at' => $request->expires_at,
                'status' => 'active',
                'created_at' => now(),
                'updated_at' => now()
            ]);

            // 记录操作日志
            $this->logAdminOperation('create_api_key', '创建API密钥', 'api_key', $id, null, [
                'key_name' => $request->key_name,
                'user_id' => $request->user_id
            ]);

            return response()->json([
                'success' => true,
                'message' => 'API密钥创建成功',
                'data' => [
                    'api_key' => $apiKey,
                    'secret_key' => $secretKey
                ]
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => '创建失败: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * 显示API密钥详情
     */
    public function show($id)
    {
        $apiKey = DB::table('api_keys as ak')
            ->join('users as u', 'ak.user_id', '=', 'u.id')
            ->where('ak.id', $id)
            ->select([
                'ak.*',
                'u.username',
                'u.email'
            ])
            ->first();

        if (!$apiKey) {
            return response()->json([
                'success' => false,
                'message' => 'API密钥不存在'
            ], 404);
        }

        // 获取使用统计
        $stats = $this->getApiKeyStats($id);

        return response()->json([
            'success' => true,
            'data' => [
                'api_key' => $apiKey,
                'stats' => $stats
            ]
        ]);
    }

    /**
     * 显示编辑API密钥表单
     */
    public function edit($id)
    {
        $apiKey = DB::table('api_keys')->where('id', $id)->first();
        
        if (!$apiKey) {
            abort(404);
        }

        $users = DB::table('users')
            ->where('status', 'active')
            ->select('id', 'username', 'email')
            ->get();

        return view('api-keys.edit', compact('apiKey', 'users'));
    }

    /**
     * 更新API密钥
     */
    public function update(Request $request, $id)
    {
        $validator = Validator::make($request->all(), [
            'key_name' => 'required|string|max:64',
            'rate_limit_per_minute' => 'required|integer|min:1|max:1000',
            'rate_limit_per_day' => 'required|integer|min:1|max:100000',
            'allowed_origins' => 'nullable|string',
            'expires_at' => 'nullable|date|after:now',
            'status' => 'required|in:active,disabled'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => '验证失败',
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            // 获取原始数据
            $oldData = DB::table('api_keys')->where('id', $id)->first();
            
            if (!$oldData) {
                return response()->json([
                    'success' => false,
                    'message' => 'API密钥不存在'
                ], 404);
            }

            // 处理允许的域名
            $allowedOrigins = null;
            if ($request->allowed_origins) {
                $origins = array_map('trim', explode(',', $request->allowed_origins));
                $allowedOrigins = json_encode($origins);
            }

            // 更新数据
            DB::table('api_keys')
                ->where('id', $id)
                ->update([
                    'key_name' => $request->key_name,
                    'allowed_origins' => $allowedOrigins,
                    'rate_limit_per_minute' => $request->rate_limit_per_minute,
                    'rate_limit_per_day' => $request->rate_limit_per_day,
                    'expires_at' => $request->expires_at,
                    'status' => $request->status,
                    'updated_at' => now()
                ]);

            // 记录操作日志
            $this->logAdminOperation('update_api_key', '更新API密钥', 'api_key', $id, $oldData, $request->all());

            return response()->json([
                'success' => true,
                'message' => 'API密钥更新成功'
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => '更新失败: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * 切换API密钥状态
     */
    public function toggle(Request $request, $id)
    {
        $status = $request->input('status');
        
        if (!in_array($status, ['active', 'disabled'])) {
            return response()->json([
                'success' => false,
                'message' => '无效的状态值'
            ], 400);
        }

        try {
            $updated = DB::table('api_keys')
                ->where('id', $id)
                ->update([
                    'status' => $status,
                    'updated_at' => now()
                ]);

            if ($updated) {
                // 记录操作日志
                $this->logAdminOperation('toggle_api_key', '切换API密钥状态', 'api_key', $id, null, ['status' => $status]);

                return response()->json([
                    'success' => true,
                    'message' => 'API密钥状态更新成功'
                ]);
            } else {
                return response()->json([
                    'success' => false,
                    'message' => 'API密钥不存在'
                ], 404);
            }

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => '操作失败: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * 删除API密钥
     */
    public function destroy($id)
    {
        try {
            // 获取API密钥信息
            $apiKey = DB::table('api_keys')->where('id', $id)->first();
            
            if (!$apiKey) {
                return response()->json([
                    'success' => false,
                    'message' => 'API密钥不存在'
                ], 404);
            }

            // 删除API密钥
            DB::table('api_keys')->where('id', $id)->delete();

            // 记录操作日志
            $this->logAdminOperation('delete_api_key', '删除API密钥', 'api_key', $id, $apiKey, null);

            return response()->json([
                'success' => true,
                'message' => 'API密钥删除成功'
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => '删除失败: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * 获取API密钥统计信息
     */
    private function getApiKeyStats($apiKeyId)
    {
        // 今日使用量
        $todayUsage = DB::table('api_logs')
            ->where('api_key_id', $apiKeyId)
            ->whereDate('created_at', Carbon::today())
            ->count();

        // 本月使用量
        $monthUsage = DB::table('api_logs')
            ->where('api_key_id', $apiKeyId)
            ->whereMonth('created_at', Carbon::now()->month)
            ->whereYear('created_at', Carbon::now()->year)
            ->count();

        // 总使用量
        $totalUsage = DB::table('api_logs')
            ->where('api_key_id', $apiKeyId)
            ->count();

        // 成功率
        $successRate = DB::table('api_logs')
            ->where('api_key_id', $apiKeyId)
            ->selectRaw('
                COUNT(*) as total,
                COUNT(CASE WHEN status_code = 200 THEN 1 END) as success
            ')
            ->first();

        $successPercentage = $successRate->total > 0 ? 
            round(($successRate->success / $successRate->total) * 100, 2) : 0;

        return [
            'today_usage' => $todayUsage,
            'month_usage' => $monthUsage,
            'total_usage' => $totalUsage,
            'success_rate' => $successPercentage
        ];
    }

    /**
     * 记录管理员操作日志
     */
    private function logAdminOperation($operation, $description, $targetType, $targetId, $oldData, $newData)
    {
        DB::table('admin_operation_logs')->insert([
            'admin_id' => auth()->id(),
            'operation_type' => $operation,
            'operation_desc' => $description,
            'target_type' => $targetType,
            'target_id' => $targetId,
            'old_data' => $oldData ? json_encode($oldData) : null,
            'new_data' => $newData ? json_encode($newData) : null,
            'ip_address' => request()->ip(),
            'user_agent' => request()->userAgent(),
            'created_at' => now()
        ]);
    }
}
