#! python3
# -*- coding: utf-8 -*-

# A Python interface to CryptoSys API

# crsysapi.py
# $Date: 2023-05-27 09:31:00 $
# ************************** LICENSE *****************************************
# Copyright (C) 2023 David Ireland, DI Management Services Pty Limited.
# <www.di-mgt.com.au> <www.cryptosys.net>
# This code is provided 'as-is' without any express or implied warranty.
# Free license is hereby granted to use this code as part of an application
# provided this license notice is left intact. You are *not* licensed to
# share any of this code in any form of mass distribution, including, but not
# limited to, reposting on other websites or in any source code repository.
# ****************************************************************************

# Requires `CryptoSys API` to be installed on your system,
# available from <https://www.cryptosys.net/api.html>.

import platform
from ctypes import create_string_buffer, c_char_p, c_void_p, c_int, c_wchar_p

__version__ = "6.21.0.0001"
# History:
# [6.21.0] Updated for changes in CryptoSys API 6.21
# [6.20.0] First Python interface to CryptoSys API 6.20


# OUR EXPORTED CLASSES
__all__ = (
    'Error',
    'Gen', 'Aead', 'Blowfish', 'Cipher', 'CipherStream', 'Cnv', 'Crc', 'Compr',
    'Hash', 'Mac', 'Pbe', 'Prf', 'Rng', 'Wipe', 'Xof',
)

# Our global DLL/solibrary object for CryptoSys API
if platform.system() == 'Windows':
    from ctypes import windll
    _didll = windll.diCryptoSys
else:
    from ctypes import cdll
    _didll = cdll.LoadLibrary('libcryptosysapi.so')

# Global constants
_INTMAX = 2147483647
_INTMIN = -2147483648


class Error(Exception):
    """Raised when a call to a core API library function returns an error,
    or some obviously wrong parameter is detected."""

    # Google Python Style Guide: "The base exception for a module should be called Error."

    def __init__(self, value):
        """."""
        self.value = value

    @staticmethod
    def _isanint(v):
        try:
            v = int(v)
        except ValueError:
            pass
        return isinstance(v, int)

    def __str__(self):
        """Behave differently if value is an integer or not."""
        errcode = 0
        if (Error._isanint(self.value)):
            errcode = int(self.value)
            s1 = "ERROR CODE %d: %s" % (errcode, Gen.error_lookup(errcode))
        else:
            s1 = "ERROR: %s" % (self.value)
        lastcode = Gen.error_code()
        if lastcode != 0 and errcode != lastcode:
            s1 += ": (%d): %s" % (errcode, Gen.error_lookup(lastcode))
        return s1


class Gen:
    """General info about the core DLL and errors returned by it."""

    @staticmethod
    def version():
        """Return the release version of the core CryptoSys API DLL as an integer value."""
        return _didll.API_Version()

    @staticmethod
    def compile_time():
        """Return date and time the core native DLL was last compiled."""
        nchars = _didll.API_CompileTime(None, 0)
        buf = create_string_buffer(nchars + 1)
        nchars = _didll.API_CompileTime(buf, nchars)
        return buf.value.decode()

    @staticmethod
    def module_name():
        """Return full path name of the current process's DLL module."""
        nchars = _didll.API_ModuleName(None, 0, 0)
        buf = create_string_buffer(nchars + 1)
        nchars = _didll.API_ModuleName(buf, nchars, 0)
        return buf.value.decode()

    @staticmethod
    def module_info():
        """Get additional information about the core DLL module."""
        nchars = _didll.API_ModuleInfo(None, 0, 0)
        buf = create_string_buffer(nchars + 1)
        nchars = _didll.API_ModuleInfo(buf, nchars, 0)
        return buf.value.decode()

    @staticmethod
    def core_platform():
        """Return the platform the core DLL was compiled for ('Win32' or 'X64')."""
        nchars = 5
        buf = create_string_buffer(nchars + 1)
        nchars = _didll.API_Platform(buf, nchars)
        return buf.value.decode()[:nchars]

    @staticmethod
    def licence_type():
        """Return licence type: "D"=Developer "T"=Trial."""
        n = _didll.API_LicenceType(0)
        return chr(n)

    @staticmethod
    def error_lookup(n):
        """Return a description of an error code.

        Args:
            n (int): Code number

        Returns:
            str: Corresponding error message
        """
        nchars = _didll.API_ErrorLookup(None, 0, c_int(n))
        buf = create_string_buffer(nchars + 1)
        _didll.API_ErrorLookup(buf, nchars, c_int(n))
        return buf.value.decode()

    @staticmethod
    def error_code():
        """Return the error code of the *first* error that occurred when calling the last function."""
        return _didll.API_ErrorCode()


class Aead:
    """Authenticated encryption with Additional Data (AEAD) functions."""

    class AeadAlg:
        """AEAD algorithm options."""
        AES_128_GCM = 1  #: AEAD_AES_128_GCM authenticated encryption algorithm (RFC 5116)
        AES_256_GCM = 2  #: AEAD_AES_256_GCM authenticated encryption algorithm (RFC 5116)
        CHACHA20_POLY1305 = 29  #: AEAD_CHACHA20_POLY1305 authenticated encryption algorithm (RFC 7539)
        AEAD_ASCON_128 = 0x1a  #: ASCON-128 authentication scheme (provisional)
        AEAD_ASCON_128A = 0x1b  #: ASCON-128A authentication scheme (provisional)

    class Opts:
        """Advanced options."""
        DEFAULT = 0  #: Use default options
        PREFIXIV = 0x1000  #: Prepend the IV before the ciphertext in the output

    @staticmethod
    def encrypt_with_tag(input, key, iv, aeadalg, aad=None, opts=Opts.DEFAULT):
        """Encrypt data using specified AEAD algorithm in one-off operation. The authentication tag is appended to the output.

        Args:
            input (bytes): Input data to be encrypted.
            key (bytes): Key of exact length for algorithm (16 or 32 bytes).
            iv (bytes): Initialization Vector (IV) (aka nonce).
            aeadalg (Aead.Alg): AEAD algorithm.
            aad (bytes): Additional authenticated data (AAD) (optional).
            opts (Aead.Opts): Advanced options. Use :py:class:`Aead.Opts.PREFIXIV` to prepend the IV the output.

        Returns:
            bytes: Ciphertext with tag appended in a byte array.

        """
        noptions = int(aeadalg) | int(opts)
        if iv is None:
            ivlen = 0
            iv = b''
        else:
            ivlen = len(iv)
        if aad is None:
            aadlen = 0
            aad = b''
        else:
            aadlen = len(aad)
        n = _didll.AEAD_EncryptWithTag(None, 0, bytes(input), len(input), bytes(key), len(key), bytes(iv), ivlen, bytes(aad), aadlen, noptions)
        if (n < 0): raise Error(-n)
        buf = create_string_buffer(n)
        n = _didll.AEAD_EncryptWithTag(buf, n, bytes(input), len(input), bytes(key), len(key), bytes(iv), ivlen, bytes(aad), aadlen, noptions)
        return bytes(buf.raw)

    @staticmethod
    def decrypt_with_tag(input, key, iv, aeadalg, aad=None, opts=Opts.DEFAULT):
        """Decrypt data using specified AEAD algorithm in one-off operation. The authentication tag is expected appended to the output.

        Args:
            input (bytes): Input data to be decrypted.
            key (bytes): Key of exact length for algorithm (16 or 32 bytes).
            iv (bytes): Initialization Vector (IV) (aka nonce). Set as `None` if prepended to input.
            aeadalg (Aead.Alg): AEAD algorithm.
            aad (bytes): Additional authenticated data (AAD) (optional).
            opts (Aead.Opts): Advanced options. Use :py:class:`Aead.Opts.PREFIXIV` to expect the IV to be prepended to the input.

        Returns:
            bytes: Plaintext in a byte array.

        """
        noptions = int(aeadalg) | int(opts)
        if iv is None:
            ivlen = 0
            iv = b''
        else:
            ivlen = len(iv)
        if aad is None:
            aadlen = 0
            aad = b''
        else:
            aadlen = len(aad)
        n = _didll.AEAD_DecryptWithTag(None, 0, bytes(input), len(input), bytes(key), len(key), bytes(iv), ivlen, bytes(aad), aadlen, noptions)
        if (n < 0): raise Error(-n)
        buf = create_string_buffer(n)
        n = _didll.AEAD_DecryptWithTag(buf, n, bytes(input), len(input), bytes(key), len(key), bytes(iv), ivlen, bytes(aad), aadlen, noptions)
        return bytes(buf.raw)


