# bubble-aide
Bubble区块链助手，能够帮助您便捷、快速的接入Bubble区块链。 


##  安装方法

```shell
pip install bubble_aide
```


## 使用方法

```python
from eth_account import Account
from bubble_aide import Aide

# 实例化aide
uri = 'http://192.168.120.121:6789'
account = Account.from_key('f51ca759562e1daf9e5302d121f933a8152915d34fcbc27e542baf256b5e4b74')
aide = Aide(uri, account=account)  # account指定用于默认发交易的账户
print(aide.bub.block_number)    # 打印当前块高

# 发送转账交易
aide.transfer('0xc1E8e709620Cb29c33B9669C60c0600a9014c881', amount=aide.web3.to_wei(10))

# 调用锁仓合约，锁定金额到目标账户
plans = [{'Epoch': 2, 'Amount': 100 * 10 ** 18}, {'Epoch': 8, 'Amount': 300 * 10 ** 18}]
aide.restricting.restricting('0xc1E8e709620Cb29c33B9669C60c0600a9014c881', plans)

# 调用质押委托合约，查看账户处于锁定期的委托信息
print(aide.delegate.get_delegate_lock_info())

# 部署solidity合约
false = False
ture = True
abi = [{"anonymous": false, "inputs": [{"indexed": false, "internalType": "uint256", "name": "_chainId", "type": "uint256"}], "name": "_putChainID",
        "type": "event"},
       {"inputs": [], "name": "getChainID", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view",
        "type": "function"},
       {"inputs": [], "name": "putChainID", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
bytecode = '608060405234801561001057600080fd5b50610107806100206000396000f3fe6080604052348015600f57600080fd5b506004361060325760003560e01c806336319ab0146037578063564b81ef14603f575b600080fd5b603d6059565b005b60456099565b6040516050919060ae565b60405180910390f35b466000819055507f68e891aec7f9596d6e192c48cb82364ec392d423bce80abd6e1ee5ad05860256600054604051608f919060ae565b60405180910390a1565b600046905090565b60a88160c7565b82525050565b600060208201905060c1600083018460a1565b92915050565b600081905091905056fea264697066735822122037a1668252253271128182c71109922cb1e300fb08a7080a0587f360df4071ba64736f6c63430008060033'
contract = aide.deploy_contract(abi=abi, bytecode=bytecode)
print(contract.address)

# 调用solidity合约方法
print(contract.getChainID())

# 发送solidity合约交易
res = contract.putChainID(1000)

# 解析solidity事件
print(contract.PutChainID(res))

```


