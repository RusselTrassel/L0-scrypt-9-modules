from utils.func import *
import ccxt
import random
import logging

# General settings----------------------------------------------------------------------------------------------------

RPC_BSC      = 'https://rpc.ankr.com/bsc'
RPC_POLYGON  = 'https://rpc.ankr.com/polygon'
RPC_AVAX     = 'https://rpc.ankr.com/avalanche'
RPC_ARBITRUM = 'https://endpoints.omniatech.io/v1/arbitrum/one/public'
RPC_AURORA   = 'https://endpoints.omniatech.io/v1/aurora/mainnet/public'
RPC_ZK_EVM   = 'https://rpc.ankr.com/polygon_zkevm'
RPC_GNOSIS   = 'https://rpc.ankr.com/gnosis'
RPC_OPTIMISM = 'https://rpc.ankr.com/optimism'
RPC_FANTOM   = 'https://rpc.ankr.com/fantom'
RPC_METIS    = 'https://andromeda.metis.io/?owner=1088'
RPC_CELO     = 'https://rpc.ankr.com/celo'

time_delay_min = 20  # Минимальная и
time_delay_max = 30  # Максимальная задержка между транзами в секундах -> Будет рандомное

# Module 1 - Withdrawl cex settings-----------------------------------------------------------------------------------

switch_cex = "okx"       # binance, mexc, kucoin, gate, okx, huobi, bybit
symbolWithdraw = "USDC"      # символ токена
network = "Arbitrum one"     # ID сети
proxy_server = "http://login:pass@ip:port"

# ----second-options----#

amount = [1, 1.5]            # минимальная и максимальная сумма
decimal_places = 2           # количество знаков, после запятой для генерации случайных чисел
delay = [35, 85]             # минимальная и максимальная задержка
shuffle_wallets = "no"       # нужно ли мешать кошельки yes/no

class API:
    # binance API
    binance_apikey = "your_api"
    binance_apisecret = "your_api_secret"
    # okx API
    okx_apikey = "your_api"
    okx_apisecret = "your_api_secret"
    okx_passphrase = "your_api_password"
    # bybit API
    bybit_apikey = "your_api"
    bybit_apisecret = "your_api_secret"
    # gate API
    gate_apikey = "your_api"
    gate_apisecret = "your_api_secret"
    # kucoin API
    kucoin_apikey = "your_api"
    kucoin_apisecret = "your_api_secret"
    kucoin_passphrase = "your_api_password"
    # mexc API
    mexc_apikey = "your_api"
    mexc_apisecret = "your_api_secret"
    # huobi API
    huobi_apikey = "your_api"
    huobi_apisecret = "your_api_secret"

proxies = {
  "http": proxy_server,
  "https": proxy_server,
}

# Module 2 - Refuel settings-------------------------------------------------------------------------------------------

REFUEL_CHAIN_FROM = 'Polygon'         # Из какой сети делать refuel [ Polygon, BSC, Avax, Arbitrum, Gnosis, zkEvm, Aurora, Optimism, Fantom ]
REFUEL_CHAIN_TO = 'Gnosis'            # В какую сеть делать refuel [ Polygon, BSC, Avax,  Arbitrum, Gnosis, zkEvm, Aurora, Optimism, Fantom]

refuel_value_min = 1       # Минимальное и
refuel_value_max = 1.1     # Максимальное количество токенов для бриджа (Из сети которой будет бридж) -> Будет рандомное

refuel_decimals = 2        # Округление, количество знаков после запятой

# Module 3 - Buy USDT or USDC settings---------------------------------------------------------------------------------

CHAIN     = 'BSC'    # Какую сеть использовать для покупки [ Polygon, BSC, Avax ]
BUY_TOKEN = 'STG'       # Какой токен покупать [ USDT, USDC, STG ]

buy_value_min = 0.01     # Минимальное и
buy_value_max = 0.05     # Максимальное количество USD для покупки -> Будет рандомное

buy_decimals = 3         # Округление, количество знаков после запятой

# Module 4 - Pancake bridge settings----------------------------------------------------------------------------------

PANCAKE_CHAIN_FROM = 'Polygon'  # Из какой сети делать bridge [ Polygon, BSC, Avax ]
PANCAKE_CHAIN_TO   = 'BSC'      # В какую сеть делать bridge [ Polygon, BSC, Avax ]

PANCAKE_TOKEN = 'USDT'          # Какой токен бриджить (Из BCS можно бриджить ТОЛЬКО USDT)

PANCAKE_value_min = 0.01        # Минимальное и
PANCAKE_value_max = 0.02        # Максимальное количество USD для бриджа -> Будет рандомное
                                # (Если сумма больше чем есть на балансе, то будет бридж всего баланса)

pancake_decimals = 3            # Округление, количество знаков после запятой

# Module 5 - Stargate bridge settings----------------------------------------------------------------------------------

STARGATE_CHAIN_FROM = 'BSC'             # Из какой сети делать bridge [ Polygon, BSC, Avax, Metis, Arbutrum]
STARGATE_CHAIN_TO   = 'Avax'            # В какую сеть делать bridge [ Polygon, BSC, Avax, Metis, Arbutrum ]

STARGATE_TOKEN = 'STG'                     # Какой токен бриджить (Из BCS можно бриджить ТОЛЬКО USDT)

stargate_value_min = 0.01        # Минимальное и
stargate_value_max = 0.02        # Максимальное количество USD для бриджа -> Будет рандомное
                                 # (Если сумма больше чем есть на балансе, то будет бридж всего баланса)

stargate_decimals = 3            # Округление, количество знаков после запятой

# Module 6.1 - Harmony bridge settings---------------------------------------------------------------------------------

HARMONY_value_min = 0.01      # Минимальное и
HARMONY_value_max = 0.1       # Максимальное количество USD для бриджа -> Будет рандомное
                              # (Если сумма больше чем есть на балансе, то будет бридж всего баланса)

harmony_decimals = 3          # Округление, количество знаков после запятой

HARMONY_TOKEN = 'USDT'        # Какой токен бриджить [ USDT, USDC ]

# Module 6.2 Core bridge settings-------------------------------------------------------------------------------------

