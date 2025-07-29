const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// 导入配置
const { listurl } = require('./config.js');

// 创建保存目录
const saveDir = 'downloaded_pages';
if (!fs.existsSync(saveDir)) {
    fs.mkdirSync(saveDir, { recursive: true });
}

// 获取当前时间戳作为文件名
function getTimestamp() {
    return new Date().toISOString().replace(/[:.]/g, '-');
}

// 下载HTML页面
function downloadPage(url, filename) {
    return new Promise((resolve, reject) => {
        // 判断使用http还是https
        const client = url.startsWith('https://') ? https : http;
        
        const request = client.get(url, (response) => {
            if (response.statusCode !== 200) {
                reject(new Error(`请求失败，状态码: ${response.statusCode}`));
                return;
            }

            let data = '';
            
            // 设置编码
            response.setEncoding('utf8');
            
            response.on('data', (chunk) => {
                data += chunk;
            });
            
            response.on('end', () => {
                // 保存文件
                const filePath = path.join(saveDir, filename);
                fs.writeFile(filePath, data, 'utf8', (err) => {
                    if (err) {
                        reject(err);
                    } else {
                        console.log(`文件已保存: ${filePath}`);
                        resolve(filePath);
                    }
                });
            });
        });
        
        request.on('error', (err) => {
            reject(err);
        });
        
        // 设置超时
        request.setTimeout(10000, () => {
            request.abort();
            reject(new Error('请求超时'));
        });
    });
}

// 主函数
async function main() {
    try {
        console.log('开始下载页面...');
        console.log('目标URL:', listurl);
        
        const timestamp = getTimestamp();
        const filename = `page_${timestamp}.html`;
        
        const savedPath = await downloadPage(listurl, filename);
        console.log('下载完成！');
        console.log('保存路径:', savedPath);
        
    } catch (error) {
        console.error('下载失败:', error.message);
    }
}

// 运行主函数
if (require.main === module) {
    main();
}

module.exports = { downloadPage };