class Cipher:
    """Generic block cipher functions."""
    # CONSTANTS
    class Alg:
        """Block cipher algorithms."""
        TDEA   = 0x10  #: Triple DES (3DES, des-ede3)
        AES128 = 0x20  #: AES-128
        AES192 = 0x30  #: AES-192
        AES256 = 0x40  #: AES-256

        def __or__(self, other):
            # Define this to avoid warnings when we try to "or" opts with another class.
            return self | other

    class Mode:
        """Block cipher modes."""
        ECB = 0      #: Electronic Code Book mode (default)
        CBC = 0x100  #: Cipher Block Chaining mode
        OFB = 0x200  #: Output Feedback mode
        CFB = 0x300  #: Cipher Feedback mode
        CTR = 0x400  #: Counter mode

    class Pad:
        """Block cipher padding options."""
        DEFAULT = 0             #: Use default padding
        NOPAD        = 0x10000  #: No padding is added
        PKCS5        = 0x20000  #: Padding scheme in PKCS#5/#7
        ONEANDZEROES = 0x30000  #: Pad with 0x80 followed by as many zero bytes necessary to fill the block
        ANSIX923     = 0x40000  #: Padding scheme in ANSI X9.23
        W3C          = 0x50000  #: Padding scheme in W3C XMLENC

        def __or__(self, other):
            # Define this to avoid warnings when we try to "or" opts with another class.
            return self | other

    class Opts:
        """Advanced options."""
        DEFAULT = 0  #: Use default options
        PREFIXIV = 0x1000  #: Prepend the IV before the ciphertext in the output (ignored for ECB mode)

    # Internal lookup
    _blocksize = {Alg.TDEA: 8, Alg.AES128: 16, Alg.AES192: 16, Alg.AES256: 16}
    _keysize = {Alg.TDEA: 24, Alg.AES128: 16, Alg.AES192: 24, Alg.AES256: 32}

    @staticmethod
    def blockbytes(alg):
        """Return the block size in bytes for a given cipher algorithm.

        Args:
            alg (Cipher.Alg): Cipher algorithm

        Returns:
            int: Block size in bytes
        """
        return Cipher._blocksize[int(alg)]

    @staticmethod
    def keybytes(alg):
        """Return the key size in bytes for a given cipher algorithm.

        Args:
            alg (Cipher.Alg): Cipher algorithm

        Returns:
            int: Key size in bytes
        """
        return Cipher._keysize[int(alg)]

    @staticmethod
    def encrypt(data, key, iv=None, algmodepad='', alg=None, mode=Mode.ECB, pad=Pad.DEFAULT, opts=Opts.DEFAULT):
        """Encrypt data.

        Args:
            data (bytes): Input data to be encrypted
            key (bytes): Key of exact length for block cipher algorithm
            iv (bytes): Initialization Vector (IV) of exactly the block size (see :py:func:`Cipher.blockbytes`) or ``None`` for ECB mode
            algmodepad (str): String containing the block cipher algorithm, mode and padding, e.g. ``"Aes128/CBC/OneAndZeroes"``
            alg (Cipher.Alg): Cipher algorithm. Ignored if ``algmodepad`` is set, otherwise required.
            mode (Cipher.Mode): Cipher mode. Ignored if ``algmodepad`` is set.
            pad (Cipher.Pad): Padding method to use. Ignored if ``algmodepad`` is set.
            opts (Cipher.Opts): Advanced options. Use Cipher.Opts.PREFIXIV to prepend the IV to the output.

        Returns:
            bytes: Ciphertext or empty array on error.
        """
        if (algmodepad is None or len(algmodepad) == 0):
            if (alg is None): raise Error("Cipher algorithm must be specified")
            noptions = alg | mode | pad
        else:
            noptions = 0
        noptions |= opts
        ivlen = 0
        if iv is None:
            iv = b''
        else:
            ivlen = len(iv)
        n = _didll.CIPHER_EncryptBytes(None, 0, bytes(data), len(data), bytes(key), len(key), bytes(iv), ivlen, algmodepad.encode(), noptions)
        if (n < 0): raise Error(-n)
        buf = create_string_buffer(n)
        n = _didll.CIPHER_EncryptBytes(buf, n, bytes(data), len(data), bytes(key), len(key), bytes(iv), ivlen, algmodepad.encode(), noptions)
        return bytes(buf.raw)

    @staticmethod
    def decrypt(data, key, iv=None, algmodepad='', alg=None, mode=Mode.ECB, pad=Pad.DEFAULT, opts=Opts.DEFAULT):
        """Decrypt data.

        Args:
            data (bytes): Input data to be decrypted
            key (bytes): Key of exact length for block cipher algorithm
            iv (bytes): Initialization Vector (IV) of exactly the block size (see :py:func:`Cipher.blockbytes`) or ``None`` for ECB mode
            algmodepad (str): String containing the block cipher algorithm, mode and padding, e.g. ``"Aes128/CBC/OneAndZeroes"``
            alg (Cipher.Alg): Cipher algorithm. Ignored if ``algmodepad`` is set, otherwise required.
            mode (Cipher.Mode): Cipher mode. Ignored if ``algmodepad`` is set.
            pad (Cipher.Pad): Padding method to use. Ignored if ``algmodepad`` is set.
            opts (Cipher.Opts): Advanced options. Use Cipher.Opts.PREFIXIV to expect the IV to be prepended at the start of the input.

        Returns:
            bytes: Plaintext in byte array or empty array on error.
        """
        if (algmodepad is None or len(algmodepad) == 0):
            if (alg is None): raise Error("Cipher algorithm must be specified")
            noptions = alg | mode | pad
        else:
            noptions = 0
        noptions |= opts
        ivlen = 0
        if iv is None:
            iv = b''
        else:
            ivlen = len(iv)
        dlen = len(data)
        buf = create_string_buffer(dlen)
        n = _didll.CIPHER_DecryptBytes(buf, dlen, bytes(data), len(data), bytes(key), len(key), bytes(iv), ivlen, algmodepad.encode(), noptions)
        if (n < 0): raise Error(-n)
        # Shorten output if necessary
        return bytes(buf.raw)[:n]

    @staticmethod
    def encrypt_hex(datahex, keyhex, ivhex='', algmodepad='', alg=None, mode=Mode.ECB, pad=Pad.DEFAULT, opts=Opts.DEFAULT):
        """Encrypt data hex-encoded data using hex-encoded parameters.

        Args:
            datahex (str): Input data to be encrypted encoded in hexadecimal.
            keyhex (str): Hex-encoded key of exact length for block cipher algorithm.
            ivhex (str): Hex-encoded Initialization Vector (IV) of exactly the block size (see :py:func:`Cipher.blockbytes`) or ``None`` for ECB mode.
            algmodepad (str): String containing the block cipher algorithm, mode and padding, e.g. ``"Aes128/CBC/OneAndZeroes"``.
            alg (Cipher.Alg): Cipher algorithm. Ignored if ``algmodepad`` is set, otherwise required.
            mode (Cipher.Mode): Cipher mode. Ignored if ``algmodepad`` is set.
            pad (Cipher.Pad): Padding method to use. Ignored if ``algmodepad`` is set.
            opts (Cipher.Opts): Advanced options. Use Cipher.Opts.PREFIXIV to prepend the IV to the output.

        Returns:
            str: Hex-encoded ciphertext or empty array on error.
        """
        if (algmodepad is None or len(algmodepad) == 0):
            if (alg is None): raise Error("Cipher algorithm must be specified")
            noptions = alg | mode | pad
        else:
            noptions = 0
        noptions |= opts
        if ivhex is None:
            ivhex = ''
        n = _didll.CIPHER_EncryptHex(None, 0, datahex.encode(), keyhex.encode(), ivhex.encode(), algmodepad.encode(), noptions)
        if (n < 0): raise Error(-n)
        buf = create_string_buffer(n + 1)
        n = _didll.CIPHER_EncryptHex(buf, n, datahex.encode(), keyhex.encode(), ivhex.encode(), algmodepad.encode(), noptions)
        return (buf.raw.decode())[:n]

    @staticmethod
    def decrypt_hex(datahex, keyhex, ivhex='', algmodepad='', alg=None, mode=Mode.ECB, pad=Pad.DEFAULT, opts=Opts.DEFAULT):
        """Decrypt hex-encoded data using hex-encoded parameters.

        Args:
            datahex (str): Input data to be decrypted encoded in hexadecimal.
            keyhex (str): Hex-encoded key of exact length for block cipher algorithm
            ivhex (str): Hex-encoded Initialization Vector (IV) of exactly the block size (see :py:func:`Cipher.blockbytes`) or ``None`` for ECB mode
            algmodepad (str): String containing the block cipher algorithm, mode and padding, e.g. ``"Aes128/CBC/OneAndZeroes"``
            alg (Cipher.Alg): Cipher algorithm. Ignored if ``algmodepad`` is set, otherwise required.
            mode (Cipher.Mode): Cipher mode. Ignored if ``algmodepad`` is set.
            pad (Cipher.Pad): Padding method to use. Ignored if ``algmodepad`` is set.
            opts (Cipher.Opts): Advanced options. Use Cipher.Opts.PREFIXIV to expect the IV to be prepended at the start of the input.

        Returns:
            str: Hex-encoded plaintext in byte array or empty array on error.
        """
        if (algmodepad is None or len(algmodepad) == 0):
            if (alg is None): raise Error("Cipher algorithm must be specified")
            noptions = alg | mode | pad
            algmodepad = ''
        else:
            noptions = 0
        noptions |= opts
        if ivhex is None:
            ivhex = ''
        n = _didll.CIPHER_DecryptHex(None, 0, datahex.encode(), keyhex.encode(), ivhex.encode(), algmodepad.encode(), noptions)
        if (n < 0): raise Error(-n)
        if (n == 0): return ''
        buf = create_string_buffer(n + 1)
        n = _didll.CIPHER_DecryptHex(buf, n, datahex.encode(), keyhex.encode(), ivhex.encode(), algmodepad.encode(), noptions)
        # Shorten output if necessary
        return (buf.raw.decode())[:n]

    @staticmethod
    def encrypt_block(data, key, iv=None, alg=Alg.TDEA, mode=Mode.ECB):
        """encrypt_block(data, key, iv=None, alg=Alg.TDEA, mode=Mode.ECB)
        Encrypt a block of data. Must be an exact multiple of block length.

        Args:
            data (bytes): Input data to be encrypted
            key (bytes): Key of exact length for block cipher algorithm
            iv (bytes): Initialization Vector (IV) of exactly the block size (see :py:func:`Cipher.blockbytes`) or ``None`` for ECB mode
            alg (Cipher.Alg): Cipher algorithm
            mode (Cipher.Mode): Cipher mode

        Returns:
            bytes: Ciphertext in byte array or empty array on error.
            Output is always the same length as the input.
        """
        noptions = alg | mode | Cipher.Pad.NOPAD
        ivlen = 0
        if iv is None:
            iv = b''
        else:
            ivlen = len(iv)
        # Output is always the same length as the input
        n = len(data)
        buf = create_string_buffer(n)
        n = _didll.CIPHER_EncryptBytes(buf, n, bytes(data), len(data), bytes(key), len(key), bytes(iv), ivlen, None, noptions)
        if (n < 0): raise Error(-n)
        return bytearray(buf.raw)

    @staticmethod
    def decrypt_block(data, key, iv=None, alg=Alg.TDEA, mode=Mode.ECB):
        """decrypt_block(data, key, iv=None, alg=Alg.TDEA, mode=Mode.ECB)
        Decrypt a block of data. Must be an exact multiple of block length.

        Args:
            data (bytes): Input data to be decrypted
            key (bytes): Key of exact length for block cipher algorithm
            iv (bytes): Initialization Vector (IV) of exactly the block size (see :py:func:`Cipher.blockbytes`) or ``None`` for ECB mode
            alg (Cipher.Alg): Cipher algorithm
            mode (Cipher.Mode): Cipher mode

        Returns:
            bytes: Plaintext in byte array or empty array on error.
            Output is always the same length as the input.
        """
        noptions = alg | mode | Cipher.Pad.NOPAD
        ivlen = 0
        if iv is None:
            iv = b''
        else:
            ivlen = len(iv)
        # Output is always the same length as the input
        n = len(data)
        buf = create_string_buffer(n)
        n = _didll.CIPHER_DecryptBytes(buf, n, bytes(data), len(data), bytes(key), len(key), bytes(iv), ivlen, None, noptions)
        if (n < 0): raise Error(-n)
        return bytearray(buf.raw)

    @staticmethod
    def file_encrypt(fileout, filein, key, iv, algmodepad='', alg=None, mode=Mode.ECB, pad=Pad.DEFAULT, opts=Opts.DEFAULT):
        """Encrypt a file.

        Args:
            fileout (str): Name of output file to be created or overwritten
            filein (str): Name of input file
            key (bytes): Key of exact length for block cipher algorithm
            iv (bytes): Initialization Vector (IV) of exactly the block size (see :py:func:`Cipher.blockbytes`) or ``None`` for ECB mode
            algmodepad (str): String containing the block cipher algorithm, mode and padding, e.g. ``"Aes128/CBC/OneAndZeroes"``
            alg (Cipher.Alg): Cipher algorithm. Ignored if ``algmodepad`` is set, otherwise required.
            mode (Cipher.Mode): Cipher mode. Ignored if ``algmodepad`` is set.
            pad (Cipher.Pad): Padding method to use. Ignored if ``algmodepad`` is set.
            opts (Cipher.Opts): Advanced options

        Returns:
            int: 0 if successful.

        Note:
            ``fileout`` and ``filein`` must *not* be the same.
        """
        if (algmodepad is None or len(algmodepad) == 0):
            if (alg is None): raise Error("Cipher algorithm must be specified")
            noptions = alg | mode | pad
        else:
            noptions = 0
        if (opts != 0):
            noptions |= opts
        ivlen = 0
        if iv is None:
            iv = b''
        else:
            ivlen = len(iv)
        n = _didll.CIPHER_FileEncrypt(fileout.encode(), filein.encode(), bytes(key), len(key), bytes(iv), ivlen, algmodepad.encode(), noptions)
        if (n != 0): raise Error(-n)
        return n

    @staticmethod
    def file_decrypt(fileout, filein, key, iv, algmodepad='', alg=None, mode=Mode.ECB, pad=Pad.DEFAULT, opts=Opts.DEFAULT):
        """Decrypt a file.

        Args:
            fileout (str): Name of output file to be created or overwritten
            filein (str): Name of input file
            key (bytes): Key of exact length for block cipher algorithm
            iv (bytes): Initialization Vector (IV) of exactly the block size (see :py:func:`Cipher.blockbytes`) or ``None`` for ECB mode
            algmodepad (str): String containing the block cipher algorithm, mode and padding, e.g. ``"Aes128/CBC/OneAndZeroes"``
            alg (Cipher.Alg): Cipher algorithm. Ignored if ``algmodepad`` is set, otherwise required.
            mode (Cipher.Mode): Cipher mode. Ignored if ``algmodepad`` is set.
            pad (Cipher.Pad): Padding method to use. Ignored if ``algmodepad`` is set.
            opts (Cipher.Opts): Advanced options

        Returns:
            int: 0 if successful.

        Note:
            ``fileout`` and ``filein`` must *not* be the same.
        """
        if (algmodepad is None or len(algmodepad) == 0):
            if (alg is None): raise Error("Cipher algorithm must be specified")
            noptions = alg | mode | pad
        else:
            noptions = 0
        if (opts != 0):
            noptions |= opts
        ivlen = 0
        if iv is None:
            iv = b''
        else:
            ivlen = len(iv)
        n = _didll.CIPHER_FileDecrypt(fileout.encode(), filein.encode(), bytes(key), len(key), bytes(iv), ivlen, algmodepad.encode(), noptions)
        if (n != 0): raise Error(-n)
        return n

    @staticmethod
    def key_wrap(data, kek, alg):
        """
        Wrap (encrypt) key material with a key-encryption key.

        Args:
            data (bytes): Input key material to be encrypted
            kek (bytes): Key encryption key
            alg (Cipher.Alg): Cipher algorithm

        Returns:
            bytes: Wrapped key in byte array.
        """
        noptions = alg
        n = _didll.CIPHER_KeyWrap(None, 0, bytes(data), len(data), bytes(kek), len(kek), noptions)
        if (n < 0): raise Error(-n)
        buf = create_string_buffer(n)
        n = _didll.CIPHER_KeyWrap(buf, n, bytes(data), len(data), bytes(kek), len(kek), noptions)
        if (n < 0): raise Error(-n)
        return bytearray(buf.raw)

    @staticmethod
    def key_unwrap(data, kek, alg):
        """
        Unwrap (decrypt) key material with a key-encryption key.

        Args:
            data (bytes): Wrapped key
            kek (bytes): Key encryption key
            alg (Cipher.Alg): Cipher algorithm

        Returns:
            bytes: Unwrapped key material in byte array.
        """
        noptions = alg
        n = _didll.CIPHER_KeyUnwrap(None, 0, bytes(data), len(data), bytes(kek), len(kek), noptions)
        if (n < 0): raise Error(-n)
        buf = create_string_buffer(n)
        n = _didll.CIPHER_KeyUnwrap(buf, n, bytes(data), len(data), bytes(kek), len(kek), noptions)
        if (n < 0): raise Error(-n)
        return bytearray(buf.raw)


    @staticmethod
    def pad(data, alg, pad=Pad.PKCS5):
        # HINT: Repeat signature as first line of docstring to get "pad=Pad.PKCS5" not "pad=131072"
        # http://www.sphinx-doc.org/en/stable/ext/autodoc.html#confval-autodoc_docstring_signature
        """pad(data, alg, pad=Pad.PKCS5)
        Pad byte array to correct length for ECB and CBC encryption.

        Args:
            data (bytes): data to be padded
            alg (Cipher.Alg): Block cipher being used
            pad (Cipher.Pad): Padding method to use.

        Returns:
            bytes: padded data in byte array.
        """
        blklen = Cipher._blocksize[int(alg)]
        n = _didll.PAD_BytesBlock(None, 0, bytes(data), len(data), blklen, pad)
        if (n < 0): raise Error(-n)
        buf = create_string_buffer(n)
        n = _didll.PAD_BytesBlock(buf, n, bytes(data), len(data), blklen, pad)
        return bytes(buf.raw)[:n]

    @staticmethod
    def pad_hex(datahex, alg, pad=Pad.PKCS5):
        """pad_hex(datahex, alg, pad=Pad.PKCS5)
        Pad hex-encoded string to correct length for ECB and CBC encryption.

        Args:
            datahex (str): hex-encoded data to be padded
            alg (Cipher.Alg): Block cipher being used
            pad (Cipher.Pad): Padding method to use.

        Returns:
            string: padded data in hex-encoded string.
        """
        blklen = Cipher._blocksize[int(alg)]
        n = _didll.PAD_HexBlock(None, 0, datahex.encode(), blklen, pad)
        if (n < 0): raise Error(-n)
        buf = create_string_buffer(n)
        n = _didll.PAD_HexBlock(buf, n, datahex.encode(), blklen, pad)
        return (buf.raw.decode())[:n]

    @staticmethod
    def unpad(data, alg, pad=Pad.PKCS5):
        """unpad(data, alg, pad=Pad.PKCS5)
        Remove padding from an encryption block.

        Args:
            data (bytes): padded data
            alg (Cipher.Alg): Block cipher being used
            pad (Cipher.Pad): Padding method to use.

        Returns:
            bytes: Unpadded data in byte array.

        Note:
            Unless ``pad`` is ``NoPad``, the
            unpadded output is *always* shorter than the padded input.
            An error is indicated by returning the *original* data. Check its length.
        """
        blklen = Cipher._blocksize[int(alg)]
        n = len(data)
        buf = create_string_buffer(n)
        n = _didll.PAD_UnpadBytes(buf, n, bytes(data), len(data), blklen, pad)
        return bytes(buf.raw)[:n]

    @staticmethod
    def unpad_hex(datahex, alg, pad=Pad.PKCS5):
        """unpad_hex(datahex, alg, pad=Pad.PKCS5)
        Remove the padding from a hex-encoded encryption block.

        Args:
            datahex (str): hex-encoded padded data
            alg (Cipher.Alg): Block cipher being used
            pad (Cipher.Pad): Padding method to use.

        Returns:
            string: Unpadded data in hex-encoded string or unchanged data on error.

        Note:
            Unless ``pad`` is ``NoPad``, the
            unpadded output is *always* shorter than the padded input.
            An error is indicated by returning the *original* data. Check its length.
        """
        blklen = Cipher._blocksize[int(alg)]
        n = len(datahex)
        buf = create_string_buffer(n)
        n = _didll.PAD_UnpadHex(buf, n, datahex.encode(), blklen, pad)
        return (buf.raw.decode())[:n]


