import time
from web3 import Web3
import json as js
import requests
from requests.adapters import Retry

# --------------------------------------------------------------------------------------------------------------------


min_gas_bsc = 1.5  # Начальное значение газа
max_gas_bsc = 3    # Максимальное значение газа
gas_step = 0.2     # Шаг с которым будет увеличиваться это значение (1.5, 1.7, 1.9)

time_transaction = 600  # Время в секундах, после которого транза будет считаться не смайненной

OX_API_KEY = ''


# ----------------------------------------------------------------------------------------------------------------

RETRY = 30
retries = Retry(total=100, backoff_factor=1, status_forcelist=[400, 404, 500, 502, 503, 504])
adapter = requests.adapters.HTTPAdapter(max_retries=retries)


class Stargate:
    abi = js.load(open('./abi/Stargate.txt'))
    token_abi = js.load(open('./abi/Stg_token.txt'))


class Cake:
    abi = js.load(open('./abi/Cake.txt'))


class Core:
    abi = js.load(open('./abi/Core.txt'))


class Token:
    abi = js.load(open('./abi/Token.txt'))
    avax_btc = Web3.to_checksum_address('0x152b9d0FdC40C096757F570A51E494bd4b943E50')


class BitconBridge:
    address = Web3.to_checksum_address('0x2297aebd383787a160dd0d9f71508148769342e3')
    abi = js.load(open('./abi/BitcoinBridge.txt'))


class TradeJoe:
    address = Web3.to_checksum_address('0xb4315e873dbcf96ffd0acd8ea43f689d8c20fb30')
    abi = js.load(open('./abi/TradeJoe.txt'))


class Harmony:
    abi = js.load(open('./abi/Harmony.txt'))


class Bungee:
    abi = js.load(open('./abi/Bungee.txt'))


class Aptos:
    abi = js.load(open('./abi/aptos.txt'))


error_balance = {
    'message': 'insufficient funds for'
}


