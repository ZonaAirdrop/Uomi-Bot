from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from eth_abi.abi import encode
from eth_utils import to_bytes
from datetime import datetime
from colorama import init, Fore, Style
import asyncio, random, time, json, re, os
from dotenv import load_dotenv

init(autoreset=True)
load_dotenv()

class Colors:
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    WHITE = Fore.WHITE
    BRIGHT_GREEN = Fore.LIGHTGREEN_EX
    BRIGHT_MAGENTA = Fore.LIGHTMAGENTA_EX
    BRIGHT_WHITE = Fore.LIGHTWHITE_EX
    BRIGHT_BLACK = Fore.LIGHTBLACK_EX
    BLUE = Fore.BLUE

class Logger:
    @staticmethod
    def log(label, symbol, msg, color):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {color}[{symbol}] {msg}{Colors.RESET}")

    @staticmethod
    def info(msg): Logger.log("INFO", "✓", msg, Colors.GREEN)
    @staticmethod
    def warn(msg): Logger.log("WARN", "!", msg, Colors.YELLOW)
    @staticmethod
    def error(msg): Logger.log("ERR", "✗", msg, Colors.RED)
    @staticmethod
    def success(msg): Logger.log("OK", "+", msg, Colors.GREEN)
    @staticmethod
    def loading(msg): Logger.log("LOAD", "⟳", msg, Colors.CYAN)
    @staticmethod
    def step(msg): Logger.log("STEP", "➤", msg, Colors.WHITE)
    @staticmethod
    def action(msg): Logger.log("ACTION", "↪️", msg, Colors.CYAN)
    @staticmethod
    def actionSuccess(msg): Logger.log("ACTION", "✅", msg, Colors.GREEN)

logger = Logger()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

