echo "Compiling theme..."
echo $(time source .venv/bin/activate)
echo $(time python main.py build)
echo $(time python main.py release)

echo "\n"

echo "Creating .vsix file..."
echo $(time bunx vsce package)
