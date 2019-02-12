VERSION=`git describe --tags --always --abbrev=10 --dirty`
LASTCOMMITDATE=`git log -1 --format=%cd`

.phony: bundle

version:
	echo "__version__ = '$(VERSION)'" > _version.py
	echo "__lastcommitdate__ = '$(LASTCOMMITDATE)'" >> _version.py

bundle: version
	# conda activate for-bundle

	rm -rf dist
	rm -rf build

	# pyinstaller \
	# --onefile \
	# --noconsole \
	# --clean \
	# --name="dmikmcviewer" \
	# --add-data="dmi-kmc-viewer.css;." \
	# --add-data="misc.html;." \
	# --add-data="template.html;." \
	# gui.py

	pyinstaller --clean dmikmcviewer.spec

	# conda activate base
