




def format_to_literals(raw_text, line_length=110):
    # Clean the backslashes and collapse whitespace
    cleaned = raw_text.replace("\\\n", "").replace("\\n", "").replace("\\", "").replace("\n", " ")
    words = cleaned.split()
    
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        # +1 accounts for the space between words
        if current_length + len(word) + 1 > line_length and current_line:
            lines.append(" ".join(current_line) + " ")
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word) + 1
            
    if current_line:
        lines.append(" ".join(current_line))
        
    # Output the Python adjacent literal block
    output = "text = (\n"
    for line in lines:
        output += f'    "{line}"\n'
    output += ")"
    return output
