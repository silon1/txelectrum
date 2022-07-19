using Intel.Dal;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace secp256k1_signer_server
{
    public class AppletSigner : IKeyPairCreator, IBufferSigner, IDisposable
    {
        // Note: The design note of the protocol between the host and the protocol can be found in `/txe/README.md`.

        private const string APPLET_ID = "e48e7440-4f22-4639-bae5-7216d720347e";

        private Jhi m_jhi;
        private JhiSession m_session;
        private bool m_open;

        public AppletSigner()
        {
            string appletPath = Path.GetFullPath("../../../../secp256k1_signer/bin/secp256k1_signer.dalp");
            byte[] initBuffer = new byte[] { };

            m_jhi = Jhi.Instance;
            m_jhi.Install(APPLET_ID, appletPath);
            m_jhi.CreateSession(APPLET_ID, JHI_SESSION_FLAGS.None, initBuffer, out m_session);
            m_open = true;
        }

        public async Task<byte[]> CreateKeyPair(byte[] hashedPassword)
        {
            return await Task.Run(() =>
            {
                byte[] publicKey = new byte[33];
                m_jhi.SendAndRecv2(m_session, (int)RequestId.CREATE_KEY_PAIR, hashedPassword, ref publicKey, out int responseId);

                if (responseId == (int)ResponseId.OK)
                {
                    return publicKey;
                }

                throw new Exception($"Applet responsed with code {responseId}.");
            });
        }

        public async Task<byte[]> SignBuffer(byte[] hashedBuffer, byte[] hashedPassword, byte[] publicKey)
        {
            return await Task.Run(() =>
            {
                byte[] inputBuffer = new byte[publicKey.Length + hashedPassword.Length + hashedBuffer.Length];
                publicKey.CopyTo(inputBuffer, 0);
                hashedPassword.CopyTo(inputBuffer, publicKey.Length);
                hashedBuffer.CopyTo(inputBuffer, publicKey.Length + hashedPassword.Length);

                byte[] outputBuffer = new byte[256];
                m_jhi.SendAndRecv2(m_session, (int)RequestId.SIGN_BUFFER, inputBuffer, ref outputBuffer, out int responseId);

                switch ((ResponseId)responseId)
                {
                    case ResponseId.OK:
                    {
                        byte sigLength = outputBuffer[0];
                        byte[] signature = new byte[sigLength];
                        Array.Copy(outputBuffer, signature, sigLength);
                        return signature;
                    }
                    case ResponseId.MISSING_PRIVATE_KEY:
                        throw new MissingPrivateKeyError();
                    case ResponseId.WRONG_PASSWORD:
                        throw new WrongPasswordError();
                    default:
                        throw new Exception($"Applet responsed with id {responseId}.");
                }
            });
        }

        public void Dispose()
        {
            // Handling multiple Dispose calls with m_open. AppletBootstrapper calls the
            // Dispose twice, and I didn't find a way to avoid that.

            if (m_open)
            {
                m_open = false;
                m_jhi.CloseSession(m_session);
                m_jhi.Uninstall(APPLET_ID);
            }
        }

        enum RequestId
        {
            CREATE_KEY_PAIR,
            SIGN_BUFFER
        }

        enum ResponseId
        {
            OK,
            BAD_REQUEST,
            INTERNAL_ERROR,
            MISSING_PRIVATE_KEY,
            WRONG_PASSWORD,
        }
    }
}
