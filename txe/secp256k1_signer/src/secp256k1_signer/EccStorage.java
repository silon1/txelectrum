package secp256k1_signer;

import com.intel.langutil.ArrayUtils;

public class EccStorage {
	
	private final Persistence persistence;
	
	public EccStorage(Persistence persistence) {
		this.persistence = persistence;
	}
	
	public void write(byte[] compressedPublicKey, byte[] privateKey, byte[] hashedPassword) {
		final byte[] content = new byte[privateKey.length + hashedPassword.length];
		System.arraycopy(hashedPassword, 0, content, 0, hashedPassword.length);
		System.arraycopy(privateKey, 0, content, hashedPassword.length, privateKey.length);
		persistence.write(compressedPublicKey,  content);
	}

	public byte[] read(byte[] compressedPublicKey, byte[] hashedPassword) throws MissingPrivateKeyError, WrongPasswordError {
		final byte[] content = persistence.read(compressedPublicKey);
		if (content == null) {
			throw new MissingPrivateKeyError();
		}

		if (!ArrayUtils.compareByteArray(hashedPassword, 0, content, 0, hashedPassword.length)) {
			throw new WrongPasswordError();
		}

		final byte[] privateKey = new byte[32];
		System.arraycopy(content, hashedPassword.length, privateKey, 0, privateKey.length);
		return privateKey;
	}

}
