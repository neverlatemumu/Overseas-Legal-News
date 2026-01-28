import os
import datetime
from tavily import TavilyClient
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 1. 配置从 GitHub Secrets 获取钥匙
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_news():
    # 模拟资深律师的搜索策略
    queries = [
        "2026 中国地方政府 支持企业出海 最新政策",
        "2026 国外对华贸易政策 监管动态 限制与机遇",
        "2026 中国企业出海 法律实务 文章 律师点评"
    ]
    
    combined_content = ""
    for q in queries:
        try:
            search_result = tavily.search(query=q, search_depth="advanced", max_results=4)
            for res in search_result['results']:
                combined_content += f"标题: {res['title']}\n内容: {res['content']}\n链接: {res['url']}\n\n"
        except Exception as e:
            print(f"搜索出错: {e}")
    return combined_content

def summarize_with_ai(raw_data):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    你是一名在出海业务非常资深的律师，同时也熟悉法律AI。
    请根据以下原始资讯，整理出10份最相关的内容，剔除重复，分为三类：
    1. 中国地方政策；2. 国外对华政策；3. 法律实务文章。
    每条需包含：标题、概括总结（律师视角）、原文链接。
    请以HTML格式输出，确保排版美观。
    
    原始资讯：
    {raw_data}
    """
    response = model.generate_content(prompt)
    return response.text

def send_email(content):
    sender = os.getenv("EMAIL_USER")
    receiver = os.getenv("RECEIVER_EMAIL")
    # 构造邮件
    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = Header("出海AI法律助手", 'utf-8')
    message['To'] = Header("资深律师", 'utf-8')
    message['Subject'] = Header(f"出海AI资讯 - {datetime.date.today()}", 'utf-8')

    try:
        # QQ邮箱专用配置
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(sender, os.getenv("EMAIL_PASS"))
            server.sendmail(sender, [receiver], message.as_string())
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")

if __name__ == "__main__":
    print("开始获取资讯...")
    raw_info = get_news()
    print("AI 正在总结...")
    summary = summarize_with_ai(raw_info)
    print("正在发送邮件...")
    send_email(summary)
