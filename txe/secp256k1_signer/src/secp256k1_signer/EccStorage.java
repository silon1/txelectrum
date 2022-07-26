package secp256k1_signer;

import com.intel.langutil.ArrayUtils;

public class EccStorage {
	
	private final Persistence persistence;
	
	public EccStorage(final Persistence persistence) {
		this.persistence = persistence;
	}

	public EccStorage() {
		this.persistence = new FlashStoragePersistence();
	}
	
	public void write(final byte[] compressedPublicKey, final byte[] privateKey, final byte[] hashedPassword) {
		final byte[] content = new byte[privateKey.length + hashedPassword.length];
		System.arraycopy(hashedPassword, 0, content, 0, hashedPassword.length);
		System.arraycopy(privateKey, 0, content, hashedPassword.length, privateKey.length);
	
		persistence.write(compressedPublicKey,  content);
	}

	public byte[] read(final byte[] compressedPublicKey, final byte[] hashedPassword) throws MissingPrivateKeyError, WrongPasswordError {
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
