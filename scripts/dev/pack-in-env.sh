#!/bin/sh

# init virtualenv if required:
_venv=''

while [ "$1" != "" ]; do
	case "$1" in
		"--env" )
			_venv="$2"
			shift
			;;
		*)
			echo "Unknown parameter $1"
			exit 1
	esac

	shift
done

# apply args
if [ -z "$_venv" ]
then
	echo "Do not use virtualenv"
else

	if [ ! -d "build/env/${_venv}" ]; then
		echo "Create virtualenv: $_venv"
		virtualenv build/env/${_venv}
	fi

	echo "Enable virtualenv: $_venv"
	. build/env/${_venv}/bin/activate
fi

pip install --upgrade --force-reinstall PyInstaller

_packagefile="$(python setup.py --fullname).tar.gz"
_packageversion="$(python setup.py --version)"

echo '****************************************'
python -V
pip --version
echo "pyinstaller: `pyinstaller --version`"
echo "$PATH"
echo '****************************************'
echo "package: $_packagefile"
echo "version: $_packageversion"
echo '****************************************'

# ------------------------------------------------------------------------------
# install latest package
# ------------------------------------------------------------------------------
python setup.py sdist

# !!! patch APScheduler
_apschedulerpath=$(echo -e "import apscheduler\nprint(apscheduler.__file__)" | python)
cp $_apschedulerpath $_apschedulerpath.bak
echo "# These will be removed in APScheduler 4.0.
release = '3.3.1cf' # __import__('pkg_resources').get_distribution('APScheduler').version.split('-')[0]
version_info = '3.3.1cf' # tuple(int(x) if x.isdigit() else x for x in release.split('.'))
version = __version__ = '.'.join(str(x) for x in version_info[:3])
" > $_apschedulerpath

echo '****************************************'
echo 'apscheduler was patched'
echo $_apschedulerpath
echo '****************************************'

pip install dist/$_packagefile

# ------------------------------------------------------------------------------
# creating the bundle
# ------------------------------------------------------------------------------
pyinstaller -y --clean --log-level=INFO pyinstaller/recordingmonitor.spec

tar --directory=dist -czf dist/unav-recordingmonitor-bundle-${_packageversion}.tgz ./recordingmonitor

# ------------------------------------------------------------------------------
# cleanup
# ------------------------------------------------------------------------------
if [ ! -z "$_venv" ]
then
	echo "Disable virtualenv: $_venv"
	deactivate
fi
