#!/bin/sh

# Copyright (C) Microsoft Corporation. All rights reserved.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

echo '<?xml version="1.0" encoding="UTF-8"?>'
echo '<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">'

for dir in 'xml/v1' 'ocs/v1'; do
	echo ''
	for f in `ls $dir`; do
		echo "  <edmx:Reference Uri=\"schemas/$dir/$f\">"
		for ns in `grep '<Schema' $dir/$f | grep -o 'Namespace=".*"'`; do
			echo "    <edmx:Include $ns/>"
		done
		echo '  </edmx:Reference>'
	done
done

echo ''
echo '  <edmx:DataServices>'
echo '    <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" Namespace="Service">'
echo '      <EntityContainer Name="Service" Extends="ServiceRoot.v1_0_0.ServiceContainer"/>'
echo '    </Schema>'
echo '  </edmx:DataServices>'

echo ''
echo '</edmx:Edmx>'