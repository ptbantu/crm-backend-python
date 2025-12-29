"""
邮件通知工具类 - 商机工作流专用
提供阶段流转、审批、通知等邮件发送功能
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from common.email_client import (
    init_email,
    send_email,
    send_email_sync,
    get_smtp_config,
)
from common.utils.logger import get_logger

logger = get_logger(__name__)


class OpportunityEmailHelper:
    """商机工作流邮件通知工具类"""
    
    @staticmethod
    def initialize(
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: str = "BANTU CRM系统",
    ):
        """
        初始化邮件配置
        
        Args:
            host: SMTP服务器地址（从环境变量读取）
            port: SMTP端口（默认587）
            username: SMTP用户名（从环境变量读取）
            password: SMTP密码（从环境变量读取）
            from_email: 发件人邮箱（从环境变量读取）
            from_name: 发件人名称
        """
        import os
        
        try:
            init_email(
                host=host or os.getenv("SMTP_HOST", "smtp.gmail.com"),
                port=port or int(os.getenv("SMTP_PORT", "587")),
                username=username or os.getenv("SMTP_USERNAME"),
                password=password or os.getenv("SMTP_PASSWORD"),
                use_tls=True,
                from_email=from_email or os.getenv("SMTP_FROM_EMAIL"),
                from_name=from_name,
            )
            logger.info("邮件配置已初始化（商机工作流）")
        except Exception as e:
            logger.warning(f"邮件初始化失败（将使用占位符）: {e}")
    
    @staticmethod
    async def send_stage_transition_notification(
        opportunity_id: str,
        opportunity_name: str,
        from_stage: str,
        to_stage: str,
        to_emails: List[str],
        transition_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> bool:
        """
        发送阶段流转通知邮件
        
        Args:
            opportunity_id: 商机ID
            opportunity_name: 商机名称
            from_stage: 原阶段名称
            to_stage: 目标阶段名称
            to_emails: 收件人邮箱列表
            transition_by: 流转操作人（可选）
            notes: 备注（可选）
        
        Returns:
            bool: 是否发送成功
        """
        subject = f"【商机阶段流转】{opportunity_name} - {from_stage} → {to_stage}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">商机阶段流转通知</h2>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>商机名称：</strong>{opportunity_name}</p>
                    <p><strong>商机ID：</strong>{opportunity_id}</p>
                    <p><strong>阶段变更：</strong><span style="color: #e74c3c;">{from_stage}</span> → <span style="color: #27ae60;">{to_stage}</span></p>
                    {f'<p><strong>操作人：</strong>{transition_by}</p>' if transition_by else ''}
                    {f'<p><strong>备注：</strong>{notes}</p>' if notes else ''}
                    <p><strong>时间：</strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                <p style="color: #7f8c8d; font-size: 12px;">此邮件由BANTU CRM系统自动发送，请勿回复。</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
商机阶段流转通知

商机名称：{opportunity_name}
商机ID：{opportunity_id}
阶段变更：{from_stage} → {to_stage}
{f'操作人：{transition_by}' if transition_by else ''}
{f'备注：{notes}' if notes else ''}
时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

此邮件由BANTU CRM系统自动发送，请勿回复。
        """
        
        return await send_email(
            to_emails=to_emails,
            subject=subject,
            content=text_content,
            html_content=html_content,
        )
    
    @staticmethod
    async def send_approval_request_notification(
        opportunity_id: str,
        opportunity_name: str,
        stage_name: str,
        to_emails: List[str],
        requested_by: Optional[str] = None,
        approval_url: Optional[str] = None,
    ) -> bool:
        """
        发送审批请求通知邮件
        
        Args:
            opportunity_id: 商机ID
            opportunity_name: 商机名称
            stage_name: 阶段名称
            to_emails: 审批人邮箱列表
            requested_by: 请求人（可选）
            approval_url: 审批链接（可选）
        
        Returns:
            bool: 是否发送成功
        """
        subject = f"【待审批】{opportunity_name} - {stage_name}阶段需要审批"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #e74c3c;">待审批通知</h2>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <p><strong>商机名称：</strong>{opportunity_name}</p>
                    <p><strong>商机ID：</strong>{opportunity_id}</p>
                    <p><strong>阶段：</strong>{stage_name}</p>
                    {f'<p><strong>请求人：</strong>{requested_by}</p>' if requested_by else ''}
                    <p><strong>时间：</strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                {f'<p style="text-align: center; margin: 30px 0;"><a href="{approval_url}" style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">立即审批</a></p>' if approval_url else ''}
                
                <p style="color: #7f8c8d; font-size: 12px;">此邮件由BANTU CRM系统自动发送，请勿回复。</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
待审批通知

商机名称：{opportunity_name}
商机ID：{opportunity_id}
阶段：{stage_name}
{f'请求人：{requested_by}' if requested_by else ''}
时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{f'审批链接：{approval_url}' if approval_url else ''}

