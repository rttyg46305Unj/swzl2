USER_SITE=$(python3 -c "import site; print(site.getusersitepackages())")
echo "Installing/updating Swizzler..."
cp swzlr.py swzlr
chmod +x swzlr
sudo mkdir -p /usr/local/bin/ 
sudo mv swzlr /usr/local/bin/
echo "Installing/updating libswzl2..."
mkdir -p "$USER_SITE"
cp libswzl2.py "$USER_SITE/libswzl2.py"
echo "Installation process finished. Try running 'swzlr -h' to confirm it works."
