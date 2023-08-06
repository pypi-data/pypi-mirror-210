from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from core.base_models import BaseModelTimeAndDeleted
from .constants import InParcelEntityRelaDataSource, InParcelEntityRelaType, InParcelSource, InParcelStatus, InParcelEventConst, InParcelConnectCustomer, InParcelTaskType
import datetime
from ..sparrow_shipping.constants import express_pay_method

"""
收包裹
每个包裹一行，不能有重复的运单号
"""
class InParcel(BaseModelTimeAndDeleted):
    shipping_number = models.CharField("包裹单号", max_length=64, db_index=True, unique=True)
    express_code = models.CharField('快递公司代号', max_length=64, blank=True, null=True, db_index=True)
    express_name = models.CharField('快递公司名称', max_length=64, blank=True, null=True)
    status = models.CharField('包裹状态', max_length=32, blank=True, null=True, choices=InParcelStatus.INPARCEL_STATUS_CHOICES, db_index=True, default=InParcelStatus.INIT)
    postage_paymethod = models.CharField('快递费支付方式', max_length=32, blank=True, null=True, choices=express_pay_method.EXPRESS_PAY_METHOD_CHOISE, default=express_pay_method.SENDER_PAY)
    latest_task_id = models.PositiveIntegerField('最后一次操作的任务ID', null=True)
    opt_user_id = models.CharField('最后操作人ID', max_length=255, blank=True, null=True, db_index=True)
    opt_user_username = models.CharField('最后操作人手机号', max_length=15, blank=True, null=True, db_index=True)
    opt_user_displayname = models.CharField('最后操作人姓名', max_length=15, blank=True, null=True)
    inparcel_source = models.CharField("包裹来源", choices=InParcelSource.CHOICES, max_length=20, blank=True, null=True)
    actual_prodcnt = models.PositiveIntegerField('包裹中实际商品数量', null=True, default=0)
    total_rela_prodcnt = models.PositiveIntegerField('包裹关联商品数量', null=True, default=0)
    total_return_shop_prodcnt = models.PositiveIntegerField('包裹已归还专柜商品数量', null=True, default=0)
    total_shop_confirm_prodcnt = models.PositiveIntegerField('包裹专柜已确收商品数量', null=True, default=0)
    complete_time = models.DateTimeField('完成时间', null=True)
    complete_user_id = models.CharField('完成操作人ID', max_length=255, null=True, db_index=True)
    complete_user_username = models.CharField('完成操作人手机号', max_length=15, null=True, db_index=True)
    complete_user_displayname = models.CharField('完成操作人姓名', max_length=15, null=True)

    @property
    def inparcel_footprints(self):
        return InParcelFootPrint.objects.filter(inparcel_id=self.id)
    
    @property
    def refused_history(self):
        return InParcelRefused.objects.filter(inparcel_id=self.id)
    
    @property
    def notes(self):
        return InParcelNote.objects.filter(inparcel_id=self.id).order_by('-created_time')

    class Meta:
        ordering = ['-created_time']


"""
收包裹任务
按快递公司收包裹，选择快递公司后，创建一个任务。
拒收包裹时，包裹是一个一个操作的，也会为这个包裹创建一个任务
"""
class InParcelTask(BaseModelTimeAndDeleted):
    express_code = models.CharField('快递公司代号', max_length=64, blank=True, null=True, db_index=True)
    express_name = models.CharField('快递公司名称', max_length=64, blank=True, null=True)
    task_type = models.CharField('任务操作：确收/拒收', max_length=32, blank=True, null=True, choices=InParcelTaskType.CHOICES, default=InParcelTaskType.RECEIVE)
    opt_user_id = models.CharField('最后操作人ID', max_length=255, blank=True, null=True, db_index=True)
    opt_user_username = models.CharField('最后操作人手机号', max_length=15, blank=True, null=True, db_index=True)
    opt_user_displayname = models.CharField('最后操作人姓名', max_length=15, blank=True, null=True)

    class Meta:
        ordering = ['-created_time']


"""
收包裹跟任务的关联关系
"""
class InParcelTaskRela(BaseModelTimeAndDeleted):
    task_id = models.PositiveIntegerField('任务ID', blank=True, null=True)
    inparcel_id = models.PositiveIntegerField('包裹ID', blank=True, null=True)

"""
拒收包裹时的额外字段，肯定会关联一个包裹的
"""
class InParcelRefused(BaseModelTimeAndDeleted):
    inparcel_id = models.PositiveIntegerField('包裹ID', blank=True, null=True)
    refuse_reason = models.CharField('拒收理由', max_length=255, blank=True, null=True)
    connect_customer = models.CharField('联系顾客', max_length=255, blank=True, null=True, db_index=True, choices=InParcelConnectCustomer.CHOICES, default=InParcelConnectCustomer.NOT_CONNECT)
    opt_user_id = models.CharField('操作人ID', max_length=255, blank=True, null=True, db_index=True)
    opt_user_username = models.CharField('操作人手机号', max_length=15, blank=True, null=True, db_index=True)
    opt_user_displayname = models.CharField('操作人姓名', max_length=15, blank=True, null=True)
    
    @property
    def media_list(self):
        media = InParcelMedia.objects.filter(refused_id=self.id)
        return media
    
    @property
    def inparcel(self):
        return InParcel.objects.filter(id=self.inparcel_id).first()

