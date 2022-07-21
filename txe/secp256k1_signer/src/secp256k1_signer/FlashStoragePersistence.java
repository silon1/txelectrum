package secp256k1_signer;

import java.util.Hashtable;

import com.intel.util.FlashStorage;

public class FlashStoragePersistence implements Persistence {
	private static final int MAPPER_FILE = 0;
	private static final int CONTENT_FILE = 1;
	private static final int MAPPER_ENTRY_BYTES = 12;
	
	private final Hashtable<ByteArrayHash, Metadata> mapper;
	
	private class Metadata {
		public final int offset;
		public final int length;
		
		public Metadata(int offset, int length) {
			this.offset = offset;
			this.length = length;
		}
	}
	
	public FlashStoragePersistence() {
		mapper = new Hashtable<ByteArrayHash, Metadata>();
		
		final int fileSize = FlashStorage.getFlashDataSize(MAPPER_FILE);
		if (fileSize == 0) {
			// The mapper file doesn't exist. This is the first time using the flash storage.
			return;
		}
		

		// Loading the mapper that was written into the MAPPER_FILE.

		final byte[] prevMapper = new byte[fileSize];
		FlashStorage.readFlashData(MAPPER_FILE, prevMapper, 0);
		
		for (int i = 0; i < prevMapper.length; i += MAPPER_ENTRY_BYTES) {
			final int hash = bytesToInt(prevMapper, i);
			final ByteArrayHash identifierHash = new ByteArrayHash(hash);
			final int offset = bytesToInt(prevMapper, i + 4);
			final int length = bytesToInt(prevMapper, i + 8);
			mapper.put(identifierHash, new Metadata(offset, length));
		}
	}

	public void write(final byte[] identifier, final byte[] content) {
		// Writing the content into the CONTENT_FILE, and updating the mapper.
		
		final int contentOffset = FlashStorage.getFlashDataSize(CONTENT_FILE);
		final byte[] newContentFile = new byte[contentOffset + content.length];
		if (contentOffset != 0) {
			// The file CONTENT_FILE exists. Read the previous contents to
			// append the new content to the end.
			FlashStorage.readFlashData(CONTENT_FILE, newContentFile, 0);
		}

		final ByteArrayHash identifierHash = new ByteArrayHash(identifier);
		mapper.put(identifierHash, new Metadata(contentOffset, content.length));
		
		System.arraycopy(content, 0, newContentFile, contentOffset, content.length);
		FlashStorage.writeFlashData(CONTENT_FILE, newContentFile, 0, newContentFile.length);
		

		// Updating the MAPPER_FILE with the new entry in the mapper.
		
		final int fileSize = FlashStorage.getFlashDataSize(MAPPER_FILE);
		byte[] savedMapper;
		
		if (fileSize != 0) {
			// The file mapper exists. Loading the old mapper into savedMapper.
			// Allocating MAPPER_ENTRY_BYTES at the end for the new entry.
			savedMapper = new byte[fileSize + MAPPER_ENTRY_BYTES];
			FlashStorage.readFlashData(MAPPER_FILE, savedMapper, 0);
		} else {
			// The file mapper doesn't exist. Creating a new file mapper with
			// space for the new entry.
			savedMapper = new byte[MAPPER_ENTRY_BYTES];
		}

		final int index = savedMapper.length - MAPPER_ENTRY_BYTES;
		intToBytes(identifierHash.hashCode(), savedMapper, index);
		intToBytes(contentOffset, savedMapper, index + 4);
		intToBytes(content.length, savedMapper, index + 8);
		FlashStorage.writeFlashData(MAPPER_FILE, savedMapper, 0, savedMapper.length);
	}

	public byte[] read(final byte[] identifier) {
		final ByteArrayHash identifierHash = new ByteArrayHash(identifier);
		final Metadata metadata = mapper.get(identifierHash);
		if (metadata == null) {
			return null;
		}

		final int contentFileSize = FlashStorage.getFlashDataSize(CONTENT_FILE);
		final byte[] contentFile = new byte[contentFileSize];
		FlashStorage.readFlashData(CONTENT_FILE, contentFile, 0);
		
		final byte[] content = new byte[metadata.length];
		System.arraycopy(contentFile, metadata.offset, content, 0, metadata.length);
		return content;
	}
	
	private int bytesToInt(final byte[] bytes, final int offset) {
		// Source: https://stackoverflow.com/a/7619315
		return ((bytes[offset + 0] & 0xFF) << 0 ) | 
			   ((bytes[offset + 1] & 0xFF) << 8 ) | 
			   ((bytes[offset + 2] & 0xFF) << 16) | 
			   ((bytes[offset + 3] & 0xFF) << 24);
	}
	
	private void intToBytes(final int value, final byte[] bytes, final int offset) {
		// Source: https://stackoverflow.com/a/7619315
		bytes[offset + 0] = (byte)(value >> 0 );
	    bytes[offset + 1] = (byte)(value >> 8 );
	    bytes[offset + 2] = (byte)(value >> 16);
	    bytes[offset + 3] = (byte)(value >> 24);
	}
}