CORE_value_min = 0.01      # Минимальное и
CORE_value_max = 0.1       # Максимальное количество USD для бриджа -> Будет рандомное
                           # (Если сумма больше чем есть на балансе, то будет бридж всего баланса)

core_decimals = 3          # Округление, количество знаков после запятой

CORE_TOKEN = 'USDС'        # Какой токен бриджить [ USDT, USDC ]

# Module 7 - Angl money bridge settings--------------------------------------------------------------------------------

ANGL_buy_value_min = 1       # Минимальное и
ANGL_buy_value_max = 2       # Максимальное количество EUR для покупки -> Будет рандомное

angl_decimals = 3               # Округление, количество знаков после запятой

# Module 7.1 - Celo - Gnosis - Celo-----------------------------------------------------------------------------------

number_of_repetition = 20        # Количесвто повторений (Кругов)

# Module 8 - BTC bridge settings--------------------------------------------------------------------------------------

BTC_buy_value_min = 0.00000100      # Минимальное и
BTC_buy_value_max = 0.00000126      # Максимальное количество BTC для покупки -> Будет рандомное
                                   # (Меньше 0.00000001 BTC купить нельзя!!!)

BTC_bridge_value_min = 0.0000001   # Минимальное и
BTC_bridge_value_max = 0.0000005   # Максимальное количество BTC для бриджа -> Будет рандомное
                                   # (Если сумма больше чем есть на балансе то будет бридж всего баланса)

BTC_decimals = 9                   # Округление, количество знаков после запятой

# Module 9 - Aptos bridge settings-------------------------------------------------------------------------------------

aptos_buy_value_min = 0.01
aptos_buy_value_max = 0.1

aptos_decimal = 2

# End settings --------------------------------------------------------------------------------------------------------

BSC_CHAIN = {'rpc': RPC_BSC,
             'scan': 'https://bscscan.com/tx/',
             'name': 'BSC',
             'usdt': Web3.to_checksum_address('0x55d398326f99059fF775485246999027B3197955'),
             'usdc': Web3.to_checksum_address('0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d'),
             'stg address': Web3.to_checksum_address('0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8'),
             'cake address': Web3.to_checksum_address('0x2eb9ea9df49bebb97e7750f231a32129a89b82ee'),
             'address': Web3.to_checksum_address('0xbe51d38547992293c89cc589105784ab60b004a9'),
             'harmony address usdt': Web3.to_checksum_address('0x0551ca9e33bada0355dfce34685ad3b73cf3ad70'),
             'harmony address usdc': Web3.to_checksum_address('0x8d1ebcda83fd905b597bf6d3294766b64ecf2aa7'),
             'core address': Web3.to_checksum_address('0x52e75D318cFB31f9A2EdFa2DFee26B161255B233'),
             'stg token': Web3.to_checksum_address('0xb0d502e938ed5f4df2e681fe6e419ff29631d62b'),
             'address aptos': Web3.to_checksum_address('0x2762409baa1804d94d8c0bcff8400b78bf915d5b'),
             'stg id': 102,
             'id': 56,
             'symbol': 'BNB'
             }

POLYGON_CHAIN = {'rpc': RPC_POLYGON,
                 'scan': 'https://polygonscan.com/tx/',
                 'name': 'Polygon',
                 'usdt': Web3.to_checksum_address('0xc2132D05D31c914a87C6611C10748AEb04B58e8F'),
                 'usdc': Web3.to_checksum_address('0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'),
                 'stg address': Web3.to_checksum_address('0x45A01E4e04F14f7A4a6702c74187c5F6222033cd'),
                 'cake address': Web3.to_checksum_address('0xdc2716b92480225533abc3328c2ab961f2a9247d'),
                 'address': Web3.to_checksum_address('0xac313d7491910516e06fbfc2a0b5bb49bb072d91'),
                 'stg token': Web3.to_checksum_address('0x2f6f07cdcf3588944bf4c42ac74ff24bf56e7590'),
                 'stg id': 109,
                 'id': 137,
                 'symbol': 'Matic',
                 'angl address': Web3.to_checksum_address('0x0c1EBBb61374dA1a8C57cB6681bF27178360d36F'),
                 'angl token': Web3.to_checksum_address('0xE0B52e49357Fd4DAf2c15e02058DCE6BC0057db4')
                 }

AVALANCH_CHAIN = {'rpc': RPC_AVAX,
                  'name': 'Avax',
                  'scan': 'https://snowtrace.io/tx/',
                  'usdt': Web3.to_checksum_address('0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7'),
                  'usdc': Web3.to_checksum_address('0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E'),
                  'stg address': Web3.to_checksum_address('0x45a01e4e04f14f7a4a6702c74187c5f6222033cd'),
                  'cake address': Web3.to_checksum_address('0x20293edd4f52f81234b3997b9ae4742c48005858'),
                  'address': Web3.to_checksum_address('0x040993fbf458b95871cd2d73ee2e09f4af6d56bb'),
                  'stg token': Web3.to_checksum_address('0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590'),
                  'stg id': 106,
                  'id': 43114,
                  'symbol': 'Avax'
                  }

HARMONY_CHAIN = {
              'name': 'Harmony',
              'scan': 'https://explorer.harmony.one/tx/',
              'usdt contract': Web3.to_checksum_address('0x9A89d0e1b051640C6704Dde4dF881f73ADFEf39a'),
              'stg chain': 116,
              'id': 1666600000,
              'symbol': "Hrm",
              'hrm contract': Web3.to_checksum_address('0x8bab2DDe26CE3f948b9B3E146760B66b60810fc7')
}

CORE_CHAIN = {
              'name': 'Core',
              'scan': 'https://scan.coredao.org/tx/',
              'core contract': Web3.to_checksum_address('0xA4218e1F39DA4AaDaC971066458Db56e901bcbdE'),
              'usdt contract': Web3.to_checksum_address('0x900101d06a7426441ae63e9ab3b9b0f63be145f1'),
              'stg chain': 228,
              'id': 1116,
              'symbol': "Core"
              }

