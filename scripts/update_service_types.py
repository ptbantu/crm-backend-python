#!/usr/bin/env python3
"""
更新产品的服务类型ID
使用 Python 在应用层进行匹配，避免数据库排序规则冲突
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker, Session
from service_management.models.product import Product
from service_management.models.service_type import ServiceType
from service_management.config import settings


def update_product_service_types():
    """更新产品的服务类型ID"""
    # 创建数据库连接（使用同步连接，pymysql 驱动）
    database_url = settings.DATABASE_URL
    engine = create_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
    )
    
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as db:
        # 获取所有服务类型
        service_types = db.query(ServiceType).all()
        
        # 创建服务类型映射
        service_type_map = {st.code: st.id for st in service_types}
        
        print(f"找到 {len(service_types)} 个服务类型")
        for st in service_types:
            print(f"  - {st.code}: {st.name}")
        
        # 获取所有产品
        products = db.query(Product).all()
        
        print(f"\n找到 {len(products)} 个产品")
        
        # 更新规则
        update_count = 0
        
        for product in products:
            service_type_id = None
            
            # 落地签
            if (product.name and ('落地签' in product.name or 'B1' in product.name)) or \
               (product.code and product.code.startswith('B1')):
                service_type_id = service_type_map.get('LANDING_VISA')
            
            # 商务签
            elif (product.name and '商务签' in product.name) or \
                 (product.code and (product.code.startswith('C211') or product.code.startswith('C212'))):
                service_type_id = service_type_map.get('BUSINESS_VISA')
            
            # 工作签
            elif (product.name and ('工作签' in product.name or 'KITAS' in product.name)) or \
                 (product.code and product.code.startswith('C312')):
                service_type_id = service_type_map.get('WORK_VISA')
            
            # 家属签
            elif (product.name and '家属' in product.name) or \
                 (product.code and product.code.startswith('C317')):
                service_type_id = service_type_map.get('FAMILY_VISA')
            
            # 公司注册
            elif (product.name and ('公司' in product.name or '注册' in product.name)) or \
                 (product.code and (product.code.startswith('CPMA') or product.code.startswith('CPMDN') or product.code.startswith('VO_'))):
                service_type_id = service_type_map.get('COMPANY_REGISTRATION')
            
            # 许可证
            elif (product.name and '许可证' in product.name) or \
                 (product.code and (product.code.startswith('PSE') or product.code.startswith('API_'))):
                service_type_id = service_type_map.get('LICENSE')
            
            # 税务服务
            elif (product.name and ('税务' in product.name or '税' in product.name)) or \
                 (product.code and (product.code.startswith('Tax_') or product.code.startswith('LPKM') or product.code.startswith('NPWP'))):
                service_type_id = service_type_map.get('TAX_SERVICE')
            
            # 驾照
            elif (product.name and '驾照' in product.name) or \
                 (product.code and product.code.startswith('SIM_')):
                service_type_id = service_type_map.get('DRIVING_LICENSE')
            
            # 接送服务
            elif (product.name and '接送' in product.name) or \
                 (product.code and product.code.startswith('Jemput')):
                service_type_id = service_type_map.get('PICKUP_SERVICE')
            
            # 其他
            else:
                service_type_id = service_type_map.get('OTHER')
            
            # 更新产品
            if service_type_id and product.service_type_id != service_type_id:
                product.service_type_id = service_type_id
                update_count += 1
                print(f"  更新: {product.name} ({product.code}) -> {service_type_id}")
        
        # 提交更改
        db.commit()
        
        print(f"\n✅ 成功更新 {update_count} 个产品的服务类型ID")
        
        # 验证结果
        result = db.query(
            ServiceType.code,
            ServiceType.name,
            func.count(Product.id).label('count')
        ).outerjoin(
            Product, Product.service_type_id == ServiceType.id
        ).group_by(
            ServiceType.id, ServiceType.code, ServiceType.name
        ).order_by(
            ServiceType.display_order
        ).all()
        
        print("\n服务类型统计:")
        for row in result:
            print(f"  {row.code}: {row.name} - {row.count} 个产品")
    
    engine.dispose()


if __name__ == "__main__":
    update_product_service_types()

