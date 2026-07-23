MODULE_TOPDIR = ../..

PGM = r.dtm.import.sh

include $(MODULE_TOPDIR)/include/Make/Script.make
include $(MODULE_TOPDIR)/include/Make/Python.make

default: script $(PGM).md $(PGM).html

$(PGM).md: README.md
	$(INSTALL_DATA)  README.md $(PGM).md

$(PGM).html: $(PGM).md
	echo "Creating extensions html file..."
	pandoc -f markdown+hard_line_breaks -t html $(PGM).md -o $(PGM).html
	sed -i 's+<br />+<br>+g' $(PGM).html
	sed -i 's+"image-alt" />+"image-alt">+g' $(PGM).html
