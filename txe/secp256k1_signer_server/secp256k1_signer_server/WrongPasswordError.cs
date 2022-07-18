using System;
using System.Runtime.Serialization;

namespace secp256k1_signer_server
{
    [Serializable]
    internal class WrongPasswordError : Exception
    {
        public WrongPasswordError()
        {
        }

        public WrongPasswordError(string message) : base(message)
        {
        }

        public WrongPasswordError(string message, Exception innerException) : base(message, innerException)
        {
        }

        protected WrongPasswordError(SerializationInfo info, StreamingContext context) : base(info, context)
        {
        }
    }
}