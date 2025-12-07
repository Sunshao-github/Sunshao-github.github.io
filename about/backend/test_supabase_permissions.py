#!/usr/bin/env python3
"""
简单的Supabase权限测试脚本
"""

import supabase
import os

# Supabase配置
SUPABASE_URL = "https://lyokdigjpgzgloyhkmkm.supabase.co"
# 使用现有的匿名密钥进行测试
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx5b2tkaWdqcGd6Z2xveWhrbWttIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3MDc5NzksImV4cCI6MjA4MDI4Mzk3OX0.mGBP2vN7hXnWW8aN246zzwUUSXiqXyemR8kn-LMUI88"
BUCKET_NAME = "notes"

def test_supabase_connection():
    """测试Supabase连接"""
    print("=== 测试Supabase连接 ===")
    
    try:
        # 初始化Supabase客户端
        client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ 成功初始化Supabase客户端")
        return client
    except Exception as e:
        print(f"✗ 初始化Supabase客户端失败: {e}")
        return None

def test_bucket_access(client):
    """测试存储桶访问权限"""
    print("\n=== 测试存储桶访问 ===")
    
    try:
        # 尝试列出存储桶
        buckets = client.storage.list_buckets()
        print(f"✓ 成功列出存储桶: {len(buckets)} 个")
        
        # 检查目标存储桶是否存在
        target_bucket = None
        for bucket in buckets:
            print(f"  - 存储桶: {bucket.name} (公共: {bucket.public})")
            if bucket.name == BUCKET_NAME:
                target_bucket = bucket
        
        if not target_bucket:
            print(f"✗ 目标存储桶 '{BUCKET_NAME}' 不存在")
            return False
        else:
            print(f"✓ 找到目标存储桶: {target_bucket.name} (公共: {target_bucket.public})")
    except Exception as e:
        print(f"✗ 存储桶操作失败: {e}")
        return False
    
    return True

def test_database_access(client):
    """测试数据库访问权限"""
    print("\n=== 测试数据库访问 ===")
    
    try:
        # 尝试查询表列表
        tables = client.rpc("pg_tables").execute()
        print(f"✓ 成功查询表列表")
        
        # 检查目标表是否存在
        has_markdown_table = False
        for table in tables.data:
            if table["tablename"] == "markdown_files":
                has_markdown_table = True
                break
        
        if not has_markdown_table:
            print(f"✗ 目标表 'markdown_files' 不存在")
        else:
            print(f"✓ 找到目标表: markdown_files")
    except Exception as e:
        print(f"✗ 数据库操作失败: {e}")
        return False
    
    return True

def test_simple_upload(client):
    """测试简单文件上传"""
    print("\n=== 测试简单文件上传 ===")
    
    # 创建一个简单的测试文件
    test_content = "# 测试文件\n这是一个用于测试的文件"
    test_filename = "test_simple_upload.md"
    
    try:
        # 获取存储桶引用
        bucket = client.storage.from_(BUCKET_NAME)
        
        # 上传文件
        result = bucket.upload(
            path=test_filename,
            file=test_content.encode('utf-8'),
            file_options={"content-type": "text/markdown"}
        )
        
        print(f"✓ 文件上传成功: {test_filename}")
        
        # 尝试删除测试文件
        bucket.remove([test_filename])
        print(f"✓ 测试文件已删除")
        
        return True
    except Exception as e:
        print(f"✗ 文件上传失败: {e}")
        
        # 尝试获取更多错误信息
        if hasattr(e, 'status_code'):
            print(f"  状态码: {e.status_code}")
        if hasattr(e, 'message'):
            print(f"  错误消息: {e.message}")
        
        return False

def test_rls_policies(client):
    """测试RLS策略"""
    print("\n=== 测试RLS策略 ===")
    
    try:
        # 尝试查询数据（不应该返回任何结果，但不应该出错）
        response = client.table("markdown_files").select("*").limit(1).execute()
        print(f"✓ 查询表成功")
        print(f"  返回记录数: {len(response.data) if response.data else 0}")
        return True
    except Exception as e:
        print(f"✗ 查询表失败: {e}")
        return False

def main():
    """主函数"""
    print("=== Supabase权限测试 ===")
    print(f"URL: {SUPABASE_URL}")
    print(f"存储桶: {BUCKET_NAME}")
    print()
    
    # 1. 测试Supabase连接
    client = test_supabase_connection()
    if not client:
        print("\n✗ 连接测试失败，程序退出")
        return
    
    # 2. 测试存储桶访问
    if not test_bucket_access(client):
        print("\n✗ 存储桶访问测试失败")
    
    # 3. 测试数据库访问
    if not test_database_access(client):
        print("\n✗ 数据库访问测试失败")
    
    # 4. 测试RLS策略
    if not test_rls_policies(client):
        print("\n✗ RLS策略测试失败")
    
    # 5. 测试简单上传
    if not test_simple_upload(client):
        print("\n✗ 简单上传测试失败")
    
    print("\n=== 测试完成 ===")
    print("\n提示: 如果出现403 Unauthorized错误，可能是因为:")
    print("1. 存储桶或表的RLS策略限制了访问")
    print("2. 正在使用匿名密钥而不是服务角色密钥")
    print("3. 需要在Supabase控制台手动设置权限")

if __name__ == "__main__":
    main()
