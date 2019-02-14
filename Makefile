VERSION=`git describe --tags --always --abbrev=10 --dirty`
LASTCOMMITDATE=`git log -1 --format=%cd`

.phony: bundle

version:
	echo "__version__ = '$(VERSION)'" > _version.py
	echo "__lastcommitdate__ = '$(LASTCOMMITDATE)'" >> _version.py

bundle-viewer: version
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

# Doesn't work
bundle-describer: version
	# pyinstaller \
	# --onefile \
	# --console \
	# --clean \
	# --name="dmikmcdescriber" \
	# describer.py

	pyinstaller --clean dmikmcdescriber.spec