def approve(private_key, chain, token_to_approve, address_to_approve, gas, log):
    web3 = Web3(Web3.HTTPProvider(chain['rpc']))
    account = web3.eth.account.from_key(private_key)
    address_wallet = account.address
    token_contract = web3.eth.contract(address=token_to_approve, abi=Token.abi)
    max_amount = 2 ** 256 - 1
    dick = {
        'from': address_wallet,
        'nonce': web3.eth.get_transaction_count(address_wallet)
    }
    if chain['name'] == 'BSC':
        gas_bsc = min_gas_bsc + gas
        if gas_bsc > max_gas_bsc:
            gas_bsc = min_gas_bsc
        log.info(f'Сеть BSC, gas = {gas_bsc}\n')
        dick['gasPrice'] = Web3.to_wei(gas_bsc, 'gwei')
    else:
        dick['gasPrice'] = web3.eth.gas_price
    try:
        tx = token_contract.functions.approve(address_to_approve, max_amount).build_transaction(dick)
        time.sleep(2)
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        time.sleep(2)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        log.info('Отправил транзакцию')
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0
        log.info(f'approve || {chain["scan"]}{web3.to_hex(tx_hash)}\n')
        return 1
    except Exception as error:
        log.info(f'approve error || {error}')
        if isinstance(error.args[0], dict):
            if 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            elif 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            else:
                log.info(error)
                log.info('')
        elif 'is not in the chain after' in error.args[0]:
            log.info('Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
            gas += gas_step
        else:
            log.info(error)
            log.info(f'Пытаюсь еще раз\n')
        time.sleep(35)
        return 0


def swap_eur(private_key, chain, amount, log):
    try:
        web3 = Web3(Web3.HTTPProvider(chain['rpc']))
        account = web3.eth.account.from_key(private_key)
        address_wallet = account.address
        from_token_address = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        to_token_address = '0xE0B52e49357Fd4DAf2c15e02058DCE6BC0057db4'

        url = f'https://api-angle.1inch.io/v5.0/137/quote?fromTokenAddress={to_token_address}&toTokenAddress\
={from_token_address}&amount={int(1 * amount * 10 ** 18)}&fromAddress={address_wallet}&slippage=1&disableEstimate=true&connectorTokens='

        res = requests.get(url)
        json_data = res.json()
        value = json_data['toTokenAmount']
        url = f'https://api-angle.1inch.io/v5.0/137/swap?fromTokenAddress={from_token_address}&toTokenAddress\
={to_token_address}&amount={value}&fromAddress={address_wallet}&slippage=0.98&disableEstimate=true&connectorTokens='
        res = requests.get(url)
        json_data = res.json()

        txn = {
            'chainId': 137,
            'data': json_data['tx']['data'],
            'from': address_wallet,
            'to': Web3.to_checksum_address(json_data['tx']['to']),
            'value': int(json_data['tx']['value']),
            'nonce': web3.eth.get_transaction_count(address_wallet),
            'gasPrice': web3.eth.gas_price
        }
        gas = web3.eth.estimate_gas(txn)
        time.sleep(1)
        txn.update({'gas': int(gas * 2)})
        signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0
        log.info(f'Buy EUR || https://polygonscan.com/tx/{hash_}\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'is not in the chain after' in error.args[0]:
                log.info('Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def sold_eur(private_key, chain, log):
    try:
        web3 = Web3(Web3.HTTPProvider(chain['rpc']))
        account = web3.eth.account.from_key(private_key)
        address_wallet = account.address
        to_token_address = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        from_token_address = '0xE0B52e49357Fd4DAf2c15e02058DCE6BC0057db4'

        token_contract = web3.eth.contract(address=Web3.to_checksum_address(from_token_address), abi=Token.abi)
        token_balance = token_contract.functions.balanceOf(address_wallet).call()
        if token_balance == 0:
            log.info(f'Баланс на аккаунте {address_wallet} 0 eur')
            time.sleep(30)
            return 0

        url = f'https://api-angle.1inch.io/v5.0/137/swap?fromTokenAddress={from_token_address}&toTokenAddress\
={to_token_address}&amount={token_balance}&fromAddress={address_wallet}&slippage=0.98&disableEstimate=true&connectorTokens='
        res = requests.get(url)
        json_data = res.json()

        allowance = token_contract.functions.allowance(address_wallet,
                                                       Web3.to_checksum_address('0x1111111254EEB25477B68fb85Ed929f73A960582')).call()
        if allowance < Web3.to_wei(100000, 'ether'):
            log.info('Нужен аппрув, делаю')
            for _ in range(20):
                gas = 0
                res_ = approve(private_key, chain, Web3.to_checksum_address('0xE0B52e49357Fd4DAf2c15e02058DCE6BC0057db4'),
                               Web3.to_checksum_address('0x1111111254EEB25477B68fb85Ed929f73A960582'), gas, log)
                if res_ == 1:
                    break
            time.sleep(25)
        txn = {
            'chainId': 137,
            'data': json_data['tx']['data'],
            'from': address_wallet,
            'to': Web3.to_checksum_address(json_data['tx']['to']),
            'nonce': web3.eth.get_transaction_count(address_wallet),
            'gasPrice': web3.eth.gas_price
        }
        gas = web3.eth.estimate_gas(txn)
        time.sleep(1)
        txn.update({'gas': int(gas * 2)})
        signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0
        log.info(f'Sold EUR || https://polygonscan.com/tx/{hash_}\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'is not in the chain after' in error.args[0]:
                log.info('Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def check_stargate(hash_, log):
    try:
        url_ = 'https://api-mainnet.layerzero-scan.com/tx/' + hash_
        with requests.Session() as s:
            s.mount('http://', adapter)
            s.mount('https://', adapter)
            res_ = js.loads(s.get(url_, timeout=600).text)
        log.info(res_['messages'])
        if res_['messages'] == []:
            return 1

        if res_['messages'][0]['status'] != 'DELIVERED':
            return 1
        else:
            return 0
    except:
        return 1


def bridge_angle(private_key, chain, chain_to, log):
    try:
        web3 = Web3(Web3.HTTPProvider(chain['rpc']))
        account = web3.eth.account.from_key(private_key)
        address_wallet = account.address
        angl_address = chain['angl address']
        angl_abi = js.load(open('./abi/Angl.txt'))
        eur_address = chain['angl token']
        angl_contract = web3.eth.contract(address=angl_address, abi=angl_abi)
        eur_contract = web3.eth.contract(address=eur_address, abi=Token.abi)
        balance = eur_contract.functions.balanceOf(address_wallet).call()
        if balance == 0:
            log.info(f'Баланс на аккаунте {address_wallet} 0 eur')
            time.sleep(30)
            return 0

        adapter_params = '0x00010000000000000000000000000000000000000000000000000000000000030d40'
        allowance = eur_contract.functions.allowance(address_wallet, angl_address).call()
        if allowance < Web3.to_wei(100000, 'ether'):
            log.info('Нужен аппрув, делаю')
            for _ in range(20):
                gas = 0
                res_ = approve(private_key, chain, eur_address, angl_address, gas, log)
                if res_ == 1:
                    break
            time.sleep(25)

        zro_payment_address = '0x0000000000000000000000000000000000000000'
        fees = angl_contract.functions.estimateSendFee(chain_to['stg id'], address_wallet, 0, True, adapter_params).call()[0]
        if int(fees[0] * 1.05) > int(balance):
            raise ValueError(error_balance)
        dick = {
            'from': address_wallet,
            'value': fees,
            'nonce': web3.eth.get_transaction_count(address_wallet),
            'gasPrice': web3.eth.gas_price
        }

        swap_txn = angl_contract.functions.send(chain_to['stg id'], address_wallet, balance, address_wallet, zro_payment_address,
                                                adapter_params).build_transaction(dick)
        signed_txn = web3.eth.account.sign_transaction(swap_txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0

        log.info(f'Angl money bridge from {chain["name"]} to {chain_to["name"]} || {chain["scan"]}{hash_}\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'is not in the chain after' in error.args[0]:
                log.info('Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def bridge_angle1(private_key, chain, chain_to, log):
    try:
        web3 = Web3(Web3.HTTPProvider(chain['rpc']))
        account = web3.eth.account.from_key(private_key)
        address_wallet = account.address
        angl_address = chain['angl address']
        angl_abi = js.load(open('./abi/Angl.txt'))
        eur_address = chain['angl token']
        angl_contract = web3.eth.contract(address=angl_address, abi=angl_abi)
        eur_contract = web3.eth.contract(address=eur_address, abi=Token.abi)
        balance = eur_contract.functions.balanceOf(address_wallet).call()

        if balance == 0:
            log.info(f'Баланс на аккаунте {address_wallet} 0 eur')
            return 'eur'

        adapter_params = '0x00010000000000000000000000000000000000000000000000000000000000030d40'
        allowance = eur_contract.functions.allowance(address_wallet, angl_address).call()
        if allowance < Web3.to_wei(100000, 'ether'):
            log.info('Нужен аппрув, делаю')
            for _ in range(20):
                gas = 0
                res_ = approve(private_key, chain, eur_address, angl_address, gas, log)
                if res_ == 1:
                    break
            time.sleep(25)

        zro_payment_address = '0x0000000000000000000000000000000000000000'
        fees = angl_contract.functions.estimateSendFee(chain_to['stg id'], address_wallet, 0, True, adapter_params).call()[0]
        if int(fees[0] * 1.05) > int(balance):
            raise ValueError(error_balance)
        dick = {
            'from': address_wallet,
            'value': fees,
            'nonce': web3.eth.get_transaction_count(address_wallet),
            'gasPrice': web3.eth.gas_price
        }

        swap_txn = angl_contract.functions.send(chain_to['stg id'], address_wallet, balance, address_wallet, zro_payment_address,
                                                adapter_params).build_transaction(dick)
        signed_txn = web3.eth.account.sign_transaction(swap_txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0

        log.info(f'Angl money bridge from {chain["name"]} to {chain_to["name"]} || {chain["scan"]}{hash_}\n')
        time.sleep(40)
        while check_stargate(hash_, log):
            log.info('Бридж еще не закончился')
            time.sleep(120)
        log.info('Бридж закончился\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'is not in the chain after' in error.args[0]:
                log.info('Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def buy_btc(private_key, chain, amount, log):
    try:
        web3 = Web3(Web3.HTTPProvider(chain['rpc']))
        account = web3.eth.account.from_key(private_key)
        address_wallet = account.address
        from_token_address = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        url = f'https://avalanche.api.0x.org/swap/v1/quote?buyToken={from_token_address}&sellToken\
={Token.avax_btc}&sellAmount={int(amount * 10 ** 8)}&slippagePercentage={1 / 100}'
        json_data = get_api_call_data(url)
        amount = json_data['buyAmount']
        url = f'https://avalanche.api.0x.org/swap/v1/quote?buyToken={Token.avax_btc}&sellToken\
={from_token_address}&sellAmount={amount}&slippagePercentage={1 / 100}'
        json_data = get_api_call_data(url)
        txn = {
            'chainId': web3.eth.chain_id,
            'data': json_data['data'],
            'from': address_wallet,
            'to': Web3.to_checksum_address(json_data['to']),
            'value': int(json_data['value']),
            'nonce': web3.eth.get_transaction_count(address_wallet),
            'gasPrice': web3.eth.gas_price
        }
        gas = web3.eth.estimate_gas(txn)
        time.sleep(1)
        txn.update({'gas': int(gas * 2)})
        signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
        log.info('Отправил транзакцию')
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0

        log.info(f'Buy BTC | https://snowtrace.io/tx/{hash_}\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'is not in the chain after' in error.args[0]:
                log.info('Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def bitcon_bridge(private_key, chain_to, chain_from_not_btc, amount, log):
    web3 = Web3(Web3.HTTPProvider(chain_from_not_btc['rpc']))
    account = web3.eth.account.from_key(private_key)
    address_wallet = account.address
    bitcoin_bridge_contract = web3.eth.contract(address=BitconBridge.address, abi=BitconBridge.abi)
    time.sleep(2)
    token_contract = web3.eth.contract(address=Web3.to_checksum_address(Token.avax_btc), abi=Token.abi)
    try:
        to_address = '0x000000000000000000000000' + address_wallet[2:]
        balance = token_contract.functions.balanceOf(address_wallet).call()
        amount_in = int(amount * 10 ** 8)
        if balance < amount_in:
            amount_in = balance
        amount_out_min = amount_in - (amount_in * 10) // 1000
        _adapterParams = '0x0002000000000000000000000000000000000000000000000000000000000003d090000000000000000000\
0000000000000000000000000000000000000000000000' + address_wallet[2:]
        # Check allowance
        allowance = token_contract.functions.allowance(address_wallet, BitconBridge.address).call()
        decimal = token_contract.functions.decimals().call()
        if allowance < 1000000 * 10 ** decimal:
            log.info('Нужен аппрув, делаю')
            for _ in range(RETRY):
                gas = 0
                res_ = approve(private_key, chain_from_not_btc, Token.avax_btc,  BitconBridge.address, gas, log)
                if res_ == 1:
                    break
            time.sleep(25)
        refund_address = address_wallet
        zro_payment_address = '0x0000000000000000000000000000000000000000'
        call_params = (refund_address, zro_payment_address, _adapterParams)
        fees = bitcoin_bridge_contract.functions.estimateSendFee(chain_to, to_address, amount_in, True, _adapterParams).call()
        balance = web3.eth.get_balance(address_wallet)
        if int(fees[0] * 1.05) > int(balance):
            raise ValueError(error_balance)
        dick = {
            'from': address_wallet,
            'value': fees[0],
            'nonce': web3.eth.get_transaction_count(address_wallet),
            'gasPrice': web3.eth.gas_price
        }
        swap_txn = bitcoin_bridge_contract.functions.sendFrom(address_wallet, chain_to, to_address,
                                                              amount_in, amount_out_min,
                                                              call_params).build_transaction(dick)
        signed_txn = web3.eth.account.sign_transaction(swap_txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0

        log.info(f'Bitcoin bridge|| https://snowtrace.io/tx/{hash_}\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'is not in the chain after' in error.args[0]:
                log.info(f'Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def get_api_call_data(url):
    try:
        with requests.Session() as s:
            s.mount('http://', adapter)
            s.mount('https://', adapter)
            headers = {
                '0x-api-key': OX_API_KEY
            }
            call_data = s.get(url, headers=headers, timeout=60)
            api_data = call_data.json()
        return api_data
    except:
        return 0


def buy_token(private_key, chain, to_token_address, amount, gas, log):
    try:
        web3 = Web3(Web3.HTTPProvider(chain['rpc']))
        account = web3.eth.account.from_key(private_key)
        address_wallet = account.address
    except Exception as error:
        log.info(error)
        log.info('Пытаюсь еще раз')
        return 0

    url_chains = {
        'BSC': 'bsc.',
        'Arbitrum': 'arbitrum.',
        'Polygon': 'polygon.',
        'Avax': 'avalanche.',
    }

    try:
        token_contract = web3.eth.contract(address=to_token_address, abi=Token.abi)
        decimal = token_contract.functions.decimals().call()
        from_token_address = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
        amount_to_swap = int(amount * 10 ** decimal)
        _url = f'https://{url_chains[chain["name"]]}api.0x.org/swap/v1/quote?buyToken={from_token_address}&sellToken\
={to_token_address}&sellAmount={amount_to_swap}&slippagePercentage={1 / 100}'

        json_data = get_api_call_data(_url)

        amount_to_swap = json_data['buyAmount']
        _url = f'https://{url_chains[chain["name"]]}api.0x.org/swap/v1/quote?buyToken={to_token_address}&sellToken\
={from_token_address}&sellAmount={amount_to_swap}&slippagePercentage={1 / 100}'

        json_data = get_api_call_data(_url)

        txn = {
            'chainId': web3.eth.chain_id,
            'data': json_data['data'],
            'from': address_wallet,
            'to': Web3.to_checksum_address(json_data['to']),
            'value': int(json_data['value']),
            'nonce': web3.eth.get_transaction_count(address_wallet),
        }
        if chain['name'] == 'BSC':
            gas_bsc = min_gas_bsc + gas
            log.info(f'Сеть BSC, gas = {gas_bsc}\n')
            if gas_bsc > max_gas_bsc:
                gas_bsc = max_gas_bsc
            txn['gasPrice'] = Web3.to_wei(gas_bsc, 'gwei')
        else:
            txn['gasPrice'] = web3.eth.gas_price

        gas = web3.eth.estimate_gas(txn)
        time.sleep(1)
        txn.update({'gas': int(gas * 2)})

        signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0
        log.info(f'Buy token || {chain["scan"]}{tx_hash.hex()}\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'cannot swap 0' in error.args[0]:
                log.info('Критическая, нет usd для трансфера')
            elif 'is not in the chain after' in error.args[0]:
                log.info(f'Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
                gas += gas_step
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def get_and_check_chain_buy_usdt(chain, token, POLYGON_CHAIN, BSC_CHAIN, AVALANCH_CHAIN):
    if chain == 'Polygon':
        _chain = POLYGON_CHAIN
    elif chain == 'BSC':
        _chain = BSC_CHAIN
    elif chain == 'Avax':
        _chain = AVALANCH_CHAIN
    else:
        raise ValueError(f"\n>>> Неверное значение переменной CHAIN. Ожидается 'Polygon' or 'BSC' or 'Avax'.\nВы ввели {chain}")

    if token == 'USDT':
        _token = 'usdt'
    elif token == 'USDC':
        _token = 'usdc'
    elif token == 'STG':
        _token = 'stg token'
    else:
        raise ValueError(f"\n>>> Неверное значение переменной TOKEN. Ожидается 'USDC' or 'USDT'.\nВы ввели {token}")

    return _chain, _token


def core_bridge(private_key, chain, core_address, token_adderess, amount, gas, log):
    try:
        web3 = Web3(Web3.HTTPProvider(chain['rpc']))
        account = web3.eth.account.from_key(private_key)
        address_wallet = account.address
        adapter_params = '0x'
        core_contract = web3.eth.contract(address=core_address, abi=Core.abi)
        fees = core_contract.functions.estimateBridgeFee(True, adapter_params).call()
        # Check allowance
        token_contract = web3.eth.contract(address=token_adderess, abi=Token.abi)
        allowance = token_contract.functions.allowance(address_wallet, core_address).call()
        decimal = token_contract.functions.decimals().call()
        if allowance < 1000000 * 10 ** decimal:
            log.info('Нужен аппрув, делаю')
            for _ in range(20):
                res_ = approve(private_key, chain, token_adderess, core_address, gas, log)
                if res_ == 1:
                    break
            time.sleep(25)

        value = Web3.to_wei(amount, 'ether')
        token_balance = token_contract.functions.balanceOf(address_wallet).call()
        if token_balance < value:
            value = token_balance
        if token_balance == 0:
            log.info('На балнсе 0 usd')
            return 'error'
        gas_bsc = min_gas_bsc + gas
        if gas_bsc > max_gas_bsc:
            gas_bsc = max_gas_bsc
        log.info(f'Сеть BSC, gas = {gas_bsc}\n')
        dick = {
            'from': address_wallet,
            'value': fees[0],
            'nonce': web3.eth.get_transaction_count(address_wallet),
            'gasPrice': Web3.to_wei(gas_bsc, 'gwei')
        }

        zro_payment_address = '0x0000000000000000000000000000000000000000'
        swap_txn = core_contract.functions.bridge(token_adderess, value, address_wallet, (address_wallet,
                                                  zro_payment_address), adapter_params).build_transaction(dick)

        signed_txn = web3.eth.account.sign_transaction(swap_txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0
        log.info(f'Core bridge || {chain["scan"]}{hash_}\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'cannot swap 0' in error.args[0]:
                log.info('Критическая, нет usd для трансфера')
            elif 'is not in the chain after' in error.args[0]:
                log.info(f'Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
                gas += gas_step
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def get_and_check_token(token):
    if token == 'USDT':
        _token = 'usdt'
    elif token == 'USDC':
        _token = 'usdc'
    else:
        raise ValueError(f"\n>>> Неверное значение переменной TOKEN. Ожидается 'USDT' or 'USDC'.\nВы ввели {token}")

    return _token


def harmony_bridge(private_key, chain_from, chain_to, token_address, harmony_address, amount, gas, log):
    try:
        web3 = Web3(Web3.HTTPProvider(chain_from['rpc']))
        account = web3.eth.account.from_key(private_key)
        address_wallet = account.address
        harmony_contract = web3.eth.contract(address=harmony_address, abi=Harmony.abi)
        adapter_params = '0x0001000000000000000000000000000000000000000000000000000000000007a120'
        token_contract = web3.eth.contract(address=token_address, abi=Token.abi)
        # Check allowance
        allowance = token_contract.functions.allowance(address_wallet, harmony_address).call()
        decimal = token_contract.functions.decimals().call()
        if allowance < 1000000 * 10 ** decimal:
            log.info('Нужен аппрув, делаю')
            for _ in range(20):
                res_ = approve(private_key, chain_from, token_address, harmony_address, gas, log)
                if res_ == 1:
                    break
            time.sleep(25)
        token_id = Web3.to_wei(amount, 'ether')
        token_balance = token_contract.functions.balanceOf(address_wallet).call()
        if token_balance < token_id:
            token_id = token_balance
        if token_balance == 0:
            return 'error'
        gas_bsc = min_gas_bsc + gas
        if gas_bsc > max_gas_bsc:
            gas_bsc = max_gas_bsc
        log.info(f'Сеть BSC, gas = {gas_bsc}\n')
        fees = harmony_contract.functions.estimateSendFee(chain_to['stg chain'], address_wallet, 1, True,
                                                          adapter_params).call()
        dick = {'from': address_wallet, 'value': fees[0], 'nonce': web3.eth.get_transaction_count(address_wallet),
                'gasPrice': Web3.to_wei(gas_bsc, 'gwei')}
        zro_payment_address = '0x0000000000000000000000000000000000000000'
        swap_txn = harmony_contract.functions.sendFrom(address_wallet, chain_to['stg chain'], address_wallet,
                                                       token_id, address_wallet, zro_payment_address,
                                                       adapter_params).build_transaction(dick)

        signed_txn = web3.eth.account.sign_transaction(swap_txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0

        log.info(f'Harmony bridge || {chain_from["scan"]}{hash_}\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'cannot swap 0' in error.args[0]:
                log.info('Критическая, нет usd для трансфера')
            elif 'is not in the chain after' in error.args[0]:
                log.info(f'Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
                gas += gas_step
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def get_and_check_token_harmony(token):
    if token == 'USDT':
        _token = 'usdt'
        _harmony_address = 'harmony address usdt'
    elif token == 'USDC':
        _token = 'usdc'
        _harmony_address = 'harmony address usdc'
    else:
        raise ValueError(f"\n>>> Неверное значение переменной TOKEN. Ожидается 'USDT' or 'USDC'.\nВы ввели {token}")

    return _token, _harmony_address


def pancake_bridge(private_key, chain_to_stg, chain_from_not_stg, token_name, value, gas, log):
    try:
        web3 = Web3(Web3.HTTPProvider(chain_from_not_stg['rpc']))
        account = web3.eth.account.from_key(private_key)
        address_wallet = account.address
        if chain_from_not_stg['name'] == 'BSC':
            token_name = 'usdt'
        stargate_contract = web3.eth.contract(address=chain_from_not_stg['stg address'], abi=Stargate.abi)
        token_contract = web3.eth.contract(address=chain_from_not_stg[token_name], abi=Token.abi)
        cake_contract = web3.eth.contract(address=chain_from_not_stg['cake address'], abi=Cake.abi)
        # Check allowance
        time.sleep(2)
        decimal = token_contract.functions.decimals().call()
        allowance = token_contract.functions.allowance(address_wallet, chain_from_not_stg['cake address']).call()
        if allowance < 1000000 * 10 ** decimal:
            log.info('Нужен аппрув, делаю')
            for _ in range(20):
                res_ = approve(private_key, chain_from_not_stg, chain_from_not_stg[token_name],
                               chain_from_not_stg['cake address'], gas, log)
                if res_ == 1:
                    break
            time.sleep(25)

        if token_name == 'usdt':
            source_pool_id = 2
            dest_pool_id = 2
        else:
            source_pool_id = 1
            dest_pool_id = 1

        if chain_from_not_stg['name'] == 'BSC':
            source_pool_id = 2

        if chain_to_stg['stg id'] == 102:
            dest_pool_id = 2

        token_balance = token_contract.functions.balanceOf(address_wallet).call()

        if token_balance == 0:
            log.info(f'На аккаунте {address_wallet} нет токенов для бриджа')
            return 'error'

        value = int(value * 10 ** decimal)

        if value > token_balance:
            amount_in = token_balance
        else:
            amount_in = value

        amount_out_min = amount_in - (amount_in * 10) // 1000
        to = address_wallet
        fees = stargate_contract.functions.quoteLayerZeroFee(chain_to_stg['stg id'], 1,
                                                             "0x0000000000000000000000000000000000000001",
                                                             "0x",
                                                             [0, 0, "0x0000000000000000000000000000000000000001"]
                                                             ).call()
        balance = web3.eth.get_balance(address_wallet)
        if int(fees[0] * 1.1) > int(balance):
            raise ValueError(error_balance)
        dick = {
            'from': address_wallet,
            'value': int(fees[0] * 1.1),
            'nonce': web3.eth.get_transaction_count(address_wallet)
        }
        if chain_from_not_stg['name'] == 'BSC':
            gas_bsc = min_gas_bsc + gas
            if gas_bsc > max_gas_bsc:
                gas_bsc = max_gas_bsc
            log.info(f'Сеть BSC, gas = {gas_bsc}\n')
            dick['gasPrice'] = Web3.to_wei(gas_bsc, 'gwei')
        else:
            dick['gasPrice'] = web3.eth.gas_price

        dst_gas_for_call = 0
        dst_native_amount = 0
        dst_native_addr = address_wallet
        params = (dst_gas_for_call, dst_native_amount, dst_native_addr)
        patern_id = '0x0002'
        tenth_bps = 0
        fee_collector = '0x68C7ABB8b1c3D1cE467E28265770F3a7ECF32654'
        feeObj = (tenth_bps, fee_collector)
        swap_txn = cake_contract.functions.swapTokens(
            chain_to_stg['stg id'], source_pool_id, dest_pool_id, amount_in, amount_out_min, params,
            to, patern_id, feeObj).build_transaction(dick)
        signed_txn = web3.eth.account.sign_transaction(swap_txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0

        log.info(f'Pancake bridge from {chain_from_not_stg["name"]} to {chain_to_stg["name"]} || {chain_from_not_stg["scan"]}{hash_}\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'cannot swap 0' in error.args[0]:
                log.info('Критическая, нет usd для трансфера')
            elif 'is not in the chain after' in error.args[0]:
                log.info(f'Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
                gas += gas_step
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def get_and_check_chain(chain_from, chain_to, token, POLYGON_CHAIN, BSC_CHAIN, AVALANCH_CHAIN, METIS_CHAIN,
                        ARBITRUM_CHAIN):
    if chain_from == 'Polygon':
        _chain_from = POLYGON_CHAIN
    elif chain_from == 'BSC':
        _chain_from = BSC_CHAIN
    elif chain_from == 'Avax':
        _chain_from = AVALANCH_CHAIN
    elif chain_from == 'Metis':
        _chain_from = METIS_CHAIN
    elif chain_from == 'Arbitrum':
        _chain_from = ARBITRUM_CHAIN
    else:
        raise ValueError(f"\n>>> Неверное значение переменной CHAIN. Ожидается 'Polygon' or 'BSC' or 'Avax' or 'Metis' or 'Arbitrum'.\nВы ввели {chain_from}")

    if chain_to == 'Polygon':
        _chain_to = POLYGON_CHAIN
    elif chain_to == 'BSC':
        _chain_to = BSC_CHAIN
    elif chain_to == 'Avax':
        _chain_to = AVALANCH_CHAIN
    elif chain_to == 'Metis':
        _chain_to = METIS_CHAIN
    elif chain_to == 'Arbitrum':
        _chain_to = ARBITRUM_CHAIN
    else:
        raise ValueError(f"\n>>> Неверное значение переменной CHAIN. Ожидается 'Polygon' or 'BSC' or 'Avax' or 'Metis'.\nВы ввели {chain_to}")

    if token == 'USDT':
        _token = 'usdt'
    elif token == 'USDC':
        _token = 'usdc'
    elif token == 'STG':
        _token = 'stg token'
    else:
        raise ValueError(f"\n>>> Неверное значение переменной TOKEN. Ожидается 'USDC' or 'USDT'.\nВы ввели {token}")

    return _chain_from, _chain_to, _token


def check_bunge_transaction(hash_, log):
    try:
        url_ = 'https://refuel.socket.tech/transaction?sourceTxHash='
        res_ = js.loads(requests.get(url_ + hash_).text)
        log.info(res_)
        if res_['success'] is False:
            return 1
        if res_['result']['status'] != 'Tx is confirmed & processed':
            return 1
        else:
            return 0
    except:
        return 1


def refuel(private_key, chain_from, chain_to, value, arr, gas, log):
    web3 = Web3(Web3.HTTPProvider(chain_from['rpc']))
    account = web3.eth.account.from_key(private_key)
    address_wallet = account.address
    balance = web3.eth.get_balance(address_wallet)
    value = Web3.to_wei(value, 'ether')
    if value > balance:
        log.info('Сумма больше, чем есть на балансе, скидываю весь баланс')
        value = int(balance * 0.9)
    dick = {
        'from': address_wallet,
        'value': value,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(address_wallet)
    }
    if chain_from['name'] == 'BSC':
        gas_bsc = min_gas_bsc + gas
        if gas_bsc > max_gas_bsc:
            gas_bsc = max_gas_bsc
        log.info(f'Сеть BSC, gas = {gas_bsc}\n')
        dick['gasPrice'] = Web3.to_wei(gas_bsc, 'gwei')
    try:
        contract = web3.eth.contract(address=chain_from['address'], abi=Bungee.abi)
        contract_txn = contract.functions.depositNativeToken(chain_to, address_wallet).build_transaction(dick)
        signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        time.sleep(2)
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0
        log.info(f'Refuel || {chain_from["scan"]}{hash_}\n')
        arr.append(hash_)
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'is not in the chain after' in error.args[0]:
                log.info(f'Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
                gas += gas_step
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def get_and_check_chain_refuel(chain_from, chain_to, POLYGON_CHAIN, BSC_CHAIN, AVALANCH_CHAIN, ARBITRUM_CHAIN,
                               OPTIMISM_CHAIN, AURORA_CHAIN, ZK_EVM_CHAIN, GNOSIS_CHAIN, FANTOM_CHAIN):
    if chain_from == 'Polygon':
        _chain_from = POLYGON_CHAIN
    elif chain_from == 'BSC':
        _chain_from = BSC_CHAIN
    elif chain_from == 'Avax':
        _chain_from = AVALANCH_CHAIN
    elif chain_from == 'Arbitrum':
        _chain_from = ARBITRUM_CHAIN
    elif chain_from == 'Aurora':
        _chain_from = AURORA_CHAIN
    elif chain_from == 'zkEvm':
        _chain_from = ZK_EVM_CHAIN
    elif chain_from == 'Gnosis':
        _chain_from = GNOSIS_CHAIN
    elif chain_from == 'Optimism':
        _chain_from = OPTIMISM_CHAIN
    elif chain_from == 'Fantom':
        _chain_from = FANTOM_CHAIN
    else:
        raise ValueError(f"\n>>> Неверное значение переменной CHAIN_FROM. Ожидается 'Polygon' or 'BSC' or 'Avax'.\nВы ввели {chain_from}")

    if chain_to == 'Polygon':
        _chain_to = POLYGON_CHAIN
    elif chain_to == 'BSC':
        _chain_to = BSC_CHAIN
    elif chain_to == 'Avax':
        _chain_to = AVALANCH_CHAIN
    elif chain_to == 'Arbitrum':
        _chain_to = ARBITRUM_CHAIN
    elif chain_to == 'Aurora':
        _chain_to = AURORA_CHAIN
    elif chain_to == 'zkEvm':
        _chain_to = ZK_EVM_CHAIN
    elif chain_to == 'Gnosis':
        _chain_to = GNOSIS_CHAIN
    elif chain_to == 'Optimism':
        _chain_to = OPTIMISM_CHAIN
    elif chain_to == 'Fantom':
        _chain_to = FANTOM_CHAIN
    else:
        raise ValueError(f"\n>>> Неверное значение переменной CHAIN_TO. Ожидается 'Polygon' or 'BSC' or 'Avax'.\nВы ввели {chain_to}")

    return _chain_from, _chain_to


def stargate_bridge(private_key, chain_to_stg, chain_from_not_stg, token_name, value, gas, log):
    try:
        web3 = Web3(Web3.HTTPProvider(chain_from_not_stg['rpc']))
        account = web3.eth.account.from_key(private_key)
        address_wallet = account.address
        if chain_from_not_stg['name'] == 'BSC':
            token_name = 'usdt'
        token_contract = web3.eth.contract(address=chain_from_not_stg[token_name], abi=Token.abi)
        stargate_contract = web3.eth.contract(address=chain_from_not_stg['stg address'], abi=Stargate.abi)
        # Check allowance
        time.sleep(2)
        decimal = token_contract.functions.decimals().call()
        allowance = token_contract.functions.allowance(address_wallet, chain_from_not_stg['stg address']).call()
        if allowance < 1000000 * 10 ** decimal:
            log.info('Нужен аппрув, делаю')
            for _ in range(20):
                res_ = approve(private_key, chain_from_not_stg, chain_from_not_stg[token_name],
                               chain_from_not_stg['stg address'], gas, log)
                if res_ == 1:
                    break
            time.sleep(25)

        if token_name == 'usdt':
            source_pool_id = 2
            dest_pool_id = 2
        else:
            source_pool_id = 1
            dest_pool_id = 1

        if chain_from_not_stg['name'] == 'BSC':
            source_pool_id = 2

        if chain_to_stg['stg id'] == 102:
            dest_pool_id = 2

        if chain_to_stg['name'] == 'METIS' or chain_from_not_stg['name'] == 'METIS':
            source_pool_id = 19
            dest_pool_id = 19

        refund_address = address_wallet
        token_balance = token_contract.functions.balanceOf(address_wallet).call()

        if token_balance == 0:
            log.info(f'На аккаунте {address_wallet} нет токенов для бриджа')
            return 'error'

        value = value * 10 ** decimal

        if value > token_balance:
            amount_in = token_balance
        else:
            amount_in = int(value)

        amount_out_min = amount_in - (amount_in * 10) // 1000
        lz_tx_obj = [0, 0, '0x0000000000000000000000000000000000000001']
        to = address_wallet
        data = '0x'
        fees = stargate_contract.functions.quoteLayerZeroFee(chain_to_stg['stg id'], 1,
                                                             "0x0000000000000000000000000000000000000001",
                                                             "0x",
                                                             [0, 0, "0x0000000000000000000000000000000000000001"]
                                                             ).call()
        balance = web3.eth.get_balance(address_wallet)
        if int(fees[0] * 1.1) > int(balance):
            raise ValueError(error_balance)
        dick = {
            'from': address_wallet,
            'value': fees[0],
            'nonce': web3.eth.get_transaction_count(address_wallet)
        }
        if chain_from_not_stg['name'] == 'BSC':
            gas_bsc = min_gas_bsc + gas
            if gas_bsc > max_gas_bsc:
                gas_bsc = max_gas_bsc
            log.info(f'Сеть BSC, gas = {gas_bsc}\n')
            dick['gasPrice'] = Web3.to_wei(gas_bsc, 'gwei')
        else:
            dick['gasPrice'] = web3.eth.gas_price

        swap_txn = stargate_contract.functions.swap(
            chain_to_stg['stg id'], source_pool_id, dest_pool_id, refund_address, amount_in, amount_out_min,
            lz_tx_obj, to, data).build_transaction(dick)
        gas = web3.eth.estimate_gas(swap_txn)
        time.sleep(1)
        swap_txn.update({'gas': int(gas * 1.3)})
        signed_txn = web3.eth.account.sign_transaction(swap_txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0

        log.info(f'Stargate bridge from {chain_from_not_stg["name"]} to {chain_to_stg["name"]} || {chain_from_not_stg["scan"]}{hash_}\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'cannot swap 0' in error.args[0]:
                log.info('Критическая, нет usd для трансфера')
            elif 'is not in the chain after' in error.args[0]:
                log.info(f'Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
                gas += gas_step
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def stargate_bridge_stg(private_key, chain_to_stg, chain_from_not_stg, token_name, value, gas, log):
    try:
        web3 = Web3(Web3.HTTPProvider(chain_from_not_stg['rpc']))
        account = web3.eth.account.from_key(private_key)
        address_wallet = account.address
        stargate_contract = web3.eth.contract(address=chain_from_not_stg['stg token'], abi=Stargate.token_abi)
        token_contract = web3.eth.contract(address=chain_from_not_stg[token_name], abi=Token.abi)
        tx_param = '0x00010000000000000000000000000000000000000000000000000000000000014c08'
        # Check allowance
        time.sleep(2)
        decimal = token_contract.functions.decimals().call()
        allowance = token_contract.functions.allowance(address_wallet, chain_from_not_stg['stg token']).call()
        if allowance < 1000000 * 10 ** decimal:
            log.info('Нужен аппрув, делаю')
            for _ in range(20):
                res_ = approve(private_key, chain_from_not_stg, chain_from_not_stg[token_name],
                               chain_from_not_stg['stg token'], gas, log)
                if res_ == 1:
                    break
            time.sleep(25)

        token_balance = token_contract.functions.balanceOf(address_wallet).call()

        if token_balance == 0:
            log.info(f'На аккаунте {address_wallet} нет токенов для бриджа')
            return 'error'

        value = value * 10 ** decimal

        if value > token_balance:
            amount_in = token_balance
        else:
            amount_in = int(value)

        zero_param = '0x0000000000000000000000000000000000000000'
        fees = stargate_contract.functions.estimateSendTokensFee(chain_to_stg['stg id'], True, tx_param).call()
        balance = web3.eth.get_balance(address_wallet)
        if int(fees[0] * 1.1) > int(balance):
            raise ValueError(error_balance)
        dick = {
            'from': address_wallet,
            'value': int(fees[0] * 1.05),
            'nonce': web3.eth.get_transaction_count(address_wallet)
        }
        if chain_from_not_stg['name'] == 'BSC':
            gas_bsc = min_gas_bsc + gas
            if gas_bsc > max_gas_bsc:
                gas_bsc = max_gas_bsc
            log.info(f'Сеть BSC, gas = {gas_bsc}\n')
            dick['gasPrice'] = Web3.to_wei(gas_bsc, 'gwei')
        else:
            dick['gasPrice'] = web3.eth.gas_price

        swap_txn = stargate_contract.functions.sendTokens(chain_to_stg['stg id'], address_wallet, amount_in, zero_param,
                                                          tx_param).build_transaction(dick)
        signed_txn = web3.eth.account.sign_transaction(swap_txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0

        log.info(f'Stargate bridge from {chain_from_not_stg["name"]} to {chain_to_stg["name"]} || {chain_from_not_stg["scan"]}{hash_}\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'cannot swap 0' in error.args[0]:
                log.info('Критическая, нет usd для трансфера')
            elif 'is not in the chain after' in error.args[0]:
                log.info(f'Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
                gas += gas_step
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def aptos_bridge(private_key, chain, address, value, gas, log):
    try:
        web3 = Web3(Web3.HTTPProvider(chain['rpc']))
        account = web3.eth.account.from_key(private_key)
        address_wallet = account.address
    except Exception as error:
        log.info(error)
        time.sleep(60)
        return 0
    try:
        aptos_contract = web3.eth.contract(address=chain['address aptos'], abi=Aptos.abi)
        token_contract = web3.eth.contract(address=chain['usdt'], abi=Token.abi)
        call_params = (address_wallet, '0x0000000000000000000000000000000000000000')
        adapter_params = '0x000200000000000000000000000000000000000000000000000000000000000027100000000000000000000000000\
000000000000000000000000000000000000000' + address[2:]
        allowance = token_contract.functions.allowance(address_wallet, chain['address aptos']).call()
        decimal = token_contract.functions.decimals().call()
        if allowance < 1000000 * 10 ** decimal:
            log.info('Нужен аппрув, делаю')
            for _ in range(20):
                res_ = approve(private_key, chain, chain['usdt'], chain['address aptos'], gas, log)
                if res_ == 1:
                    break
            time.sleep(25)
        fee = aptos_contract.functions.quoteForSend(call_params, adapter_params).call()
        balance = web3.eth.get_balance(address_wallet)
        if int(fee[0] * 1.1) > int(balance):
            raise ValueError(error_balance)

        dick = {
            'from': address_wallet,
            'value': fee[0],
            'nonce': web3.eth.get_transaction_count(address_wallet)
        }
        if chain['name'] == 'BSC':
            gas_bsc = min_gas_bsc + gas
            if gas_bsc > max_gas_bsc:
                gas_bsc = max_gas_bsc
            log.info(f'Сеть BSC, gas = {gas_bsc}\n')
            dick['gasPrice'] = Web3.to_wei(gas_bsc, 'gwei')
        else:
            dick['gasPrice'] = web3.eth.gas_price

        amount = int(value * 10 ** decimal)
        token_balance = token_contract.functions.balanceOf(address_wallet).call()
        if amount > token_balance:
            amount = token_balance
        swap_txn = aptos_contract.functions.sendToAptos(chain['usdt'], address, amount, call_params,
                                                        adapter_params).build_transaction(dick)
        signed_txn = web3.eth.account.sign_transaction(swap_txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0

        log.info(f'Aptos bridge || {chain["scan"]}{hash_}\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'cannot swap 0' in error.args[0]:
                log.info('Критическая, нет usd для трансфера')
            elif 'is not in the chain after' in error.args[0]:
                log.info(f'Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
                gas += gas_step
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0


def withdrawl_eur(private_key, chain, log):
    try:
        web3 = Web3(Web3.HTTPProvider(chain['rpc']))
        account = web3.eth.account.from_key(private_key)
        address_wallet = account.address
    except Exception as error:
        log.info(error)
        time.sleep(60)
        return 0

    try:
        lz_eur_address = chain['lz eur']
        abi = js.load(open('./abi/withdrawl_eur.txt'))
        lz_eur_contract = web3.eth.contract(address=lz_eur_address, abi=abi)
        balance = lz_eur_contract.functions.balanceOf(address_wallet).call()
        dick = {
            'from': address_wallet,
            'nonce': web3.eth.get_transaction_count(address_wallet),
            'gasPrice': web3.eth.gas_price
        }
        contract_txn = lz_eur_contract.functions.withdraw(balance, address_wallet).build_transaction(dick)
        signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        log.info('Отправил транзакцию')
        hash_ = str(web3.to_hex(tx_hash))
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=time_transaction, poll_latency=30)
        if tx_receipt.status == 1:
            log.info(f'Транзакция смайнилась успешно')
        else:
            log.info(f'Транзакция сфейлилась, пытаюсь еще раз')
            return 0

        log.info(f'Withdrawl LayerZero Bridge agEUR || {chain["scan"]}{hash_}\n')
        return 1
    except Exception as error:
        log.info('Произошла ошибка')
        if isinstance(error.args[0], str):
            if 'cannot swap 0' in error.args[0]:
                log.info('Критическая, нет usd для трансфера')
            elif 'is not in the chain after' in error.args[0]:
                log.info(f'Транзакция не смайнилась {time_transaction} секунд. Пытаюсь еще раз\n')
            else:
                log.info(f'{error}\n')
        elif isinstance(error.args[0], dict):
            if 'insufficient funds for' in error.args[0]['message']:
                log.info('Ошибка, скорее всего нехватает комсы')
            elif 'execute this request' in error.args[0]['message']:
                log.info('Ошибка запроса на RPC, пытаюсь еще раз')
            else:
                log.info(f'{error}\n')
        else:
            log.info(f'{error}\n')
        time.sleep(35)
        return 0
