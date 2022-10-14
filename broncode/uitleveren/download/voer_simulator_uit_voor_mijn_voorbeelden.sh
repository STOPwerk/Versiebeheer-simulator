#!/bin/bash

SCRIPT_PYTHON=python3
if ! [ -z "${STOP_PYTHON}" ]
then
	if ! command -v "${STOP_PYTHON}" &> /dev/null
	then
		echo "Kan '${STOP_PYTHON}' niet vinden!"
		SCRIPT_PYTHON=python3
	else
		SCRIPT_PYTHON="${STOP_PYTHON}"
	fi
fi

if ! command -v "$SCRIPT_PYTHON" &> /dev/null
then
	SCRIPT_PYTHON=python
	if ! command -v "$SCRIPT_PYTHON" &> /dev/null
	then
		echo "Kan python of python3 niet vinden!"
		echo "Zorg dat python of python3 in het PATH staat"
		echo "of zet het pad van python in de environment variabele STOP_PYTHON"
		exit
	fi
fi

"$SCRIPT_PYTHON" simulator/applicatie.py --meldingen logs --alle "mijn voorbeelden"