class CipherStream:
    """Stream cipher functions."""

    class Alg:
        """Stream cipher algorithm."""
        ARCFOUR = 1  #: ARCFOUR (RC4) algorithm
        SALSA20 = 2  #: Salsa20 algorithm
        CHACHA20 = 3  #: Chacha20 algorithm

    @staticmethod
    def bytes(data, key, iv, alg, counter=0):
        """Encipher data in array of bytes using specified stream cipher.

        Args:
            data (bytes): Input data to be encrypted.
            key (bytes): Key (length restrictions apply, see Remarks).
            iv (bytes): Initialization Vector (IV, nonce) or None for Arcfour.
            alg (CipherStream.Alg): Stream cipher algorithm.
            counter (int): Counter value for ChaCha20 only, otherwise ignored.

        Returns:
            bytes: Ciphertext in a byte array.

        Note:
            - **Arcfour:** any length key; no IV.
            - **Salsa20:** key must be exactly 16 or 32 bytes and IV exactly 8 bytes long.
            - **ChaCha20:** key must be exactly 16 or 32 bytes and IV exactly 8, 12, or 16 bytes long. Counter is ignored if IV is 16 bytes.
        """
        noptions = int(alg)
        if iv is None:
            ivlen = 0
            iv = b''
        else:
            ivlen = len(iv)
        n = len(data)
        buf = create_string_buffer(n)
        r = _didll.CIPHER_StreamBytes(buf, bytes(data), len(data), bytes(key), len(key), bytes(iv), ivlen, counter, noptions)
        if (r != 0): raise Error(-r if r < 0 else r)
        return bytes(buf.raw)

    @staticmethod
    def file(fileout, filein, key, iv, alg, counter=0):
        """Encipher data in a file using specified stream cipher.

        Args:
            fileout (str): Name of output file to be created or overwritten.
            filein (str): Name of input file
            key (bytes): Key (length restrictions apply, see Remarks).
            iv (bytes): Initialization Vector (IV, nonce) or None for Arcfour.
            alg (CipherStream.Alg): Stream cipher algorithm.
            counter (int): Counter value for ChaCha20 only, otherwise ignored.

        Returns:
            int: 0 if successful.

        Note:
            - **Arcfour:** any length key; no IV.
            - **Salsa20:** key must be exactly 16 or 32 bytes and IV exactly 8 bytes long.
            - **ChaCha20:** key must be exactly 16 or 32 bytes and IV exactly 8, 12, or 16 bytes long. Counter is ignored if IV is 16 bytes.
        """
        noptions = int(alg)
        if iv is None:
            ivlen = 0
            iv = b''
        else:
            ivlen = len(iv)
        r = _didll.CIPHER_StreamFile(fileout.encode(), filein.encode(), bytes(key), len(key), bytes(iv), ivlen, counter, noptions)
        if (r != 0): raise Error(-r if r < 0 else r)
        return r


