"""
 DEX SWAP Main
"""

import logging

import requests
from dxsp import __version__
from dxsp.config import settings

from pycoingecko import CoinGeckoAPI
from web3 import Web3


class DexSwap:
    """swap  class"""

    def __init__(self, w3: Web3 | None = None,):
        """build a dex object """
        self.logger = logging.getLogger(name="DexSwap")
        self.logger.info("DexSwap: %s", __version__)

        self.w3 = w3 or Web3(Web3.HTTPProvider(settings.dex_rpc))
        try:
            if self.w3.net.listening:
                self.logger.info("connected %s", self.w3)
        except Exception as e:
            self.logger.error("connectivity failed %s", e)
            return

        self.protocol_type = settings.dex_protocol_type
        self.chain_id = settings.dex_chain_id
        # USER
        self.wallet_address = self.w3.to_checksum_address(
            settings.dex_wallet_address)
        self.private_key = settings.dex_private_key

        # COINGECKO 🦎
        try:
            self.cg = CoinGeckoAPI()
            assetplatform = self.cg.get_asset_platforms()
            output_dict = [x for x in assetplatform if x['chain_identifier']
                           == int(self.chain_id)]
            self.cg_platform = output_dict[0]['id']
            self.logger.debug("cg_platform %s", self.cg_platform)
        except Exception as e:
            self.logger.error("CG🦎: %s", e)

    async def get_quote(
                self,
                symbol
            ):
        self.logger.debug("get_quote")
        asset_in_address = await self.search_contract(symbol)
        asset_out_symbol = settings.trading_quote_ccy
        asset_out_address = await self.search_contract(asset_out_symbol)
        if asset_out_address is None:
            self.logger.warning("No Valid Contract")
            return
        try:
            if self.protocol_type in ["uniswap_v2", "uniswap_v3"]:
                self.logger.debug("uniswap getquote")
                return await self.get_quote_uniswap(
                    asset_in_address,
                    asset_out_address)
            if self.protocol_type == "0x":
                self.logger.debug("0x getquote")
                return await self.get_quote_0x(
                    asset_in_address,
                    asset_out_address,)

        except Exception as e:
            self.logger.error("get_quote %s", e)
            return

    async def get_swap(
                self,
                asset_out_symbol: str,
                asset_in_symbol: str,
                amount: int,
                ):
        """main swap function"""

        self.logger.debug("get_swap")
        try:
            # ASSET OUT
            asset_out_address = await self.search_contract(
                asset_out_symbol)
            asset_out_contract = await self.get_token_contract(
                asset_out_symbol)
            if asset_out_contract is None:
                raise ValueError("No contract identified")
            asset_out_balance = await self.get_token_balance(asset_out_symbol)
            if asset_out_balance == (0 or None):
                raise ValueError("No Money")
            # ASSETS IN
            asset_in_address = await self.search_contract(asset_in_symbol)
            self.logger.debug("asset_in_address %s", asset_in_address)
            if asset_in_address is None:
                return

            # AMOUNT
            asset_out_decimals = asset_out_contract.functions.decimals().call()
            self.logger.debug("asset_out_decimals %s", asset_out_decimals)
            asset_out_amount = amount * 10 ** asset_out_decimals
            asset_out_amount_converted = self.w3.to_wei(
                asset_out_amount, 'ether')

            order_amount = int(
                (asset_out_amount_converted *
                 (settings.dex_trading_slippage/100)))
            self.logger.debug("order_amount %s", order_amount)

            # VERIFY IF ASSET OUT IS APPROVED otherwise get it approved
            if await self.get_approve(asset_out_address) is None:
                return

            # UNISWAP V2
            if self.protocol_type in ["uniswap_v2", "uniswap_v3"]:
                swap_order = await self.get_swap_uniswap(
                    asset_out_address,
                    asset_in_address,
                    order_amount)
            # 0x
            elif self.protocol_type == "0x":
                swap_order = await self.get_quote_0x(
                    asset_out_address,
                    asset_in_address,
                    order_amount)
                await self.get_sign(swap_order)

            if swap_order:
                self.logger.debug("swap_order %s", swap_order)
                signed_order = await self.get_sign(swap_order)
                order_hash = str(self.w3.to_hex(signed_order))
                order_hash_details = self.w3.wait_for_transaction_receipt(
                                        order_hash,
                                        timeout=120,
                                        poll_latency=0.1)
                if order_hash_details['status'] == "1":
                    await self.get_confirmation(
                        order_hash,
                        order_hash_details,
                        asset_out_symbol,
                        asset_out_address,
                        order_amount,)
        except Exception as e:
            self.logger.error("get_swap %s", e)
            return

    async def get_confirmation(self,
                               order_hash,
                               order_hash_details,
                               asset_out_symbol,
                               asset_out_address,
                               order_amount,
                               ):
        """ trade confirmation function"""
        self.logger.debug("get_confirmation")
        try:
            trade_blockNumber = order_hash_details['blockNumber']
            trade_receipt = self.w3.eth.get_transaction_receipt(order_hash)
            trade_block = self.w3.eth.get_block(trade_blockNumber)
            trade = {}
            trade['id'] = trade_receipt['transactionHash']
            trade['timestamp'] = trade_block['timestamp']
            trade['instrument'] = asset_out_symbol
            trade['contract'] = asset_out_address
            trade['amount'] = order_amount
            trade['fee'] = trade_receipt['gasUsed']
            trade['price'] = "TBD"
            trade['confirmation'] += f"➕ Size: {round(trade['amount'],4)}\n"
            trade['confirmation'] += f"⚫️ Entry: {round(trade['price'],4)}\n"
            trade['confirmation'] += f"ℹ️ {trade['id']}\n"
            trade['confirmation'] += f"🗓️ {trade['datetime']}"
            self.logger.info("trade %s", trade)
            return trade
        except Exception as e:
            self.logger.error("get_confirmation %s", e)
            return

    async def execute_order(self, order_params):
        """execute swap function"""
        action = order_params.get('action')
        instrument = order_params.get('instrument')
        quantity = order_params.get('quantity', 1)

        try:
            asset_out_symbol = (
                settings.trading_quote_ccy if
                action == "BUY" else instrument)
            asset_in_symbol = (
                instrument if action == "BUY"
                else settings.trading_quote_ccy)
            try:
                asset_out_contract = await self.get_token_contract(
                    asset_out_symbol)
                asset_out_decimals = (
                    asset_out_contract.functions.decimals().call()
                    or 18)
            except Exception as e:
                self.logger.error("execute_order decimals: %s", e)
                asset_out_decimals = 18
            asset_out_balance = await self.get_token_balance(asset_out_symbol)

            #  Amount to risk percentage - DEFAULT OPTION is 10%
            asset_out_amount = (
                (asset_out_balance) /
                (settings.trading_risk_amount
                 ** asset_out_decimals)
                )*(float(quantity)/100)

            order = await self.get_swap(
                    asset_out_symbol,
                    asset_in_symbol,
                    asset_out_amount
                    )
            if order:
                return order['confirmation']

        except Exception as e:
            self.logger.debug("error execute_order %s", e)
            return "error processing order in DXSP"

