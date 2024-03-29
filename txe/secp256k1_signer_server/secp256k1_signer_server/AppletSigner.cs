﻿using Intel.Dal;
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
        // Note: The design note of the protocol between the host and the applet can be found in `/txe/README.md`.

        private const string APPLET_ID = "e48e7440-4f22-4639-bae5-7216d720347e";
        private const string APPLET_DIR = "../../../../secp256k1_signer/bin";

        private Jhi m_jhi;
        private JhiSession m_session;
        private bool m_open;

        public AppletSigner()
        {
            string appletPath = Path.GetFullPath($"{APPLET_DIR}/secp256k1_signer.dalp");
            if (!File.Exists(appletPath))
            {
                // Maybe the applet was built for debugging. In this case, the file name is secp256k1_signer-debug.dalp.
                appletPath = Path.GetFullPath($"{APPLET_DIR}/secp256k1_signer-debug.dalp");
                if (!File.Exists(appletPath))
                {
                    // The applet wasn't built yet.
                    throw new FileNotFoundException("The applet binary was not found. First build the applet before running the host.");
                }
            }

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
                m_jhi.SendAndRecv2(m_session, (int)RequestId.CREATE_KEYPAIR, hashedPassword, ref publicKey, out int responseId);

                if (responseId == (int)ResponseId.OK)
                {
                    return publicKey;
                }

                throw new Exception($"Applet responsed with id {responseId} ({(ResponseId)responseId}) on request CREATE_KEYPAIR.");
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
                        Array.Copy(outputBuffer, 1, signature, 0, sigLength);
                        return signature;
                    }
                    case ResponseId.MISSING_PRIVATE_KEY:
                        throw new MissingPrivateKeyError();
                    case ResponseId.WRONG_PASSWORD:
                        throw new WrongPasswordError();
                    default:
                        throw new Exception($"Applet responsed with id {responseId} ({(ResponseId)responseId}) on request SIGN_BUFFER.");
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
            CREATE_KEYPAIR,
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
