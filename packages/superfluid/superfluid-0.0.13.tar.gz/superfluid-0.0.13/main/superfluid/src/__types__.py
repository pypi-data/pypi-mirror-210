from typing import Optional, TypedDict
from enum import Enum

from eth_typing import HexAddress

from .utils import normalize_address


class GetFlowParams:
    super_token: HexAddress = None
    sender: HexAddress = None
    receiver: HexAddress = None

    def __init__(self, super_token: HexAddress, sender: HexAddress, receiver: HexAddress) -> None:
        """
            * @param super_token - the superToken of the agreement
            * @param sender - the sender of the flow
            * @param receiver - the receiver of the flow
        """
        self.super_token = normalize_address(super_token)
        self.sender = normalize_address(sender)
        self.receiver = normalize_address(receiver)


class Web3FlowInfo(TypedDict):
    timestamp: int
    flowRate: int
    deposit: int
    owedDeposit: int


class GetAccountFlowInfoParams:
    super_token: HexAddress = None
    account: HexAddress = None

    def __init__(self, super_token: HexAddress, account: HexAddress) -> None:
        """
            * @param super_token - the superToken of the agreement
            * @param account - the account to get its info
        """
        self.super_token = normalize_address(super_token)
        self.account = normalize_address(account)


class GetFlowOperatorDataParams:
    super_token: HexAddress = None
    sender: HexAddress = None
    flow_operator: HexAddress = None

    def __init__(self, super_token: HexAddress, sender: HexAddress, flow_operator: HexAddress) -> None:
        """
            * @param super_token - the superToken of the agreement
            * @param sender - the sender of the flow
            * @param flow_operator - the flow operator
        """
        self.super_token = normalize_address(super_token)
        self.sender = normalize_address(sender)
        self.flow_operator = normalize_address(flow_operator)


class Web3FlowOperatorData(TypedDict):
    flowOperatorId: str
    permissions: int
    flowRateAllowance: int


class GetFlowOperatorDataParamsByID:
    super_token: HexAddress = None
    flow_operator_id: bytes = None

    def __init__(self, super_token: HexAddress, flow_operator_id: bytes) -> None:
        """
            * @param super_token - the super token of the agreement
            * @param flow_operator_id - the flow operator
        """
        self.super_token = normalize_address(super_token)
        self.flow_operator_id = flow_operator_id


class ShouldUseCallAgreement:

    should_use_call_agreement: Optional[bool] = None

    def __init__(self, should_use_call_agreement: Optional[bool] = None) -> None:
        """
            * @param should_use_call_agreement - whether or not to use the host contract
        """
        self.should_use_call_agreement = should_use_call_agreement


class ModifyFlowParams(ShouldUseCallAgreement):

    flow_rate: Optional[int] = None
    receiver: HexAddress = None
    sender: Optional[HexAddress] = None
    user_data: Optional[bytes] = None
    super_token: HexAddress = None

    def __init__(self, receiver: HexAddress, super_token: HexAddress, flow_rate: Optional[int] = None, sender: Optional[HexAddress] = None, user_data: Optional[bytes] = None, should_use_call_agreement: Optional[bool] = None) -> None:
        """
            * @param receiver - receiver of a flow
            * @param super_token - the super token of the agreement
            * @param flow_rate(Optional) - flow rate for the flow
            * @param sender(Optional) - sender of the flow
            * @param user_data(Optional) - user data for the flow
        """
        super().__init__(should_use_call_agreement)
        self.receiver = normalize_address(receiver)
        self.super_token = normalize_address(super_token)
        self.flow_rate = flow_rate
        self.sender = normalize_address(sender)
        self.user_data = user_data


class CreateFlowParams(ModifyFlowParams):

    def __init__(self, sender: HexAddress, receiver: HexAddress, super_token: HexAddress, flow_rate: int, user_data: Optional[bytes] = None,  should_use_call_agreement: Optional[bool] = None) -> None:

        super().__init__(receiver,
                         super_token, sender=sender, flow_rate=flow_rate, user_data=user_data, should_use_call_agreement=should_use_call_agreement)


class UpdateFlowParams(CreateFlowParams):
    pass


class DeleteFlowParams(ModifyFlowParams):

    def __init__(self, sender: HexAddress, receiver: HexAddress, super_token: HexAddress, flow_rate: Optional[int] = None, user_data: Optional[bytes] = None, should_use_call_agreement: Optional[bool] = None) -> None:
        super().__init__(receiver,
                         super_token, sender=sender, flow_rate=flow_rate, user_data=user_data, should_use_call_agreement=should_use_call_agreement)


class BatchOperationType(Enum):

    UNSUPPORTED = "UNSUPPORTED"  # 0
    ERC20_APPROVE = "ERC20_APPROVE"  # 1
    ERC20_TRANSFER_FROM = "ERC20_TRANSFER_FROM"  # 2
    ERC777_SEND = "ERC777_SEND"  # 3
    ERC20_INCREASE_ALLOWANCE = "ERC20_INCREASE_ALLOWANCE"  # 4
    ERC20_DECREASE_ALLOWANCE = "ERC20_DECREASE_ALLOWANCE"  # 5
    SUPERTOKEN_UPGRADE = "SUPERTOKEN_UPGRADE"  # 101
    SUPERTOKEN_DOWNGRADE = "SUPERTOKEN_DOWNGRADE"  # 102
    SUPERFLUID_CALL_AGREEMENT = "SUPERFLUID_CALL_AGREEMENT"  # 201
    CALL_APP_ACTION = "CALL_APP_ACTION"  # 202
