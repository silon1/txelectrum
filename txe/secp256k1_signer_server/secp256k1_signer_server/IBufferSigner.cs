using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace secp256k1_signer_server
{
    public interface IBufferSigner
    {
        Task<byte[]> SignBuffer(byte[] hashedBuffer, byte[] hashedPassword, byte[] publicKey);
    }
}
