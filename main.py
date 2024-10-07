import re
import json
import os 

ACTION = 'ACTION'
AMOUNT = 'AMOUNT'
SOURCE = 'SOURCE'
DESTINATION = 'DESTINATION'
NOTES = 'NOTES'

ACTIONS = ["masuk", "tambah", "keluar", "bayar"]

def lexer(text):
    text = text.lower()
    token_specification = [
        (ACTION, r'\b(?:masuk|tambah|keluar|bayar)\b'),  
        (AMOUNT, r'\b\d{1,3}(?:\.\d{3})*(?:rb)?\b'),             
        (SOURCE, r'(?<=dari\s)(?:(?!\s+ke\s+|\s+utk\s+|\s+untuk\s+).)*'),                   
        (DESTINATION, r'ke\s+([^u]+)'),                  
        (NOTES, r'(?:utk|untuk)\s+(.+)'),                
        ('SKIP', r'[ \t]+'),                             
    ]
    
    tokens = []
    for token_expr in token_specification:
        name, pattern = token_expr
        matches = re.findall(pattern, text)
        for match in matches:
            if name != 'SKIP':
                if isinstance(match, tuple):
                    match = match[0]
                tokens.append((name, match.strip()))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def parse_command(self):
        action = self.expect(ACTION)
        amount = self.expect(AMOUNT)
        
        source, destination = None, None
        
        token_type, _ = self.current_token()
        if token_type == SOURCE:
            source = self.expect(SOURCE)
            if self.current_token()[0] == DESTINATION:
                destination = self.expect(DESTINATION)
        elif token_type == DESTINATION:
            destination = self.expect(DESTINATION)
            if self.current_token()[0] == SOURCE:
                source = self.expect(SOURCE)
        notes = None
        if self.current_token()[0] == NOTES:
            notes = self.expect(NOTES)

        return {
            'action': action,
            'amount': amount,
            'source': source,
            'destination': destination,
            'notes': notes
        }

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def expect(self, expected_type):
        token_type, token_value = self.current_token()
        if token_type == expected_type:
            self.pos += 1
            return token_value
        else:
            if expected_type in [SOURCE, DESTINATION, NOTES]:
                return None  
            raise SyntaxError(f"Expected {expected_type}, got {token_type}")


def load_parsed_commands(filename='parsed_commands.json'):
   
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            try:
                return json.load(json_file)  
            except json.JSONDecodeError:
                return []  
    else:
        return []  

def save_parsed_commands(parsed_commands, filename='parsed_commands.json'):
    with open(filename, 'w') as json_file:
        json.dump(parsed_commands, json_file, indent=4)

def add_parsed_command(new_command, filename='parsed_commands.json'):
    parsed_commands = load_parsed_commands(filename)
    parsed_commands.append(new_command)
    save_parsed_commands(parsed_commands, filename)
    balance = calculate_balance(parsed_commands)
    print(f"Transaksi ditambahkan, saldo sekarang: Rp {balance:,}")

def parse_amount(amount_str):
    if '.' in amount_str:
        amount_str = amount_str.replace('.', '')
    if 'rb' in amount_str:
        return int(amount_str.replace('rb', '')) * 1000  
    return int(amount_str)  
    
def calculate_balance(parsed_commands):
    balance = 0
    for command in parsed_commands:
        amount = parse_amount(command['amount'])
        if command['action'] == 'masuk' or command['action'] == 'tambah':  
            balance += amount
        elif command['action'] == 'keluar' or command['action'] == 'bayar':  
            balance -= amount
    return balance
def _main_() : 
    command = input("Masukkan laporan keuangan : ")
    tokens = lexer(command)
    parser = Parser(tokens)
    pres = parser.parse_command()
    add_parsed_command(pres)
    print()
    print("Catatan Keuangan telah diperbaharui.")

_main_()