class Blowfish:
    """Blowfish cipher algorithm (Schneier, 1993)."""

    # Local constants
    __ENCRYPT = 1
    __DECRYPT = 0

    @staticmethod
    def encrypt_block(data, key, modestr="ECB", iv=None):
        """Encrypt a block of data. Must be an exact multiple of 8 bytes.

        Args:
            data (bytes): Input data to be encrypted
            key (bytes): Key of length between 1 and 56 bytes (448 bits)
            modestr (str): Cipher mode {"[ECB]"|"CBC"|"CFB"|"OFB"|"CTR"}
            iv (bytes): Initialization Vector (IV) of exactly 8 bytes or ``None`` for ECB mode

        Returns:
            bytes: Ciphertext in byte array or empty array on error.
            Output is always the same length as the input.
        """
        if iv is None:
            iv = b''
        # Output is always the same length as the input
        n = len(data)
        buf = create_string_buffer(n)
        n = _didll.BLF_BytesMode(buf, bytes(data), len(data), bytes(key), len(key), Blowfish.__ENCRYPT, modestr.encode(), bytes(iv))
        if (n != 0): raise Error(-n if n < 0 else n)
        return bytearray(buf.raw)

    @staticmethod
    def decrypt_block(data, key, modestr="ECB", iv=None):
        """Decrypt a block of data. Must be an exact multiple of 8 bytes.

        Args:
            data (bytes): Input data to be decrypted
            key (bytes): Key of length between 1 and 56 bytes (448 bits)
            modestr (str): Cipher mode {"[ECB]"|"CBC"|"CFB"|"OFB"|"CTR"}
            iv (bytes): Initialization Vector (IV) of exactly 8 bytes or ``None`` for ECB mode

        Returns:
            bytes: Plaintext in byte array or empty array on error.
            Output is always the same length as the input.
        """
        if iv is None:
            iv = b''
        # Output is always the same length as the input
        n = len(data)
        buf = create_string_buffer(n)
        n = _didll.BLF_BytesMode(buf, bytes(data), len(data), bytes(key), len(key), Blowfish.__DECRYPT, modestr.encode(), bytes(iv))
        if (n != 0): raise Error(-n if n < 0 else n)
        return bytearray(buf.raw)