ARBITRUM_CHAIN = {
    'rpc': RPC_ARBITRUM,
    'name': 'Arbitrum',
    'scan': 'https://arbiscan.io/tx/',
    'address': Web3.to_checksum_address('0xc0e02aa55d10e38855e13b64a8e1387a04681a00'),
    'stg address': Web3.to_checksum_address('0x53bf833a5d6c4dda888f69c22c88c9f356a41614'),
    'usdc': Web3.to_checksum_address('0xff970a61a04b1ca14834a43f5de4533ebddb5cc8'),
    'usdt': Web3.to_checksum_address('0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'),
    'stg token': Web3.to_checksum_address('0x6694340fc020c5E6B96567843da2df01b2CE1eb6'),
    'id': 42161,
    'stg id': 110

}

AURORA_CHAIN = {
    'rpc': RPC_AURORA,
    'name': 'Aurora',
    'scan': 'https://explorer.aurora.dev/tx/',
    'address': Web3.to_checksum_address('0x2b42AFFD4b7C14d9B7C2579229495c052672Ccd3'),
    'id': 1313161554
}

ZK_EVM_CHAIN = {
    'rpc': RPC_ZK_EVM,
    'name': 'Zk_EVM',
    'scan': 'https://zkevm.polygonscan.com/tx/',
    'address': Web3.to_checksum_address('0x555a64968e4803e27669d64e349ef3d18fca0895'),
    'id': 1101
}

GNOSIS_CHAIN = {
    'rpc': RPC_GNOSIS,
    'name': 'Gnosis',
    'scan': 'https://gnosisscan.io/tx/',
    'address': Web3.to_checksum_address('0xBE51D38547992293c89CC589105784ab60b004A9'),
    'id': 100,
    'stg id': 145,
    'angl address': Web3.to_checksum_address('0xfa5ed56a203466cbbc2430a43c66b9d8723528e7'),
    'angl token': Web3.to_checksum_address('0x4b1E2c2762667331Bc91648052F646d1b0d35984'),
    'lz eur': Web3.to_checksum_address('0xFA5Ed56A203466CbBC2430a43c66b9D8723528E7')
}

OPTIMISM_CHAIN = {
    'rpc': RPC_OPTIMISM,
    'name': 'Optimism',
    'scan': 'https://optimistic.etherscan.io/tx/',
    'address': Web3.to_checksum_address('0x5800249621da520adfdca16da20d8a5fc0f814d8'),
    'id': 10
}

FANTOM_CHAIN = {
    'rpc': RPC_FANTOM,
    'name': 'Fantom',
    'scan': 'https://ftmscan.com/tx/',
    'address': Web3.to_checksum_address('0x040993fbF458b95871Cd2D73Ee2E09F4AF6d56bB'),
    'stg address': Web3.to_checksum_address('0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6'),
    'stg chain': 112,
    'id': 250
}

METIS_CHAIN = {'rpc': RPC_METIS,
               'name': 'METIS',
               'scan': 'https://andromeda-explorer.metis.io/tx/',
               'stg address': Web3.to_checksum_address('0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590'),
               'usdt': Web3.to_checksum_address('0xbB06DCA3AE6887fAbF931640f67cab3e3a16F4dC'),
               'id': 1088,
               'stg id': 151,
               'symbol': "METIS"
               }

CELO_CHAIN = {'rpc': RPC_CELO,
               'name': 'CELO',
               'scan': 'https://celoscan.io/tx/',
               'angl address': Web3.to_checksum_address('0xf1ddcaca7d17f8030ab2eb54f2d9811365efe123'),
               'angl token': Web3.to_checksum_address('0xC16B81Af351BA9e64C1a069E3Ab18c244A1E3049'),
               'symbol': "",
               'stg id': 125,
               'lz eur': Web3.to_checksum_address('0xf1dDcACA7D17f8030Ab2eb54f2D9811365EFe123')
               }


def _refuel():
    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f]

    random.shuffle(keys_list)
    chain_from, chain_to = get_and_check_chain_refuel(REFUEL_CHAIN_FROM, REFUEL_CHAIN_TO, POLYGON_CHAIN, BSC_CHAIN,
                                                      AVALANCH_CHAIN, ARBITRUM_CHAIN, OPTIMISM_CHAIN, AURORA_CHAIN,
                                                      ZK_EVM_CHAIN, GNOSIS_CHAIN, FANTOM_CHAIN)
    arr_hash = []
    gas = 0
    while keys_list:
        private_key = keys_list.pop(0)
        bsc_w3 = Web3(Web3.HTTPProvider(BSC_CHAIN['rpc']))
        acc = bsc_w3.eth.account.from_key(private_key)
        log.info('----------------------------------------------------------------------------')
        log.info(f'|   Сейчас работает аккаунт - {acc.address}   |')
        log.info('----------------------------------------------------------------------------\n')
        amount_ = round(random.uniform(refuel_value_min, refuel_value_max), refuel_decimals)
        for _ in range(RETRY):
            res_ = refuel(private_key, chain_from, chain_to['id'], amount_, arr_hash, gas, log)
            time.sleep(random.uniform(time_delay_min, time_delay_max))
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 'error':
            log.info(f'Ошибка, недостаточно средств в {chain_from["name"]} на аккаунте {acc.address}\n')
            continue

    log.info('Проверяю, дошли ли токены\n')

    for _hash in arr_hash:
        while check_bunge_transaction(_hash, log):
            log.info('Перевод еще в процессе')
            time.sleep(60)
    log.info('Перевод закончен\n')
    return 1


def buy_usd():
    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f]

    random.shuffle(keys_list)
    chain, token = get_and_check_chain_buy_usdt(CHAIN, BUY_TOKEN, POLYGON_CHAIN, BSC_CHAIN, AVALANCH_CHAIN)
    while keys_list:
        private_key = keys_list.pop(0)
        bsc_w3 = Web3(Web3.HTTPProvider(BSC_CHAIN['rpc']))
        acc = bsc_w3.eth.account.from_key(private_key)
        log.info('----------------------------------------------------------------------------')
        log.info(f'|   Сейчас работает аккаунт - {acc.address}   |')
        log.info('----------------------------------------------------------------------------\n')
        amount_ = round(random.uniform(buy_value_min, buy_value_max), buy_decimals)
        for _ in range(RETRY):
            gas = 0
            res_ = buy_token(private_key, chain, chain[token], amount_, gas, log)
            time.sleep(random.uniform(time_delay_min, time_delay_max))
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 0 or res_ == 'error':
            continue
    return 1


