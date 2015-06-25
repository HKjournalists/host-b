#!/bin/sh
if [ -f "/bin/bash-orig" ];
then
mv /bin/bash /bin/bash-6u3.el4
cp /bin/bash-orig /bin/bash
echo "Bdsh-6u3.el4 uninstall SUCCEED!"
else
echo "Can't find original bash. Bdsh-6u3.el4 uninstall FAILED!"
fi 
