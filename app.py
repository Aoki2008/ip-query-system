from flask import Flask, request, jsonify
import geoip2.database
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
app = Flask(__name__, static_folder=os.path.abspath('.'), static_url_path='/')

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/ip-lookup.html')
def ip_lookup_page():
    return app.send_static_file('ip-lookup.html')

@app.route('/help.html')
def help_page():
    return app.send_static_file('help.html')

@app.route('/about.html')
def about_page():
    return app.send_static_file('about.html')

@app.route('/query-ip')
def query_ip():
    ip = request.args.get('ip')
    logger.info(f'收到IP查询请求: {ip}')
    
    if not ip:
        logger.warning('IP参数为空')
        return jsonify({'error': 'IP参数不能为空'}), 400
    
    try:
        # 检查数据库文件是否存在
        import os
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GeoLite2-City.mmdb')
        if not os.path.exists(db_path):
            logger.error(f'数据库文件不存在: {os.path.abspath(db_path)}')
            return jsonify({'error': 'GeoLite2-City.mmdb数据库文件未找到，请从MaxMind官网下载'}), 500
        
        logger.info(f'使用数据库文件: {os.path.abspath(db_path)}')
        with geoip2.database.Reader(db_path) as reader:
            logger.info(f'查询IP: {ip}')
            response = reader.city(ip)
            logger.info(f'查询成功，IP信息: {response}')
            
            data = {
                'ip': ip,
                'country': response.country.name,
                'region': response.subdivisions.most_specific.name if response.subdivisions else '',
                'city': response.city.name,
                'postal': response.postal.code,
                'lat': response.location.latitude,
                'lon': response.location.longitude,
                'timezone': response.location.time_zone,
                'isp': response.traits.isp
            }
            logger.info(f'返回查询结果: {data}')
            return jsonify(data)
    except FileNotFoundError:
        return jsonify({'error': 'GeoLite2-City.mmdb数据库文件未找到，请从MaxMind官网下载'}), 500
    except Exception as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)