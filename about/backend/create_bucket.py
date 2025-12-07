#!/usr/bin/env python3
"""
创建Supabase存储桶脚本
"""

import supabase

# Supabase配置
SUPABASE_URL = "https://lyokdigjpgzgloyhkmkm.supabase.co"
# 使用现有密钥
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx5b2tkaWdqcGd6Z2xveWhrbWttIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3MDc5NzksImV4cCI6MjA4MDI4Mzk3OX0.mGBP2vN7hXnWW8aN246zzwUUSXiqXyemR8kn-LMUI88"
BUCKET_NAME = "notes"

def create_bucket():
    """创建存储桶"""
    print("=== 创建Supabase存储桶 ===")
    print(f"URL: {SUPABASE_URL}")
    print(f"存储桶名称: {BUCKET_NAME}")
    print()
    
    # 初始化Supabase客户端
    try:
        client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ 成功初始化Supabase客户端")
    except Exception as e:
        print(f"✗ 初始化Supabase客户端失败: {e}")
        return False
    
    # 检查存储桶是否已存在
    try:
        buckets = client.storage.list_buckets()
        existing_bucket = None
        
        for bucket in buckets:
            print(f"✓ 现有存储桶: {bucket.name}")
            if bucket.name == BUCKET_NAME:
                existing_bucket = bucket
                break
        
        if existing_bucket:
            print(f"✓ 存储桶 '{BUCKET_NAME}' 已存在")
            return True
    except Exception as e:
        print(f"✗ 检查存储桶失败: {e}")
    
    # 创建存储桶
    try:
        print(f"\n创建存储桶 '{BUCKET_NAME}'...")
        # 使用正确的API参数格式
        result = client.storage.create_bucket(
            BUCKET_NAME, 
            {"public": True}
        )
        print(f"✓ 成功创建存储桶: {BUCKET_NAME}")
        
        # 列出创建后的存储桶进行验证
        buckets = client.storage.list_buckets()
        print(f"\n✓ 当前存储桶列表:")
        for bucket in buckets:
            print(f"  - {bucket.name} (公共: {bucket.public})")
        
        return True
    except Exception as e:
        print(f"✗ 创建存储桶失败: {e}")
        
        # 尝试获取更多错误信息
        if isinstance(e, dict) and 'message' in e:
            print(f"  错误详情: {e['message']}")
        
        return False

def main():
    """主函数"""
    if create_bucket():
        print("\n=== 创建存储桶成功 ===")
        print("下一步:")
        print("1. 登录到Supabase控制台")
        print(f"2. 导航到Storage -> Buckets -> {BUCKET_NAME}")
        print(f"3. 确保存储桶权限已正确设置")
        print(f"4. 尝试手动上传文件到 {BUCKET_NAME} 存储桶")
    else:
        print("\n=== 创建存储桶失败 ===")
        print("请按照以下步骤手动创建存储桶:")
        print("1. 登录到Supabase控制台")
        print("2. 导航到Storage -> Buckets")
        print(f"3. 点击'Create bucket'按钮")
        print(f"4. 输入存储桶名称: {BUCKET_NAME}")
        print("5. 选择'Public'访问级别")
        print("6. 点击'Create bucket'完成创建")

if __name__ == "__main__":
    main()
