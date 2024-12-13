if not exist "build" mkdir build
python src/main.py code.bs build/out.bf
python src/bf.py build/out.bf 16 false