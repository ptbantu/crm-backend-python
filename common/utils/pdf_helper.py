"""
PDF生成工具类 - 商机工作流专用
提供报价单、合同、发票PDF生成功能
"""
from typing import Optional, Dict, Any, List
from io import BytesIO
from datetime import datetime
from decimal import Decimal

from common.utils.logger import get_logger

logger = get_logger(__name__)

# 注意：这里使用占位符，实际需要安装PDF生成库（如reportlab、weasyprint、xhtml2pdf等）
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab未安装，PDF生成功能将使用占位符")


class OpportunityPDFHelper:
    """商机工作流PDF生成工具类"""
    
    @staticmethod
    def generate_quotation_pdf(
        quotation_data: Dict[str, Any],
        template_data: Optional[Dict[str, Any]] = None,
    ) -> BytesIO:
        """
        生成报价单PDF
        
        Args:
            quotation_data: 报价单数据
                - quotation_no: 报价单编号
                - opportunity_name: 商机名称
                - customer_name: 客户名称
                - customer_address: 客户地址
                - items: 报价单明细列表
                    - item_name: 项目名称
                    - quantity: 数量
                    - unit_price: 单价
                    - total_price: 总价
                - total_amount: 总金额
                - currency: 货币
                - valid_until: 有效期
                - created_at: 创建时间
            template_data: 模板数据（可选）
                - company_name: 公司名称
                - company_address: 公司地址
                - company_phone: 公司电话
                - company_email: 公司邮箱
        
        Returns:
            BytesIO: PDF文件数据流
        """
        if not REPORTLAB_AVAILABLE:
            logger.warning("reportlab未安装，返回占位符PDF")
            return BytesIO(b"PDF_PLACEHOLDER")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # 标题样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        
        # 添加标题
        story.append(Paragraph("报价单", title_style))
        story.append(Spacer(1, 20))
        
        # 公司信息
        company_info = template_data or {}
        company_text = f"""
        <b>公司名称：</b>{company_info.get('company_name', 'BANTU')}<br/>
        <b>地址：</b>{company_info.get('company_address', '')}<br/>
        <b>电话：</b>{company_info.get('company_phone', '')}<br/>
        <b>邮箱：</b>{company_info.get('company_email', '')}
        """
        story.append(Paragraph(company_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 报价单基本信息
        info_data = [
            ['报价单编号', quotation_data.get('quotation_no', '')],
            ['商机名称', quotation_data.get('opportunity_name', '')],
            ['客户名称', quotation_data.get('customer_name', '')],
            ['客户地址', quotation_data.get('customer_address', '')],
            ['货币', quotation_data.get('currency', 'CNY')],
            ['有效期至', quotation_data.get('valid_until', '')],
            ['创建时间', quotation_data.get('created_at', datetime.now().strftime('%Y-%m-%d'))],
        ]
        
        info_table = Table(info_data, colWidths=[80*mm, 110*mm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # 报价单明细
        items = quotation_data.get('items', [])
        if items:
            item_data = [['序号', '项目名称', '数量', '单价', '总价']]
            for idx, item in enumerate(items, 1):
                item_data.append([
                    str(idx),
                    item.get('item_name', ''),
                    str(item.get('quantity', 0)),
                    str(item.get('unit_price', 0)),
                    str(item.get('total_price', 0)),
                ])
            
            # 添加总计行
            total_amount = quotation_data.get('total_amount', 0)
            item_data.append(['', '', '', '总计', str(total_amount)])
            
            items_table = Table(item_data, colWidths=[20*mm, 80*mm, 30*mm, 40*mm, 40*mm])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (-1, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(items_table)
        
        # 生成PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_contract_pdf(
        contract_data: Dict[str, Any],
        template_data: Optional[Dict[str, Any]] = None,
    ) -> BytesIO:
        """
        生成合同PDF
        
        Args:
            contract_data: 合同数据
                - contract_no: 合同编号
                - opportunity_name: 商机名称
                - party_a_name: 甲方名称
                - party_a_address: 甲方地址
                - party_b_name: 乙方名称（公司名称）
                - party_b_address: 乙方地址
                - total_amount: 合同总金额
                - currency: 货币
                - effective_from: 生效日期
                - effective_to: 失效日期
                - signed_at: 签署日期
            template_data: 模板数据（可选）
        
        Returns:
            BytesIO: PDF文件数据流
        """
        if not REPORTLAB_AVAILABLE:
            logger.warning("reportlab未安装，返回占位符PDF")
            return BytesIO(b"PDF_PLACEHOLDER")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # 标题
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        story.append(Paragraph("合同", title_style))
        story.append(Spacer(1, 20))
        
        # 合同基本信息
        info_data = [
            ['合同编号', contract_data.get('contract_no', '')],
            ['商机名称', contract_data.get('opportunity_name', '')],
            ['甲方', contract_data.get('party_a_name', '')],
            ['甲方地址', contract_data.get('party_a_address', '')],
            ['乙方', contract_data.get('party_b_name', 'BANTU')],
            ['乙方地址', contract_data.get('party_b_address', '')],
            ['合同金额', f"{contract_data.get('total_amount', 0)} {contract_data.get('currency', 'CNY')}"],
            ['生效日期', contract_data.get('effective_from', '')],
            ['失效日期', contract_data.get('effective_to', '')],
            ['签署日期', contract_data.get('signed_at', '')],
        ]
        
        info_table = Table(info_data, colWidths=[80*mm, 110*mm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(info_table)
        
        # 生成PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_invoice_pdf(
        invoice_data: Dict[str, Any],
        template_data: Optional[Dict[str, Any]] = None,
    ) -> BytesIO:
        """
        生成发票PDF
        
        Args:
            invoice_data: 发票数据
                - invoice_no: 发票编号
                - customer_name: 客户名称
                - customer_bank_account: 客户银行账户
                - invoice_amount: 发票金额
                - tax_amount: 税额
                - currency: 货币
                - invoice_type: 发票类型
                - issued_at: 开具日期
            template_data: 模板数据（可选）
        
        Returns:
            BytesIO: PDF文件数据流
        """
        if not REPORTLAB_AVAILABLE:
            logger.warning("reportlab未安装，返回占位符PDF")
            return BytesIO(b"PDF_PLACEHOLDER")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # 标题
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        story.append(Paragraph("发票", title_style))
        story.append(Spacer(1, 20))
        
        # 发票信息
        info_data = [
            ['发票编号', invoice_data.get('invoice_no', '')],
            ['客户名称', invoice_data.get('customer_name', '')],
            ['客户银行账户', invoice_data.get('customer_bank_account', '')],
            ['发票金额', f"{invoice_data.get('invoice_amount', 0)} {invoice_data.get('currency', 'CNY')}"],
            ['税额', f"{invoice_data.get('tax_amount', 0)} {invoice_data.get('currency', 'CNY')}"],
            ['发票类型', invoice_data.get('invoice_type', '')],
            ['开具日期', invoice_data.get('issued_at', datetime.now().strftime('%Y-%m-%d'))],
        ]
        
        info_table = Table(info_data, colWidths=[80*mm, 110*mm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(info_table)
        
        # 生成PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
