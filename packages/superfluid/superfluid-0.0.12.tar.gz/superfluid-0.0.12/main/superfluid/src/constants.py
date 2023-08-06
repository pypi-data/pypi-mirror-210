from decouple import config

import json


with open(".abis/cfa_v1.json") as cfa_v1:
    cfa_v1_abi = cfa_v1.read()

CFA_V1_ABI = json.loads(cfa_v1_abi)

with open(".abis/cfa_v1_forwarder.json") as cfa_v1_forwarder:
    cfa_v1_forwarder_abi = cfa_v1_forwarder.read()

CFA_V1_FORWARDER_ABI = json.loads(cfa_v1_forwarder_abi)

with open(".abis/host.json") as host:
    host_abi = host.read()

HOST_ABI = json.loads(host_abi)

RPC_FOR_MUMBAI = config("RPC_FOR_MUMBAI")

CFA_V1_ADDRESS = "0x49e565Ed1bdc17F3d220f72DF0857C26FA83F873"

HOST_ADDRESS = "0xEB796bdb90fFA0f28255275e16936D25d3418603"

CFA_V1_FORWARDER_ADDRESS = "0xcfA132E353cB4E398080B9700609bb008eceB125"

PRIVATE_KEY = config("PRIVATE_KEY")
