# check if run as root
if [ "$EUID" -ne 0 ]
    then >&2 echo "ERROR: Please run me as root"
    exit
fi

# Determine distribution
echo "Updating Turandot..."

. /opt/turandot/venv/bin/activate
pip3 install turandot[gtk]

echo "Done!"
