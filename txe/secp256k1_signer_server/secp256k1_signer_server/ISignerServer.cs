using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Runtime.Serialization;
using System.Text;

namespace secp256k1_signer_server
{
    public interface ISignerServer
    {
        void Start();
        void AddMessageResponder(IMessageResponder messageResponder);
    }

    public enum MessageType
    {
        CREATE_KEYPAIR = 1,
        SIGN_BUFFER = 2,
        ERROR = 3,
    }

    public enum ErrorType
    {
        MISSING_PRIVATE_KEY = 0,
        WRONG_PASSWORD = 1,
    }

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

    public interface IMessageResponder
    {
        Message RespondeMessage(Message message);
    }

    public class CreateKeyPairResponder : IMessageResponder
    {
        private IKeyPairCreator m_keyPairCreator;

        public CreateKeyPairResponder(IKeyPairCreator keyPairCreator)
        {
            m_keyPairCreator = keyPairCreator;
        }

        public Message RespondeMessage(Message message)
        {
            return new Message
            {
                MessageType = MessageType.CREATE_KEYPAIR,
                Payload = m_keyPairCreator.CreateKeyPair(message.Payload),
            };
        }
    }

    public interface IKeyPairCreator
    {
        byte[] CreateKeyPair(byte[] password);
    }

    public class SignBufferResponder : IMessageResponder
    {
        private IBufferSigner m_signer;

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
            catch (MissingPrivateKeyError)
            {
                return Message.Error(ErrorType.MISSING_PRIVATE_KEY);
            }
            catch (WrongPasswordError)
            {
                return Message.Error(ErrorType.WRONG_PASSWORD);
            }
        }
    }

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

    public interface IBufferSigner
    {
        byte[] SignBuffer(byte[] publicKey, byte[] password, byte[] hashedBuffer);
    }

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

    public class SignerServer : IDisposable, ISignerServer
    {
        public void AddMessageResponder(IMessageResponder messageResponder)
        {
            throw new NotImplementedException();
        }

        public void Start()
        {
            throw new NotImplementedException();
        }

        public void Dispose()
        {
            throw new NotImplementedException();
        }
    }
}
