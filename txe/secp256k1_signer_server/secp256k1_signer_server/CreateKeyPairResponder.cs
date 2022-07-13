namespace secp256k1_signer_server
{
    public class CreateKeyPairResponder : IMessageResponder
    {
        private IKeyPairCreator m_keyPairCreator;

        public CreateKeyPairResponder(IKeyPairCreator keyPairCreator)
        {
            m_keyPairCreator = keyPairCreator;
        }

        public Message RespondeMessage(Message message)
        {
            try
            {
                return new Message
                {
                    MessageType = MessageType.CREATE_KEYPAIR,
                    Payload = m_keyPairCreator.CreateKeyPair(message.Payload),
                };
            }
            catch (ProtocolError e)
            {
                return Message.Error(e.ErrorType);
            }
        }
    }
}
