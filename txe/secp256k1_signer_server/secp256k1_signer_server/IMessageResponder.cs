namespace secp256k1_signer_server
{
    public interface IMessageResponder
    {
        MessageType MessageType { get; }
        Message RespondeMessage(Message message);
    }
}