# 📝CONTRACT SEARCH
    # async def search_contract(
    #                         self,
    #                         token
    #                         ):
    #     """search a contract function"""
    #     self.logger.debug("search_contract")

    #     try:
    #         token_contract = await self.get_contract_address(
    #             settings.token_personal_list,
    #             token)
    #         if token_contract is None:
    #             token_contract = await self.get_contract_address(
    #                 settings.token_testnet_list,
    #                 token)
    #             if token_contract is None:
    #                 token_contract = await self.get_contract_address(
    #                     settings.token_mainnet_list,
    #                     token)
    #                 if token_contract is None:
    #                     token_contract = await self.search_cg_contract(
    #                         token)
    #         if token_contract is not None:
    #             self.logger.info("%s token: contract found %s",
    #                              token, token_contract)
    #             return self.w3.to_checksum_address(token_contract)
    #         return f"no contract found for {token}"
    #     except Exception as e:
    #         self.logger.error("search_contract %s", e)
    #         return
    async def search_contract(self, token):
        """search a contract function"""
        self.logger.debug("search_contract")

        try:
            contract_lists = [
                settings.token_personal_list,
                settings.token_testnet_list,
                settings.token_mainnet_list,
            ]

            for contract_list in contract_lists:
                token_contract = await self.get_contract_address(
                    contract_list,
                    token
                )
                if token_contract is not None:
                    self.logger.info("%s token: contract found %s",
                                     token, token_contract)
                    return self.w3.to_checksum_address(token_contract)

            token_contract = await self.search_cg_contract(token)
            if token_contract is not None:
                self.logger.info("%s token: contract found %s",
                                 token, token_contract)
                return self.w3.to_checksum_address(token_contract)

            return f"no contract found for {token}"
        except Exception as e:
            self.logger.error("search_contract %s", e)
            return

    async def search_cg(self, token):
        """search coingecko"""
        try:
            search_results = self.cg.search(query=token)
            search_dict = search_results['coins']
            filtered_dict = [x for x in search_dict if
                             x['symbol'] == token.upper()]
            api_dict = [sub['api_symbol'] for sub in filtered_dict]
            for i in api_dict:
                coin_dict = self.cg.get_coin_by_id(i)
                try:
                    if coin_dict['platforms'][f'{self.cg_platform}']:
                        return coin_dict
                except (KeyError, requests.exceptions.HTTPError):
                    pass
        except Exception as e:
            self.logger.error("search_cg %s", e)
            return

    async def search_cg_contract(self, token):
        """search coingecko contract"""
        try:
            coin_info = await self.search_cg(token)
            return (coin_info['platforms'][f'{self.cg_platform}']
                    if coin_info is not None else None)
        except Exception as e:
            self.logger.error(" search_cg_contract: %s", e)
            return

    async def get_contract_address(self, token_list_url, symbol):
        """Given a token symbol and json tokenlist, get token address"""
        try:
            token_list = await self._get(token_list_url)
            token_search = token_list['tokens']
            for keyval in token_search:
                if (keyval['symbol'] == symbol and
                   keyval['chainId'] == self.chain_id):
                    return keyval['address']
        except Exception as e:
            self.logger.debug("get_contract_address %s", e)
            return

    async def get_token_contract(self, token):
        """Given a token symbol, returns a contract object. """
        self.logger.debug("get_token_contract %s", token)
        try:
            token_address = await self.search_contract(token)
            token_abi = await self.get_abi(token_address)
            if token_abi is None:
                self.logger.debug("using setting dex_erc20_abi_url")
                token_abi = requests.get(settings.dex_erc20_abi_url).text
            return self.w3.eth.contract(
                address=token_address,
                abi=token_abi)
        except Exception as e:
            self.logger.error("get_token_contract %s", e)
            return