"""
收包裹/拒收包裹的图片、视频资源
"""
class InParcelMedia(BaseModelTimeAndDeleted):
    inparcel_id = models.PositiveIntegerField('包裹ID', blank=True, null=True)
    media_url = models.ImageField("媒体路径", null=True, blank=True, max_length=255)
    media_type = models.CharField("媒体类型", null=True, blank=True, max_length=20)
    refused_id = models.PositiveIntegerField('拒收操作ID', blank=True, null=True)

"""
收包裹操作日志
"""
class InParcelFootPrint(BaseModelTimeAndDeleted):
    inparcel_id = models.PositiveIntegerField('InParcel ID', blank=True, null=True, db_index=True)
    task_id = models.PositiveIntegerField('Task ID', blank=True, null=True, db_index=True)
    shipping_number = models.CharField("运单号", max_length=64, db_index=True)
    # event 事件
    event = models.CharField('事件', max_length=32, blank=True, null=True, db_index=True)
    # event_name 事件名称
    event_name = models.CharField('事件名称', max_length=32, blank=True, null=True)
    # event_time 事件发生时间
    event_time = models.CharField('事件发生时间', max_length=128, blank=True, null=True, db_index=True)
    # opt_user_id 操作人ID
    opt_user_id = models.CharField('操作人ID', max_length=255, blank=True, null=True, db_index=True)
    # opt_user_username 操作人账号
    opt_user_username = models.CharField('操作人账号', max_length=15, help_text=u'申请人账号', blank=True, null=True, db_index=True)
    # opt_user_displayname 操作人姓名
    opt_user_displayname = models.CharField('操作人姓名', max_length=15, help_text=u'申请人姓名', blank=True, null=True)
    # from_status 开始状态
    from_status = models.CharField('起始状态', max_length=128, blank=True, null=True, db_index=True)
    # to_status 结束状态
    to_status = models.CharField('结果状态', max_length=128, blank=True, null=True, db_index=True)
    # message 消息
    message = models.CharField('信息', max_length=2048, blank=True, null=True)
    # message_level 消息级别
    message_level = models.PositiveIntegerField("Log Level", default=1, db_index=True)
    # message_detail 消息明细
    message_detail = models.CharField('开发看的信息', max_length=2048, blank=True, null=True)

    def __str__(self):
        return "日志【id={id}】: 发起人【{opt_user_displayname} {opt_user_username}】在时间【{event_time}】执行了事件【{event}】, \
            包裹【id={inparcel_id}; number={shipping_number}】从状态【{from_status}】变成了【{to_status}】, \
            具体信息为【level:{message_level}; msg={message}】; message_detail={message_detail}".\
            format(
                id=self.id, 
                opt_user_displayname=self.opt_user_displayname,
                opt_user_username=self.opt_user_username,
                event_time=self.event_time,
                event=self.event,
                inparcel_id=self.inparcel_id,
                shipping_number=self.shipping_number,
                from_status=self.from_status,
                to_status=self.to_status,
                message=self.message,
                message_level=self.message_level,
                message_detail=self.message_detail
            )
    class Meta:
        ordering = ['-created_time']

"""
收包裹关联

收包裹关联类型

# 关联发货单、换货单、退货单
发货单Distribute ID models.CharField(max_length=100, primary_key=True, default=get_uuid4_hex, editable=False)
发货单Distribute number models.CharField("Distribute number", max_length=40, db_index=True, unique=True, default=get_sparrow_distribute_number)

换货单行ExchangeLine id = models.CharField(max_length=100, primary_key=True, default=get_uuid4_hex, editable=False)
换货单行ExchangeLine exline_number = models.CharField("换货分单编号", max_length=64, db_index=True, unique=True)

售后单lineID 售后单line = 
"""
   
class InParcelEntityRela(BaseModelTimeAndDeleted):
    inparcel_id = models.PositiveIntegerField('包裹ID', blank=False, null=False, db_index=True)
    shipping_number = models.CharField("运单号", max_length=64, db_index=True)
    # 关联发货单、换货单、退货单
    rela_entity_type = models.CharField("实体类型", null=False, blank=False, max_length=255, db_index=True, choices=InParcelEntityRelaType.CHOICES)
    rela_entity_id = models.CharField("实体ID", null=False, blank=False, max_length=255, db_index=True)
    rela_entity_number = models.CharField("实体Number", null=True, blank=True, max_length=255, db_index=True)

    data_source = models.CharField('数据来源', blank=False, null=False, max_length=32, choices=InParcelEntityRelaDataSource.CHOICES, default=InParcelEntityRelaDataSource.RECEIVE_INPARCEL)
    # 关联商品数量 默认1
    rela_prodcnt = models.PositiveIntegerField('包裹关联商品数量', null=True, default=1)
    # 归还专柜数量 0 or 1
    return_shop_prodcnt = models.PositiveIntegerField('归还专柜数量', null=True, default=0)
    # 专柜确收数量 0 or 1
    shop_confirm_prodcnt = models.PositiveIntegerField('专柜确收数量', null=True, default=0)

class InParcelNote(BaseModelTimeAndDeleted):
    inparcel_id = models.PositiveIntegerField('包裹ID', blank=False, null=False, db_index=True)
    shipping_number = models.CharField("运单号", max_length=64, db_index=True)
    content = models.CharField("备注内容", max_length=256)
    note_user_id = models.CharField('操作人ID', max_length=255, blank=True, null=True, db_index=True)
    note_user_username = models.CharField('操作人账号', max_length=15, help_text=u'申请人账号', blank=True, null=True, db_index=True)
    note_user_displayname = models.CharField('操作人姓名', max_length=15, help_text=u'申请人姓名', blank=True, null=True)
    