from ..core.constants import ShippingMethod

class AfsplusType:
    ''' 特殊售后类型 '''
    # 修改配送方式
    MODY_SHIPPING_METHOD = "mody_shipping_method"

    CHOICES = (
        (MODY_SHIPPING_METHOD, "修改配送方式"),
    )

    AFSPLUS_TYPE_DICT = dict(CHOICES)


class AfsplusTypeSub:
    ''' 特殊售后子类型 '''
    # S2E = "s2e"  # 自提转快递
    # E2S = "e2s"  # 快递转自提
    # 2022.11 发货仓需求
    TO_EXPRESS = "2e"  # 转快递
    TO_SELF_SERVICE = "2s"  # 转自提

    CHOICES = (
        # (S2E, "自提转快递"),
        # (E2S, "快递转自提"),
        (TO_EXPRESS, "转为快递"),
        (TO_SELF_SERVICE, "转为自提")
    )

    AFSPLUS_SUB_TYPE_DICT = dict(CHOICES)

    # MODY_SHIPPING_METHOD_SUB = [S2E, E2S]
    MODY_SHIPPING_METHOD_SUB = [TO_EXPRESS, TO_SELF_SERVICE]

    # 当申请特需售后时, 期望的配送方式与要申请的特需售后类型的对应关系
    ShippingMethod2TypeSubDict = {
        ShippingMethod.EXPRESS: TO_EXPRESS,
        ShippingMethod.SELF_SERVICE: TO_SELF_SERVICE,
    }


class AfsplusStatus:
    ''' 特殊售后状态 '''
    OPENING = "opening"
    OPENED = "opened"
    OPEN_FAILED = "open_failed"
    CLOSED = "closed"
    CLOSE_FAILED = "close_failed"
    CLOSING = "closing"
    COMPLETING = "completing"
    COMPLETE_FAILED = "completed_failed"
    COMPLETED = "completed"
    PENDING_PAY = "pending_pay"
    PENDING_REFUND = "pending_refund"
    PENDING_MODIFY = "pending_modify"

    AFSPLUS_STATUS_CHOICES = (
        (OPENING, "初始态"),
        (OPENED, "已申请"),
        (OPEN_FAILED, "申请失败"),
        (CLOSED, "已关闭"),
        (CLOSING, "关闭中"),
        (CLOSE_FAILED, "关闭失败"),
        (COMPLETING, "完成中"),
        (COMPLETED, "已完成"),
        (COMPLETE_FAILED, "完成失败"),
        (PENDING_PAY, "待支付"),
        (PENDING_REFUND, "待退款"),
        (PENDING_MODIFY, "待修改"),
    )

    AFSPLUS_STATUS_DICT = dict(AFSPLUS_STATUS_CHOICES)

    AFSPLUS_STATUS_DICT_FOR_C = {
        OPENING: "已申请",
        OPENED: "已申请",
        OPEN_FAILED: "待客服处理",
        CLOSED: "已关闭",
        CLOSING: "已关闭",
        CLOSE_FAILED: "待客服处理",
        COMPLETING: "已完成",
        COMPLETED: "已完成",
        COMPLETE_FAILED: "待客服处理",
        PENDING_PAY: "待支付",
        PENDING_REFUND: "待退款",
        PENDING_MODIFY: "修改中",
    }


    MESSAGE_DICT_FOR_C = {
        COMPLETED: "售后服务已完成，感谢您对汉光的支持",
        COMPLETING: "售后服务已完成，感谢您对汉光的支持",
        COMPLETE_FAILED: "请等待客服处理",
        CLOSED: "售后已关闭",
        CLOSING: "售后已关闭",
        CLOSE_FAILED: "请等待客服处理",
        PENDING_PAY: "请及时支付运费，逾期售后申请将关闭",
        PENDING_REFUND: "正在为您处理退运费，运费金额将原路返回到您的账户",
        PENDING_MODIFY: "正在为您修改配送方式",
        OPENING: "售后服务已申请, 请耐心等待",
        OPENED: "售后服务已申请, 请耐心等待",
        OPEN_FAILED: "请等待客服处理",
    }
