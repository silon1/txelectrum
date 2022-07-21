using Nancy;
using Nancy.Bootstrapper;
using Nancy.TinyIoc;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace secp256k1_signer_server
{
    public class AppletBootstrapper : DefaultNancyBootstrapper
    {
        protected override void ApplicationStartup(TinyIoCContainer container, IPipelines pipelines)
        {
            // The bootstrapper will call the signer's Dispose method when the server is being closed.
            var signer = new AppletSigner();
            container.Register<IKeyPairCreator, AppletSigner>(signer);
            container.Register<IBufferSigner, AppletSigner>(signer);

            pipelines.OnError += (ctx, e) =>
            {
                Console.WriteLine(e);
                return HttpStatusCode.InternalServerError;
            };
        }
    }
}