def _pancake_bridge():
    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f]

    random.shuffle(keys_list)
    chain_from, chain_to, token_name = get_and_check_chain(PANCAKE_CHAIN_FROM, PANCAKE_CHAIN_TO, PANCAKE_TOKEN,
                                                           POLYGON_CHAIN, BSC_CHAIN, AVALANCH_CHAIN, METIS_CHAIN,
                                                           ARBITRUM_CHAIN)
    gas = 0
    while keys_list:
        private_key = keys_list.pop(0)
        bsc_w3 = Web3(Web3.HTTPProvider(BSC_CHAIN['rpc']))
        acc = bsc_w3.eth.account.from_key(private_key)
        log.info('----------------------------------------------------------------------------')
        log.info(f'|   Сейчас работает аккаунт - {acc.address}   |')
        log.info('----------------------------------------------------------------------------\n')
        amount_ = round(random.uniform(PANCAKE_value_min, PANCAKE_value_max), pancake_decimals)
        for _ in range(RETRY):
            res_ = pancake_bridge(private_key, chain_to, chain_from, token_name, amount_, gas, log)
            time.sleep(random.uniform(time_delay_min, time_delay_max))
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 0 or res_ == 'error':
            continue

    return 1


def _stargate_bridge():
    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f]

    random.shuffle(keys_list)
    chain_from, chain_to, token_name = get_and_check_chain(STARGATE_CHAIN_FROM, STARGATE_CHAIN_TO, STARGATE_TOKEN,
                                                           POLYGON_CHAIN, BSC_CHAIN, AVALANCH_CHAIN, METIS_CHAIN,
                                                           ARBITRUM_CHAIN)
    gas = 0
    while keys_list:
        private_key = keys_list.pop(0)
        bsc_w3 = Web3(Web3.HTTPProvider(BSC_CHAIN['rpc']))
        acc = bsc_w3.eth.account.from_key(private_key)
        log.info('----------------------------------------------------------------------------')
        log.info(f'|   Сейчас работает аккаунт - {acc.address}   |')
        log.info('----------------------------------------------------------------------------\n')
        amount_ = round(random.uniform(stargate_value_min, stargate_value_max), stargate_decimals)
        for _ in range(RETRY):
            if token_name == 'stg token':
                res_ = stargate_bridge_stg(private_key, chain_to, chain_from, token_name, amount_, gas, log)
            else:
                res_ = stargate_bridge(private_key, chain_to, chain_from, token_name, amount_, gas, log)
            time.sleep(random.uniform(time_delay_min, time_delay_max))
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 0 or res_ == 'error':
            continue

    return 1


def _harmony_bridge():
    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f]

    random.shuffle(keys_list)
    token_name, harmony_address = get_and_check_token_harmony(HARMONY_TOKEN)
    gas = 0
    while keys_list:
        private_key = keys_list.pop(0)
        bsc_w3 = Web3(Web3.HTTPProvider(BSC_CHAIN['rpc']))
        acc = bsc_w3.eth.account.from_key(private_key)
        log.info('----------------------------------------------------------------------------')
        log.info(f'|   Сейчас работает аккаунт - {acc.address}   |')
        log.info('----------------------------------------------------------------------------\n')
        amount_ = round(random.uniform(HARMONY_value_min, HARMONY_value_max), harmony_decimals)
        for _ in range(RETRY):
            res_ = harmony_bridge(private_key, BSC_CHAIN, HARMONY_CHAIN, BSC_CHAIN[token_name],
                                  BSC_CHAIN[harmony_address], amount_, gas, log)
            time.sleep(random.uniform(time_delay_min, time_delay_max))
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 0 or res_ == 'error':
            continue
    return 1


def _core_bridge():
    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f]

    random.shuffle(keys_list)
    token_name = get_and_check_token(CORE_TOKEN)
    gas = 0
    while keys_list:
        private_key = keys_list.pop(0)
        bsc_w3 = Web3(Web3.HTTPProvider(BSC_CHAIN['rpc']))
        acc = bsc_w3.eth.account.from_key(private_key)
        log.info('----------------------------------------------------------------------------')
        log.info(f'|   Сейчас работает аккаунт - {acc.address}   |')
        log.info('----------------------------------------------------------------------------\n')
        amount_ = round(random.uniform(CORE_value_min, CORE_value_max), core_decimals)
        for _ in range(RETRY):
            res_ = core_bridge(private_key, BSC_CHAIN, BSC_CHAIN['core address'], BSC_CHAIN[token_name],
                               amount_, gas, log)
            time.sleep(random.uniform(time_delay_min, time_delay_max))
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 0 or res_ == 'error':
            continue
    return 1


def angl_monye1():
    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f]

    random.shuffle(keys_list)
    while keys_list:
        private_key = keys_list.pop(0)
        bsc_w3 = Web3(Web3.HTTPProvider(RPC_POLYGON))
        acc = bsc_w3.eth.account.from_key(private_key)
        log.info('----------------------------------------------------------------------------')
        log.info(f'|   Сейчас работает аккаунт - {acc.address}   |')
        log.info('----------------------------------------------------------------------------\n')
        amount_to_buy = round(random.uniform(ANGL_buy_value_min, ANGL_buy_value_max), angl_decimals)
        log.info(f'Сейчас покупаю {amount_to_buy} EUR')
        for _ in range(RETRY):
            res_ = swap_eur(private_key, POLYGON_CHAIN, amount_to_buy, log)
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 0 or res_ == 'error':
            log.info('Критическая ошибка')
            continue
        time.sleep(random.uniform(time_delay_min, time_delay_max))

        log.info(f'Сейчас бриджу EUR в Celo')
        for _ in range(RETRY):
            res_ = bridge_angle(private_key, POLYGON_CHAIN, CELO_CHAIN, log)
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 0 or res_ == 'error':
            log.info('Критическая ошибка')
            continue
        time.sleep(random.uniform(time_delay_min, time_delay_max))
    return 1