class Cnv:
    """Character conversion routines."""

    @staticmethod
    def tohex(data):
        """
        Encode binary data as a hexadecimal string.

        Args:
            data (bytes): binary data to be encoded.

        Returns:
            str: Hex-encoded string.
            Letters [A-F] are in uppercase. Use ``s.lower()`` for lowercase.
        Examples:
            >>> Cnv.tohex(b"abc\xe9")
            '616263E9'
            >>> Cnv.tohex(bytearray([0xde, 0xad, 0xbe, 0xef])).lower()
            'deadbeef'
        """
        nbytes = len(data)
        if (nbytes == 0): return ""
        nc = _didll.CNV_HexStrFromBytes(None, 0, bytes(data), nbytes)
        if (nc < 0): raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        nc = _didll.CNV_HexStrFromBytes(buf, nc, bytes(data), nbytes)
        return buf.value.decode()[:nc]

    @staticmethod
    def fromhex(s):
        """Decode a hexadecimal-encoded string into a byte array.

        Args:
            s (str): Hex-encoded string

        Returns:
            bytes: Binary data in byte array.

        Note:
            Whitespace and ASCII punctuation characters in the input are ignored,
            but other non-hex characters, e.g. ``[G-Zg-z]``, will cause an error.

        Examples:
            >>> Cnv.fromhex("61:62:63")
            'abc'

        """
        n = _didll.CNV_BytesFromHexStr(None, 0, s.encode())
        if (n < 0): raise Error(-n)
        if (n == 0): return bytes()
        buf = create_string_buffer(n)
        n = _didll.CNV_BytesFromHexStr(buf, n, s.encode())
        return bytes(buf.raw)[:n]

    @staticmethod
    def tobase64(data):
        """Encode binary data as a base64 string.

        Args:
            data (bytes): binary data to be encoded.

        Returns:
            str: Base64-encoded string.

        Example:
            >>> Cnv.tobase64(Cnv.fromhex('fedcba9876543210'))
            '/ty6mHZUMhA='
        """
        nbytes = len(data)
        if (nbytes == 0): return ""
        nc = _didll.CNV_B64StrFromBytes(None, 0, bytes(data), nbytes)
        if (nc < 0): raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        nc = _didll.CNV_B64StrFromBytes(buf, nc, bytes(data), nbytes)
        return buf.value.decode()[:nc]

    @staticmethod
    def frombase64(s):
        """Decode a base64-encoded string into a byte array.

        Args:
            s (str): Base64-encoded data

        Returns:
            bytes: Binary data in byte array.

        Note:
            Whitespace characters are ignored,
            but other non-base64 characters will cause an error.
        """
        n = _didll.CNV_BytesFromB64Str(None, 0, s.encode())
        if (n < 0): raise Error(-n)
        if (n == 0): return bytes("")
        buf = create_string_buffer(n)
        n = _didll.CNV_BytesFromB64Str(buf, n, s.encode())
        return bytes(buf.raw)[:n]

    @staticmethod
    def shortpathname(pathName):
        """Retrieve the Windows short path form of the specified path.

        Args:
            pathName (str): Path name.

        Returns:
            str: Windows short path name of file or empty string if file does not exist.

        Note:
            Windows only. The file path must exist. The short path name is guaranteed to be ASCII and
            can be used as a filename argument in any function in this Toolkit.

        Example:
            >>> Cnv.shortpathname("work/你好.txt")
            'work/FC0F~1.TXT'
        """

        n = _didll.CNV_ShortPathName(None, 0, pathName)
        if (n < 0): raise Error(-n)
        if (n == 0): return str("")
        buf = create_string_buffer(n)
        n = _didll.CNV_ShortPathName(buf, n, pathName)
        return (buf.raw.decode())[:n]


class Crc:
    """CRC-32 computations."""

    @staticmethod
    def bytes(data):
        """Computes the CRC-32 checksum of an array of bytes."""
        return _didll.CRC_Bytes(data, len(data), 0) & 0xffffffff

    @staticmethod
    def file(filename):
        """Computes the CRC-32 checksum of a file."""
        return _didll.CRC_File(filename.encode(), 0) & 0xffffffff


