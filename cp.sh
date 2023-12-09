for dir in */; do
    if [ -d "$dir" ]; then
        # Save the current directory
        original_dir=$(pwd)

        # Change to the target directory
        cd "$dir"

        # Copy and run the script
        cp ../converter.py .
        python converter.py
        cp *.epub ../

        # Return to the original directory
        cd "$original_dir"
    fi
done
