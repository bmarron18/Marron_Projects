#!/bin/bash
#===== QUICK START =============
# chmod +x AdjacentStringLiterals_Prompts.sh
# ./AdjacentStringLiterals_Prompts.sh INPUT_user_prompt-backslash.txt

# Check if an input file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <input_file>"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="OUTPUT_user_prompt-literals.txt"

# Process the text file and output adjacent string literal format to the new file
{
    echo "user_prompt = ("
    cat "$INPUT_FILE" |         tr -d '\\' |         tr '\n' ' ' |         sed 's/  */ /g' |         awk '
        {
            line = ""
            for (i=1; i<=NF; i++) {
                if (length(line $i " ") > 100) {
                    print "    \"" line "\""
                    line = $i " "
                } else {
                    line = line $i " "
                }
            }
            if (length(line) > 0) {
                sub(/ $/, "", line)
                print "    \"" line "\""
            }
        }'
    echo ")"
} > "$OUTPUT_FILE"

echo "Formatting complete. Results written to: $OUTPUT_FILE"
