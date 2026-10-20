MODULE_TOPDIR = ../..

PGM = r.dtm.import.st

include $(MODULE_TOPDIR)/include/Make/Script.make
include $(MODULE_TOPDIR)/include/Make/Python.make

default: script $(PGM).md $(PGM).html

$(PGM).md: README.md
	$(INSTALL_DATA)  README.md $(PGM).md

$(PGM).html: $(PGM).md
	echo "Creating extensions html file..."
	pandoc -f markdown+hard_line_breaks-implicit_figures -t html $(PGM).md -o $(PGM).html
	sed -i -E 's#[[:space:]]*/>#>#g' $(PGM).html
	sed -i -E '/<col style="width: [0-9]+%">/d' $(PGM).html
	sed -i '/<colgroup>/d; /<\/colgroup>/d' $(PGM).html
	sed -i '/<hr>/d' $(PGM).html
