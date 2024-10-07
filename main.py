import re
import json
import os 

# Token types
ACTION = 'ACTION'
AMOUNT = 'AMOUNT'
SOURCE = 'SOURCE'
DESTINATION = 'DESTINATION'
NOTES = 'NOTES'

# Grammar definitions
ACTIONS = ["masuk", "tambah", "keluar", "bayar"]
UTK_VARIANTS = ["utk", "untuk"]

# Lexer: Tokenize the input based on our grammar rules
def lexer(text):
    text = text.lower()
    token_specification = [
        (ACTION, r'\b(?:masuk|tambah|keluar|bayar)\b'),  # Actions
        (AMOUNT, r'\b\d{1,3}(?:\.\d{3})*(?:rb)?\b'),                # Amounts (e.g., 20rb, 20.000)
        # Use a capturing group for 'dari' and 'ke'
        (SOURCE, r'dari\s+([^k]+)'),                     # Capture after 'dari' up to 'ke'
        # (SOURCE, r'dari\s+^(?:(?!ke).)* |dari\s+^(?:(?!utk).)*|dari\s+^(?:(?!utk).)*  '), 
        (DESTINATION, r'ke\s+([^u]+)'),                  # Capture after 'ke' up to 'utk|untuk'
        (NOTES, r'(?:utk|untuk)\s+(.+)'),                # Capture everything after 'utk/untuk'
        ('SKIP', r'[ \t]+'),                             # Skip whitespace
    ]
    
    tokens = []
    for token_expr in token_specification:
        name, pattern = token_expr
        matches = re.findall(pattern, text)
        for match in matches:
            if name != 'SKIP':
                # Add tokens, ensuring we handle capturing groups
                if isinstance(match, tuple):
                    match = match[0]
                tokens.append((name, match.strip()))
    return tokens

# Parser: Recursive descent parsing
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def parse_command(self):
        # Action and amount are required
        action = self.expect(ACTION)
        amount = self.expect(AMOUNT)
        
        # Either SOURCE or DESTINATION is required
        source, destination = None, None
        
        # Peek at the next token to check if it's SOURCE or DESTINATION
        token_type, _ = self.current_token()
        if token_type == SOURCE:
            source = self.expect(SOURCE)
            # After source, check if destination exists (optional)
            if self.current_token()[0] == DESTINATION:
                destination = self.expect(DESTINATION)
        elif token_type == DESTINATION:
            destination = self.expect(DESTINATION)
            # After destination, check if source exists (optional)
            if self.current_token()[0] == SOURCE:
                source = self.expect(SOURCE)

        # Notes are optional
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
                return None  # Optional fields can return None
            raise SyntaxError(f"Expected {expected_type}, got {token_type}")



# Function to load existing parsed commands from the JSON file
def load_parsed_commands(filename='parsed_commands.json'):
    # Check if the file exists
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            try:
                return json.load(json_file)  # Load existing data
            except json.JSONDecodeError:
                return []  # If file is empty or corrupt, return empty list
    else:
        return []  # If the file doesn't exist, return empty list

# Function to save the updated parsed commands array to the JSON file
def save_parsed_commands(parsed_commands, filename='parsed_commands.json'):
    with open(filename, 'w') as json_file:
        json.dump(parsed_commands, json_file, indent=4)

# Function to add a new parsed command
def add_parsed_command(new_command, filename='parsed_commands.json'):
    # Load existing parsed commands
    parsed_commands = load_parsed_commands(filename)
    
    # Append the new command
    parsed_commands.append(new_command)
    
    # Save the updated list
    save_parsed_commands(parsed_commands, filename)
    
    # Calculate the balance after the transaction
    balance = calculate_balance(parsed_commands)
    
    # Show the balance
    print(f"Transaction added. Current Balance (Saldo): Rp {balance:,}")

def parse_amount(amount_str):
    if '.' in amount_str:
        amount_str = amount_str.replace('.', '')
    if 'rb' in amount_str:
        return int(amount_str.replace('rb', '')) * 1000  # Convert '60rb' to 60000
    return int(amount_str)  # In case there are non-'rb' formats
    
def calculate_balance(parsed_commands):
    balance = 0
    for command in parsed_commands:
        amount = parse_amount(command['amount'])
        if command['action'] == 'masuk' or command['action'] == 'tambah':  # 'masuk' means incoming transaction
            balance += amount
        elif command['action'] == 'keluar' or command['action'] == 'bayar':  # 'keluar' means outgoing transaction
            balance -= amount
    return balance
# Example command
commands = [
    "Bayar 20.000 dari gopay utk bayar utang ketoprak Yazid",   # All fields
    "Bayar 50.000 ke bri",                                     # Only action, amount, and destination
    "Tambah 100rb ke kas",                                   # Only action, amount, and source
    "Masuk 200rb dari ortu ke mandiri",                        # With both source and destination
    "Keluar 20.000",                                            # Error, neither source nor destination
    "Keluar 60rb dari bri teman utk beli gacoan"
]

# for command in commands:
#     try:
#         print(f"\nCommand: {command}")
#         # Tokenize the input
#         tokens = lexer(command)
#         print(f"Tokens: {tokens}")
        
#         # Parse the tokenized input
#         parser = Parser(tokens)
#         parsed_command = parser.parse_command()
#         print(f"Parsed Command: {parsed_command}")
#         # Convert the dictionary to a JSON string
#         json_data = json.dumps(parsed_command, indent=4)
#         with open('parsed_command.json', 'w') as json_file:
#             json_file.write(json_data)
#     except SyntaxError as e:
#         print(f"Syntax Error: {e}")
# Example of a new parsed command
new_command = {
    'action': 'keluar',
    'amount': '60rb',
    'source': 'bri',
    'destination': None,
    'notes': 'beli gacoan'
}
new_command2 = {
    'action': 'masuk',
    'amount': '120rb',
    'source': 'bri',
    'destination': None,
    'notes': 'transfer'
}

# Add the new parsed command to the JSON file
# add_parsed_command(new_command)
# add_parsed_command(new_command2)
command = input()
tokens = lexer(command)
parser = Parser(tokens)
pres = parser.parse_command()
add_parsed_command(pres)
print()
print("Parsed command added to the JSON file.")
