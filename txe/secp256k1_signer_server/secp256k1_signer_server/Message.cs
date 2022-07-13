using System;

namespace secp256k1_signer_server
{
    public struct Message
    {
        public MessageType MessageType { get; set; }
        public byte[] Payload { get; set; }

        public static Message Error(ErrorType errorType)
        {
            return new Message
            {
                MessageType = MessageType.ERROR,
                Payload = BitConverter.GetBytes((int)errorType),
            };
        }
    }
}
