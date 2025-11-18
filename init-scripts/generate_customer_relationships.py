#!/usr/bin/env python3
"""
生成客户关系数据库关系图
只包含客户管理相关的表
"""

import re
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

class CustomerSQLParser:
    """解析 SQL 文件，提取客户关系相关的表结构和关系"""
    
    # 只关注客户关系相关的表
    CUSTOMER_RELATED_TABLES = {
        # 核心客户表
        'customers', 'contacts', 'customer_sources', 'customer_channels', 'customer_documents',
        # 服务相关
        'service_records', 'service_types',
        # 订单和付款
        'orders', 'payment_stages', 'payments',
        # 关联表（需要显示关系）
        'users', 'products', 'organizations'
    }
    
    def __init__(self):
        self.tables: Dict[str, Dict] = {}  # 表名 -> {fields: [], fks: []}
        self.relationships: List[Tuple[str, str, str]] = []  # (from_table, to_table, fk_field)
        
    def parse_sql_file(self, file_path: Path):
        """解析 SQL 文件"""
        print(f"📖 解析文件: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 CREATE TABLE
        create_table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\((.*?)\);'
        
        # 解析 ALTER TABLE ADD CONSTRAINT（外键约束）
        alter_constraint_pattern = r'ALTER\s+TABLE\s+`?(\w+)`?\s+ADD\s+CONSTRAINT\s+\w+\s+FOREIGN\s+KEY\s+\(`?(\w+)`?\)\s+REFERENCES\s+`?(\w+)`?'
        for match in re.finditer(alter_constraint_pattern, content, re.IGNORECASE):
            table_name = match.group(1)
            fk_field = match.group(2)
            ref_table = match.group(3)
            
            # 只处理客户相关的表
            if table_name not in self.CUSTOMER_RELATED_TABLES and ref_table not in self.CUSTOMER_RELATED_TABLES:
                continue
            
            if table_name not in self.tables:
                self.tables[table_name] = {
                    'fields': [],
                    'fks': [],
                    'pks': []
                }
            
            # 确保字段在字段列表中
            if fk_field not in self.tables[table_name]['fields']:
                self.tables[table_name]['fields'].append(fk_field)
            
            # 检查是否已存在
            if not any(fk['field'] == fk_field and fk['ref_table'] == ref_table 
                      for fk in self.tables[table_name]['fks']):
                self.relationships.append((table_name, ref_table, fk_field))
                self.tables[table_name]['fks'].append({
                    'field': fk_field,
                    'ref_table': ref_table
                })
        
        # 查找所有 CREATE TABLE
        for match in re.finditer(create_table_pattern, content, re.DOTALL | re.IGNORECASE):
            table_name = match.group(1)
            table_body = match.group(2)
            
            # 只处理客户相关的表
            if table_name not in self.CUSTOMER_RELATED_TABLES:
                continue
            
            if table_name not in self.tables:
                self.tables[table_name] = {
                    'fields': [],
                    'fks': [],
                    'pks': []
                }
            
            # 解析字段
            self._parse_table_body(table_name, table_body)
        
        # 解析 ALTER TABLE ADD COLUMN
        alter_table_pattern = r'ALTER\s+TABLE\s+`?(\w+)`?\s+ADD\s+COLUMN\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s+([^,;]+)'
        for match in re.finditer(alter_table_pattern, content, re.IGNORECASE):
            table_name = match.group(1)
            field_name = match.group(2)
            field_def = match.group(3)
            
            # 只处理客户相关的表
            if table_name not in self.CUSTOMER_RELATED_TABLES:
                continue
            
            if table_name not in self.tables:
                self.tables[table_name] = {
                    'fields': [],
                    'fks': [],
                    'pks': []
                }
            
            # 检查是否是外键
            fk_match = re.search(r'FOREIGN\s+KEY\s+\(`?(\w+)`?\)\s+REFERENCES\s+`?(\w+)`?', field_def, re.IGNORECASE)
            if fk_match:
                ref_table = fk_match.group(2)
                # 只处理客户相关的表
                if ref_table in self.CUSTOMER_RELATED_TABLES:
                    self.relationships.append((table_name, ref_table, field_name))
                    self.tables[table_name]['fks'].append({
                        'field': field_name,
                        'ref_table': ref_table
                    })
            
            self.tables[table_name]['fields'].append(field_name)
        
        # 解析独立的 FOREIGN KEY 约束（在 CREATE TABLE 中）
        fk_pattern = r'FOREIGN\s+KEY\s+\(`?(\w+)`?\)\s+REFERENCES\s+`?(\w+)`?'
        for match in re.finditer(fk_pattern, content, re.IGNORECASE):
            # 查找这个外键所在的表
            pos = match.start()
            # 向前查找最近的 CREATE TABLE
            before = content[:pos]
            create_match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?', before, re.IGNORECASE)
            if create_match:
                table_name = create_match.group(1)
                fk_field = match.group(1)
                ref_table = match.group(2)
                
                # 只处理客户相关的表
                if table_name not in self.CUSTOMER_RELATED_TABLES and ref_table not in self.CUSTOMER_RELATED_TABLES:
                    continue
                
                if table_name not in self.tables:
                    self.tables[table_name] = {
                        'fields': [],
                        'fks': [],
                        'pks': []
                    }
                
                # 检查是否已存在
                if not any(fk['field'] == fk_field and fk['ref_table'] == ref_table 
                          for fk in self.tables[table_name]['fks']):
                    self.relationships.append((table_name, ref_table, fk_field))
                    self.tables[table_name]['fks'].append({
                        'field': fk_field,
                        'ref_table': ref_table
                    })
    
    def _parse_table_body(self, table_name: str, table_body: str):
        """解析表体，提取字段、主键和外键"""
        lines = [line.strip() for line in table_body.split('\n') if line.strip()]
        
        for line in lines:
            # 跳过注释
            if line.startswith('--'):
                continue
            
            # 解析主键
            pk_match = re.match(r'`?(\w+)`?\s+CHAR\(36\)\s+PRIMARY\s+KEY', line, re.IGNORECASE)
            if pk_match:
                pk_field = pk_match.group(1)
                if pk_field not in self.tables[table_name]['pks']:
                    self.tables[table_name]['pks'].append(pk_field)
                if pk_field not in self.tables[table_name]['fields']:
                    self.tables[table_name]['fields'].append(pk_field)
                continue
            
            # 解析字段定义
            field_match = re.match(r'`?(\w+)`?\s+', line)
            if field_match:
                field_name = field_match.group(1)
                if field_name not in self.tables[table_name]['fields']:
                    self.tables[table_name]['fields'].append(field_name)
                
                # 检查是否是外键字段（通过字段名模式）
                if field_name.endswith('_id') and field_name != 'id':
                    # 尝试推断关联表
                    potential_table = field_name.replace('_id', '').replace('_', '')
                    # 检查是否是已知的表
                    for known_table in self.CUSTOMER_RELATED_TABLES:
                        if known_table.startswith(potential_table) or potential_table in known_table:
                            if known_table != table_name:
                                # 检查是否已存在
                                if not any(fk['field'] == field_name and fk['ref_table'] == known_table 
                                          for fk in self.tables[table_name]['fks']):
                                    self.relationships.append((table_name, known_table, field_name))
                                    self.tables[table_name]['fks'].append({
                                        'field': field_name,
                                        'ref_table': known_table
                                    })
    
    def generate_dot(self) -> str:
        """生成 Graphviz DOT 格式"""
        lines = [
            'digraph CUSTOMER_RELATIONSHIPS {',
            '  rankdir=TB;',
            '  node [shape=record, style=filled];',
            '  ',
        ]
        
        # 按域分组表
        domains = {
            'Customer Core': ['customers', 'contacts', 'customer_sources', 'customer_channels', 'customer_documents'],
            'Service': ['service_records', 'service_types'],
            'Order & Payment': ['orders', 'payment_stages', 'payments'],
            'Related': ['users', 'products', 'organizations']
        }
        
        # 颜色方案
        colors = {
            'Customer Core': 'lightblue',
            'Service': 'lightgreen',
            'Order & Payment': 'lightyellow',
            'Related': 'lightgray'
        }
        
        # 添加表定义
        for domain, table_list in domains.items():
            lines.append(f'  // {domain} Domain')
            for table_name in table_list:
                if table_name in self.tables:
                    table = self.tables[table_name]
                    fields = table['fields'][:12]  # 限制字段数量
                    field_labels = []
                    
                    # 添加主键
                    for pk in table['pks']:
                        field_labels.append(f'{pk} (PK)')
                    
                    # 添加外键
                    for fk in table['fks']:
                        if fk['ref_table'] in self.CUSTOMER_RELATED_TABLES:
                            field_labels.append(f'{fk["field"]} (FK→{fk["ref_table"]})')
                    
                    # 添加其他重要字段
                    for field in fields:
                        if field not in [pk for pk in table['pks']] and \
                           field not in [fk['field'] for fk in table['fks']]:
                            # 只显示重要字段
                            if any(keyword in field.lower() for keyword in ['name', 'type', 'status', 'date', 'amount', 'code']):
                                field_labels.append(field)
                    
                    if len(table['fields']) > 12:
                        field_labels.append('...')
                    
                    # 使用 \l 分隔字段（Graphviz 格式）
                    separator = '\\l'
                    label = f'{table_name}|{separator.join(field_labels)}'
                    color = colors.get(domain, 'lightblue')
                    lines.append(f'  {table_name} [label="{label}", fillcolor="{color}"];')
            lines.append('')
        
        # 添加关系（只显示客户相关表之间的关系）
        lines.append('  // Relationships')
        for from_table, to_table, fk_field in self.relationships:
            if from_table in self.tables and to_table in self.tables:
                if from_table in self.CUSTOMER_RELATED_TABLES and to_table in self.CUSTOMER_RELATED_TABLES:
                    lines.append(f'  {from_table} -> {to_table} [label="{fk_field}"];')
        
        lines.append('}')
        
        return '\n'.join(lines)
    
    def generate_mermaid(self) -> str:
        """生成 Mermaid ER 图格式"""
        lines = [
            'erDiagram',
            ''
        ]
        
        # 按域分组表
        domains = {
            'Customer Core': ['customers', 'contacts', 'customer_sources', 'customer_channels', 'customer_documents'],
            'Service': ['service_records', 'service_types'],
            'Order & Payment': ['orders', 'payment_stages', 'payments'],
            'Related': ['users', 'products', 'organizations']
        }
        
        # 添加表定义
        for domain, table_list in domains.items():
            lines.append(f'    %% {domain} Domain')
            for table_name in sorted(table_list):
                if table_name in self.tables:
                    table = self.tables[table_name]
                    lines.append(f'    {table_name} {{')
                    
                    # 添加主键
                    for pk in table['pks']:
                        lines.append(f'        {pk} string PK')
                    
                    # 添加外键
                    for fk in table['fks']:
                        if fk['ref_table'] in self.CUSTOMER_RELATED_TABLES:
                            lines.append(f'        {fk["field"]} string FK')
                    
                    # 添加其他重要字段（限制数量）
                    other_fields = [f for f in table['fields'] 
                                  if f not in [pk for pk in table['pks']] 
                                  and f not in [fk['field'] for fk in table['fks']]
                                  and any(keyword in f.lower() for keyword in ['name', 'type', 'status', 'date', 'amount', 'code'])][:8]
                    for field in other_fields:
                        lines.append(f'        {field} string')
                    
                    if len(table['fields']) > len(table['pks']) + len(table['fks']) + 8:
                        lines.append('        ...')
                    
                    lines.append('    }')
                    lines.append('')
        
        # 添加关系
        lines.append('    %% Relationships')
        for from_table, to_table, fk_field in self.relationships:
            if from_table in self.tables and to_table in self.tables:
                if from_table in self.CUSTOMER_RELATED_TABLES and to_table in self.CUSTOMER_RELATED_TABLES:
                    lines.append(f'    {from_table} ||--o{{ {to_table} : "{fk_field}"')
        
        return '\n'.join(lines)


def main():
    """主函数"""
    script_dir = Path(__file__).parent
    sql_files = [
        script_dir / '01_schema_unified.sql',
        script_dir / '07_sync_database_fields.sql',
        script_dir / '08_service_records.sql',
        script_dir / '09_customer_documents_and_payment_stages.sql',
        script_dir / '10_enhance_customer_tables.sql'
    ]
    
    parser = CustomerSQLParser()
    
    # 解析所有 SQL 文件
    for sql_file in sql_files:
        if sql_file.exists():
            parser.parse_sql_file(sql_file)
        else:
            print(f"⚠️  文件不存在: {sql_file.name}")
    
    # 生成 DOT 格式
    dot_content = parser.generate_dot()
    dot_file = script_dir / 'CUSTOMER_RELATIONSHIPS.dot'
    with open(dot_file, 'w', encoding='utf-8') as f:
        f.write(dot_content)
    print(f"✅ 生成 DOT 文件: {dot_file}")
    
    # 生成 Mermaid 格式
    mermaid_content = parser.generate_mermaid()
    mmd_file = script_dir / 'CUSTOMER_RELATIONSHIPS.mmd'
    with open(mmd_file, 'w', encoding='utf-8') as f:
        f.write(mermaid_content)
    print(f"✅ 生成 Mermaid 文件: {mmd_file}")
    
    # 生成 PNG 图片（如果安装了 Graphviz）
    try:
        png_file = script_dir / 'CUSTOMER_RELATIONSHIPS.png'
        subprocess.run(
            ['dot', '-Tpng', '-o', str(png_file), str(dot_file)],
            check=True,
            capture_output=True
        )
        print(f"✅ 生成 PNG 图片: {png_file}")
    except FileNotFoundError:
        print("⚠️  Graphviz 未安装，跳过 PNG 生成")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  生成 PNG 失败: {e.stderr.decode()}")
    
    # 生成 SVG 图片
    try:
        svg_file = script_dir / 'CUSTOMER_RELATIONSHIPS.svg'
        subprocess.run(
            ['dot', '-Tsvg', '-o', str(svg_file), str(dot_file)],
            check=True,
            capture_output=True
        )
        print(f"✅ 生成 SVG 图片: {svg_file}")
    except FileNotFoundError:
        print("⚠️  Graphviz 未安装，跳过 SVG 生成")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  生成 SVG 失败: {e.stderr.decode()}")
    
    # 打印统计信息
    print(f"\n📊 统计信息:")
    print(f"  - 表数量: {len(parser.tables)}")
    print(f"  - 关系数量: {len(parser.relationships)}")
    print(f"\n📋 包含的表:")
    for table_name in sorted(parser.tables.keys()):
        print(f"  - {table_name}")


if __name__ == '__main__':
    main()

