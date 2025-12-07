#!/usr/bin/env python3
"""
使用Supabase客户端向markdown_files表添加sort_order字段
"""

import supabase
import os

# 初始化Supabase客户端
SUPABASE_URL = "https://lyokdigjpgzgloyhkmkm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx5b2tkaWdqcGd6Z2xveWhrbWttIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3MDc5NzksImV4cCI6MjA4MDI4Mzk3OX0.mGBP2vN7hXnWW8aN246zzwUUSXiqXyemR8kn-LMUI88"
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

def add_sort_order_column():
    """向markdown_files表添加sort_order字段"""
    try:
        # 执行SQL命令添加sort_order字段
        sql = "ALTER TABLE public.markdown_files ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0;"
        response = supabase_client.rpc("_rpc_admin_execute_sql", {"sql": sql}).execute()
        print("添加sort_order字段成功！")
        print(f"响应: {response}")
    except Exception as e:
        print(f"添加sort_order字段失败: {e}")
        # 尝试使用supabase-py的其他方式执行SQL
        try:
            # 注意：这需要Supabase项目启用了POSTGRES_REST_API的RPC功能
            # 或者需要在Supabase控制台手动执行SQL
            print("\n请在Supabase控制台手动执行以下SQL语句:")
            print(sql)
        except Exception as e2:
            print(f"获取SQL语句失败: {e2}")

if __name__ == "__main__":
    add_sort_order_column()