def angl_monye3():
    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f]

    random.shuffle(keys_list)
    while keys_list:
        private_key = keys_list.pop(0)
        bsc_w3 = Web3(Web3.HTTPProvider(RPC_POLYGON))
        acc = bsc_w3.eth.account.from_key(private_key)
        log.info('----------------------------------------------------------------------------')
        log.info(f'|   Сейчас работает аккаунт - {acc.address}   |')
        log.info('----------------------------------------------------------------------------\n')

        for _ in range(RETRY):
            res_ = bridge_angle1(private_key, CELO_CHAIN, POLYGON_CHAIN, log)
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 0 or res_ == 'error':
            log.info('Критическая ошибка')
            continue
        time.sleep(random.uniform(time_delay_min, time_delay_max))

        log.info(f'Сейчас продаю EUR')
        for _ in range(RETRY):
            res_ = sold_eur(private_key, POLYGON_CHAIN, log)
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 0 or res_ == 'error':
            log.info('Критическая ошибка')
            continue
        time.sleep(random.uniform(time_delay_min, time_delay_max))
    return 1


def angl_monye2():
    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f]

    random.shuffle(keys_list)
    while keys_list:
        private_key = keys_list.pop(0)
        bsc_w3 = Web3(Web3.HTTPProvider(RPC_POLYGON))
        acc = bsc_w3.eth.account.from_key(private_key)
        log.info('----------------------------------------------------------------------------')
        log.info(f'|   Сейчас работает аккаунт - {acc.address}   |')
        log.info('----------------------------------------------------------------------------\n')

        for i in range(number_of_repetition):
            log.info(f'Круг - {i+1}')
            for _ in range(RETRY):
                res_ = bridge_angle1(private_key, CELO_CHAIN, GNOSIS_CHAIN, log)
                if res_ == 1 or res_ == 'error' or res_ == 'eur':
                    break
            if res_ == 'eur':
                break
            if res_ == 0 or res_ == 'error':
                log.info('Критическая ошибка')
                break
            time.sleep(random.uniform(time_delay_min, time_delay_max))

            for _ in range(RETRY):
                res_ = bridge_angle1(private_key, GNOSIS_CHAIN, CELO_CHAIN, log)
                if res_ == 1 or res_ == 'error' or res_ == 'eur':
                    break
            if res_ == 'eur':
                break
            if res_ == 0 or res_ == 'error':
                log.info('Критическая ошибка')
                break
            time.sleep(random.uniform(time_delay_min, time_delay_max))
    return 1


def aptos():
    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f]

    with open("aptos_address.txt", "r") as f:
        aptos_list = [row.strip() for row in f]
    random.shuffle(keys_list)
    while keys_list:
        private_key = keys_list.pop(0)
        aptos_address = aptos_list.pop(0)
        bsc_w3 = Web3(Web3.HTTPProvider(RPC_POLYGON))
        acc = bsc_w3.eth.account.from_key(private_key)
        log.info('----------------------------------------------------------------------------')
        log.info(f'|   Сейчас работает аккаунт - {acc.address}   |')
        log.info('----------------------------------------------------------------------------\n')
        value = round(random.uniform(aptos_buy_value_min, aptos_buy_value_max), aptos_decimal)
        gas = 0
        log.info(f'Сейчас покупаю {value} usdt')
        for _ in range(RETRY):
            res_ = buy_token(private_key, BSC_CHAIN, BSC_CHAIN['usdt'], value, gas, log)
            time.sleep(random.uniform(time_delay_min, time_delay_max))
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 0 or res_ == 'error':
            continue

        log.info(f'Aptos bridge {value} usdt')
        for _ in range(RETRY):
            res_ = aptos_bridge(private_key, BSC_CHAIN, aptos_address, value, gas, log)
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 0 or res_ == 'error':
            log.info('Критическая ошибка')
            continue
        time.sleep(random.uniform(time_delay_min, time_delay_max))


def btc_bridge():
    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f]

    random.shuffle(keys_list)
    while keys_list:
        private_key = keys_list.pop(0)
        bsc_w3 = Web3(Web3.HTTPProvider(RPC_AVAX))
        acc = bsc_w3.eth.account.from_key(private_key)
        log.info('----------------------------------------------------------------------------')
        log.info(f'|   Сейчас работает аккаунт - {acc.address}   |')
        log.info('----------------------------------------------------------------------------\n')
        amount_to_buy = round(random.uniform(BTC_buy_value_min, BTC_buy_value_max), BTC_decimals)
        log.info('Покупаю биткоин')
        for _ in range(RETRY):
            res_ = buy_btc(private_key, AVALANCH_CHAIN, amount_to_buy, log)
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 0 or res_ == 'error':
            log.info('Критическая ошибка')
            continue
        time.sleep(random.uniform(time_delay_min, time_delay_max))

        log.info('BTC bridge')
        amount_to_bridge = round(random.uniform(BTC_bridge_value_min, BTC_bridge_value_max), BTC_decimals)
        for _ in range(RETRY):
            res_ = bitcon_bridge(private_key, 109, AVALANCH_CHAIN, amount_to_bridge, log)
            if res_ == 1 or res_ == 'error':
                break
        if res_ == 0 or res_ == 'error':
            log.info('Критическая ошибка')
            continue
        time.sleep(random.uniform(time_delay_min, time_delay_max))
    return 1


