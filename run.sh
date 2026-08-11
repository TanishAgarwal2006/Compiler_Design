# #!/bin/bash

# echo "========================================"
# echo "   Running Compiler Lexer Test Suite"
# echo "========================================"

# echo ""

# for file in test/*.c
# do
#     echo "----------------------------------------"
#     echo "Testing: $file"
#     echo "----------------------------------------"

#     python3 src/main.py "$file"

#     echo ""
# done


# echo "========================================"
# echo "   Test Suite Completed"
# echo "========================================"

# prints output to output.txt
#!/bin/bash

OUTPUT="output.txt"

echo "========================================" > $OUTPUT
echo "   Running Compiler Lexer Test Suite" >> $OUTPUT
echo "========================================" >> $OUTPUT
echo "" >> $OUTPUT


for file in test/*.c
do
    echo "----------------------------------------" >> $OUTPUT
    echo "Testing: $file" >> $OUTPUT
    echo "----------------------------------------" >> $OUTPUT

    ./venv/bin/python src/main.py "$file" >> $OUTPUT 2>&1

    echo "" >> $OUTPUT
done


echo "========================================" >> $OUTPUT
echo "   Test Suite Completed" >> $OUTPUT
echo "========================================" >> $OUTPUT


echo "All outputs stored in $OUTPUT"