class Hash:
    """Message digest hash functions."""

    # CONSTANTS
    class Alg:
        """Hash algorithms."""
        SHA1   = 0  #: SHA-1 (default)
        SHA224 = 6  #: SHA-224
        SHA256 = 3  #: SHA-256
        SHA384 = 4  #: SHA-384
        SHA512 = 5  #: SHA-512
        SHA3_224 = 0xA  #: SHA-3-224
        SHA3_256 = 0xB  #: SHA-3-256
        SHA3_384 = 0xC  #: SHA-3-384
        SHA3_512 = 0xD  #: SHA-3-512
        MD5 = 1  #: MD5
        RMD160 = 7  #: RIPEMD-160
        ASCON_HASH = 0xAF  #: ASCON-HASH
        ASCON_HASHA = 0xBF #: ASCON-HASHA

        def __or__(self, other):
            return self | other

    @staticmethod
    def length(alg):
        """length(alg)
        Return length of message digest output in bytes.

        Args:
            alg (Hash.Alg): Hash algorithm.

        Returns:
            int: Length of the hash function output in bytes.

        Examples:
            >>> Hash.length(Hash.Alg.SHA256)
            32
            >>> Hash.length(Hash.Alg.SHA512)
            64
        """
        n = _didll.HASH_Length(alg)
        if (n < 0): raise Error(-n)
        return n

    @staticmethod
    def data(data, alg=Alg.SHA1):
        """data(data, alg=Alg.SHA1)
        Compute message digest as a byte array from bytes data.

        Args:
            data (bytes): Message data
            alg (Hash.Alg): Hash algorithm to be used

        Returns:
            bytes: Message digest in byte array.
        """
        n = _didll.HASH_Bytes(None, 0, bytes(data), len(data), alg)
        if (n < 0): raise Error(-n)
        buf = create_string_buffer(n)
        _didll.HASH_Bytes(buf, n, bytes(data), len(data), alg)
        return bytearray(buf.raw)

    @staticmethod
    def file(filename, alg=Alg.SHA1):
        """file(filename, alg=Alg.SHA1)
        Compute message digest as a byte array from data in a file.

        Args:
            filename (str): Name of file containing message data
            alg (Hash.Alg): Hash algorithm to be used (ASCON is not supported in file mode)

        Returns:
            bytes: Message digest in byte array.
        """
        n = _didll.HASH_File(None, 0, filename.encode(), alg)
        if (n < 0): raise Error(-n)
        buf = create_string_buffer(n)
        _didll.HASH_File(buf, n, filename.encode(), alg)
        return bytearray(buf.raw)

    @staticmethod
    def hex_from_data(data, alg=Alg.SHA1):
        """hex_from_data(data, alg=Alg.SHA1)
        Compute message digest in hexadecimal format from bytes data.

        Args:
            data (bytes): Message data in byte array.
            alg (Hash.Alg): Hash algorithm to be used.

        Returns:
            string: Message digest in hex-encoded format.

        Examples:
            >>> Hash.hex_from_data(b'abc')
            'a9993e364706816aba3e25717850c26c9cd0d89d'
            >>> Hash.hex_from_data(b'abc', Hash.Alg.SHA256)
            'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
        """
        nc = _didll.HASH_HexFromBytes(None, 0, bytes(data), len(data), alg)
        if (nc < 0): raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        _didll.HASH_HexFromBytes(buf, nc, bytes(data), len(data), alg)
        return buf.value.decode()

    @staticmethod
    def hex_from_string(s, alg=Alg.SHA1):
        """hex_from_string(s, alg=Alg.SHA1)
        Compute message digest in hexadecimal format from a string.

        Args:
            s (str): Message data in UTF-8 string.
            alg (Hash.Alg): Hash algorithm to be used.

        Returns:
            str: Message digest in hex-encoded format.

        Examples:
            >>> Hash.hex_from_string('abc', Hash.Alg.SHA256)
            'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
            >>> Hash.hex_from_string('Olá mundo')  # UTF-8
            'f6c2fc0dd7f1131d8cb5ac7420d77a4c28ac1aa0'
            >>> Hash.hex_from_string("", Hash.Alg.ASCON_HASHA)
            'aecd027026d0675f9de7a8ad8ccf512db64b1edcf0b20c388a0c7cc617aaa2c4'
        """
        return Hash.hex_from_data(s.encode(), alg)

    @staticmethod
    def hex_from_file(filename, alg=Alg.SHA1):
        """hex_from_file(filename, alg=Alg.SHA1)
        Compute message digest in hexadecimal format from data in a file.

        Args:
            filename (str): Name of file containing message data
            alg (Hash.Alg): Hash algorithm to be used (ASCON is not supported in file mode)

        Returns:
            str: Message digest in hex-encoded format
        """
        nc = _didll.HASH_HexFromFile(None, 0, filename.encode(), alg)
        if (nc < 0): raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        _didll.HASH_HexFromFile(buf, nc, filename.encode(), alg)
        return buf.value.decode()

    @staticmethod
    def hex_from_hex(datahex, alg=Alg.SHA1):
        """hex_from_hex(datahex, alg=Alg.SHA1)
        Compute message digest in hexadecimal format from data in a hexadecimal-encoded string.

        Args:
            datahex (str): Message data in hex-encoded format
            alg (Hash.Alg): Hash algorithm to be used

        Returns:
            str: Message digest in hex-encoded format.

        Examples:
            >>> Hash.hex_from_hex('616263')  # HEX('abc')
            'a9993e364706816aba3e25717850c26c9cd0d89d'
        """
        nc = _didll.HASH_HexFromHex(None, 0, datahex.encode(), alg)
        if (nc < 0): raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        _didll.HASH_HexFromHex(buf, nc, datahex.encode(), alg)
        return buf.value.decode()

    @staticmethod
    def hex_from_bits(data, databitlen, alg=Alg.SHA1):
        """hex_from_bits(data, databitlen, alg=Alg.SHA1)
        Compute message digest in hexadecimal format from bit-oriented data.

        Args:
            data (bytes): Message data in byte array.
            databitlen (int): Length of message data in bits.
            alg (Hash.Alg): Hash algorithm to be used (only the SHA family is supported).

        Returns:
            string: Message digest in hex-encoded format.

        Note:
            Pass a bitstring as an array of bytes in `data` in big-endian order with the most-significant bit first.
            The bitstring will be truncated to the number of bits specified in `databitlen`.
            The number of bytes in `data` must be at least `ceil(databitlen / 8)`.

        Examples:
            >>> Hash.hex_from_bits(Cnv.fromhex("5180"), 9, Hash.Alg.SHA1)  # 0101 0001 1
            '0f582fa68b71ecdf1dcfc4946019cf5a18225bd2'
            >>> Hash.hex_from_bits(Cnv.fromhex("2590A0"), 22, Hash.Alg.SHA3_256)  # 1001 0110 0100 0010 1000 00
            'd5863d4b1ff41551c92a9e08c52177e32376c9bd100c611c607db840096eb22f'
        """
        nc = _didll.HASH_HexFromBits(None, 0, bytes(data), databitlen, alg)
        if (nc < 0): raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        _didll.HASH_HexFromBits(buf, nc, bytes(data), databitlen, alg)
        return buf.value.decode()


class Mac:
    """Message authentication code (MAC) functions."""

    # CONSTANTS
    class Alg:
        """MAC algorithms."""
        HMAC_SHA1 = 0  #: HMAC-SHA-1 (default)
        HMAC_SHA224 = 6  #: HMAC-SHA-224
        HMAC_SHA256 = 3  #: HMAC-SHA-256
        HMAC_SHA384 = 4  #: HMAC-SHA-384
        HMAC_SHA512 = 5  #: HMAC-SHA-512
        HMAC_SHA3_224 = 0xA  #: HMAC-SHA-3-224
        HMAC_SHA3_256 = 0xB  #: HMAC-SHA-3-256
        HMAC_SHA3_384 = 0xC  #: HMAC-SHA-3-384
        HMAC_SHA3_512 = 0xD  #: HMAC-SHA-3-512
        HMAC_MD5 = 1  #: HMAC-MD5
        HMAC_RMD160 = 7  #: HMAC-RMD160
        CMAC_TDEA = 0x100  #: CMAC-TDEA (CMAC-DESEDE)
        CMAC_AES128 = 0x101  #: CMAC-AES128
        CMAC_AES192 = 0x102  #: CMAC-AES192
        CMAC_AES256 = 0x103  #: CMAC-AES256
        MAC_POLY1305 = 0x200  #: Poly1305
        KMAC_128 = 0x201  #: KMAC128 with a fixed-length output of 256 bits (32 bytes)
        KMAC_256 = 0x202  #: KMAC256 with a fixed-length output of 512 bits (64 bytes)

    @staticmethod
    def data(data, key, alg=Alg.HMAC_SHA1):
        """data(data, key, alg=Alg.HMAC_SHA1)
        Compute a message authentication code (MAC) as a byte array from bytes data.

        Args:
            data (bytes): Message to be signed in byte array.
            key (bytes): Key in byte array.
            alg (Mac.Alg): MAC algorithm to be used.

        Returns:
            bytes: MAC in byte format
        """
        n = _didll.MAC_Bytes(None, 0, bytes(data), len(data), bytes(key), len(key), alg)
        if (n < 0): raise Error(-n)
        buf = create_string_buffer(n)
        n = _didll.MAC_Bytes(buf, n, bytes(data), len(data), bytes(key), len(key), alg)
        return bytearray(buf.raw)

    @staticmethod
    def hex_from_data(data, key, alg=Alg.HMAC_SHA1):
        """hex_from_data(data, key, alg=Alg.HMAC_SHA1)
        Compute a message authentication code (MAC) in hexadecimal format from bytes data.

        Args:
            data (bytes): Message to be signed in byte array.
            key (bytes): Key in byte array.
            alg (Mac.Alg): MAC algorithm to be used.

        Returns:
            str: MAC in hex-encoded format.

        Examples:
            >>> Mac.hex_from_data(b"Hi There", Cnv.fromhex("0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b"))
            'b617318655057264e28bc0b6fb378c8ef146be00'
        """
        nc = _didll.MAC_HexFromBytes(None, 0, bytes(data), len(data), bytes(key), len(key), alg)
        if (nc < 0): raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        nc = _didll.MAC_HexFromBytes(buf, nc, bytes(data), len(data), bytes(key), len(key), alg)
        return buf.value.decode()

    @staticmethod
    def hex_from_string(s, key, alg=Alg.HMAC_SHA1):
        """hex_from_string(s, key, alg=Alg.HMAC_SHA1)
        Compute a message authentication code (MAC) in hexadecimal format from string data.

        Args:
            s (str): Message data in UTF-8 string.
            key (bytes): Key in byte array.
            alg (Mac.Alg): MAC algorithm to be used.

        Returns:
            str: Message digest in hex-encoded format.
        """
        return Mac.hex_from_data(s.encode(), key, alg)

    @staticmethod
    def hex_from_hex(datahex, keyhex, alg=Alg.HMAC_SHA1):
        """hex_from_hex(datahex, keyhex, alg=Alg.HMAC_SHA1)
        Compute a message authentication code (MAC) in hex format from data in hex-encoded strings.

        Args:
            datahex (str): Message to be signed in hex-encoded format.
            keyhex (str): Key in hex-encoded format.
            alg (Mac.Alg): MAC algorithm to be used.

        Returns:
            str: HMAC in hex-encoded format.

        Examples:
            >>> # HEX('Hi There') = 4869205468657265
            >>> Mac.hex_from_hex("4869205468657265", "0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b")
            'b617318655057264e28bc0b6fb378c8ef146be00'
        """
        nc = _didll.MAC_HexFromHex(None, 0, datahex.encode(), keyhex.encode(), alg)
        if (nc < 0): raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        nc = _didll.MAC_HexFromHex(buf, nc, datahex.encode(), keyhex.encode(), alg)
        return buf.value.decode()


