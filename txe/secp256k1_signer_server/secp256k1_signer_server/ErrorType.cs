namespace secp256k1_signer_server
{
    public enum ErrorType
    {
        BADLY_FORMED_MESSAGE    = 0x0000,
        INTERNAL_ERROR          = 0x0001,
        TIMEOUT_ERROR           = 0x0002,
        UNKNOWN_ERROR           = 0x00FF,

        MISSING_PRIVATE_KEY     = 0x0200,
        WRONG_PASSWORD          = 0x0201,
    }
}
