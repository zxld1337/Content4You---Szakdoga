from security import get_password_hash, verify_password


def test_password_hashing():
    """
    TESZT 1: Biztosítja, hogy a hashelt jelszó nem egyezik meg a nyers jelszóval.
    Ezzel bizonyitva, hogy a titkosítás (bcrypt) lefut.
    """
    plain_password = "SecretPassword123!"
    hashed_password = get_password_hash(plain_password)

    assert plain_password != hashed_password
    assert len(hashed_password) > 20 


def test_password_verification_success():
    """
    TESZT 2: Biztosítja, hogy a helyes jelszó megadása esetén a validáció sikeres (True).
    """
    plain_password = "SecretPassword123!"
    hashed_password = get_password_hash(plain_password)

    is_valid = verify_password(plain_password, hashed_password)
    
    assert is_valid is True


def test_password_verification_failure():
    """
    TESZT 3: Biztosítja, hogy rossz jelszó esetén a validáció sikertelen (False).
    """
    plain_password = "SecretPassword123!"
    wrong_password = "WrongPassword456"
    hashed_password = get_password_hash(plain_password)

    is_valid = verify_password(wrong_password, hashed_password)
    
    assert is_valid is False