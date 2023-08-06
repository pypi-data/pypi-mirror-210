from .utils import get_seats_by_dis_ids

def decorator_shelfseat_info_in_distribute_list(serializer_data):
    '''
    为发货单列表补充货位信息

    :param serializer_data: [{'id': '发货单id', ...}, ...]
    '''
    dis_ids = [distribute_dict['id'] for distribute_dict in serializer_data]
    seats_info_dict = get_seats_by_dis_ids(dis_ids)
    for distribute_dict in serializer_data:
        storage_record_dict = seats_info_dict.get(distribute_dict['id'], None)
        distribute_dict.update({'storage_info': storage_record_dict})

