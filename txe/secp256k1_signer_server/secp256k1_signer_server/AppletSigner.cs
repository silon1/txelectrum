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

        public async Task<byte[]> CreateKeyPair(byte[] password)
        {
            return await new ExampleSigner().CreateKeyPair(password);
        }

        public async Task<byte[]> SignBuffer(byte[] hashedBuffer, byte[] password, byte[] publicKey)
        {
            return await new ExampleSigner().SignBuffer(hashedBuffer, password, publicKey);
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
    }
}