class Rng:
    """Random Number Generator to NIST SP800-90."""

    # FIELDS
    SEED_BYTES = 64  #: Size in bytes of seed file

    @staticmethod
    def bytestring(n):
        """Generate an array of n random bytes.

        Args:
            n (int): Required number of random bytes.

        Returns:
            bytes: Array of random bytes.
        """
        if (n < 0 or n > _INTMAX): raise Error('n out of range')
        buf = create_string_buffer(n)
        n = _didll.RNG_KeyBytes(buf, n, None, 0)
        return bytes(buf.raw)

    @staticmethod
    def number(lower, upper):
        """Generate a random integer in a given range.

        Args:
            lower (int): lower value of range
            upper (int): upper value of range

        Returns:
            int: Random integer x: ``lower <= x <= upper``
        """
        if (lower < _INTMIN) or (lower > _INTMAX): raise Error('out of range')
        if (upper < _INTMIN) or (upper > _INTMAX): raise Error('out of range')
        n = _didll.RNG_Number(lower, upper)
        return n

    @staticmethod
    def octet():
        """Generate a single random octet (byte).

        Returns:
            int: Single byte value randomly chosen between 0 and 255
        """
        n = _didll.RNG_Number(0, 255)
        return n

    @staticmethod
    def initialize(seedfilename):
        """Initialize the RNG generator using a seed file.

        Use a seed file to increase the entropy for the current session.
        Initialization is recommended but not mandatory.
        The seed file is automatically updated by this procedure.

        Args:
            seedfilename (str): Full path name of seed file.
                If the seed file does not exist, it will be created.

        Returns:
            int: Zero if successful.
        """
        n = _didll.RNG_Initialize(seedfilename.encode(), 0)
        if (n != 0): raise Error(-n if n < 0 else n)
        return n

    @staticmethod
    def update_seedfile(seedfilename):
        """Update the RNG seed file with more entropy.

        Args:
            seedfilename (str): Full path name of seed file.
                The seed file must exist and be writable.

        Returns:
            int: Zero if successful.
        """
        n = _didll.RNG_UpdateSeedFile(seedfilename.encode(), 0)
        if (n != 0): raise Error(-n if n < 0 else n)
        return n


class Compr:
    """Compression utilities."""

    class Alg:
        """Key derivation function algorithms."""
        ZLIB = 0x0  #: zlib algorithm (default)
        ZSTD = 0x1  #: Zstandard algorithm

    @staticmethod
    def compress(data, alg=Alg.ZLIB):
        """Compress data using compression algorithm.

        Args:
             data (bytes): Data to be compressed.
             alg (Compr.Alg): Compression algorithm.

        Returns:
             bytes: Compressed data.
        """
        opts = alg
        n = _didll.COMPR_Compress(None, 0, bytes(data), len(data), opts)
        if (n < 0): raise Error(-n)
        if (n == 0): return bytes("")
        buf = create_string_buffer(n)
        n = _didll.COMPR_Compress(buf, n, bytes(data), len(data), opts)
        return bytes(buf.raw)[:n]

    @staticmethod
    def uncompress(data, alg=Alg.ZLIB):
        """Uncompress data using compression algorithm.

        Args:
             data (bytes): Compressed data to be uncompressed.
             alg (Compr.Alg): Compression algorithm.

        Returns:
             bytes: Uncompressed data.
        """
        opts = alg
        n = _didll.COMPR_Uncompress(None, 0, bytes(data), len(data), opts)
        if (n < 0): raise Error(-n)
        if (n == 0): return bytes("")
        buf = create_string_buffer(n)
        n = _didll.COMPR_Uncompress(buf, n, bytes(data), len(data), opts)
        return bytes(buf.raw)[:n]


class Pbe:
    """Password-based encryption."""

    class PrfAlg:
        """PRF algorithms."""
        HMAC_SHA1   = 0  #: HMAC-SHA-1 (default)
        HMAC_SHA224 = 6  #: HMAC-SHA-224
        HMAC_SHA256 = 3  #: HMAC-SHA-256
        HMAC_SHA384 = 4  #: HMAC-SHA-384
        HMAC_SHA512 = 5  #: HMAC-SHA-512

    @staticmethod
    def kdf2(dklen, password, salt, count, prfalg=0):
        """Derive a key of any length from a password using the PBKDF2 algorithm.

        Args:
            dklen (int): Required length of key in bytes
            password (str): Password
            salt (bytes): Salt in byte array
            count (int): Iteration count
            prfalg (PrfAlg): Algorithm to use in PRF [default = HMAC-SHA-1]

        Returns:
            bytes: Derived key in byte array.

        Examples:
            >>> Cnv.tohex(Pbe.kdf2(24, 'password', Cnv.fromhex('78578E5A5D63CB06'), 2048))
            'BFDE6BE94DF7E11DD409BCE20A0255EC327CB936FFE93643'

        """
        if (dklen <= 0 or dklen > _INTMAX): raise Error('dklen out of range')
        buf = create_string_buffer(dklen)
        n = _didll.PBE_Kdf2(buf, dklen, password.encode(), len(password.encode()), bytes(salt), len(salt), count, prfalg)
        if (n != 0): raise Error(-n if n < 0 else n)
        return bytes(buf.raw)

    @staticmethod
    def scrypt(dklen, pwdbytes, salt, N, r, p):
        """Derive a key of any length from a password using the SCRYPT algorithm from RFC7914.

        Args:
            dklen (int): Required length of key in bytes
            pwdbytes (bytes): Password encoded in bytes
            salt (bytes): Salt in byte array
            N (int): CPU/Memory cost parameter, a number greater than one and a power of 2.
            r (int): Block size r.
            p (int): Parallelization parameter p.

        Returns:
            bytes: Derived key in byte array.

        Examples:
            >>> Cnv.tohex(Pbe.kdf2(64, b'password', b'NaCl', 1024, 8, 16))
            'FDBABE1C9D3472007856E7190D01E9FE7C6AD7CBC8237830E77376634B373162'
            '2EAF30D92E22A3886FF109279D9830DAC727AFB94A83EE6D8360CBDFA2CC0640'
            >>> Cnv.tohex(Pbe.scrypt(64, b'', b'', 16, 1, 1))
            '77D6576238657B203B19CA42C18A0497F16B4844E3074AE8DFDFFA3FEDE21442'
            'FCD0069DED0948F8326A753A0FC81F17E8D3E0FB2E0D3628CF35E20C38D18906'
        """

        if (dklen <= 0 or dklen > _INTMAX): raise Error('dklen out of range')
        buf = create_string_buffer(dklen)
        n = _didll.PBE_Scrypt(buf, dklen, bytes(pwdbytes), len(pwdbytes), bytes(salt), len(salt), N, r, p)
        if (n != 0): raise Error(-n if n < 0 else n)
        return bytes(buf.raw)


class Prf:
    """Pseudorandom function (PRF) Functions."""

    class Alg:
        """Key derivation function algorithms."""
        KMAC128 = 0x201  #: KMAC128 as per NIST SP 800-185
        KMAC256 = 0x202  #: KMAC256 as per NIST SP 800-185

    @staticmethod
    def bytes(numbytes, msg, key, prfalg, customstring=""):
        """Generate output bytes using a pseudorandom function (PRF).

        Args:
            numbytes (int): Required number of output bytes.
            msg (bytes): Input message data.
            key (bytes): Key.
            prfalg (Prf.Alg): PRF algorithm
            customstring (str): Customization string (optional).

        Returns:
            bytes: Output data.

        """
        # NB numbytes is arbitrary, returns numbytes on success
        if (numbytes <= 0 or numbytes > _INTMAX): raise Error('numbytes out of range')
        buf = create_string_buffer(numbytes)
        opts = prfalg
        n = _didll.PRF_Bytes(buf, numbytes, bytes(msg), len(msg), bytes(key), len(key), customstring.encode(), opts)
        if (n < 0): raise Error(-n if n < 0 else n)
        return bytes(buf.raw)


