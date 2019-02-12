VERSION=`git describe --tags --always --abbrev=10 --dirty`

.phony: bundle

version:
	echo "__version__ = '$(VERSION)'" > _version.py

bundle: version
	# conda activate for-bundle

	rm -rf dist
	rm -rf build

	pyinstaller \
	--onefile \
	--noconsole \
	--name="dmi-kmc Viewer" \
	--add-data="dmi-kmc-viewer.css;." \
	--add-data="misc.html;." \
	--add-data="template.html;." \
	gui.py

	# conda activate base
