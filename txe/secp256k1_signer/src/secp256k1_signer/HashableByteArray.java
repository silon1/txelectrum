package secp256k1_signer;

public class HashableByteArray {
	
	private byte[] array;
	
	public HashableByteArray(byte[] array) {
		this.array = array;
	}
	
	public boolean equals(Object o) {
		if (o == null || !(o instanceof HashableByteArray)) {
			return false;
		}
        return hashCode() == o.hashCode();
    }

    public int hashCode() {
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
