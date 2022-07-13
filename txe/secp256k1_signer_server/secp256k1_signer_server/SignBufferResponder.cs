namespace secp256k1_signer_server
{
    public class SignBufferResponder : IMessageResponder
    {
        private IBufferSigner m_signer;

        public MessageType MessageType => MessageType.SIGN_BUFFER;

        public SignBufferResponder(IBufferSigner signer)
        {
            m_signer = signer;
        }

        public Message RespondeMessage(Message message)
        {
            // The payload contains the public key, password and hashed buffer to sign.
            byte[] publicKey = null;
            byte[] password = null;
            byte[] hashedBuffer = null;

            try
            {
                return new Message
                {
                    MessageType = MessageType.SIGN_BUFFER,
                    Payload = m_signer.SignBuffer(publicKey, password, hashedBuffer),
                };
            }
            catch (ProtocolError e)
            {
                return Message.Error(e.ErrorType);
            }
        }
    }
}