# 🛠️ W3 UTILS
    async def _get(
        self,
        url,
        params=None,
        headers=None
            ):
        try:
            self.logger.debug("url: %s", url)
            # self.logger.debug("_header: %s", settings.headers)
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10)
            # self.logger.debug("_response: %s", response)
            if response:
                # self.logger.debug("_json: %s", response.json())
                return response.json()

        except Exception as e:
            self.logger.error("_get: %s", e)

    async def router(self):
        try:
            router_abi = await self.get_abi(settings.dex_router_contract_addr)
            if router_abi is None:
                self.logger.debug("using setting dex_router_abi_url")
                router_abi = requests.get(settings.dex_router_abi_url).text
            self.logger.debug("router_abi: %s", router_abi)
            router = self.w3.eth.contract(
                address=self.w3.to_checksum_address(
                    settings.dex_router_contract_addr),
                abi=router_abi)
            return router
        except Exception as e:
            self.logger.error("router setup: %s", e)

    async def quoter(self):
        try:
            quoter_abi = await self.get_abi(settings.dex_quoter_contract_addr)
            self.logger.debug("quoter_abi: %s", quoter_abi)
            quoter = self.w3.eth.contract(
                address=self.w3.to_checksum_address(
                    settings.dex_quoter_contract_addr),
                abi=quoter_abi)
            return quoter
        except Exception as e:
            self.logger.error("quoter setup: %s", e)

    async def get_approve(self, asset_out_address):

        try:
            if self.protocol_type in ["uniswap_v2", "uniswap_v3"]:
                await self.get_approve_uniswap(asset_out_address)
        except Exception as e:
            self.logger.error("get_approve %s", e)
            return None

    async def get_sign(self, transaction):

        try:
            self.logger.debug("get_sign: transaction %s", transaction)
            if self.protocol_type in ['uniswap_v2', 'uniswap_v3']:
                transaction_params = {
                            'from': self.wallet_address,
                            'gas': await self.get_gas(transaction),
                            'gasPrice': await self.get_gasPrice(transaction),
                            'nonce': self.w3.eth.get_transaction_count(
                                self.wallet_address),
                            }
                transaction = transaction.build_transaction(transaction_params)
            signed = self.w3.eth.account.sign_transaction(
                transaction,
                settings.dex_private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            return tx_hash
        except (ValueError, TypeError, KeyError) as e:
            self.logger.error("get_sign: %s", e)
            raise
        except Exception as e:
            self.logger.error("get_sign: %s", e)
            raise RuntimeError("Failed to sign transaction")

    async def get_gas(
        self,
        tx
         ):
        # Log the transaction
        self.logger.debug("get_gas %s", tx)
        # Estimate the gas cost of the transaction
        gasestimate = self.w3.eth.estimate_gas(tx) * 1.25
        # Return the estimated gas cost in wei
        return int(self.w3.to_wei(gasestimate, 'wei'))

    async def get_gasPrice(self, tx):
        '''
        Get the gas price for a transaction
        '''
        gasprice = self.w3.eth.generate_gas_price()
        return self.w3.to_wei(gasprice, 'gwei')

    async def get_abi(self, addr):
        # Log a debug message to the logger
        self.logger.debug("get_abi %s", addr)
        if settings.dex_block_explorer_api:
            try:
                # Create a dictionary of parameters
                params = {
                    "module": "contract",
                    "action": "getabi",
                    "address": addr,
                    "apikey": settings.dex_block_explorer_api
                    }
                # Make a GET request to the block explorer URL
                resp = await self._get(
                    url=settings.dex_block_explorer_url,
                    params=params,)
                # If the response status is 1, log the ABI
                if resp['status'] == "1":
                    self.logger.debug("ABI found %s", resp)
                    abi = resp["result"]
                    return abi
                # If no ABI is identified, log a warning
                self.logger.warning("No ABI identified")
                return None
            except Exception as e:
                # Log an error
                self.logger.error("get_abi %s", e)
                return None
        else:
            # If no block_explorer_api is set, log a warning
            self.logger.warning("No block_explorer_api.")
            return

    async def get_block_explorer_status(self, txHash):
        try:
            if settings.block_explorer_api:
                checkTransactionSuccessURL = (
                    settings.block_explorer_url
                    + "?module=transaction&action=gettxreceiptstatus&txhash="
                    + str(txHash)
                    + "&apikey="
                    + str(settings.block_explorer_api))
                checkTransactionRequest = self._get(checkTransactionSuccessURL)
                return checkTransactionRequest['status']
        except Exception as e:
            self.logger.error("get_block_explorer_status %s", e)
            return
# 🔒 USER RELATED

    async def get_token_balance(
        self,
        token
         ):

        try:
            token_contract = await self.get_token_contract(token)
            token_balance = 0
            token_balance = token_contract.functions.balanceOf(
                self.wallet_address).call()
            return 0 if token_balance <= 0 else token_balance
        except Exception as e:
            self.logger.error("get_token_balance: %s", e)
            return 0

    async def get_account_balance(
        self
         ):

        try:
            balance = self.w3.eth.get_balance(
                self.w3.to_checksum_address(
                    self.wallet_address))
            balance = (self.w3.from_wei(balance, 'ether'))
            try:
                trading_quote_ccy_balance = (
                    await self.get_trading_quote_ccy_balance())
                if trading_quote_ccy_balance:
                    balance += "💵" + trading_quote_ccy_balance
            except Exception:
                pass

            return round(balance, 5)

        except Exception as e:
            self.logger.error("get_account_balance: %s", e)
            return 0

    async def get_trading_quote_ccy_balance(
        self
         ):

        try:
            trading_quote_ccy_balance = await self.get_token_balance(
                settings.trading_quote_ccy)
            if trading_quote_ccy_balance:
                return trading_quote_ccy_balance
            return 0
        except Exception as e:
            self.logger.error("quote_ccy_balance: %s", e)
            return 0

    async def get_account_position(
        self
         ):

        try:
            self.logger.debug("get_account_position")
            return
        except Exception as e:
            self.logger.error("get_account_position: %s", e)
            return 0

    async def get_account_margin(
        self
         ):

        try:
            self.logger.debug("get_account_margin")
            return
        except Exception as e:
            self.logger.error("get_account_margin: %s", e)
            return 0

# PROTOCOL SPECIFIC
# uniswap  🦄
    async def get_quote_uniswap(
        self,
        asset_in_address,
        asset_out_address,
        amount=1
    ):
        self.logger.debug("get_quote_uniswap")
        try:
            if self.protocol_type == "uniswap_v2":
                router_instance = await self.router()
                quote = router_instance.functions.getAmountsOut(
                    amount,
                    [asset_in_address, asset_out_address]).call()
                self.logger.error("quote %s", quote)
                if isinstance(quote, list):
                    quote = str(quote[0])
            elif self.protocol_type == "uniswap_v3":
                quoter = await self.quoter()
                sqrtPriceLimitX96 = 0
                fee = 3000
                quote = quoter.functions.quoteExactInputSingle(
                    asset_in_address,
                    asset_out_address,
                    fee, amount, sqrtPriceLimitX96).call()
            return ("🦄 " + quote + " " +
                    settings.trading_quote_ccy)
        except Exception as e:
            self.logger.error("get_quote_uniswap %s", e)
            return

    async def get_approve_uniswap(self, asset_out_address):

        try:
            asset_out_abi = await self.get_abi(asset_out_address)
            asset_out_contract = self.w3.eth.contract(
                address=asset_out_address,
                abi=asset_out_abi)
            approval_check = asset_out_contract.functions.allowance(
                            self.w3.to_checksum_address(self.wallet_address),
                            self.w3.to_checksum_address(
                                settings.dex_router_contract_addr)
                            ).call()
            self.logger.debug("approval_check %s", approval_check)
            if (approval_check == 0):
                approved_amount = (self.w3.to_wei(2**64-1, 'ether'))
                approval_transaction = asset_out_contract.functions.approve(
                                self.w3.to_checksum_address(
                                    settings.dex_router_contract_addr),
                                approved_amount)
                self.logger.debug("approval_TX %s", approval_transaction)
                approval_txHash = await self.get_sign(approval_transaction)
                self.logger.debug("approval_txHash %s", approval_txHash)
                approval_txHash_complete = (
                    self.w3.eth.wait_for_transaction_receipt(
                        approval_txHash,
                        timeout=120,
                        poll_latency=0.1))
                return approval_txHash_complete
        except Exception as e:
            self.logger.error("get_approve_uniswap %s", e)
            return None

    async def get_swap_uniswap(
        self,
        asset_out_address,
        asset_in_address,
        amount
    ):
        try:
            if self.protocol_type == "uniswap_v2":
                order_path_dex = [asset_out_address, asset_in_address]

                deadline = self.w3.eth.get_block("latest")["timestamp"] + 3600
                order_min_amount = self.get_quote_uniswap(
                    asset_in_address,
                    asset_out_address,
                    amount)[0]
                router_instance = await self.router()
                swap_order = (
                    router_instance.functions.swapExactTokensForTokens(
                        amount, order_min_amount,
                        order_path_dex, self.wallet_address,
                        deadline))
                return swap_order
            if self.protocol_type == "uniswap_v3":
                return None
        except Exception as e:
            self.logger.error("get_approve_uniswap %s", e)

# 0️⃣x
    async def get_quote_0x(
        self,
        asset_in_address,
        asset_out_address,
        amount=1
    ):
        try:
            asset_out_amount = self.w3.to_wei(amount, 'ether')

            quote_url = (
                settings.dex_0x_url
                + "/swap/v1/quote?buyToken="
                + str(asset_in_address)
                + "&sellToken="
                + str(asset_out_address)
                + "&buyAmount="
                + str(asset_out_amount))
            quote_response = await self._get(
                quote_url,
                params=None,
                headers={"0x-api-key": settings.dex_0x_api_key}
                )
            self.logger.debug("quote_response %s", quote_response)
            if quote_response:
                quote = quote_response['guaranteedPrice']
                self.logger.debug("quote_amount %s", quote)
                return round(float(quote), 3)
        except Exception as e:
            self.logger.error("get_quote_0x %s", e)
