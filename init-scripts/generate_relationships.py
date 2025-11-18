#!/usr/bin/env python3
"""
生成数据库关系图
从 init-scripts 目录中的 SQL 文件解析表结构并生成 Graphviz DOT 和 Mermaid 格式的关系图
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

class SQLParser:
    """解析 SQL 文件，提取表结构和关系"""
    
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
        alter_table_pattern = r'ALTER\s+TABLE\s+`?(\w+)`?\s+ADD\s+COLUMN\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s+([^,;]+)'
        
        # 解析 ALTER TABLE ADD CONSTRAINT（外键约束）
        alter_constraint_pattern = r'ALTER\s+TABLE\s+`?(\w+)`?\s+ADD\s+CONSTRAINT\s+\w+\s+FOREIGN\s+KEY\s+\(`?(\w+)`?\)\s+REFERENCES\s+`?(\w+)`?'
        for match in re.finditer(alter_constraint_pattern, content, re.IGNORECASE):
            table_name = match.group(1)
            fk_field = match.group(2)
            ref_table = match.group(3)
            
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
            
            if table_name not in self.tables:
                self.tables[table_name] = {
                    'fields': [],
                    'fks': [],
                    'pks': []
                }
            
            # 解析字段
            self._parse_table_body(table_name, table_body)
        
        # 解析 ALTER TABLE ADD COLUMN
        for match in re.finditer(alter_table_pattern, content, re.IGNORECASE):
            table_name = match.group(1)
            field_name = match.group(2)
            field_def = match.group(3)
            
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
                self.relationships.append((table_name, ref_table, field_name))
                self.tables[table_name]['fks'].append({
                    'field': field_name,
                    'ref_table': ref_table
                })
            
            self.tables[table_name]['fields'].append(field_name)
        
        # 解析 FOREIGN KEY 约束
        fk_pattern = r'FOREIGN\s+KEY\s+\(`?(\w+)`?\)\s+REFERENCES\s+`?(\w+)`?'
        for match in re.finditer(fk_pattern, content, re.IGNORECASE):
            fk_field = match.group(1)
            ref_table = match.group(2)
            
            # 找到这个外键属于哪个表
            # 向前查找最近的 CREATE TABLE
            pos = match.start()
            before = content[:pos]
            table_match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?', before, re.IGNORECASE)
            if table_match:
                table_name = table_match.group(1)
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
    
    def _parse_table_body(self, table_name: str, body: str):
        """解析表体，提取字段和约束"""
        lines = [line.strip() for line in body.split('\n') if line.strip()]
        
        for line in lines:
            # 跳过注释
            if line.startswith('--'):
                continue
            
            # 跳过 CONSTRAINT 和 FOREIGN KEY 约束行（单独处理）
            if re.match(r'^\s*(CONSTRAINT|FOREIGN\s+KEY|PRIMARY\s+KEY|UNIQUE)', line, re.IGNORECASE):
                # 解析独立的 FOREIGN KEY 约束
                fk_match = re.search(r'FOREIGN\s+KEY\s+\(`?(\w+)`?\)\s+REFERENCES\s+`?(\w+)`?', line, re.IGNORECASE)
                if fk_match:
                    fk_field = fk_match.group(1)
                    ref_table = fk_match.group(2)
                    if not any(fk['field'] == fk_field and fk['ref_table'] == ref_table 
                              for fk in self.tables[table_name]['fks']):
                        self.relationships.append((table_name, ref_table, fk_field))
                        self.tables[table_name]['fks'].append({
                            'field': fk_field,
                            'ref_table': ref_table
                        })
                continue
            
            # 解析字段定义（排除 CONSTRAINT 行）
            # 匹配: field_name TYPE [constraints]
            field_match = re.match(r'`?(\w+)`?\s+([^,]+?)(?:,|$)', line)
            if field_match:
                field_name = field_match.group(1).strip()
                field_def = field_match.group(2).strip()
                
                # 跳过关键字字段和 SQL 关键字
                skip_keywords = ['FOREIGN', 'KEY', 'CONSTRAINT', 'PRIMARY', 'UNIQUE', 
                               'INDEX', 'ALTER', 'ADD', 'CREATE', 'TABLE', 'IF', 'NOT', 
                               'EXISTS', 'ENGINE', 'DEFAULT', 'CHARSET', 'COLLATE', 'COMMENT']
                if field_name.upper() in skip_keywords:
                    continue
                
                # 检查主键
                if 'PRIMARY KEY' in field_def.upper() or (field_name == 'id' and 'PRIMARY' in field_def.upper()):
                    if field_name not in self.tables[table_name]['pks']:
                        self.tables[table_name]['pks'].append(field_name)
                
                # 检查内联外键（字段定义中的 REFERENCES）
                fk_match = re.search(r'REFERENCES\s+`?(\w+)`?', field_def, re.IGNORECASE)
                if fk_match:
                    ref_table = fk_match.group(1)
                    if not any(fk['field'] == field_name and fk['ref_table'] == ref_table 
                              for fk in self.tables[table_name]['fks']):
                        self.relationships.append((table_name, ref_table, field_name))
                        self.tables[table_name]['fks'].append({
                            'field': field_name,
                            'ref_table': ref_table
                        })
                
                if field_name not in self.tables[table_name]['fields']:
                    self.tables[table_name]['fields'].append(field_name)
    
    def generate_dot(self) -> str:
        """生成 Graphviz DOT 格式"""
        lines = [
            'digraph BANTU_CRM {',
            '  rankdir=LR;',
            '  node [shape=record, style=filled, fillcolor=lightblue];',
            '  ',
        ]
        
        # 按域分组表
        domains = {
            'Core': ['users', 'roles', 'user_roles', 'organizations', 'organization_employees'],
            'Product': ['service_types', 'product_categories', 'products', 'vendor_products', 'product_prices', 
                       'product_price_history', 'vendor_product_financials'],
            'Customer': ['customers', 'contacts', 'customer_sources', 'customer_channels', 'visa_records'],
            'Order': ['orders', 'order_statuses', 'order_assignments', 'order_stages', 
                     'deliverables', 'payments'],
            'Extension': ['vendor_extensions', 'agent_extensions']
        }
        
        # 添加表定义
        for domain, table_list in domains.items():
            lines.append(f'  // {domain} Domain')
            for table_name in table_list:
                if table_name in self.tables:
                    table = self.tables[table_name]
                    fields = table['fields'][:15]  # 限制字段数量
                    field_labels = []
                    
                    # 添加主键
                    for pk in table['pks']:
                        field_labels.append(f'{pk} (PK)')
                    
                    # 添加外键
                    for fk in table['fks']:
                        field_labels.append(f'{fk["field"]} (FK)')
                    
                    # 添加其他重要字段
                    for field in fields:
                        if field not in [pk for pk in table['pks']] and \
                           field not in [fk['field'] for fk in table['fks']]:
                            field_labels.append(field)
                    
                    if len(table['fields']) > 15:
                        field_labels.append('...')
                    
                    # 使用 \l 分隔字段（Graphviz 格式）
                    separator = '\\l'
                    label = f'{table_name}|{separator.join(field_labels)}'
                    lines.append(f'  {table_name} [label="{label}"];')
            lines.append('')
        
        # 添加关系
        lines.append('  // Relationships')
        for from_table, to_table, fk_field in self.relationships:
            if from_table in self.tables and to_table in self.tables:
                lines.append(f'  {from_table} -> {to_table} [label="{fk_field}"];')
        
        lines.append('}')
        
        return '\n'.join(lines)
    
    def generate_mermaid(self) -> str:
        """生成 Mermaid ER 图格式"""
        lines = [
            'erDiagram',
            ''
        ]
        
        # 添加表定义
        for table_name, table in sorted(self.tables.items()):
            lines.append(f'    {table_name} {{')
            
            # 添加主键
            for pk in table['pks']:
                lines.append(f'        {pk} string PK')
            
            # 添加外键
            for fk in table['fks']:
                lines.append(f'        {fk["field"]} string FK')
            
            # 添加其他重要字段（限制数量）
            other_fields = [f for f in table['fields'] 
                          if f not in [pk for pk in table['pks']] 
                          and f not in [fk['field'] for fk in table['fks']]][:10]
            for field in other_fields:
                lines.append(f'        {field} string')
            
            if len(table['fields']) > len(table['pks']) + len(table['fks']) + 10:
                lines.append('        ...')
            
            lines.append('    }')
            lines.append('')
        
        # 添加关系
        lines.append('    %% Relationships')
        for from_table, to_table, fk_field in self.relationships:
            if from_table in self.tables and to_table in self.tables:
                lines.append(f'    {from_table} ||--o{{ {to_table} : "{fk_field}"')
        
        return '\n'.join(lines)


def main():
    """主函数"""
    script_dir = Path(__file__).parent
    sql_files = [
        script_dir / '01_schema_unified.sql',
        script_dir / '05_product_service_enhancement.sql',
        script_dir / '08_service_types.sql'
    ]
    
    parser = SQLParser()
    
    # 解析所有 SQL 文件
    for sql_file in sql_files:
        if sql_file.exists():
            parser.parse_sql_file(sql_file)
        else:
            print(f"⚠️  文件不存在: {sql_file}")
    
    print(f"\n✅ 解析完成: 发现 {len(parser.tables)} 个表, {len(parser.relationships)} 个关系\n")
    
    # 生成 DOT 文件
    dot_content = parser.generate_dot()
    dot_file = script_dir / 'RELATIONSHIPS.dot'
    with open(dot_file, 'w', encoding='utf-8') as f:
        f.write(dot_content)
    print(f"✅ 生成 Graphviz DOT 文件: {dot_file}")
    
    # 生成 Mermaid 文件
    mermaid_content = parser.generate_mermaid()
    mermaid_file = script_dir / 'RELATIONSHIPS.mmd'
    with open(mermaid_file, 'w', encoding='utf-8') as f:
        f.write(mermaid_content)
    print(f"✅ 生成 Mermaid 文件: {mermaid_file}")
    
    # 尝试生成 SVG（如果 graphviz 可用）
    try:
        import subprocess
        svg_file = script_dir / 'RELATIONSHIPS.svg'
        result = subprocess.run(
            ['dot', '-Tsvg', str(dot_file), '-o', str(svg_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ 生成 SVG 文件: {svg_file}")
        else:
            print(f"⚠️  生成 SVG 失败: {result.stderr}")
            print("   提示: 安装 graphviz 后可以自动生成 SVG")
    except FileNotFoundError:
        print("⚠️  graphviz 未安装，跳过 SVG 生成")
        print("   提示: 安装 graphviz 后可以自动生成 SVG")
    except Exception as e:
        print(f"⚠️  生成 SVG 时出错: {e}")
    
    print("\n📊 关系图文件已生成:")
    print(f"   - {dot_file.name} (Graphviz DOT)")
    print(f"   - {mermaid_file.name} (Mermaid)")
    print(f"\n💡 使用方法:")
    print(f"   - 查看 SVG: 直接打开 {dot_file.stem}.svg (如果已生成)")
    print(f"   - 生成 SVG: dot -Tsvg {dot_file.name} -o RELATIONSHIPS.svg")
    print(f"   - 生成 PNG: dot -Tpng {dot_file.name} -o RELATIONSHIPS.png")
    print(f"   - Mermaid: 可以在支持 Mermaid 的 Markdown 编辑器中查看")


if __name__ == '__main__':
    main()

