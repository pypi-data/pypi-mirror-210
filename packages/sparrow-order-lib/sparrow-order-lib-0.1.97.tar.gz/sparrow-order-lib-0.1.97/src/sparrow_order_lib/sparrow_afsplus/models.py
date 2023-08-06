from django.db import models
from ..core.base_models import BaseModelTimeAndDeleted
from ..core.common_utils import get_uuid4_hex


from .constants import AfsplusStatus, AfsplusType, AfsplusTypeSub

from ..core.constants import ShippingMethod
# Create your models here.


class DistributeAfsplus(BaseModelTimeAndDeleted):
    ''' 发货单特殊标记 '''
    # id 主键
    id = models.CharField(max_length=100, primary_key=True,
                          default=get_uuid4_hex, editable=False)
    # order_id 订单ID
    order_id = models.PositiveIntegerField(
        'Order ID', blank=True, null=True, db_index=True)
    # order_number 订单编号
    order_number = models.CharField(
        'Order Number', max_length=64, blank=True, null=True, db_index=True)
    # distribute_id 发货单ID
    distribute_id = models.CharField(
        '新发货单 ID', max_length=100, blank=True, null=True)
    # distribute_number 发货单编号
    distribute_number = models.CharField(
        "Distribute Number", max_length=128, blank=True, null=True)

    # if_need_afsplus -- 是否需特售
    if_need_afsplus = models.BooleanField("是否需特售", default=False)
    # afsplus_status -- 是否已特售  -- 废弃
    afsplus_status = afsplus_status = models.CharField(
        '特殊售后单状态', max_length=32, db_index=True,
        null=True, choices=AfsplusStatus.AFSPLUS_STATUS_CHOICES
    )
    # 是否已特售
    if_done_afsplus = models.BooleanField("是否已特售", default=False, null=True)
    # 特殊售后ID
    afsplus_id = models.PositiveIntegerField('特殊售后单主键', db_index=True)
    # 特殊售后编号
    afsplus_number = models.CharField('特殊售后单单号', max_length=32, db_index=True)
    # 特殊售后类型
    afsplus_type = models.CharField(
        "特殊售后类型", max_length=64, db_index=True, null=True, choices=AfsplusType.CHOICES)
    # 特殊售后子类型
    afsplus_type_sub = models.CharField(
        "特殊售后子类型", max_length=64, db_index=True, null=True, choices=AfsplusTypeSub.CHOICES)

    # 2022.11 发货仓
    shipping_method_before = models.CharField("修改前配送方式", max_length=32, blank=True, null=True, choices=ShippingMethod.CHOICES)
    shipping_method_after = models.CharField("修改后配送方式", max_length=32, blank=True, null=True, choices=ShippingMethod.CHOICES)

    class Meta:
        app_label = 'sparrow_afsplus'

    @property
    def afsplus_type_show(self):
        ''' 展示给前端的售后类型 '''
        return some_obj_to_afsplus_type_show(self)


def some_obj_to_afsplus_type_show(obj):
    ''' 当某个对象有 afsplus_type  和 afsplus_type_sub 时, 可调用 '''
    type_en = AfsplusType.AFSPLUS_TYPE_DICT[obj.afsplus_type]
    type_sub_en = AfsplusTypeSub.AFSPLUS_SUB_TYPE_DICT.get(obj.afsplus_type_sub, "")
    type_show = type_en
    if type_sub_en:
        type_show = type_show + '-' + type_sub_en
    return type_show