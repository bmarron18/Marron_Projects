#!/bin/bash
#===== QUICK START =============
# chmod +x to_literals.sh
# ./to_literals.sh your_prompt.txt


# Check if an input file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <input_file>"
    exit 1
fi

INPUT_FILE="$1"

# Process the text file and output adjacent string literal format
echo "text = ("
cat "$INPUT_FILE" |     tr -d '\\' |     tr '
' ' ' |     sed 's/  */ /g' |     awk '
    {
        line = ""
        for (i=1; i<=NF; i++) {
            if (length(line $i " ") > 100) {
                print "    "" line """
                line = $i " "
            } else {
                line = line $i " "
            }
        }
        if (length(line) > 0) {
            sub(/ $/, "", line)
            print "    "" line """
        }
    }'
echo ")"
