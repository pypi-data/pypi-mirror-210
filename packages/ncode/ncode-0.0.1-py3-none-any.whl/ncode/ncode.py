class Nomancode:
    def __init__(self, code_list):
        self.code_list = code_list

    def encoder(self, text):
        alphabet = {
            'A': '01', 'B': '02', 'C': '03', 'D': '04', 'E': '05',
            'F': '06', 'G': '07', 'H': '08', 'I': '09', 'J': '10',
            'K': '11', 'L': '12', 'M': '13', 'N': '14', 'O': '15',
            'P': '16', 'Q': '17', 'R': '18', 'S': '19', 'T': '20',
            'U': '21', 'V': '22', 'W': '23', 'X': '24', 'Y': '25',
            'Z': '26', ' ': '27'
        }

        encoded_list = []
        for char in text:
            encoded_list.append(alphabet[char])

        return encoded_list

    def decoder(self):
        alphabet = {
            '01': 'A', '02': 'B', '03': 'C', '04': 'D', '05': 'E',
            '06': 'F', '07': 'G', '08': 'H', '09': 'I', '10': 'J',
            '11': 'K', '12': 'L', '13': 'M', '14': 'N', '15': 'O',
            '16': 'P', '17': 'Q', '18': 'R', '19': 'S', '20': 'T',
            '21': 'U', '22': 'V', '23': 'W', '24': 'X', '25': 'Y',
            '26': 'Z', '27': ' '
        }

        decoded_str = ''
        for code in self.code_list:
            decoded_str += alphabet[code]

        return decoded_str
    
    def toList(codes):
        codes = codes.split(" ")

        return codes
    
    def toChar(codes):
        codes = " ".join(codes)

        return codes