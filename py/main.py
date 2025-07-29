# 导入需要的库
import requests  # 用于发送HTTP请求，获取网页内容
import os        # 用于操作文件系统
from urllib.parse import urlparse  # 用于解析URL，提取文件名
import time      # 用于添加延时，避免请求过于频繁
import re        # 用于正则表达式处理
from bs4 import BeautifulSoup  # 用于解析HTML内容
from concurrent.futures import ThreadPoolExecutor, as_completed  # 用于多线程处理
import threading  # 用于线程锁

# 导入配置文件
from config import urls, THREAD_CONFIG  # 从config.py文件中导入urls列表和线程配置

# 全局变量用于统计
success_count = 0
total_count = 0
processed_count = 0
lock = threading.Lock()  # 线程锁，用于保护共享变量

def extract_novel_content(html_content):
    """
    从HTML内容中提取小说标题和正文内容
    
    参数说明：
    html_content: HTML网页内容
    
    返回值：
    tuple: (章节标题, 小说正文内容)
    """
    try:
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取章节标题
        title_element = soup.find('div', class_='m-title col-md-12')
        if title_element:
            title = title_element.find('h1').get_text().strip()
        else:
            title = "未知章节"
        
        # 提取小说内容
        content_div = soup.find('div', id='content')
        if not content_div:
            return title, "未找到小说内容"
        
        # 创建内容副本以避免修改原始内容
        content_copy = BeautifulSoup(str(content_div), 'html.parser')
        content_div = content_copy.find('div', id='content')
        
        # 移除不需要的元素
        # 1. 移除class="m-tpage"的div
        tpage_divs = content_div.find_all('div', class_='m-tpage')
        for div in tpage_divs:
            div.decompose()
        
        # 2. 移除网站声明段落
        for p in content_div.find_all('p'):
            if '斗破小说网' in p.get_text():
                p.decompose()
        
        # 3. 移除所有script标签
        for script in content_div.find_all('script'):
            script.decompose()
        
        # 4. 移除广告相关的div（通过特征识别）
        for div in content_div.find_all('div'):
            # 如果div中包含script标签或广告相关内容，移除
            if div.find('script') or 'chambulwacs' in str(div):
                div.decompose()
        
        # 5. 处理HTML注释 - 移除<!--adstart-->到<!--adend-->之间的内容
        html_str = str(content_div)
        # 使用正则表达式移除广告注释块
        import re
        html_str = re.sub(r'<!--adstart-->.*?<!--adend-->', '', html_str, flags=re.DOTALL)
        
        # 重新解析清理后的HTML
        cleaned_soup = BeautifulSoup(html_str, 'html.parser')
        content_div = cleaned_soup.find('div')
        
        # 获取纯文本内容
        text_content = content_div.get_text()
        
        # 清理文本内容
        # 替换HTML实体
        text_content = text_content.replace('&nbsp;', ' ')
        text_content = text_content.replace('\xa0', ' ')  # 处理非断行空格
        
        # 清理多余的空白字符
        lines = text_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # 只保留非空行
                # 将多个空格合并为一个
                line = re.sub(r'[ \t]+', ' ', line)
                cleaned_lines.append(line)
        
        # 重新组合文本，每段之间用双换行分隔
        text_content = '\n\n'.join(cleaned_lines)
        
        # 进一步清理：移除开头可能残留的无用文本
        text_content = text_content.strip()
        
        # 如果内容太短，可能提取失败
        if len(text_content) < 50:
            return title, f"内容提取可能不完整，原始长度: {len(text_content)}\n\n{text_content}"
        
        return title, text_content
        
    except Exception as e:
        print(f"解析HTML内容时出错: {str(e)}")
        return "解析失败", f"内容解析失败: {str(e)}"

