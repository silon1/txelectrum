using System;

namespace secp256k1_signer_server
{
    public class SignerApplet : IKeyPairCreator, IBufferSigner, IDisposable
    {
        public byte[] CreateKeyPair(byte[] password)
        {
            throw new NotImplementedException();
        }

        public byte[] SignBuffer(byte[] password, byte[] publicKey, byte[] hashedBuffer)
        {
            throw new NotImplementedException();
        }

        public void Dispose()
        {
            throw new NotImplementedException();
        }
    }
}
