namespace secp256k1_signer_server
{
    public interface IKeyPairCreator
    {
        byte[] CreateKeyPair(byte[] password);
    }
}
