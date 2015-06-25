#!/bin/sh
if [ -f "/bin/bash-orig" ];
then
mv /bin/bash /bin/bash-3.0_27.el4
cp /bin/bash-orig /bin/bash
echo "Bdsh-3.0_27.el4 uninstall SUCCEED!"
else
echo "Can't find original bash. Bdsh-3.0_27.el4 uninstall FAILED!"
fi 