class Wipe:
    """Wipe data securely."""
    class Options:
        """Wipe options."""
        DEFAULT = 0x0    #: Default options (DOD 7-pass).
        DOD7PASS = 0x0  #: DOD 7-pass (default).
        SIMPLE = 0x1  #: Overwrite with single pass of zero bytes (quicker but less secure).

    @staticmethod
    def file(filename, opts=Options.DEFAULT):
        """Securely wipe and delete a file.

        Args:
            filename (str): Name of file to be wiped.
            opts (Wipe.Options): Options.
        """
        n = _didll.WIPE_File(filename.encode(), opts)
        if (n != 0): raise Error(-n if n < 0 else n)

    @staticmethod
    def data(data):
        """Zeroize data in memory.

        Args:
            data (bytes): data to be wiped.
        """
        n = _didll.WIPE_Data(bytes(data), len(data))
        if (n != 0): raise Error(-n if n < 0 else n)


class Xof:
    """Extendable-output function (XOF)."""

    class Alg:
        """Extendable-output function (XOF) algorithm."""
        SHAKE128 = 0x203  #: SHAKE128 as per FIPS PUB 202
        SHAKE256 = 0x204  #: SHAKE256 as per FIPS PUB 202
        MGF1_SHA1 = 0x210    #: MGF1-SHA-1 as per PKCS#1
        MGF1_SHA256 = 0x213  #: MGF1-SHA-256
        MGF1_SHA512 = 0x215  #: MGF1-SHA-512
        ASCON_XOF = 0x20A  #: ASCON-XOF
        ASCON_XOFA = 0x20B  #: ASCON-XOFA

    @staticmethod
    def bytes(numbytes, msg, xofalg):
        """Generate bytes using an extendable-output function (XOF).

        Args:
            numbytes (int): Required number of output bytes.
            msg (bytes): Input message data.
            xofalg (Xof.Alg): XOF algorithm

        Returns:
            bytes: Output data.

        """
        # NB numbytes is arbitrary, returns numbytes on success
        if (numbytes <= 0 or numbytes > _INTMAX): raise Error('numbytes out of range')
        buf = create_string_buffer(numbytes)
        opts = xofalg
        n = _didll.XOF_Bytes(buf, numbytes, bytes(msg), len(msg), opts)
        if (n < 0): raise Error(-n if n < 0 else n)
        return bytes(buf.raw)


class _NotUsed:
    """Dummy for parsing."""
    pass


# PROTOTYPES (derived from diCryptoSys.h)
# If wrong argument type is passed, these will raise an `ArgumentError` exception
#     ArgumentError: argument 1: <type 'exceptions.TypeError'>: wrong type
_didll.API_Version.argtypes = []
_didll.API_LicenceType.argtypes = [c_int]
_didll.API_ErrorCode.argtypes = []
_didll.API_ErrorLookup.argtypes = [c_char_p, c_int, c_int]
_didll.API_CompileTime.argtypes = [c_char_p, c_int]
_didll.API_ModuleName.argtypes = [c_char_p, c_int, c_int]
_didll.API_ModuleInfo.argtypes = [c_char_p, c_int, c_int]
_didll.API_Platform.argtypes = [c_char_p, c_int]
_didll.API_PowerUpTests.argtypes = [c_int]
_didll.AEAD_EncryptWithTag.argtypes = [c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_int]
_didll.AEAD_DecryptWithTag.argtypes = [c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_int]
_didll.CIPHER_EncryptBytes.argtypes = [c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int]
_didll.CIPHER_DecryptBytes.argtypes = [c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int]
_didll.CIPHER_EncryptHex.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
_didll.CIPHER_DecryptHex.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
_didll.CIPHER_FileEncrypt.argtypes = [c_char_p, c_char_p, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int]
_didll.CIPHER_FileDecrypt.argtypes = [c_char_p, c_char_p, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int]
_didll.CIPHER_KeyWrap.argtypes = [c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_int]
_didll.CIPHER_KeyUnwrap.argtypes = [c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_int]
_didll.PAD_BytesBlock.argtypes = [c_char_p, c_int, c_char_p, c_int, c_int, c_int]
_didll.PAD_HexBlock.argtypes = [c_char_p, c_int, c_char_p, c_int, c_int]
_didll.PAD_UnpadBytes.argtypes = [c_char_p, c_int, c_char_p, c_int, c_int, c_int]
_didll.PAD_UnpadHex.argtypes = [c_char_p, c_int, c_char_p, c_int, c_int]
_didll.CIPHER_StreamBytes.argtypes = [c_char_p, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_int, c_int]
_didll.CIPHER_StreamFile.argtypes = [c_char_p, c_char_p, c_char_p, c_int, c_char_p, c_int, c_int, c_int]
_didll.BLF_BytesMode.argtypes = [c_char_p, c_char_p, c_int, c_char_p, c_int, c_int, c_char_p, c_char_p]
_didll.BLF_BytesMode.argtypes = [c_char_p, c_char_p, c_int, c_char_p, c_int, c_int, c_char_p, c_char_p]
_didll.CNV_HexStrFromBytes.argtypes = [c_char_p, c_int, c_char_p, c_int]
_didll.CNV_BytesFromHexStr.argtypes = [c_char_p, c_int, c_char_p]
_didll.CNV_B64StrFromBytes.argtypes = [c_char_p, c_int, c_char_p, c_int]
_didll.CNV_BytesFromB64Str.argtypes = [c_char_p, c_int, c_char_p]
_didll.CNV_ShortPathName.argtypes = [c_char_p, c_int, c_wchar_p]
_didll.CRC_Bytes.argtypes = [c_char_p, c_int, c_int]
_didll.CRC_File.argtypes = [c_char_p, c_int]
_didll.HASH_Bytes.argtypes = [c_char_p, c_int, c_void_p, c_int, c_int]
_didll.HASH_File.argtypes = [c_char_p, c_int, c_char_p, c_int]
_didll.HASH_HexFromBytes.argtypes = [c_char_p, c_int, c_void_p, c_int, c_int]
_didll.HASH_HexFromFile.argtypes = [c_char_p, c_int, c_char_p, c_int]
_didll.HASH_HexFromHex.argtypes = [c_char_p, c_int, c_char_p, c_int]
_didll.HASH_HexFromBits.argtypes = [c_char_p, c_int, c_char_p, c_int, c_int]
_didll.MAC_Bytes.argtypes = [c_char_p, c_int, c_void_p, c_int, c_void_p, c_int, c_int]
_didll.MAC_HexFromBytes.argtypes = [c_char_p, c_int, c_void_p, c_int, c_void_p, c_int, c_int]
_didll.MAC_HexFromHex.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_int]
_didll.RNG_KeyBytes.argtypes = [c_char_p, c_int, c_char_p, c_int]
_didll.RNG_Number.argtypes = [c_int, c_int]
_didll.RNG_Initialize.argtypes = [c_char_p, c_int]
_didll.RNG_UpdateSeedFile.argtypes = [c_char_p, c_int]
_didll.COMPR_Compress.argtypes = [c_char_p, c_int, c_char_p, c_int, c_int]
_didll.COMPR_Uncompress.argtypes = [c_char_p, c_int, c_char_p, c_int, c_int]
_didll.PBE_Kdf2.argtypes = [c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_int, c_int]
_didll.PBE_Scrypt.argtypes = [c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_int, c_int, c_int]
_didll.PRF_Bytes.argtypes = [c_char_p, c_int, c_char_p, c_int, c_char_p, c_int, c_char_p, c_int]
_didll.WIPE_File.argtypes = [c_char_p, c_int]
_didll.WIPE_Data.argtypes = [c_char_p, c_int]
_didll.XOF_Bytes.argtypes = [c_char_p, c_int, c_char_p, c_int, c_int]
