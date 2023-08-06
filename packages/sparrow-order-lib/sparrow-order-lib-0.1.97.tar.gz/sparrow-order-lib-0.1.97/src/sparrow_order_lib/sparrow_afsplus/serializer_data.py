from .utils import get_distribute_afsplus_infos


def decorator_afsplus_status_in_distribute_list(serializer_data):
    ''' 每个发货单上增加特需售后状态 '''
    dis_ids = [distribute_dict['id'] for distribute_dict in serializer_data]
    afsplus_infos = get_distribute_afsplus_infos(dis_ids)
    dis_id_2_afsplus_info_map = {
        dic['distribute_id']: dic for dic in afsplus_infos
    }

    default_afsplus_info = {
        'if_need_afsplus': False,
        'afsplus_type_show': "",
        'if_done_afsplus': False,
    }

    for distribute_dict in serializer_data:
        distribute_id = distribute_dict['id']
        afsplus_info = dis_id_2_afsplus_info_map.get(distribute_id, default_afsplus_info)

        if_need_afsplus_real = False
        if_need_afsplus = afsplus_info['if_need_afsplus']  # 是否需要特售
        if_done_afsplus = afsplus_info['if_done_afsplus']  # 是否已特售
        if_need_afsplus_real = if_need_afsplus and not if_done_afsplus

        distribute_dict['if_need_afsplus'] = if_need_afsplus_real
        distribute_dict['afsplus_type_show'] = afsplus_info['afsplus_type_show']

    return serializer_data