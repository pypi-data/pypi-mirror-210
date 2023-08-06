

import uuid

from .models import DistributeAfsplus


def get_distribute_afsplus_infos(dis_ids):
    ''' 根据发货单ID查询在途 DistributeAfsplus '''
    objs = DistributeAfsplus.objects.filter(distribute_id__in=dis_ids, if_need_afsplus=True)

    results = [
        {
            'distribute_id': obj.distribute_id,
            'if_need_afsplus': obj.if_need_afsplus,
            'afsplus_type_show': obj.afsplus_type_show,
            'if_done_afsplus': obj.if_done_afsplus,
        } for obj in objs
    ]
    return results


