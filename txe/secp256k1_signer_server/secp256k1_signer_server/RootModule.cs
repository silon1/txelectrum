using Nancy;
using Nancy.Extensions;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Dynamic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace secp256k1_signer_server
{
    public class RootModule : NancyModule
    {
        private IKeyPairCreator m_keyPairCreator;
        private IBufferSigner m_bufferSigner;

        public RootModule(IKeyPairCreator keyPairCreator, IBufferSigner bufferSigner)
        {
            m_keyPairCreator = keyPairCreator;
            m_bufferSigner = bufferSigner;

            Post("/create_keypair", OnCreateKeyPair);
            Post("/sign_buffer", OnSignBuffer);
        }

        private async Task<object> OnCreateKeyPair(dynamic args)
        {
            string bodyJson = Request.Body.AsString();
            dynamic body = JsonConvert.DeserializeObject<ExpandoObject>(bodyJson);

            if (!TryGetHashedPassword(body, out byte[] hashedPassword))
            {
                return HttpStatusCode.BadRequest;
            }

            var publicKey = await m_keyPairCreator.CreateKeyPair(hashedPassword);
            return new
            {
                public_key = GetHex(publicKey)
            };
        }

        private async Task<object> OnSignBuffer(dynamic args)
        {
            string bodyJson = Request.Body.AsString();
            dynamic body = JsonConvert.DeserializeObject<ExpandoObject>(bodyJson);

            byte[] hashedPassword = null;
            byte[] publicKey = null;
            byte[] hashedBuffer = null;
            if (!TryGetHashedPassword(body, out hashedPassword) ||
                !TryGetPublicKey(body, out publicKey) ||
                !TryGetHashedBuffer(body, out hashedBuffer))
            {
                return HttpStatusCode.BadRequest;
            }

            try
            {
                var sig = await m_bufferSigner.SignBuffer(hashedBuffer, hashedPassword, publicKey);
                return new
                {
                    signature = GetHex(sig)
                };
            }
            catch (WrongPasswordError)
            {
                return HttpStatusCode.Unauthorized;
            }
            catch (MissingPrivateKeyError)
            {
                return HttpStatusCode.NotFound;
            }
        }

        private bool TryGetHashedPassword(dynamic body, out byte[] hashedPassword)
        {
            return TryGetHexParam(body, "hashed_password", 20, out hashedPassword);
        }

        private bool TryGetPublicKey(dynamic body, out byte[] publicKey)
        {
            return TryGetHexParam(body, "public_key", 33, out publicKey);
        }

        private bool TryGetHashedBuffer(dynamic body, out byte[] hashedBuffer)
        {
            return TryGetHexParam(body, "hashed_buffer", 32, out hashedBuffer);
        }

        private bool TryGetHexParam(dynamic body, string paramName, int length, out byte[] result)
        {
            IDictionary<string, object> dictBody = body;
            if (!dictBody.ContainsKey(paramName))
            {
                result = null;
                return false;
            }

            Regex pattern = new Regex($"^[A-Fa-f0-9]{{{length * 2}}}$");
            string hex = dictBody[paramName].ToString();
            if (!pattern.IsMatch(hex))
            {
                result = null;
                return false;
            }

            result = FromHex(hex);
            return true;
        }

        private string GetHex(byte[] buffer)
        {
            return BitConverter.ToString(buffer).Replace("-", string.Empty);
        }

        private byte[] FromHex(string hex)
        {
            byte[] result = new byte[hex.Length / 2];
            for (int i = 0; i < hex.Length; i += 2)
            {
                result[i / 2] = Convert.ToByte(hex.Substring(i, 2), 16);
            }
            return result;
        }
    }
}
