from ..sparrow_distribute.models import Distributeline, DistributelineEcard, ExpressRela
from ..sparrow_orders.constants import DeliverTimeType, PayMethod
from ..sparrow_orders.models import ShippingAddress
from ..sparrow_shipping.models import NewExpressOrder

from .serializers import ShippingAddressSerializer, NewExpressOrderSerializer, \
    DistributelineSerializer


def decorator_dislines_in_distribute_list(serializer_data, serializer_cls=DistributelineSerializer):
    '''
    发货单行
    '''
    dis_ids = [distribute_dict['id'] for distribute_dict in serializer_data]
    disline_obj_list = Distributeline.objects.filter(distribute_id__in=dis_ids)

    disline_ids = [disline_obj.id for disline_obj in disline_obj_list]

    disline_ecard_list = DistributelineEcard.objects.filter(distribute_line_id__in=disline_ids)
    disline_id_2_disline_ecard_dict = {disline_ecard.distribute_line_id: disline_ecard for disline_ecard in
                                       disline_ecard_list}
    dis_id2lines_dict = {}
    for disline_obj in disline_obj_list:
        if disline_obj.id in disline_id_2_disline_ecard_dict:
            disline_obj.ecard_info = disline_id_2_disline_ecard_dict[disline_obj.id]
        else:
            disline_obj.ecard_info = None
        distribute_id = disline_obj.distribute_id
        if distribute_id not in dis_id2lines_dict:
            dis_id2lines_dict[distribute_id] = []
        dis_id2lines_dict[distribute_id].append(disline_obj)
    for distribute_dict in serializer_data:
        distribute_id = distribute_dict['id']
        disline_obj_list = dis_id2lines_dict.get(distribute_id, None)
        if not disline_obj_list:
            distribute_dict.update({'distributelines': []})
        else:
            disline_serializer = serializer_cls(instance=disline_obj_list, many=True, required=False)
            disline_serializer_data = disline_serializer.data
            distribute_dict.update({'distributelines': disline_serializer_data})


def decorator_expressorder_in_distribute_list(serializer_data, serializer_cls=NewExpressOrderSerializer):
    '''
    运单信息
    '''
    distribute_ids = [distribute_dict['id'] for distribute_dict in serializer_data]
    rela_obj_list = ExpressRela.objects.filter(distribute_id__in=distribute_ids)
    rela_obj_dict = {str(rela_obj.distribute_id): str(rela_obj.newexpressorder_id) for rela_obj in rela_obj_list}

    expressorder_id_list = [rela_obj.newexpressorder_id for rela_obj in rela_obj_list]
    expressorder_obj_list = NewExpressOrder.objects.filter(id__in=expressorder_id_list)
    expressorder_dict = {str(expressorder_obj.id): expressorder_obj for expressorder_obj in expressorder_obj_list}

    distribute_express_info_dict = {}
    for distribute_id in distribute_ids:
        distribute_id_key = str(distribute_id)
        if distribute_id_key not in rela_obj_dict:
            distribute_express_info_dict[distribute_id_key] = None
        else:
            newexpressorder_id = rela_obj_dict[distribute_id_key]
            newexpressorder_id_key = str(newexpressorder_id)
            if newexpressorder_id_key not in expressorder_dict:
                distribute_express_info_dict[distribute_id_key] = None
            else:
                expressorder_obj = expressorder_dict[newexpressorder_id_key]
                expressorder_obj_serializer = serializer_cls(instance=expressorder_obj, required=False)
                distribute_express_info_dict[distribute_id_key] = expressorder_obj_serializer.data

    for distribute_dict in serializer_data:
        distribute_id = distribute_dict['id']
        expressorder_obj_data = distribute_express_info_dict[distribute_id]
        distribute_dict.update({"express_order": expressorder_obj_data})


def decorator_shippingaddr_in_distribute_list(serializer_data, serializer_cls=ShippingAddressSerializer):
    '''
    快递地址
    '''
    shipping_address_id_list = [distribute_dict['shipping_address_id'] for distribute_dict in serializer_data]
    shipaddr_obj_list = ShippingAddress.objects.filter(id__in=shipping_address_id_list)
    shipaddrid_2_obj_dict = {str(shipaddr_obj.id): shipaddr_obj for shipaddr_obj in shipaddr_obj_list}
    for distribute_dict in serializer_data:
        shipping_address_id = distribute_dict['shipping_address_id']
        shipaddr_obj = shipaddrid_2_obj_dict.get(str(shipping_address_id), None)
        if not shipaddr_obj:
            distribute_dict.update({'shipping_address': None})
        else:
            shipaddr_obj_serializer = serializer_cls(instance=shipaddr_obj, required=False)
            distribute_dict.update({'shipping_address': shipaddr_obj_serializer.data})


def decorator_deliver_time_str_in_distribute_list(serializer_data):
    """ 对于分阶段支付订单, 对每个发货单行添加发货时间 """

    for distribute_data in serializer_data:
        if 'distributelines' not in distribute_data:
            continue

        if distribute_data["pay_method"] != PayMethod.TWICE:
            continue

        disline_datas = distribute_data['distributelines']

        for disline_data in disline_datas:

            deliver_time = disline_data.get('deliver_time')
            deliver_time_type = disline_data.get('deliver_time_type')
            deliver_relative_time = disline_data.get('deliver_relative_time')

            deliver_time_str = ""

            if deliver_time:  # 已支付尾款或固定发货时间
                deliver_time_show = str(deliver_time)
                deliver_time_show = deliver_time_show[0:10]
                deliver_time_str = "预计{}前发货".format(str(deliver_time_show))
            elif deliver_relative_time and deliver_time_type == DeliverTimeType.PAY_RELATIVE_TIME:  # 相对发货时间
                deliver_time_str = "付尾款后{}日内发货".format(int(float((deliver_relative_time))))

            disline_data["deliver_time_str"] = deliver_time_str


def decorator_product_group_in_distribute_list(serializer_data):
    '''
    商品库存状态
    '''

    # 遍历每一个订单
    for distribute_dict in serializer_data:

        if "distributelines" not in distribute_dict:
            continue
        distributelines = distribute_dict['distributelines']

        # 遍历每一个订单行
        productlines = {}
        for distributeline in distributelines:
            if "product_id" not in distributeline or not distributeline["product_id"]:
                continue

            if distributeline["line_id"] in productlines:
                # 旧
                _prod = productlines[distributeline["line_id"]]

                _prod["quantity"] = _prod["quantity"] + distributeline["quantity"]
                _prod["lines"].append(distributeline)
            else:
                # 新
                productlines[distributeline["line_id"]] = {
                    "product_id": distributeline["product_id"],
                    "quantity": distributeline["quantity"],
                    "title": distributeline["title"],
                    "is_gift": distributeline["is_gift"],
                    "sku_attr": distributeline["sku_attr"],
                    "shop_sku": distributeline["shop_sku"],
                    "lines": [distributeline],
                    "shop_income_price": distributeline["shop_income_price"],
                }

        # 不再返回
        distribute_dict['distributelines'] = None
        distribute_dict["products"] = productlines


def lanyue_valid_distributedetail(serializer_data, shop_id=0):
    """ 避免销售在地址栏直接输入其他专柜的发货单 """

    for distribute_data in serializer_data:
        if 'distributelines' not in distribute_data:
            continue

        disline_datas = distribute_data['distributelines']
        for disline_data in disline_datas:
            if disline_data["shop_id"] != shop_id:
                return False

    return True