using System;

namespace secp256k1_signer_server
{
    public class ProtocolError : Exception
    {
        public ErrorType ErrorType { get; }

        public ProtocolError(ErrorType errorType)
        {
            ErrorType = errorType;
        }
    }
}
