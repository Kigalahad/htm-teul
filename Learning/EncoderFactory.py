#  !python2
#  -*- coding: utf-8 -*-
#  EncoderFactory.py
#  Autor: Larvasapiens <sebasnr95@gmail.com>
#  Fecha creación: 2015-11-22
#  Fecha última modificación: 2015-11-22
#  Versión: 1.0 [Stable]

from __future__ import print_function

import random
import numpy

from nupic.encoders.category import CategoryEncoder
from nupic.encoders.base import Encoder

""" A collection of encoders for use in different Learning Models """

def unifiedCategoryEnc(categories, w=11):
    """
    Goes through the training data, exctracts the categories and makes
    one Category Encoder for all of them.
    """
    categoryList = []
    for inputCats in categories:
        categoryList.extend(list(inputCats))
        
    return CategoryEncoder(
            w=w,
            categoryList=categoryList,
            forced=True
        )
        
def charToBinary(character, wordLen=8, bitSeparation=0):
    """ 
    Returns: a list of integers containing the binary representation of
    character.
    """
    
    charBits = bin(ord(character))[2:]
    
    if (wordLen < len(charBits)):
        raise ValueError("The wordLen is not big enough to store the binary "\
            "representation of the character '{0}': {1}".format(character, charBits))
    else:
        charBitsList = []
        
        for bit in charBits:
            charBitsList.extend([0] * bitSeparation)
            charBitsList.append(int(bit))
        # Add the missing zeros to complete the wordLen
        word = [0]*((wordLen * (bitSeparation + 1)) - len(charBitsList))
        word.extend(charBitsList)
        return word
        
class RandomizedLetterEncoder(Encoder):
    """
    Encoder for strings. It encodes each letter into binary and appends
    a random chain of bits at the end.
    """

    def __init__(self, width, nRandBits, bitSeparation=0):
        """
        @param width: The size of the encoded list of bits output.
        @param nRandBits: The number of random bits that the output
            will have after the binary representation of the
            string. 0 for a pure string to binary conversion.
        @param bitSeparation: The separation between bits when encoding
            the string. This won't affect the random bits.
        """
        
        if nRandBits > width:
            raise ValueError("nRandBits can't be greater than width.")
        if bitSeparation < 0:
            raise ValueError("bitSeparation must be >= 0")
        
        self.width = width
        self.nRandBits = nRandBits
        self.bitSeparation = bitSeparation
        self.alreadyEncoded = dict()

    def getWidth(self):
    
        return self.width
    
    def encode(self, inputData, verbose=0):
        """
        @param inputData
        @param verbose=0
        """
        
        bitsPerChar = 8
        strBinaryLen = len(inputData) * bitsPerChar * (self.bitSeparation + 1)
        
        if (strBinaryLen + self.nRandBits) > self.width:
            raise ValueError("The string is too long to be encoded with the"\
                "current parameters.")
        strBinary = []
        
        # Encode each char of the string 
        for letter in inputData:
            strBinary.extend(charToBinary(letter, bitsPerChar, self.bitSeparation))
        
        if inputData not in self.alreadyEncoded:
            self.alreadyEncoded[inputData] = [
                random.randrange(strBinaryLen, self.width) \
                    for _ in xrange(self.nRandBits)
            ]
        
        output = numpy.zeros((self.width,), dtype=numpy.uint8)
        output[:strBinaryLen] = strBinary
        output[self.alreadyEncoded[inputData]] = 1
        return output
        
    def getBucketIndices(self, inputData):
    
        encodedData = self.encode(inputData)
        return numpy.where(encodedData > 0)[0]
        
class TotallyRandomEncoder(Encoder):
    """
    Encoder for strings. It encodes each letter into binary and appends
    a random chain of bits at the end.
    """

    def __init__(self, width, nActiveBits):
        """
        @param width: The size of the encoded list of bits output.
        @param nActiveBits: The number of active bits. Their possition
            is generated randomly the first time and then retrieved.
        """
        
        if nActiveBits > width:
            raise ValueError("width must be greater than nActiveBits")
        self.width = width
        self.nActiveBits = nActiveBits
        self.alreadyEncoded = dict()

    def getWidth(self):
    
        return self.width
    
    def encode(self, inputData, verbose=0):
        """
        @param inputData
        @param verbose=0
        """
        
        if inputData not in self.alreadyEncoded:
            self.alreadyEncoded[inputData] = numpy.array(
                [random.randrange(self.width) for _ in xrange(self.nActiveBits)],
                dtype=numpy.uint8
            )
        
        output = numpy.zeros(self.width, dtype=numpy.uint8)
        output[self.alreadyEncoded[inputData]] = 1
            
        return output
        
    def getBucketIndices(self, inputData):
    
        encodedData = self.encode(inputData)
        return numpy.where(encodedData > 0)[0]