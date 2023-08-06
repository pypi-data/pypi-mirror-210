import base64

from web3 import Web3

from apexpro import private_key_to_public_key_pair_hex
from apexpro.constants import REGISTER_ENVID_MAIN, OFF_CHAIN_KEY_DERIVATION_ACTION
from apexpro.constants import OFF_CHAIN_ONBOARDING_ACTION
from apexpro.eth_signing import SignWithWeb3
from apexpro.eth_signing import SignWithKey
from apexpro.eth_signing import SignOnboardingAction

GANACHE_ADDRESS = '0xc4C5036b68a42d8F1C6ba9bA8e5dd49ad5C1EF5c'
GANACHE_PRIVATE_KEY = (
    '0xb7d420d09000a5b89c846cfe687b8edebb7f7cb4c0c129cb640468ec3e4f4b20'
)

EXPECTED_SIGNATURE = (
    '0x0a30eea502e9805b95bd432fa1952e345dda3e9f72f7732aa00775865352e2b549'
    '29803c221e9e63861e4604fbc796a4e1a6ca23d49452338a3d7602aaf6d1841c00'
)


class TestOnboardingAction():

    def test_sign_via_local_node(self):
        web3 = Web3()  # Connect to a local Ethereum node.
        signer = SignWithWeb3(web3)

        action_signer = SignOnboardingAction(signer, REGISTER_ENVID_MAIN)
        signature = action_signer.sign(
            GANACHE_ADDRESS,
            action=OFF_CHAIN_ONBOARDING_ACTION,
            nonce='1194043805607919616'
        )
        assert action_signer.verify(
            signature,
            GANACHE_ADDRESS,
            action=OFF_CHAIN_ONBOARDING_ACTION,
            nonce='1194043805607919616'
        )
        assert signature == EXPECTED_SIGNATURE

    def test_sign_via_account(self):
       # web3 = Web3(None)
       # web3_account = web3.eth.account.create()
        signer = SignWithKey(GANACHE_PRIVATE_KEY)

        action_signer = SignOnboardingAction(signer, REGISTER_ENVID_MAIN)
        signature = action_signer.sign(
            signer.address,
            action=OFF_CHAIN_ONBOARDING_ACTION,
            nonce='1194146830162853888'
        )

        #signature = '0xb26fc985ada1df2057d3773eb53971017b09550e7888a76434be2cd15147f4af6f25ea667f910d9620df8e1a4caa91fb2338d641ceb0e9ccee9daa228c52bc471b00'
        r_hex = signature[2:66]
        r_int = int(r_hex, 16)
        hashed_r_bytes = bytes(Web3.solidityKeccak(['uint256'], [r_int]))
        secret_bytes = hashed_r_bytes[:30]
        s_hex = signature[66:130]
        s_int = int(s_hex, 16)
        hashed_s_bytes = bytes(Web3.solidityKeccak(['uint256'], [s_int]))
        key_bytes = hashed_s_bytes[:16]
        passphrase_bytes = hashed_s_bytes[16:31]

        key_hex = key_bytes.hex()
        key_uuid = '-'.join([
           key_hex[:8],
           key_hex[8:12],
           key_hex[12:16],
           key_hex[16:20],
           key_hex[20:],
        ])

        apex = {
           'secret': base64.urlsafe_b64encode(secret_bytes).decode(),
           'key': key_uuid,
           'passphrase': base64.urlsafe_b64encode(passphrase_bytes).decode(),
        }
        assert action_signer.verify(
            signature,
            signer.address,
            action=OFF_CHAIN_ONBOARDING_ACTION,
        )

    def test_sign_via_private_key(self):
        signer = SignWithKey(GANACHE_PRIVATE_KEY)

        action_signer = SignOnboardingAction(signer, REGISTER_ENVID_MAIN)
        signature = action_signer.sign_message(
            GANACHE_ADDRESS,
            action=OFF_CHAIN_KEY_DERIVATION_ACTION,
        )

        signature_int = int(signature, 16)
        hashed_signature = Web3.solidityKeccak(['uint256'], [signature_int])
        private_key_int = int(hashed_signature.hex(), 16) >> 5
        private_key_hex = hex(private_key_int)
        public_x, public_y = private_key_to_public_key_pair_hex(
            private_key_hex,
        )
        return {
            'public_key': public_x,
            'public_key_y_coordinate': public_y,
            'private_key': private_key_hex
        }

        assert action_signer.verify(
            signature,
            GANACHE_ADDRESS,
            action=OFF_CHAIN_KEY_DERIVATION_ACTION,
        )
        assert signature == EXPECTED_SIGNATURE
