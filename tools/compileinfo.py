from tools.structs import staticValues
from tools.encoding import securityEncoding
import crc8

class CompileDong():
    '''
    Method for compiling all dongle information into formats that we want
    so that we can write the whole thing to a file.
    '''
    def makeWhiteDong(pcbid:str):
        '''
        Function for generating a white eAmusement dongle.
        Doesn't need an mcode.

        Here's the white dongle structure:
        - type (1)
        - signing key
        - pcbid
        '''
        # Create an empty dongle
        whitedong = []

        # Append the type
        whitedong.append(staticValues.key_type_white)

        # Add the signing key
        whitedong.append(staticValues.security_key_white)

        # Add the PCBID
        whitedong.append(pcbid)

        # Send it back to who asked for it
        return whitedong

    def makeBlackDong(key:str, mcode:list, pcbid):
        '''
        Function for generating a black security dongle.

        Here's the proper data structure:
        - type (0)
        - signing key (game specific)
        - mcode (game specific)
        - pcbid
        '''
        # Values
        sign_key_temp = [0]*8
        pcbid_temp = [0]*8
        pcbid_reversed = []

        # Init sign_key_temp with the sign key so we can sign the mcode
        keyasbytes = key.encode('utf-8')
        for index, item in enumerate(sign_key_temp):
            sign_key_temp[index] = item ^ keyasbytes[index]

        # Convert the mcode into a string so we can sign it
        mcodestr = ""
        for code in mcode:
            mcodestr = mcodestr+code

        # Convert the mcode into a byte array
        mcodebit = mcodestr.encode('utf-8')

        # Sign the mcode
        for index, item in enumerate(sign_key_temp):
            sign_key_temp[index] = item ^ mcodebit[index]

        # Pack the sign key
        packedsignkey = securityEncoding.encode_8_to_6(sign_key_temp)

        # Encode the given PCBID into binary data
        pcbid_encode = bytes(pcbid, encoding=('utf-8'))

        # Reverse the PCBID
        for index, item in enumerate(pcbid_temp):
            pcbid_temp[index] = item ^ pcbid_encode[index]
        for i in reversed(pcbid_temp):
            pcbid_reversed.append(i)

        # Pack the mcode
        packed_payload = securityEncoding.encode_8_to_6(mcodebit)
        
        # Generate the signature
        signature = securityEncoding.create_signature(pcbid_reversed, packedsignkey)

        ## Now that we have compiled all of the data, we should go ahead and populate
        ## an array with it, and send it off.
        
        # Generate an array
        blackdong = []

        # Append the reversed PCBID
        for i in pcbid_reversed:
            blackdong.append(i)

        # Append the signature
        for i in signature:
            blackdong.append(i)

        # Append the payload
        for i in packed_payload:
            blackdong.append(i)

        # Lastly, we need the CRC of the data. We do this by 
        # converting to str, then using crc8. We will
        # append it AFTER the 19 blanks.
        datastring = ""
        for i in blackdong:
            datastring = datastring+(str(i))
        calccrc = crc8.crc8(datastring.encode('utf-8'))
        calccrc = calccrc.digest()

        # Append 19 empty spaces
        for i in range(19):
            blackdong.append(0x00)

        # Lastly, we need to append the CRC
        for byte in calccrc:
            blackdong.append(byte)

        # Send it back to who asked for it
        return blackdong