def download_and_extract_novel(url_info, save_directory):
    """
    下载网页并提取小说内容，保存为文本文件（多线程版本）
    
    参数说明：
    url_info: tuple (index, url) - URL索引和地址
    save_directory: 保存文件的目录
    
    返回值：
    tuple: (bool, str, int) - (是否成功, 章节标题, URL索引)
    """
    index, url = url_info
    thread_id = threading.current_thread().name
    
    try:
        with lock:
            global processed_count
            processed_count += 1
            print(f"[线程{thread_id}] 正在处理第 {processed_count}/{total_count} 个URL (索引{index+1}): {url}")
        
        # 设置请求头，模拟浏览器访问，避免被网站拒绝
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 添加请求延时（如果配置了的话）
        if THREAD_CONFIG['request_delay'] > 0:
            time.sleep(THREAD_CONFIG['request_delay'])
        
        # 发送GET请求获取网页内容
        response = requests.get(url, headers=headers, timeout=THREAD_CONFIG['timeout'])
        
        # 检查请求是否成功（状态码200表示成功）
        if response.status_code == 200:
            # 自动检测网页编码，确保中文内容正确显示
            response.encoding = response.apparent_encoding
            
            # 提取小说内容
            title, content = extract_novel_content(response.text)
            
            # 生成安全的文件名（移除不安全字符）
            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', title) + '.txt'
            save_path = os.path.join(save_directory, safe_filename)
            
            # 如果文件已存在，添加序号避免覆盖
            counter = 1
            original_save_path = save_path
            while os.path.exists(save_path):
                name, ext = os.path.splitext(original_save_path)
                save_path = f"{name}_{counter}{ext}"
                counter += 1
            
            # 将小说内容写入文件
            with open(save_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            with lock:
                print(f"[线程{thread_id}] 成功保存章节: {title}")
            
            return True, title, index
            
        else:
            with lock:
                print(f"[线程{thread_id}] 请求失败，状态码: {response.status_code}, URL: {url}")
            return False, f"请求失败(状态码{response.status_code})", index
            
    except requests.exceptions.Timeout:
        with lock:
            print(f"[线程{thread_id}] 请求超时: {url}")
        return False, "请求超时", index
    except requests.exceptions.ConnectionError:
        with lock:
            print(f"[线程{thread_id}] 连接错误: {url}")
        return False, "连接错误", index
    except Exception as e:
        with lock:
            print(f"[线程{thread_id}] 发生未知错误: {str(e)}, URL: {url}")
        return False, f"未知错误: {str(e)}", index

def main(max_workers=None):
    """
    主函数：执行多线程下载任务
    
    参数说明：
    max_workers: 最大线程数，默认使用配置文件中的设置
    """
    global success_count, total_count, processed_count
    
    # 如果没有指定线程数，使用配置文件中的设置
    if max_workers is None:
        max_workers = THREAD_CONFIG['max_workers']
    
    print("=== 多线程小说内容提取程序开始运行 ===")
    print(f"共找到 {len(urls)} 个URL需要处理")
    print(f"使用 {max_workers} 个线程并发处理")
    print(f"请求延时: {THREAD_CONFIG['request_delay']} 秒")
    print(f"请求超时: {THREAD_CONFIG['timeout']} 秒")
    
    # 创建保存目录（如果不存在）
    save_directory = "novel_chapters"
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
        print(f"创建保存目录: {save_directory}")
    
    # 初始化统计变量
    success_count = 0
    total_count = len(urls)
    processed_count = 0
    
    # 准备URL列表，每个元素包含索引和URL
    url_list = [(i, url) for i, url in enumerate(urls)]
    
    # 记录开始时间
    start_time = time.time()
    
    # 使用线程池执行下载任务
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_url = {
            executor.submit(download_and_extract_novel, url_info, save_directory): url_info 
            for url_info in url_list
        }
        
        # 处理完成的任务
        for future in as_completed(future_to_url):
            url_info = future_to_url[future]
            try:
                success, title, index = future.result()
                if success:
                    with lock:
                        success_count += 1
            except Exception as exc:
                with lock:
                    print(f'URL索引 {url_info[0]+1} 生成异常: {exc}')
    
    # 计算耗时
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 显示最终结果
    print(f"\n=== 处理完成 ===")
    print(f"成功处理: {success_count}/{total_count} 个章节")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"平均每个章节: {elapsed_time/total_count:.2f} 秒")
    print(f"文件保存在: {os.path.abspath(save_directory)} 目录中")

def set_thread_count(count):
    """
    设置线程数
    
    参数说明：
    count: 线程数量
    """
    if count > 0 and count <= 20:  # 限制线程数在合理范围内
        THREAD_CONFIG['max_workers'] = count
        print(f"线程数已设置为: {count}")
    else:
        print("线程数必须在1-20之间")

# 程序入口点
if __name__ == "__main__":
    # 可以通过命令行参数设置线程数，或者直接修改MAX_WORKERS变量
    import sys
    
    if len(sys.argv) > 1:
        try:
            thread_count = int(sys.argv[1])
            set_thread_count(thread_count)
        except ValueError:
            print("线程数参数必须是整数，使用默认值5")
    
    # 当直接运行这个文件时，执行main函数
    main()
