from web3 import Web3

from apexpro.constants import REGISTER_ENVID_MAIN
from apexpro.eth_signing import SignWithWeb3
from apexpro.eth_signing import SignWithKey
from apexpro.eth_signing import SignEthPrivateAction

GANACHE_ADDRESS = '0xc4C5036b68a42d8F1C6ba9bA8e5dd49ad5C1EF5c'
GANACHE_PRIVATE_KEY = (
    '0xb7d420d09000a5b89c846cfe687b8edebb7f7cb4c0c129cb640468ec3e4f4b20'
)
PARAMS = {
    'method': 'POST',
    'request_path': 'v3/test',
    'body': '{}',
    'timestamp': '2021-01-08T10:06:12.500Z',
}

EXPECTED_SIGNATURE = (
    '0x3ec5317783b313b0acac1f13a23eaaa2fca1f45c2f395081e9bfc20b4cc1acb17e'
    '3d755764f37bf13fa62565c9cb50475e0a987ab0afa74efde0b3926bb7ab9d1b00'
)


class TestApiKeyAction():

    def test_sign_via_local_node(self):
        web3 = Web3("https://goerli.infura.io/v3/87a1b65a33cf4655ab405128ed0a854b")  # Connect to a local Ethereum node.
        signer = SignWithWeb3(web3)

        action_signer = SignEthPrivateAction(signer, REGISTER_ENVID_MAIN)
        signature = action_signer.sign(GANACHE_ADDRESS, **PARAMS)
        assert action_signer.verify(
            signature,
            GANACHE_ADDRESS,
            **PARAMS,
        )
        assert signature == EXPECTED_SIGNATURE

    def test_sign_via_account(self):
        web3 = Web3("https://goerli.infura.io/v3/87a1b65a33cf4655ab405128ed0a854b")
        web3_account = web3.eth.account.create()
        signer = SignWithKey(web3_account.key)

        action_signer = SignEthPrivateAction(signer, REGISTER_ENVID_MAIN)
        signature = action_signer.sign(signer.address, **PARAMS)
        assert action_signer.verify(
            signature,
            signer.address,
            **PARAMS,
        )

    def test_sign_via_private_key(self):
        signer = SignWithKey(GANACHE_PRIVATE_KEY)

        action_signer = SignEthPrivateAction(signer, REGISTER_ENVID_MAIN)
        signature = action_signer.sign(GANACHE_ADDRESS, **PARAMS)
        assert action_signer.verify(
            signature,
            GANACHE_ADDRESS,
            **PARAMS,
        )
        assert signature == EXPECTED_SIGNATURE
