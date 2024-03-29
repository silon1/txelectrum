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
	
	// Note: The design note of the protocol between the host and the protocol can be found in `/txe/README.md`.
	
	// Request codes
	private static final int CREATE_KEYPAIR = 0;
	private static final int SIGN_BUFFER = 1;
	
	// Response codes
	private static final int OK = 0;
	private static final int BAD_REQUEST = 1;
	private static final int INTERNAL_ERROR = 2;
	private static final int MISSING_PRIVATE_KEY = 3;
	private static final int WRONG_PASSWORD = 4;
	
	// Buffer length's
	private static final int SHA1_BYTES = 20;
	private static final int SHA256_BYTES = 32;
	private static final int COMPRESSED_PUBLIC_KEY_BYTES = 33;
	private static final int DIGITAL_SIGNATURE_BYTES = 256;
	
	private EccAlg signer;
	private EccStorage storage;

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
	public int onInit(final byte[] request) {
		DebugPrint.printString("Hello, DAL!");
		signer = EccAlg.create(EccAlg.ECC_CURVE_TYPE_SECP256K1);
		storage =  new EccStorage();
		return APPLET_SUCCESS;
	}
	
	/**
	 * This method will be called by the VM to handle a command sent to this
	 * Trusted Application instance.
	 * 
	 * @param	requestId		the request ID (Trusted Application specific) 
	 * @param	inputBuffer		the input data for this command 
	 * @return	the return value should not be used by the applet
	 */
	public int invokeCommand(final int requestId, final byte[] inputBuffer) {
		int responseId = 0;
		byte[] outputBuffer = null;

		try {
			switch (requestId) {
			case CREATE_KEYPAIR:
				outputBuffer = new byte[COMPRESSED_PUBLIC_KEY_BYTES];
				responseId = createKeyPair(inputBuffer, outputBuffer);
				break;
			case SIGN_BUFFER:
				outputBuffer = new byte[DIGITAL_SIGNATURE_BYTES];
				responseId = signBuffer(inputBuffer, outputBuffer);
				break;
			default:
				// Unkown request id.
				responseId = BAD_REQUEST;
				outputBuffer = new byte[0];
				break;
			}
		} catch (Exception e) {
			responseId = INTERNAL_ERROR;
			outputBuffer = new byte[0];
		}
		
		setResponseCode(responseId);
		setResponse(outputBuffer, 0, outputBuffer.length);
		return APPLET_SUCCESS;
	}
	
	
	public int createKeyPair(final byte[] inputBuffer, final byte[] outputBuffer) {
		if (inputBuffer.length != SHA1_BYTES) {
			return BAD_REQUEST;
		}

		final short privateKeySize = signer.getPrivateKeySize();
		final byte[] privateKey = new byte[privateKeySize];
		final EccAlg.CurvePoint publicKey = new EccAlg.CurvePoint(EccAlg.ECC_CURVE_TYPE_SECP256K1);

		signer.generateKeys();
		signer.getKeys(publicKey, privateKey, (short) 0);
		compressPublicKey(publicKey, outputBuffer);

		storage.write(outputBuffer, privateKey, inputBuffer);
		
		return OK;
	}

	public int signBuffer(final byte[] inputBuffer, final byte[] outputBuffer) {
		if (inputBuffer.length != COMPRESSED_PUBLIC_KEY_BYTES + SHA1_BYTES + SHA256_BYTES) {
			return BAD_REQUEST;
		}

		final byte[] compressedPublicKey = new byte[COMPRESSED_PUBLIC_KEY_BYTES];
		final byte[] hashedPassword = new byte[SHA1_BYTES];
		System.arraycopy(inputBuffer, 0, compressedPublicKey, 0, compressedPublicKey.length);
		System.arraycopy(inputBuffer, compressedPublicKey.length, hashedPassword, 0, hashedPassword.length);
		
		try {
			final byte[] privateKey = storage.read(compressedPublicKey, hashedPassword);
			signer.setPrivateKey(privateKey, (short) 0, (short) privateKey.length);
			
			// EccAlg must recalculate and initalize the public key before signing the hash.
			EccAlg.CurvePoint publicKey = new EccAlg.CurvePoint(EccAlg.ECC_CURVE_TYPE_SECP256K1);
			signer.calculatePublicKey(publicKey);
			signer.setPublicKey(publicKey);
			
			final short sigSize = signer.getSignatureSize();
			final byte[] sigR = new byte[sigSize];
			final byte[] sigS = new byte[sigSize];
			final short hashIndex = (short) (compressedPublicKey.length + hashedPassword.length);
			signer.signHash(inputBuffer, hashIndex, (short) SHA256_BYTES, sigR, (short) 0, sigS, (short) 0);
			copyDigitalSignature(sigR, sigS, outputBuffer);
			
			return OK;
		} catch (MissingPrivateKeyError e) {
			return MISSING_PRIVATE_KEY;
		} catch (WrongPasswordError e) {
			return WRONG_PASSWORD;
		}
	}
	
	public void compressPublicKey(final EccAlg.CurvePoint publicKey, final byte[] output) {
		// Source: https://bitcoin.stackexchange.com/a/92683
		
		// Checks if y value is even or odd. y is in big-endian, thus the last byte determines
		// if it is even or odd.
		if ((publicKey.y[publicKey.y.length - 1] & 0x01) == 0) {
			// y value is even.
			output[0] = 0x02;
		} else {
			// y value is odd.
			output[0] = 0x03;
		}
		
		System.arraycopy(publicKey.x, 0, output, 1, publicKey.x.length);
	}
	
	public void copyDigitalSignature(final byte[] sigR, final byte[] sigS, final byte[] outputBuffer) {
		// Source: https://bitcoin.stackexchange.com/a/92683

		final byte sigRLength = (byte) ((sigR[0] & 0xFF) <= 0x7F ? sigR.length : sigR.length + 1);
		final byte sigSLength = (byte) ((sigS[0] & 0xFF) <= 0x7F ? sigS.length : sigS.length + 1);
		final byte sigSize = (byte) (6 + sigRLength + sigSLength);

		// Not part of DER format; It's a part of the protocol between the applet and the host.
		outputBuffer[0] = sigSize;

		outputBuffer[1] = 0x30;
		outputBuffer[2] = (byte) (sigSize -  2);
		outputBuffer[3] = 0x02;
		outputBuffer[4] = sigRLength;
		outputBuffer[5] = 0;
		System.arraycopy(sigR, 0, outputBuffer, 5 + sigRLength - sigR.length, sigR.length);
		outputBuffer[5 + sigRLength] = 0x02;
		outputBuffer[6 + sigRLength] = sigSLength;
		outputBuffer[7 + sigRLength] = 0;
		System.arraycopy(sigS, 0, outputBuffer, 7 + sigRLength + sigSLength - sigS.length, sigS.length);
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
