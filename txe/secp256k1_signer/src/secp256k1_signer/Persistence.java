package secp256k1_signer;

public interface Persistence {
	/**
	 * Writes content into a file identifed by a unique identifier.
	 * If the file exists, its content will be overwritten.
	 * Otherwise, a new file will be created.
	 */
	void write(byte[] identifier, byte[] content);

	/**
	 * Reads content from a file identified by a unique identifier.
	 * @return The content of the file if exists. Otherwise, null.
	 */
	byte[] read(byte[] identifier);
}
