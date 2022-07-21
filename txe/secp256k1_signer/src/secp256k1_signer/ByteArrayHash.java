package secp256k1_signer;

public class ByteArrayHash {
	
	private final int hash;
	
	public ByteArrayHash(final byte[] array) {
		hash = calcHashCode(array);
	}
	
	public ByteArrayHash(final int hash) {
		this.hash = hash;
	}
	
	public boolean equals(final Object o) {
		if (o == null || !(o instanceof ByteArrayHash)) {
			return false;
		}
        return hashCode() == o.hashCode();
    }
	
	public int hashCode() {
		return hash;
	}

    private int calcHashCode(final byte[] array) {
    	// Copied from http://hg.openjdk.java.net/jdk8/jdk8/jdk/file/687fd7c7986d/src/share/classes/java/util/Arrays.java

        if (array == null)
            return 0;
        int result = 1;
        for (long element : array) {
            int elementHash = (int)(element ^ (element >>> 32));
            result = 31 * result + elementHash;
        }

        return result;
    }
}
