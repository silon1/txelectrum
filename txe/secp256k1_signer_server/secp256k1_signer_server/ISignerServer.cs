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
}
