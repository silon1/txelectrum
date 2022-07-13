namespace secp256k1_signer_server
{
    public interface IBufferSigner
    {
        byte[] SignBuffer(byte[] publicKey, byte[] password, byte[] hashedBuffer);
    }
}
