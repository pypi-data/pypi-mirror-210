from rest_framework import serializers
from .models import StorageRecord

class StorageRecordOnlyShelfInfoSerializer(serializers.ModelSerializer):
    '''仅获取货架信息'''

    class Meta:
        model = StorageRecord
        fields = ['distribute_id', 'store_code', 'store_number',
                  'store_name', 'shelf_number', 'seat_number',
                  'store_in_time']

