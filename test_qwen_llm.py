#!/usr/bin/env python3
"""
测试 Qwen 3.5 LLM 在 LM Studio 本地端点上的回复能力
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LM Studio 配置（本地）
LLM_BASE_URL = "http://127.0.0.1:1234/v1"
LLM_API_KEY = "lm-studio"

def test_llm_simple():
    """测试简单文本对话"""
    print("\n=== 测试 1: 简单对话 ===")
    
    url = f"{LLM_BASE_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
    
    payload = {
        "model": "qwen/qwen3-vl-4b",
        "messages": [
            {
                "role": "system",
                "content": "你是命运石之门(steins gate)的牧濑红莉栖(kurisu),一个天才少女,性格傲娇,不喜欢被叫克里斯蒂娜"
            },
            {
                "role": "user",
                "content": "你好，请介绍一下自己"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 256
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"状态码: {response.status_code}")
        logger.info(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0]["message"]["content"]
            print(f"\n✅ LLM 回复成功：\n{message}")
            return True
        else:
            print(f"\n❌ 响应格式异常：{result}")
            return False
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False

def test_llm_stream():
    """测试流式回复"""
    print("\n=== 测试 2: 流式回复 ===")
    
    url = f"{LLM_BASE_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
    
    payload = {
        "model": "qwen/qwen3-vl-4b",
        "messages": [
            {
                "role": "system",
                "content": "你是命运石之门(steins gate)的牧濑红莉栖(kurisu),一个天才少女,性格傲娇,不喜欢被叫克里斯蒂娜"
            },
            {
                "role": "user",
                "content": "请用三句话解释什么是时间旅行"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 256,
        "stream": True
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        logger.info(f"状态码: {response.status_code}")
        print("\n✅ 流式回复内容：")
        
        full_content = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    try:
                        data = json.loads(line_str[6:])
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                print(content, end="", flush=True)
                                full_content += content
                    except json.JSONDecodeError:
                        pass
        
        print("\n")
        return bool(full_content)
        
    except Exception as e:
        print(f"\n❌ 流式请求失败: {e}")
        return False

def check_model_available():
    """检查模型是否可用"""
    print("\n=== 检查模型可用性 ===")
    
    url = f"{LLM_BASE_URL}/models"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if "data" in result:
            models = [m.get("id") for m in result["data"]]
            print(f"✅ 可用模型列表：")
            for model in models:
                print(f"  - {model}")
            
            if "qwen/qwen3-vl-4b" in models or any("qwen" in m.lower() for m in models):
                print(f"\n✅ 已找到 Qwen 模型")
                return True
            else:
                print(f"\n⚠️ 未找到 qwen/qwen3-vl-4b，请检查 LM Studio 中加载的模型")
                return False
        else:
            print(f"❌ 响应格式异常：{result}")
            return False
            
    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Qwen 3.5 LLM 本地回复测试")
    print(f"LM Studio 端点: {LLM_BASE_URL}")
    print("=" * 60)
    
    # 1. 检查模型
    if not check_model_available():
        print("\n请先在 LM Studio 中加载 qwen/qwen3-vl-4b 模型")
        exit(1)
    
    # 2. 测试简单对话
    result1 = test_llm_simple()
    
    # 3. 测试流式回复
    result2 = test_llm_stream()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结：")
    print(f"  简单对话: {'✅ 通过' if result1 else '❌ 失败'}")
    print(f"  流式回复: {'✅ 通过' if result2 else '❌ 失败'}")
    
    if result1 and result2:
        print("\n✅ LLM 完全可用！可以进行完整的对话了")
    else:
        print("\n❌ LLM 存在问题，需要检查配置或模型")
    print("=" * 60)
