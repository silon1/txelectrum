package secp256k1_signer;

import java.util.Hashtable;
import java.util.Vector;

public class ExamplePersistence implements Persistence {
	
	private final Vector<byte[]> filesContent;
	private final Hashtable<HashableByteArray, Integer> mapper;
	
	public ExamplePersistence() {
		mapper = new Hashtable<HashableByteArray, Integer>();
		filesContent = new Vector<byte[]>();
	}

	public void write(byte[] identifier, byte[] content) {
		final HashableByteArray hashableId = new HashableByteArray(identifier);
		final int index = mapper.contains(hashableId) ? mapper.get(hashableId) : filesContent.size();
		mapper.put(hashableId, index);

		final byte[] copiedContent = new byte[content.length];
		System.arraycopy(content, 0, copiedContent, 0, content.length);
		filesContent.addElement(copiedContent);
	}

	public byte[] read(byte[] identifier) {
		final HashableByteArray hashableId = new HashableByteArray(identifier);
		final Integer index = mapper.get(hashableId);
		if (index == null) {
			return null;
		}

		final byte[] fileContent = filesContent.get(index);
		final byte[] content = new byte[fileContent.length];
		System.arraycopy(fileContent, 0, content, 0, fileContent.length);
		return content;
	}

}
