import base64
from Crypto.Cipher import AES

class PasswordHandler:
  """Manage password reading "pseudo"-safely."""
  
  # == Methods ==
  @staticmethod
  def get_pwd_from_folder(path : str,seed : int) -> str:
    """Read the password from a file.
    
    Parameters
    ----------
    path : str
      The path to the folder starting the password obfuscation
    seed : int
      The sequence's seed

    Returns
    -------
    str
      The read password from the file
    """
    seq = PasswordHandler._deterministic_sequence(seed)
    with open(f"{path}/{next(seq)}/{next(seq)}/{next(seq)}/{next(seq)}/{next(seq)}/f40","r") as f:
      lines            = f.readlines()
      ciphertext       = base64.b64decode(lines[0].encode("utf-8"))
      key              = b'Strong pwd GNSS.'
      iv               = b'.SSNG dwp gnortS'
      cipher = AES.new(key, AES.MODE_CBC, iv)
      padded_plaintext = cipher.decrypt(ciphertext)
      padding_size     = padded_plaintext[-1]
      plaintext        = padded_plaintext[:-padding_size]
      return plaintext.decode("utf-8")
  
  @staticmethod
  def _deterministic_sequence(seed : int):
    """Deterministic sequence for generating folder.

    Parameters
    ----------
    seed : int
      The sequence's seed

    Yields
    ------
    int
      The next value of the sequence
    """
    a = 1103515245
    c = 12345
    m = 2 ** 31 - 1
    x = seed
    while True:
      x = (a * x + c) % m
      yield x % 2