此邮件由BANTU CRM系统自动发送，请勿回复。
        """
        
        return await send_email(
            to_emails=to_emails,
            subject=subject,
            content=text_content,
            html_content=html_content,
        )
    
    @staticmethod
    async def send_quotation_notification(
        quotation_id: str,
        quotation_no: str,
        opportunity_name: str,
        customer_name: str,
        to_emails: List[str],
        quotation_url: Optional[str] = None,
    ) -> bool:
        """
        发送报价单通知邮件
        
        Args:
            quotation_id: 报价单ID
            quotation_no: 报价单编号
            opportunity_name: 商机名称
            customer_name: 客户名称
            to_emails: 收件人邮箱列表
            quotation_url: 报价单查看链接（可选）
        
        Returns:
            bool: 是否发送成功
        """
        subject = f"【报价单】{quotation_no} - {opportunity_name}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #3498db;">报价单通知</h2>
                
                <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>报价单编号：</strong>{quotation_no}</p>
                    <p><strong>商机名称：</strong>{opportunity_name}</p>
                    <p><strong>客户名称：</strong>{customer_name}</p>
                    <p><strong>时间：</strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                {f'<p style="text-align: center; margin: 30px 0;"><a href="{quotation_url}" style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">查看报价单</a></p>' if quotation_url else ''}
                
                <p style="color: #7f8c8d; font-size: 12px;">此邮件由BANTU CRM系统自动发送，请勿回复。</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
报价单通知

报价单编号：{quotation_no}
商机名称：{opportunity_name}
客户名称：{customer_name}
时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{f'查看链接：{quotation_url}' if quotation_url else ''}

此邮件由BANTU CRM系统自动发送，请勿回复。
        """
        
        return await send_email(
            to_emails=to_emails,
            subject=subject,
            content=text_content,
            html_content=html_content,
        )
    
    @staticmethod
    async def send_material_notification(
        contract_id: str,
        opportunity_name: str,
        material_name: str,
        to_emails: List[str],
        status: str = "submitted",
        notes: Optional[str] = None,
    ) -> bool:
        """
        发送办理资料通知邮件
        
        Args:
            contract_id: 合同ID
            opportunity_name: 商机名称
            material_name: 资料名称
            to_emails: 收件人邮箱列表
            status: 状态（submitted, approved, rejected）
            notes: 备注（可选）
        
        Returns:
            bool: 是否发送成功
        """
        status_map = {
            "submitted": ("已提交", "#3498db"),
            "approved": ("已审批通过", "#27ae60"),
            "rejected": ("已拒绝", "#e74c3c"),
        }
        status_text, status_color = status_map.get(status, ("未知", "#95a5a6"))
        
        subject = f"【办理资料】{material_name} - {status_text}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: {status_color};">办理资料通知</h2>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid {status_color};">
                    <p><strong>资料名称：</strong>{material_name}</p>
                    <p><strong>商机名称：</strong>{opportunity_name}</p>
                    <p><strong>合同ID：</strong>{contract_id}</p>
                    <p><strong>状态：</strong><span style="color: {status_color}; font-weight: bold;">{status_text}</span></p>
                    {f'<p><strong>备注：</strong>{notes}</p>' if notes else ''}
                    <p><strong>时间：</strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                <p style="color: #7f8c8d; font-size: 12px;">此邮件由BANTU CRM系统自动发送，请勿回复。</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
办理资料通知

资料名称：{material_name}
商机名称：{opportunity_name}
合同ID：{contract_id}
状态：{status_text}
{f'备注：{notes}' if notes else ''}
时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

此邮件由BANTU CRM系统自动发送，请勿回复。
        """
        
        return await send_email(
            to_emails=to_emails,
            subject=subject,
            content=text_content,
            html_content=html_content,
        )
    
    @staticmethod
    async def send_payment_notification(
        payment_id: str,
        payment_no: str,
        opportunity_name: str,
        amount: float,
        currency: str,
        to_emails: List[str],
        status: str = "pending",
    ) -> bool:
        """
        发送收款通知邮件
        
        Args:
            payment_id: 收款记录ID
            payment_no: 收款编号
            opportunity_name: 商机名称
            amount: 收款金额
            currency: 货币
            to_emails: 收件人邮箱列表
            status: 状态（pending, confirmed, rejected）
        
        Returns:
            bool: 是否发送成功
        """
        status_map = {
            "pending": ("待核对", "#f39c12"),
            "confirmed": ("已确认", "#27ae60"),
            "rejected": ("已拒绝", "#e74c3c"),
        }
        status_text, status_color = status_map.get(status, ("未知", "#95a5a6"))
        
        subject = f"【收款通知】{payment_no} - {amount} {currency}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: {status_color};">收款通知</h2>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid {status_color};">
                    <p><strong>收款编号：</strong>{payment_no}</p>
                    <p><strong>商机名称：</strong>{opportunity_name}</p>
                    <p><strong>收款金额：</strong><span style="font-size: 18px; font-weight: bold; color: {status_color};">{amount} {currency}</span></p>
                    <p><strong>状态：</strong><span style="color: {status_color}; font-weight: bold;">{status_text}</span></p>
                    <p><strong>时间：</strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                <p style="color: #7f8c8d; font-size: 12px;">此邮件由BANTU CRM系统自动发送，请勿回复。</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
收款通知

收款编号：{payment_no}
商机名称：{opportunity_name}
收款金额：{amount} {currency}
状态：{status_text}
时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

此邮件由BANTU CRM系统自动发送，请勿回复。
        """
        
        return await send_email(
            to_emails=to_emails,
            subject=subject,
            content=text_content,
            html_content=html_content,
        )
