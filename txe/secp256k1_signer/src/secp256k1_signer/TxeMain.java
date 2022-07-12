package secp256k1_signer;

import com.intel.util.*;
import com.intel.crypto.*;

//
// Implementation of DAL Trusted Application: secp256k1_signer 
//
// **************************************************************************************************
// NOTE:  This default Trusted Application implementation is intended for DAL API Level 7 and above
// **************************************************************************************************

public class TxeMain extends IntelApplet {
	
	private EccAlg signer;

	/**
	 * This method will be called by the VM when a new session is opened to the Trusted Application 
	 * and this Trusted Application instance is being created to handle the new session.
	 * This method cannot provide response data and therefore calling
	 * setResponse or setResponseCode methods from it will throw a NullPointerException.
	 * 
	 * @param	request	the input data sent to the Trusted Application during session creation
	 * 
	 * @return	APPLET_SUCCESS if the operation was processed successfully, 
	 * 		any other error status code otherwise (note that all error codes will be
	 * 		treated similarly by the VM by sending "cancel" error code to the SW application).
	 */
	public int onInit(byte[] request) {
		DebugPrint.printString("Hello, DAL!");
		signer = EccAlg.create(EccAlg.ECC_CURVE_TYPE_SECP256K1);
		signer.generateKeys();
		return APPLET_SUCCESS;
	}
	
	/**
	 * This method will be called by the VM to handle a command sent to this
	 * Trusted Application instance.
	 * 
	 * @param	commandId	the command ID (Trusted Application specific) 
	 * @param	request		the input data for this command 
	 * @return	the return value should not be used by the applet
	 */
	public int invokeCommand(int commandId, byte[] request) {
		
		DebugPrint.printString("Received command Id: " + commandId + ".");
		if(request != null)
		{
			DebugPrint.printString("Received buffer:");
			DebugPrint.printBuffer(request);
		}
		
		final short sigSize = signer.getSignatureSize();
		final byte[] sigR = new byte[sigSize];
		final byte[] sigS = new byte[sigSize];
		
		signer.signComplete(request, (short)0, (short)request.length, sigR, (short)0, sigS, (short)0);
		
		// sanity check
		final boolean working = signer.verifyComplete(request, (short)0, (short)request.length, sigR, (short)0, (short)sigR.length, sigS, (short)0, (short)sigS.length);
		int responseCode = working ? 0 : 1;
		
		byte[] myResponse = { 'O', 'K' };
		
		// Source: https://bitcoin.stackexchange.com/a/92683
		// I tested this code on https://kjur.github.io/jsrsasign/sample/sample-ecdsa.html
		if (commandId == 0) {
			// Send the public key uncompressed.
			final EccAlg.CurvePoint pubkey = new EccAlg.CurvePoint(EccAlg.ECC_CURVE_TYPE_SECP256K1);
			signer.getPublicKey(pubkey);
			myResponse = new byte[1 + pubkey.x.length + pubkey.y.length];
			myResponse[0] = 0x04;
			System.arraycopy(pubkey.x, 0, myResponse, 1, pubkey.x.length);
			System.arraycopy(pubkey.y, 0, myResponse, pubkey.x.length + 1, pubkey.y.length);
		} else if (commandId == 1) {
			// Send the signature.
			myResponse = new byte[6 + sigSize * 2];
			myResponse[0] = 0x30;
			myResponse[1] = (byte)(myResponse.length - 2);
			myResponse[2] = 0x02;
			myResponse[3] = (byte)sigSize;
			System.arraycopy(sigR, 0, myResponse, 4, sigSize);
			myResponse[4 + sigSize] = 0x02;
			myResponse[5 + sigSize] = (byte)sigSize;
			System.arraycopy(sigS, 0, myResponse, 6 + sigSize, sigSize);
		}

		/*
		 * To return the response data to the command, call the setResponse
		 * method before returning from this method. 
		 * Note that calling this method more than once will 
		 * reset the response data previously set.
		 */
		setResponse(myResponse, 0, myResponse.length);

		/*
		 * In order to provide a return value for the command, which will be
		 * delivered to the SW application communicating with the Trusted Application,
		 * setResponseCode method should be called. 
		 * Note that calling this method more than once will reset the code previously set. 
		 * If not set, the default response code that will be returned to SW application is 0.
		 */
		setResponseCode(responseCode);

		/*
		 * The return value of the invokeCommand method is not guaranteed to be
		 * delivered to the SW application, and therefore should not be used for
		 * this purpose. Trusted Application is expected to return APPLET_SUCCESS code 
		 * from this method and use the setResposeCode method instead.
		 */
		return APPLET_SUCCESS;
	}

	/**
	 * This method will be called by the VM when the session being handled by
	 * this Trusted Application instance is being closed 
	 * and this Trusted Application instance is about to be removed.
	 * This method cannot provide response data and therefore
	 * calling setResponse or setResponseCode methods from it will throw a NullPointerException.
	 * 
	 * @return APPLET_SUCCESS code (the status code is not used by the VM).
	 */
	public int onClose() {
		DebugPrint.printString("Goodbye, DAL!");
		return APPLET_SUCCESS;
	}
}
