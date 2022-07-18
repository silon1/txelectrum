using Intel.Dal;
using Nancy.Hosting.Self;
using System;
using System.IO;
using System.Text;

namespace secp256k1_signer_server
{
    class Program
    {
        static void Main(string[] args)
        {
#if AMULET
            // When compiled for Amulet the Jhi.DisableDllValidation flag is set to true 
            // in order to load the JHI.dll without DLL verification.
            // This is done because the JHI.dll is not in the regular JHI installation folder, 
            // and therefore will not be found by the JhiSharp.dll.
            // After disabling the .dll validation, the JHI.dll will be loaded using the Windows search path
            // and not by the JhiSharp.dll (see http://msdn.microsoft.com/en-us/library/7d83bc18(v=vs.100).aspx for 
            // details on the search path that is used by Windows to locate a DLL) 
            // In this case the JHI.dll will be loaded from the $(OutDir) folder (bin\Amulet by default),
            // which is the directory where the executable module for the current process is located.
            // The JHI.dll was placed in the bin\Amulet folder during project build.
            Jhi.DisableDllValidation = true;
#endif

            var config = new HostConfiguration()
            {
                RewriteLocalhost = false
            };

            using (var host = new NancyHost(config, new Uri("http://localhost:51841")))
            {
                host.Start();
                Console.WriteLine("Starting host...");
                Console.ReadLine();
            }

            // Send and Receive data to/from the Trusted Application
            //byte[] sendBuff = Encoding.UTF8.GetBytes("Signature of ECDSA SECP256k1"); // A message to send to the TA
            //int responseCode; // The return value that the TA provides using the IntelApplet.setResponseCode method
            //for (int command = 0; command < 2; ++command)
            //{
            //    byte[] recvBuff = new byte[2000]; // A buffer to hold the output data from the TA
            //    Console.WriteLine("Performing send and receive operation with command " + command);
            //    jhi.SendAndRecv2(session, command, sendBuff, ref recvBuff, out responseCode);
            //    Console.WriteLine("Response buffer is " + BitConverter.ToString(recvBuff).Replace("-", string.Empty));
            //    Console.WriteLine("Response buffer length is " + recvBuff.Length);
            //    Console.WriteLine("Response code is " + responseCode);
            //}

        }
    }
}