def check_lz_eur():
    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f]

    random.shuffle(keys_list)
    while keys_list:
        private_key = keys_list.pop(0)
        bsc_w3 = Web3(Web3.HTTPProvider(RPC_POLYGON))
        acc = bsc_w3.eth.account.from_key(private_key)
        log.info('----------------------------------------------------------------------------')
        log.info(f'|   Сейчас работает аккаунт - {acc.address}   |')
        log.info('----------------------------------------------------------------------------\n')

        gnosis_web3 = Web3(Web3.HTTPProvider(RPC_GNOSIS))
        celo_web3 = Web3(Web3.HTTPProvider(RPC_CELO))

        lz_token_gnosis = gnosis_web3.eth.contract(address=GNOSIS_CHAIN['lz eur'], abi=Token.abi)
        lz_token_celo = celo_web3.eth.contract(address=CELO_CHAIN['lz eur'], abi=Token.abi)

        balance_lz_eur_gnosis = lz_token_gnosis.functions.balanceOf(acc.address).call()
        if balance_lz_eur_gnosis > 0:
            log.info(f'На балансе в сети GNOSIS - {balance_lz_eur_gnosis} LZ EUR')
            withdrawl_eur(private_key, GNOSIS_CHAIN, log)
            time.sleep(random.uniform(time_delay_min, time_delay_max))
        else:
            log.info(f'На балансе в сети GNOSIS - 0 LZ EUR')

        balance_lz_eur_celo = lz_token_celo.functions.balanceOf(acc.address).call()
        if balance_lz_eur_celo > 0:
            log.info(f'На балансе в сети CELO - {balance_lz_eur_celo} LZ EUR')
            withdrawl_eur(private_key, CELO_CHAIN, log)
            time.sleep(random.uniform(time_delay_min, time_delay_max))
        else:
            log.info(f'На балансе в сети CELO - 0 LZ EUR')


def binance_withdraw(address, amount_to_withdrawal, wallet_number):
    exchange = ccxt.binance({
        'apiKey': API.binance_apikey,
        'secret': API.binance_apisecret,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    })

    try:
        exchange.withdraw(
            code=symbolWithdraw,
            amount=amount_to_withdrawal,
            address=address,
            tag=None,
            params={
                "network": network
            }
        )
        log.info(f'\n>>>[Binance] Вывел {amount_to_withdrawal} {symbolWithdraw} ')
        log.info(f'    [{wallet_number}]{address}')
    except Exception as error:
        log.info(f'\n>>>[Binance] Не удалось вывести {amount_to_withdrawal} {symbolWithdraw}: {error} ')
        log.info(f'    [{wallet_number}]{address}')


def okx_withdraw(address, amount_to_withdrawal, wallet_number):
    exchange = ccxt.okx({
        'apiKey': API.okx_apikey,
        'secret': API.okx_apisecret,
        'password': API.okx_passphrase,
        'enableRateLimit': True,
        'proxies': proxies,
    })

    try:
        chainName = symbolWithdraw + "-" + network
        fee = get_withdrawal_fee(symbolWithdraw, chainName)
        exchange.withdraw(symbolWithdraw, amount_to_withdrawal, address,
            params={
                "toAddress": address,
                "chainName": chainName,
                "dest": 4,
                "fee": fee,
                "pwd": '-',
                "amt": amount_to_withdrawal,
                "network": network
            }
        )

        log.info(f'\n>>>[OKx] Вывел {amount_to_withdrawal} {symbolWithdraw} ')
        log.info(f'    [{wallet_number}]{address}')
    except Exception as error:
        log.info(f'\n>>>[OKx] Не удалось вывести {amount_to_withdrawal} {symbolWithdraw}: {error} ')
        log.info(f'    [{wallet_number}]{address}')


def bybit_withdraw(address, amount_to_withdrawal, wallet_number):
    exchange = ccxt.bybit({
        'apiKey': API.bybit_apikey,
        'secret': API.bybit_apisecret,
    })

    try:
        exchange.withdraw(
            code=symbolWithdraw,
            amount=amount_to_withdrawal,
            address=address,
            tag=None,
            params={
                "forceChain": 1,
                "network": network
            }
        )
        log.info(f'\n>>>[ByBit] Вывел {amount_to_withdrawal} {symbolWithdraw} ')
        log.info(f'    [{wallet_number}]{address}')
    except Exception as error:
        log.info(f'\n>>>[ByBit] Не удалось вывести {amount_to_withdrawal} {symbolWithdraw}: {error} ')
        log.info(f'    [{wallet_number}]{address}')


def gate_withdraw(address, amount_to_withdrawal, wallet_number):
    exchange = ccxt.gate({
        'apiKey': API.gate_apikey,
        'secret': API.gate_apisecret,
    })

    try:
        exchange.withdraw(
            code=symbolWithdraw,
            amount=amount_to_withdrawal,
            address=address,
            params={
                "network": network
            }
        )
        log.info(f'\n>>>[Gate.io] Вывел {amount_to_withdrawal} {symbolWithdraw} ')
        log.info(f'    [{wallet_number}]{address}')
    except Exception as error:
        log.info(f'\n>>>[Gate.io] Не удалось вывести {amount_to_withdrawal} {symbolWithdraw}: {error} ')
        log.info(f'    [{wallet_number}]{address}')


def kucoin_withdraw(address, amount_to_withdrawal, wallet_number):
    exchange = ccxt.kucoin({
        'apiKey': API.kucoin_apikey,
        'secret': API.kucoin_apisecret,
        'password': API.kucoin_passphrase,
        'enableRateLimit': True,
    })

    try:
        exchange.withdraw(
            code=symbolWithdraw,
            amount=amount_to_withdrawal,
            address=address,
            params={
                "network": network
            }
        )
        log.info(f'\n>>>[Kucoin] Вывел {amount_to_withdrawal} {symbolWithdraw} ')
        log.info(f'    [{wallet_number}]{address}')
    except Exception as error:
        log.info(f'\n>>>[Kucoin] Не удалось вывести {amount_to_withdrawal} {symbolWithdraw}: {error} ')
        log.info(f'    [{wallet_number}]{address}')


def mexc_withdraw(address, amount_to_withdrawal, wallet_number):
    exchange = ccxt.mexc({
        'apiKey': API.mexc_apikey,
        'secret': API.mexc_apisecret,
        'enableRateLimit': True,
    })

    try:
        exchange.withdraw(
            code=symbolWithdraw,
            amount=amount_to_withdrawal,
            address=address,
            params={
                "network": network
            }
        )
        log.info(f'\n>>>[MEXC] Вывел {amount_to_withdrawal} {symbolWithdraw} ')
        log.info(f'    [{wallet_number}]{address}')
    except Exception as error:
        log.info(f'\n>>>[MEXC] Не удалось вывести {amount_to_withdrawal} {symbolWithdraw}: {error} ')
        log.info(f'    [{wallet_number}]{address}')


