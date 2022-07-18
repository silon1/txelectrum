using System;
using System.Runtime.Serialization;

namespace secp256k1_signer_server
{
    [Serializable]
    internal class MissingPrivateKeyError : Exception
    {
        public MissingPrivateKeyError()
        {
        }

        public MissingPrivateKeyError(string message) : base(message)
        {
        }

        public MissingPrivateKeyError(string message, Exception innerException) : base(message, innerException)
        {
        }

        protected MissingPrivateKeyError(SerializationInfo info, StreamingContext context) : base(info, context)
        {
        }
    }
}