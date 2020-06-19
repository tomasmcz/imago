install: src/pcf.so

src/pcf.so: pcf.c
	gcc -Ofast -fPIC -shared -I/usr/include/python3.6m/ pcf.c -lpython3.6m -o src/pcf.so
clean:
	rm -f src/pcf.so src/*.pyc