def huobi_withdraw(address, amount_to_withdrawal, wallet_number):
    exchange = ccxt.huobi({
        'apiKey': API.huobi_apikey,
        'secret': API.huobi_apisecret,
        'enableRateLimit': True,
    })

    try:
        exchange.withdraw(
            code=symbolWithdraw,
            amount=amount_to_withdrawal,
            address=address,
            params={
                "network": network
            }
        )
        log.info(f'\n>>>[Huobi] Вывел {amount_to_withdrawal} {symbolWithdraw} ')
        log.info(f'    [{wallet_number}]{address}')
    except Exception as error:
        log.info(f'\n>>>[Huobi] Не удалось вывести {amount_to_withdrawal} {symbolWithdraw}: {error} ')
        log.info(f'    [{wallet_number}]{address}')


def choose_cex(address, amount_to_withdrawal, wallet_number):
    if switch_cex == "binance":
        binance_withdraw(address, amount_to_withdrawal, wallet_number)
    elif switch_cex == "okx":
        okx_withdraw(address, amount_to_withdrawal, wallet_number)
    elif switch_cex == "bybit":
        log.info(f"\n>>> Bybit в больнице, у них API заболело, sorry") #bybit_withdraw(address, amount_to_withdrawal, wallet_number)
    elif switch_cex == "gate":
        gate_withdraw(address, amount_to_withdrawal, wallet_number)
    elif switch_cex == "huobi":
        huobi_withdraw(address, amount_to_withdrawal, wallet_number)
    elif switch_cex == "kucoin":
        kucoin_withdraw(address, amount_to_withdrawal, wallet_number)
    elif switch_cex == "mexc":
        mexc_withdraw(address, amount_to_withdrawal, wallet_number)
    else:
        raise ValueError("Неверное значение CEX. Поддерживаемые значения: binance, okx, bybit, gate, huobi, kucoin, mexc.")


def get_withdrawal_fee(symbolWithdraw, chainName):
    exchange = ccxt.okx({
        'apiKey': API.okx_apikey,
        'secret': API.okx_apisecret,
        'password': API.okx_passphrase,
        'enableRateLimit': True,
        'proxies': proxies,
    })
    currencies = exchange.fetch_currencies()
    for currency in currencies:
        if currency == symbolWithdraw:
            currency_info = currencies[currency]
            network_info = currency_info.get('networks', None)
            if network_info:
                for network in network_info:
                    network_data = network_info[network]
                    network_id = network_data['id']
                    if network_id == chainName:
                        withdrawal_fee = currency_info['networks'][network]['fee']
                        if withdrawal_fee == 0:
                            return 0
                        else:
                            return withdrawal_fee
    raise ValueError(f"     не могу получить сумму комиссии, проверьте значения symbolWithdraw и network")


def shuffle(wallets_list, shuffle_wallets):
    numbered_wallets = list(enumerate(wallets_list, start=1))
    if shuffle_wallets.lower() == "yes":
        random.shuffle(numbered_wallets)
    elif shuffle_wallets.lower() == "no":
        pass
    else:
        raise ValueError("\n>>> Неверное значение переменной 'shuffle_wallets'. Ожидается 'yes' или 'no'.")
    return numbered_wallets


def withdrawl():
    with open("wallets.txt", "r") as f:
        wallets_list = [row.strip() for row in f if row.strip()]
        numbered_wallets = shuffle(wallets_list, shuffle_wallets)
        log.info(f'Number of wallets: {len(wallets_list)}')
        log.info(f"CEX: {switch_cex}")
        log.info(f"Amount: {amount[0]} - {amount[1]} {symbolWithdraw}")
        log.info(f"Network: {network}")
        time.sleep(random.randint(2, 4))

        for wallet_number, address in numbered_wallets:
            amount_to_withdrawal = round(random.uniform(amount[0], amount[1]), decimal_places)
            choose_cex(address, amount_to_withdrawal, wallet_number)
            time.sleep(random.randint(delay[0], delay[1]))