async def display_welcome_screen():
    clear_console()
    now = datetime.now()
    print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}")
    print("  ╔══════════════════════════════════════╗")
    print("  ║           UOMI  B O T                      ║")
    print("  ║                                      ║")
    print(f"  ║      {Colors.YELLOW}{now.strftime('%H:%M:%S %d.%m.%Y')}{Colors.BRIGHT_GREEN}            ║")
    print("  ║                                      ║")
    print("  ║      uomi TESTNET AUTOMATION        ║")
    print(f"  ║   {Colors.BRIGHT_WHITE}ZonaAirdrop{Colors.BRIGHT_GREEN}  |  t.me/ZonaAirdr0p   ║")
    print("  ╚══════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    await asyncio.sleep(1)

class UOMI:
    def __init__(self) -> None:
        self.RPC_URL = "https://finney.uomi.ai/"
        self.WUOMI_CONTRACT_ADDRESS = "0x5FCa78E132dF589c1c799F906dC867124a2567b2"
        self.USDC_CONTRACT_ADDRESS = "0xAA9C4829415BCe70c434b7349b628017C59EC2b1"
        self.SYN_CONTRACT_ADDRESS = "0x2922B2Ca5EB6b02fc5E1EBE57Fc1972eBB99F7e0"
        self.SIM_CONTRACT_ADDRESS = "0x04B03e3859A25040E373cC9E8806d79596D70686"
        self.PERMIT_ROUTER_ADDRESS = "0x000000000022D473030F116dDEE9F6B43aC78BA3"
        self.EXECUTE_ROUTER_ADDRESS = "0x197EEAd5Fe3DB82c4Cd55C5752Bc87AEdE11f230"
        self.POSITION_ROUTER_ADDRESS = "0x906515Dc7c32ab887C8B8Dce6463ac3a7816Af38"
        self.QUOTER_ROUTER_ADDRESS = "0xCcB2B2F8395e4462d28703469F84c95293845332"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"deposit","stateMutability":"payable","inputs":[],"outputs":[]},
            {"type":"function","name":"withdraw","stateMutability":"nonpayable","inputs":[{"name":"wad","type":"uint256"}],"outputs":[]}
        ]''')
        self.UOMI_CONTRACT_ABI = [
            {
                "type": "function",
                "name": "quoteExactInput",
                "stateMutability": "nonpayable",
                "inputs": [
                    { "internalType": "bytes", "name": "path", "type": "bytes" },
                    { "internalType": "uint256", "name": "amountIn", "type": "uint256" }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "amountOut", "type": "uint256" }
                ]
            },
            {
                "type": "function",
                "name": "execute",
                "stateMutability": "payable",
                "inputs": [
                    { "internalType": "bytes", "name": "commands", "type": "bytes" },
                    { "internalType": "bytes[]", "name": "inputs", "type": "bytes[]" },
                    { "internalType": "uint256", "name": "deadline", "type": "uint256" }
                ],
                "outputs": []
            },
            {
                "type": "function",
                "name": "mint",
                "stateMutability": "nonpayable",
                "inputs": [
                    {
                        "type": "tuple",
                        "name": "params",
                        "internalType": "struct INonfungiblePositionManager.MintParams",
                        "components": [
                            { "internalType": "address", "name": "token0", "type": "address" },
                            { "internalType": "address", "name": "token1", "type": "address" },
                            { "internalType": "uint24", "name": "fee", "type": "uint24" },
                            { "internalType": "int24", "name": "tickLower", "type": "int24" },
                            { "internalType": "int24", "name": "tickUpper", "type": "int24" },
                            { "internalType": "uint256", "name": "amount0Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Desired", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount0Min", "type": "uint256" },
                            { "internalType": "uint256", "name": "amount1Min", "type": "uint256" },
                            { "internalType": "address", "name": "recipient", "type": "address" },
                            { "internalType": "uint256", "name": "deadline", "type": "uint256" }
                        ]
                    }
                ],
                "outputs": [
                    { "internalType": "uint256", "name": "tokenId", "type": "uint256" },
                    { "internalType": "uint128", "name": "liquidity", "type": "uint128" },
                    { "internalType": "uint256", "name": "amount0", "type": "uint256" },
                    { "internalType": "uint256", "name": "amount1", "type": "uint256" }
                ]
            }
        ]
        self.used_nonce = {}
        self.wrap_option = 0
        self.wrap_amount = 0
        self.swap_count = 0
        self.min_swap_amount = 0
        self.max_swap_amount = 0
        self.liquidity_count = 0
        self.wuomi_amount = 0
        self.syn_amount = 0
        self.sim_amount = 0
        self.min_delay = 0
        self.max_delay = 0

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            return address
        except Exception as e:
            logger.error(f"Generate Address Failed - {str(e)}")
            return None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None

    def generate_swap_option(self):
        swap_options = [
            ("UOMI to USDC", self.WUOMI_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS),
            ("UOMI to SYN", self.WUOMI_CONTRACT_ADDRESS, self.SYN_CONTRACT_ADDRESS),
            ("UOMI to SIM", self.WUOMI_CONTRACT_ADDRESS, self.SIM_CONTRACT_ADDRESS)
        ]

        swap_option, from_token, to_token = random.choice(swap_options)

        amount_in = round(random.uniform(self.min_swap_amount, self.max_swap_amount), 6)

        return swap_option, from_token, to_token, amount_in

    def generate_liquidity_option(self):
        swap_options = [
            ("WUOMI", "USDC", self.WUOMI_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, self.wuomi_amount),
            ("SYN", "WUOMI", self.SYN_CONTRACT_ADDRESS, self.WUOMI_CONTRACT_ADDRESS, self.syn_amount),
            ("SYN", "USDC", self.SYN_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, self.syn_amount),
            ("SIM", "WUOMI", self.SIM_CONTRACT_ADDRESS, self.WUOMI_CONTRACT_ADDRESS, self.sim_amount),
            ("SIM", "USDC", self.SIM_CONTRACT_ADDRESS, self.USDC_CONTRACT_ADDRESS, self.sim_amount),
            ("SIM", "SYN", self.SIM_CONTRACT_ADDRESS, self.SYN_CONTRACT_ADDRESS, self.sim_amount)
        ]

        ticker0, ticker1, token0, token1, amount0 = random.choice(swap_options)

        liquidity_option = f"{ticker0}/{ticker1}"

        amount0_desired = int(amount0 * (10 ** 18))

        return liquidity_option, ticker0, ticker1, token0, token1, amount0_desired
        
    async def get_web3_instance(self, retries=3, timeout=60):
        request_kwargs = {"timeout": timeout}
        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL, request_kwargs=request_kwargs))
                web3.eth.get_block_number() # Test connection
                return web3
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                raise Exception(f"Failed to Connect to RPC: {str(e)}")
            
    async def send_raw_transaction_with_retries(self, account_key, web3, tx, retries=5):
        account = Account.from_key(account_key)
        for attempt in range(retries):
            try:
                signed_tx = web3.eth.account.sign_transaction(tx, account.key)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                return tx_hash
            except TransactionNotFound:
                pass
            except Exception as e:
                logger.warn(f"[Attempt {attempt + 1}] Send TX Error: {str(e)}")
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Hash Not Found After Maximum Retries")

    async def wait_for_receipt_with_retries(self, web3, tx_hash, retries=5):
        for attempt in range(retries):
            try:
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                return receipt
            except TransactionNotFound:
                pass
            except Exception as e:
                logger.warn(f"[Attempt {attempt + 1}] Wait for Receipt Error: {str(e)}")
            await asyncio.sleep(2 ** attempt)
        raise Exception("Transaction Receipt Not Found After Maximum Retries")
        
    async def get_token_balance(self, address: str, contract_address: str, retries=5):
        for attempt in range(retries):
            try:
                web3 = await self.get_web3_instance()

                if contract_address == "UOMI":
                    balance = web3.eth.get_balance(address)
                    decimals = 18
                else:
                    token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
                    balance = token_contract.functions.balanceOf(address).call()
                    decimals = token_contract.functions.decimals().call()

                token_balance = balance / (10 ** decimals)

                return token_balance
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                logger.error(f"Failed to get token balance: {str(e)}")
                return None
        
    async def perform_wrapped(self, account: str, address: str):
        try:
            web3 = await self.get_web3_instance()

            contract_address = web3.to_checksum_address(self.WUOMI_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(self.wrap_amount, "ether")
            wrap_data = token_contract.functions.deposit()
            estimated_gas = wrap_data.estimate_gas({"from":address, "value":amount_to_wei})

            max_priority_fee = web3.to_wei(28.54, "gwei") # Example value, adjust as needed
            max_fee = max_priority_fee

            wrap_tx = wrap_data.build_transaction({
                "from": address,
                "value": amount_to_wei,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, wrap_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            self.used_nonce[address] += 1

            return tx_hash
        except Exception as e:
            logger.error(f"Wrapped operation failed: {str(e)}")
            return None
        
    async def perform_unwrapped(self, account: str, address: str):
        try:
            web3 = await self.get_web3_instance()

            contract_address = web3.to_checksum_address(self.WUOMI_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(self.wrap_amount, "ether")
            unwrap_data = token_contract.functions.withdraw(amount_to_wei)
            estimated_gas = unwrap_data.estimate_gas({"from":address})

            max_priority_fee = web3.to_wei(28.54, "gwei") # Example value, adjust as needed
            max_fee = max_priority_fee

            unwrap_tx = unwrap_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id,
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, unwrap_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            self.used_nonce[address] += 1

            return tx_hash
        except Exception as e:
            logger.error(f"Unwrapped operation failed: {str(e)}")
            return None
        
    async def approving_token(self, account: str, address: str, router_address: str, asset_address: str, amount_to_wei: int):
        try:
            web3 = await self.get_web3_instance()
            
            spender = web3.to_checksum_address(router_address)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(asset_address), abi=self.ERC20_CONTRACT_ABI)

            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount_to_wei:
                approve_data = token_contract.functions.approve(spender, 2**256 - 1)
                estimated_gas = approve_data.estimate_gas({"from": address})

                max_priority_fee = web3.to_wei(28.54, "gwei")
                max_fee = max_priority_fee

                approve_tx = approve_data.build_transaction({
                    "from": address,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": self.used_nonce[address],
                    "chainId": web3.eth.chain_id,
                })

                tx_hash = await self.send_raw_transaction_with_retries(account, web3, approve_tx)
                receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
                self.used_nonce[address] += 1

                explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
                
                logger.action(f"Thx Hash {tx_hash}")
                logger.success(f"Explore: {explorer}")
                await self.print_timer()

            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
    
    async def get_amount_out_min(self, address: str, path: str, amount_in_wei: int):
        try:
            web3 = await self.get_web3_instance()

            contract = web3.eth.contract(address=web3.to_checksum_address(self.QUOTER_ROUTER_ADDRESS), abi=self.UOMI_CONTRACT_ABI)

            amount_out = contract.functions.quoteExactInput(path, amount_in_wei).call()
            
            return amount_out
        except Exception as e:
            logger.error(f"Failed to get amount out min: {str(e)}")
            return None
        
    async def perform_swap(self, account: str, address: str, from_token: str, to_token: str, amount_in: float):
        try:
            web3 = await self.get_web3_instance()

            amount_in_wei = web3.to_wei(amount_in, "ether")

            commands = to_bytes(hexstr="0x0b00")

            wrap_eth = encode(
                ['address', 'uint256'],
                [
                    '0x0000000000000000000000000000000000000002',
                    amount_in_wei
                ]
            )

            path = bytes.fromhex(from_token[2:]) + (3000).to_bytes(3, "big") + bytes.fromhex(to_token[2:])

            amount_out_wei = await self.get_amount_out_min(address, path, amount_in_wei)
            if not amount_out_wei:
                raise Exception("GET Amount Out Min Failed")
            
            amount_out_min_wei = (amount_out_wei * (10000 - 50)) // 10000 # 0.5% slippage

            v3_swap_exact_in = encode(
                ['address', 'uint256', 'uint256', 'bytes', 'bool'],
                [
                    '0x0000000000000000000000000000000000000001',
                    amount_in_wei,
                    amount_out_min_wei,
                    path,
                    False
                ]
            )

            inputs = [wrap_eth, v3_swap_exact_in]

            deadline = int(time.time()) + 600

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.EXECUTE_ROUTER_ADDRESS), abi=self.UOMI_CONTRACT_ABI)

            swap_data = token_contract.functions.execute(commands, inputs, deadline)

            estimated_gas = swap_data.estimate_gas({"from": address, "value":amount_in_wei})

            max_priority_fee = web3.to_wei(28.54, "gwei")
            max_fee = max_priority_fee

            swap_tx = swap_data.build_transaction({
                "from": address,
                "value": amount_in_wei,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, swap_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            self.used_nonce[address] += 1

            return tx_hash
        except Exception as e:
            logger.error(f"Swap operation failed: {str(e)}")
            return None
        
    async def perform_liquidity(self, account: str, address: str, token0: str, token1: str, amount0_desired: int, amount1_desired: int):
        try:
            web3 = await self.get_web3_instance()
            
            await self.approving_token(account, address, self.POSITION_ROUTER_ADDRESS, token0, amount0_desired)
            await self.approving_token(account, address, self.POSITION_ROUTER_ADDRESS, token1, amount1_desired)
            
            amount0_min = (amount0_desired * (10000 - 100)) // 10000 # 1% slippage
            amount1_min = (amount1_desired * (10000 - 100)) // 10000 # 1% slippage
            deadline = int(time.time()) + 600

            mint_params = (
                token0, 
                token1, 
                3000, 
                -887220, 
                887220, 
                amount0_desired, 
                amount1_desired, 
                amount0_min, 
                amount1_min, 
                address, 
                deadline
            )

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.POSITION_ROUTER_ADDRESS), abi=self.UOMI_CONTRACT_ABI)

            liquidity_data = token_contract.functions.mint(mint_params)

            estimated_gas = liquidity_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(28.54, "gwei")
            max_fee = max_priority_fee

            liquidity_tx = liquidity_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": self.used_nonce[address],
                "chainId": web3.eth.chain_id
            })

            tx_hash = await self.send_raw_transaction_with_retries(account, web3, liquidity_tx)
            receipt = await self.wait_for_receipt_with_retries(web3, tx_hash)
            self.used_nonce[address] += 1

            return tx_hash
        except Exception as e:
            logger.error(f"Liquidity operation failed: {str(e)}")
            return None
        
    def print_wrap_amount_question(self, token_name: str):
        while True:
            try:
                wrap_amount = float(input(f"{Colors.BRIGHT_MAGENTA + Style.BRIGHT}Enter {token_name} Amount : {Style.RESET_ALL}").strip())
                if wrap_amount > 0:
                    self.wrap_amount = wrap_amount
                    break
                else:
                    print(f"{Colors.RED + Style.BRIGHT}{token_name} Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")
    
    def print_wrap_or_unwarp_option(self):
        while True:
            try:
                print(f"{Colors.GREEN + Style.BRIGHT}Select Wrap/Unwrap Option:{Style.RESET_ALL}")
                print(f"{Colors.WHITE + Style.BRIGHT}1. Wrap Uomi - Woumi{Style.RESET_ALL}")
                print(f"{Colors.WHITE + Style.BRIGHT}2. Unwrap Woumi - Uomi{Style.RESET_ALL}")
                print(f"{Colors.WHITE + Style.BRIGHT}3. Skipped{Style.RESET_ALL}")
                wrap_option = int(input(f"{Colors.CYAN + Style.BRIGHT}Choose [1/2/3] : {Style.RESET_ALL}").strip())

                if wrap_option in [1, 2, 3]:
                    wrap_type = (
                        "Wrap Uomi - Woumi" if wrap_option == 1 else 
                        "Unwrap Woumi - Uomi" if wrap_option == 2 else 
                        "Skipped"
                    )
                    logger.info(f"{wrap_type} Selected.")

                    if wrap_option == 1:
                        self.print_wrap_amount_question("UOMI")
                    elif wrap_option == 2:
                        self.print_wrap_amount_question("WUOMI")

                    self.wrap_option = wrap_option
                    break
                else:
                    print(f"{Colors.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    def print_swap_question(self):
        while True:
            try:
                swap_count = int(input(f"{Colors.BRIGHT_MAGENTA + Style.BRIGHT}Swap Total : {Style.RESET_ALL}").strip())
                if swap_count > 0:
                    self.swap_count = swap_count
                    break
                else:
                    print(f"{Colors.RED + Style.BRIGHT}Swap Count must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                min_swap_amount = float(input(f"{Colors.BRIGHT_MAGENTA + Style.BRIGHT}Enter Min UOMI Amount for Swap : {Style.RESET_ALL}").strip())
                if min_swap_amount > 0:
                    self.min_swap_amount = min_swap_amount
                    break
                else:
                    print(f"{Colors.RED + Style.BRIGHT}Min UOMI Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

        while True:
            try:
                max_swap_amount = float(input(f"{Colors.BRIGHT_MAGENTA + Style.BRIGHT}Enter Max UOMI Amount for Swap : {Style.RESET_ALL}").strip())
                if max_swap_amount >= min_swap_amount:
                    self.max_swap_amount = max_swap_amount
                    break
                else:
                    print(f"{Colors.RED + Style.BRIGHT}Max UOMI Amount must be >= Min UOMI.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")
    
    def print_liquidity_question(self):
        while True:
            try:
                liquidity_count = int(input(f"{Colors.BRIGHT_MAGENTA + Style.BRIGHT}Add Liquidity Total : {Style.RESET_ALL}").strip())
                if liquidity_count > 0:
                    self.liquidity_count = liquidity_count
                    break
                else:
                    print(f"{Colors.RED + Style.BRIGHT}Add Liquidity Count must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                wuomi_amount = float(input(f"{Colors.BRIGHT_MAGENTA + Style.BRIGHT}Enter WUOMI Amount for Liquidity : {Style.RESET_ALL}").strip())
                if wuomi_amount > 0:
                    self.wuomi_amount = wuomi_amount
                    break
                else:
                    print(f"{Colors.RED + Style.BRIGHT}WUOMI Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")
        
        while True:
            try:
                syn_amount = float(input(f"{Colors.BRIGHT_MAGENTA + Style.BRIGHT}Enter SYN Amount for Liquidity : {Style.RESET_ALL}").strip())
                if syn_amount > 0:
                    self.syn_amount = syn_amount
                    break
                else:
                    print(f"{Colors.RED + Style.BRIGHT}SYN Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

        while True:
            try:
                sim_amount = float(input(f"{Colors.BRIGHT_MAGENTA + Style.BRIGHT}Enter SIM Amount for Liquidity : {Style.RESET_ALL}").strip())
                if sim_amount > 0:
                    self.sim_amount = sim_amount
                    break
                else:
                    print(f"{Colors.RED + Style.BRIGHT}SIM Amount must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

    def print_delay_question(self):
        while True:
            try:
                min_delay = int(input(f"{Colors.BRIGHT_MAGENTA + Style.BRIGHT}Min Delay : {Style.RESET_ALL}").strip())
                if min_delay >= 0:
                    self.min_delay = min_delay
                    break
                else:
                    print(f"{Colors.RED + Style.BRIGHT}Min Delay must be >= 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                max_delay = int(input(f"{Colors.BRIGHT_MAGENTA + Style.BRIGHT}Max Delay : {Style.RESET_ALL}").strip())
                if max_delay >= min_delay:
                    self.max_delay = max_delay
                    break
                else:
                    print(f"{Colors.RED + Style.BRIGHT}Max Delay must be >= Min Delay.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")
         
    def print_operation_mode_menu(self):
        while True:
            try:
                print(f"{Colors.GREEN + Style.BRIGHT}Choose Operation Mode:{Style.RESET_ALL}")
                print(f"{Colors.WHITE + Style.BRIGHT}1. Single Run{Style.RESET_ALL}")
                print(f"{Colors.WHITE + Style.BRIGHT}2. 24-Hour Automation Mode{Style.RESET_ALL}")
                operation_mode = int(input(f"{Colors.CYAN + Style.BRIGHT}Enter your Choice (1 or 2) : {Style.RESET_ALL}").strip())
                
                if operation_mode in [1, 2]:
                    return operation_mode
                else:
                    print(f"{Colors.RED + Style.BRIGHT}Invalid choice. Please enter 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.RED + Style.BRIGHT}Invalid input. Please enter a number.{Style.RESET_ALL}")

    def print_main_menu(self):
        while True:
            try:
                print(f"{Colors.GREEN + Style.BRIGHT}Select An Action:{Style.RESET_ALL}")
                print(f"{Colors.WHITE + Style.BRIGHT}1. Wrap/Unwrap UOMI{Style.RESET_ALL}")
                print(f"{Colors.WHITE + Style.BRIGHT}2. Random Swap{Style.RESET_ALL}")
                print(f"{Colors.WHITE + Style.BRIGHT}3. Add Liquidity{Style.RESET_ALL}")
                print(f"{Colors.WHITE + Style.BRIGHT}4. Run All Features{Style.RESET_ALL}")
                option = int(input(f"{Colors.CYAN + Style.BRIGHT}Choose [1/2/3/4] : {Style.RESET_ALL}").strip())

                if option in [1, 2, 3, 4]:
                    option_type = (
                        "Wrap/Unwrap UOMI" if option == 1 else 
                        "Random Swap" if option == 2 else 
                        "Add Liquidity" if option == 3 else
                        "Run All Features"
                    )
                    logger.info(f"{option_type} Selected.")
                    break
                else:
                    print(f"{Colors.RED + Style.BRIGHT}Please enter either 1, 2, 3, or 4.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2, 3, or 4).{Style.RESET_ALL}")

        # Initialize operation_mode to 1 (Single Run) by default for options 1, 2, 3
        operation_mode = 1 

        if option == 1:
            self.print_wrap_or_unwarp_option()
            self.print_delay_question()

        elif option == 2:
            self.print_swap_question()
            self.print_delay_question()

        elif option == 3:
            self.print_liquidity_question()
            self.print_delay_question()

        elif option == 4:
            self.print_wrap_or_unwarp_option()
            self.print_swap_question()
            self.print_liquidity_question()
            self.print_delay_question()
            # Only ask for operation mode if "Run All Features" is selected
            operation_mode = self.print_operation_mode_menu()

        return option, operation_mode
    
    async def process_perform_wrapped(self, account: str, address: str):
        tx_hash = await self.perform_wrapped(account, address)
        if tx_hash:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            logger.action(f"Thx Hash {tx_hash}")
            logger.actionSuccess(f"Explore: {explorer}")
        else:
            logger.error("Wrapped operation failed.")

    async def process_perform_unwrapped(self, account: str, address: str):
        tx_hash = await self.perform_unwrapped(account, address)
        if tx_hash:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            logger.action(f"Thx Hash {tx_hash}")
            logger.actionSuccess(f"Explore: {explorer}")
        else:
            logger.error("Unwrapped operation failed.")

    async def process_perform_swap(self, account: str, address: str, from_token: str, to_token: str, amount_in: float):
        tx_hash = await self.perform_swap(account, address, from_token, to_token, amount_in)
        if tx_hash:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            logger.action(f"Thx Hash {tx_hash}")
            logger.actionSuccess(f"Explore: {explorer}")
        else:
            logger.error("Swap operation failed.")

    async def process_perform_liquidity(self, account: str, address: str, token0: str, token1: str, amount0_desired: int, amount1_desired: int):
        tx_hash = await self.perform_liquidity(account, address, token0, token1, amount0_desired, amount1_desired)
        if tx_hash:
            explorer = f"https://testnet.pharosscan.xyz/tx/{tx_hash}"
            logger.action(f"Thx Hash {tx_hash}")
            logger.actionSuccess(f"Explore: {explorer}")
        else:
            logger.error("Liquidity operation failed.")

    async def print_timer(self):
        delay = random.randint(self.min_delay, self.max_delay)
        if delay > 0:
            logger.info(f"Next transaction in {self.format_seconds(delay)}...")
            await asyncio.sleep(delay)

    async def process_option_1(self, account: str, address: str): # Wrap/Unwrap
        if self.wrap_option == 1: # Wrap Uomi - Woumi
            logger.step("Performing Wrap UOMI to WUOMI...")
            balance = await self.get_token_balance(address, "UOMI")
            logger.info(f"Current UOMI Balance: {balance} UOMI")
            logger.info(f"Amount to Wrap: {self.wrap_amount} UOMI")

            if not balance or balance < self.wrap_amount:
                logger.warn("Insufficient UOMI Token Balance.")
                return
            
            await self.process_perform_wrapped(account, address)

        elif self.wrap_option == 2: # Unwrap Woumi - Uomi
            logger.step("Performing Unwrap WUOMI to UOMI...")
            balance = await self.get_token_balance(address, self.WUOMI_CONTRACT_ADDRESS)
            logger.info(f"Current WUOMI Balance: {balance} WUOMI")
            logger.info(f"Amount to Unwrap: {self.wrap_amount} WUOMI")

            if not balance or balance < self.wrap_amount:
                logger.warn("Insufficient WUOMI Token Balance.")
                return
            
            await self.process_perform_unwrapped(account, address)

    async def process_option_2(self, account: str, address: str): # Random Swap
        logger.step("Initiating Random Swap operations...")
        for i in range(self.swap_count):
            logger.info(f"Swap {i+1} / {self.swap_count}")

            swap_option, from_token, to_token, amount_in = self.generate_swap_option()

            logger.info(f"Swap Pair: {swap_option}")
            logger.info(f"Amount In: {amount_in} UOMI")

            balance = await self.get_token_balance(address, "UOMI")
            logger.info(f"Current UOMI Balance: {balance} UOMI")

            if not balance or balance < amount_in:
                logger.warn("Insufficient UOMI Token Balance for swap.")
                continue
            
            await self.process_perform_swap(account, address, from_token, to_token, amount_in)
            await self.print_timer()

    async def process_option_3(self, account: str, address: str): # Add Liquidity
        logger.step("Initiating Add Liquidity operations...")
        for i in range(self.liquidity_count):
            logger.info(f"Liquidity Add {i+1} / {self.liquidity_count}")

            liquidity_option, ticker0, ticker1, token0, token1, amount0_desired = self.generate_liquidity_option()

            logger.info(f"Liquidity Pair: {liquidity_option}")

            balance0 = await self.get_token_balance(address, token0)
            balance1 = await self.get_token_balance(address, token1)
            logger.info(f"Current Balance {ticker0}: {balance0} {ticker0}")
            logger.info(f"Current Balance {ticker1}: {balance1} {ticker1}")

            path = bytes.fromhex(token0[2:]) + (3000).to_bytes(3, "big") + bytes.fromhex(token1[2:])
            amount1_desired = await self.get_amount_out_min(address, path, amount0_desired)
            if amount1_desired is None:
                logger.warn(f"Failed to fetch {ticker0} per {ticker1} current price. Skipping liquidity for this pair.")
                continue

            amount0 = amount0_desired / (10 ** 18)
            amount1 = amount1_desired / (10 ** 18)

            logger.info(f"Desired Amount {ticker0}: {amount0} {ticker0}")
            logger.info(f"Desired Amount {ticker1}: {amount1} {ticker1}")

            if not balance0 or balance0 < amount0:
                logger.warn(f"Insufficient {ticker0} Token Balance for liquidity.")
                continue
            
            if not balance1 or balance1 < amount1:
                logger.warn(f"Insufficient {ticker1} Token Balance for liquidity.")
                continue
            
            await self.process_perform_liquidity(account, address, token0, token1, amount0_desired, amount1_desired)
            await self.print_timer()

    async def process_accounts(self, account_key: str, address: str, option: int):
        try:
            web3 = await self.get_web3_instance()
            self.used_nonce[address] = web3.eth.get_transaction_count(address, "pending")

        except Exception as e:
            logger.error(f"Failed to initialize web3 for {self.mask_account(address)}: {str(e)}")
            return
        
        logger.step(f"Processing actions for account: {self.mask_account(address)}")

        if option == 1: # Wrap/Unwrap UOMI
            await self.process_option_1(account_key, address)
            
        elif option == 2: # Random Swap
            await self.process_option_2(account_key, address)

        elif option == 3: # Add Liquidity
            await self.process_option_3(account_key, address)

        elif option == 4: # Run All Features
            if self.wrap_option != 3: # Only run if not skipped
                await self.process_option_1(account_key, address)
                await asyncio.sleep(self.min_delay + (self.max_delay - self.min_delay) / 2)

            await self.process_option_2(account_key, address)
            await asyncio.sleep(self.min_delay + (self.max_delay - self.min_delay) / 2)

            await self.process_option_3(account_key, address)
            await asyncio.sleep(self.min_delay + (self.max_delay - self.min_delay) / 2)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            if not accounts:
                logger.error("No accounts found in 'accounts.txt'. Please add your private keys.")
                return

            while True:
                await display_welcome_screen()
                option, operation_mode = self.print_main_menu()
                
                logger.info(f"Total Accounts: {len(accounts)}")
                
                for account in accounts:
                    if account:
                        address = self.generate_address(account)

                        if not address:
                            logger.error(f"Invalid Private Key. Skipping account.")
                            continue
                        
                        await self.process_accounts(account, address, option)
                        await self.print_timer()

                if operation_mode == 1: # Single Run
                    logger.info("Single Run complete. Exiting...")
                    break # Exit the while loop

                elif operation_mode == 2: # 24-Hour Automation
                    logger.info("All accounts have been processed. Bot will restart after a delay.")
                    seconds = 24 * 60 * 60 # 24 hour restart timer
                    while seconds > 0:
                        formatted_time = self.format_seconds(seconds)
                        print(
                            f"{Colors.BRIGHT_BLACK}[ {datetime.now().strftime('%H:%M:%S')} ]{Colors.RESET} "
                            f"{Colors.CYAN}[⟳] Restarting in {formatted_time} ...{Colors.RESET}",
                            end="\r"
                        )
                        await asyncio.sleep(1)
                        seconds -= 1
                    clear_console() # Clear console before restarting loop

        except FileNotFoundError:
            logger.error("File 'accounts.txt' Not Found. Please create it and add your private keys.")
            return
        except Exception as e:
            logger.error(f"An unexpected error occurred in main: {e}")
            raise e

if __name__ == "__main__":
    try:
        bot = UOMI()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        logger.info("[ EXIT ] Bot Testnet Automation - Terminated by user.")
