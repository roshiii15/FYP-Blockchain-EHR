# he_keygen.py
from phe import paillier
import pickle

def main():
    public_key, private_key = paillier.generate_paillier_keypair(n_length=2048)
    with open("he_pub.pkl", "wb") as f:
        pickle.dump(public_key, f)
    with open("he_priv.pkl", "wb") as f:
        pickle.dump(private_key, f)
    print("HE keypair generated: he_pub.pkl, he_priv.pkl")

if __name__ == "__main__":
    main()