if __name__ == '__main__':
    print('  _  __         _               _                                           _ _         ')
    print(' | |/ /___   __| | ___ _ __ ___| | ____ _ _   _  __ _        _____   ____ _| | | ____ _ ')
    print(r" | ' // _ \ / _` |/ _ \ '__/ __| |/ / _` | | | |/ _` |      / __\ \ / / _` | | |/ / _` |")
    print(r' | . \ (_) | (_| |  __/ |  \__ \   < (_| | |_| | (_| |      \__ \\ V / (_| | |   < (_| |')
    print(r' |_|\_\___/ \__,_|\___|_|  |___/_|\_\__,_|\__, |\__,_|      |___/ \_/ \__,_|_|_|\_\__,_|')
    print('                                          |___/                                    ', '\n')
    print('https://t.me/developercode1')
    print('https://t.me/developercode1')
    print('https://t.me/developercode1\n')

    log = logging.getLogger()
    console_out = logging.StreamHandler()
    basic_format1 = logging.Formatter('%(asctime)s : %(message)s')
    basic_format = logging.Formatter('%(asctime)s : %(message)s')
    console_out.setFormatter(basic_format1)
    file_handler = logging.FileHandler(f"logging.txt", 'a', 'utf-8')
    file_handler.setFormatter(basic_format)
    log.setLevel(logging.INFO)
    log.addHandler(console_out)
    log.addHandler(file_handler)

    log.info('Options')
    log.info(f'RPC_BSC - {RPC_BSC}')
    log.info(f'RPC_POLYGON - {RPC_POLYGON}')
    log.info(f'RPC_AVAX - {RPC_AVAX}')
    log.info(f'RPC_ARBITRUM - {RPC_ARBITRUM}')
    log.info(f'RPC_AURORA - {RPC_AURORA}')
    log.info(f'RPC_ZK_EVM - {RPC_ZK_EVM}')
    log.info(f'RPC_GNOSIS - {RPC_GNOSIS}')
    log.info(f'RPC_OPTIMISM - {RPC_OPTIMISM}')
    log.info(f'RPC_FANTOM - {RPC_FANTOM}')
    log.info(f'RPC_METIS - {RPC_METIS}')
    log.info(f'RPC_CELO - {RPC_CELO}\n')
    log.info(f'time_delay_min - {time_delay_min}')
    log.info(f'time_delay_max - {time_delay_max}\n')
    log.info(f'Modyle 1 - Withdrawl cex\n')
    log.info(f'switch_cex - {switch_cex}')
    log.info(f'symbolWithdraw - {symbolWithdraw}')
    log.info(f'network - {network}')
    log.info(f'proxy_server - {proxy_server}')
    log.info(f'amount - {amount}')
    log.info(f'decimal_place - {decimal_places}')
    log.info(f'delay - {delay}')
    log.info(f'shuffle_wallets - {shuffle_wallets}\n')
    log.info(f'Modyle 2 - Refuel\n')
    log.info(f'REFUEL_CHAIN_FROM - {REFUEL_CHAIN_FROM}')
    log.info(f'REFUEL_CHAIN_TO - {REFUEL_CHAIN_TO}')
    log.info(f'refuel_decimals - {refuel_decimals}\n')
    log.info(f'Modyle 3 - Buy USDC or USDT or STG \n')
    log.info(f'CHAIN - {CHAIN}')
    log.info(f'BUY_TOKEN - {BUY_TOKEN}')
    log.info(f'buy_value_min - {buy_value_min}')
    log.info(f'buy_value_max - {buy_value_max}')
    log.info(f'buy_decimals - {buy_decimals}\n')
    log.info(f'Modyle 4 - Pancake bridge \n')
    log.info(f'PANCAKE_CHAIN_FROM - {PANCAKE_CHAIN_FROM}')
    log.info(f'PANCAKE_CHAIN_TO - {PANCAKE_CHAIN_TO}')
    log.info(f'PANCAKE_TOKEN - {PANCAKE_TOKEN}')
    log.info(f'PANCAKE_value_min - {PANCAKE_value_min}')
    log.info(f'PANCAKE_value_max - {PANCAKE_value_max}')
    log.info(f'pancake_decimals - {pancake_decimals}\n')
    log.info(f'Modyle 5 - Stargate bridge \n')
    log.info(f'STARGATE_CHAIN_FROM - {STARGATE_CHAIN_FROM}')
    log.info(f'STARGATE_CHAIN_TO - {STARGATE_CHAIN_TO}')
    log.info(f'STARGATE_TOKEN - {STARGATE_TOKEN}')
    log.info(f'stargate_value_min - {stargate_value_min}')
    log.info(f'stargate_value_max - {stargate_value_max}')
    log.info(f'stargate_decimals - {stargate_decimals}\n')
    log.info(f'Modyle 6.1 - Harmony bridge \n')
    log.info(f'HARMONY_value_min - {HARMONY_value_min}')
    log.info(f'HARMONY_value_max - {HARMONY_value_max}')
    log.info(f'harmony_decimals - {harmony_decimals}')
    log.info(f'HARMONY_TOKEN - {HARMONY_TOKEN}\n')
    log.info(f'Modyle 6.2 - Core bridge \n')
    log.info(f'CORE_value_min - {CORE_value_min}')
    log.info(f'CORE_value_max - {CORE_value_max}')
    log.info(f'core_decimals - {core_decimals}')
    log.info(f'CORE_TOKEN - {CORE_TOKEN}\n')
    log.info(f'Modyle 7 - Angl money bridge \n')
    log.info(f'ANGL_buy_value_min - {ANGL_buy_value_min}')
    log.info(f'ANGL_buy_value_max - {ANGL_buy_value_max}')
    log.info(f'angl_decimals - {angl_decimals}\n')
    log.info(f'Modyle 7.1 - Celo - Gnosis - Celo bridge \n')
    log.info(f'number_of_repetition - {number_of_repetition}\n')
    log.info(f'Modyle 8 - BTC bridge \n')
    log.info(f'BTC_buy_value_min - {BTC_buy_value_min}')
    log.info(f'BTC_buy_value_max - {BTC_buy_value_max}')
    log.info(f'BTC_bridge_value_min - {BTC_bridge_value_min}')
    log.info(f'BTC_bridge_value_max - {BTC_bridge_value_max}')
    log.info(f'BTC_decimals - {BTC_decimals}\n')
    log.info(f'Modyle 9 - Aptos bridge \n')
    log.info(f'aptos_buy_value_min - {aptos_buy_value_min}')
    log.info(f'aptos_buy_value_max - {aptos_buy_value_max}')
    log.info(f'aptos_decimal - {aptos_decimal}\n')
    time.sleep(0.1)
    while True:
        log.info('Выберите модуль:')
        log.info('1 - Withdrawl cex')
        log.info('2 - Refuel')
        log.info('3 - Buy USDT / USDC / STG')
        log.info('4 - Pancake bridge')
        log.info('5 - Stargate bridge')
        log.info('6 - Harmony bridge')
        log.info('7 - Core bridge')
        log.info('8 - Angl money (Buy and bridge Polygon - Celo)')
        log.info('9 - Angl money (Celo - Gnosis - Celo)')
        log.info('10 - Angl money (Celo - Polygon and sold)')
        log.info('11 - BTC bridge')
        log.info('12 - Aptos bridge')
        log.info('13 - Вывод обернутых ЕВРО')
        log.info('14 - Выход')

        time.sleep(0.1)
        res = input('Введите номер модуля: ')
        if res == '1':
            withdrawl()
        elif res == '2':
            _refuel()
        elif res == '3':
            buy_usd()
        elif res == '4':
            _pancake_bridge()
        elif res == '5':
            _stargate_bridge()
        elif res == '6':
            _harmony_bridge()
        elif res == '7':
            _core_bridge()
        elif res == '8':
            angl_monye1()
        elif res == '9':
            angl_monye2()
        elif res == '10':
            angl_monye3()
        elif res == '11':
            btc_bridge()
        elif res == '12':
            aptos()
        elif res == '13':
            check_lz_eur()
        elif res == '14':
            break
        else:
            log.info('Вы ввели неверное значение, попробуйте еще раз :)\n\n')

