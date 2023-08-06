from rest_framework import serializers
from ..sparrow_aftersale.models import Afs

from .models import Distribute, Distributeline,  FootPrint,DistributelineEcard, ExpressRelaBack
from ..sparrow_orders.constants import OrderTypes
from ..sparrow_orders.models import ShippingAddress
from ..sparrow_shipping.models import NewExpressOrder


class ShippingAddressSerializer(serializers.ModelSerializer):
    '''收件地址，修改地址的时候也用这个'''

    class Meta:
        model = ShippingAddress
        fields = '__all__'

class NewExpressOrderSerializer(serializers.ModelSerializer):

    pay_card_number_name = serializers.CharField(max_length=256,required=False)

    class Meta:
        model = NewExpressOrder
        fields = '__all__'

class LanyueLightDistributeSerializer(serializers.ModelSerializer):
    '''整个轻量发货单，包括发货单表头和表体'''
    # distributelines = DistributelineSerializer(many=True, required=False)
    # available_event_list = serializers.ListField(required=False, child=serializers.CharField(required=False))
    # shipping_address = ShippingAddressSerializer(required=False, read_only=True)
    # express_order = NewExpressOrderSerializer(required=False, read_only=True)
    # cusservice_footprints = FootPrintSerializer(many=True, required=False)
    # ex_status_for_b = serializers.IntegerField(required=False)
    class Meta:
        model = Distribute
        fields = '__all__'

class DistributelineEcardSerializer(serializers.ModelSerializer):
    '''发货单Line E卡信息'''
    class Meta:
        model = DistributelineEcard
        fields = '__all__'

class DistributelineSerializer(serializers.ModelSerializer):
    '''发货单表体'''

    title = serializers.SerializerMethodField()
    afs_version = serializers.SerializerMethodField()
    ecard_info = DistributelineEcardSerializer()

    def get_title(self, obj):
        title = obj.title
        order_type = obj.order_type
        if order_type == OrderTypes.POINTS_MALL:  # 积分商城
            title = "【积分商城】" + title
        return title

    def get_afs_version(self, obj):
        if obj.aftersale_id is not None:
            afs = Afs.objects.filter(id=obj.aftersale_id).first()
            if afs:
                return afs.afs_version
        return None

    class Meta:
        model = Distributeline
        fields = '__all__'


class LanyueWholeDistributeSerializer(serializers.ModelSerializer):
    '''整个发货单，包括发货单表头和表体'''
    distributelines = DistributelineSerializer(many=True, required=False)
    # available_event_list = serializers.ListField(required=False, child=serializers.CharField(required=False))
    shipping_address = ShippingAddressSerializer(required=False, read_only=True)
    express_order = NewExpressOrderSerializer(required=False, read_only=True)

    # cusservice_footprints = FootPrintSerializer(many=True, required=False)
    class Meta:
        model = Distribute
        fields = '__all__'

class FootPrintSerializer(serializers.ModelSerializer):
    '''整个发货单，包括发货单表头和表体'''

    class Meta:
        model = FootPrint
        fields = '__all__'

class ExpressRelaBackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpressRelaBack
        fields = '__all__'

class CSWholeDistributeDetailSerializer(serializers.ModelSerializer):
    '''整个发货单，包括发货单表头和表体'''
    distributelines = DistributelineSerializer(many=True, required=False)
    available_event_list = serializers.ListField(required=False, child=serializers.CharField(required=False))
    shipping_address = ShippingAddressSerializer(required=False, read_only=True)
    express_order = NewExpressOrderSerializer(required=False, read_only=True)
    cusservice_footprints = FootPrintSerializer(many=True, required=False)
    express_routes = serializers.ListField(required=False)
    express_history = ExpressRelaBackSerializer(many=True, required=False)
    class Meta:
        model = Distribute
        fields = '__all__'