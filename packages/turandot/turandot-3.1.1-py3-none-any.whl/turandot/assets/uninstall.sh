# check if run as root
if [ "$EUID" -ne 0 ]
    then >&2 echo "ERROR: Please run me as root"
    exit
fi

# Determine distribution
echo "Uninstalling Turandot..."

rm /usr/share/applications/turandot.desktop
rm -rf /opt/turandot

echo "Done!"
