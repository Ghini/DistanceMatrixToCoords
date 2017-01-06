#!/bin/bash
LRELEASE=$1
LOCALES=$2


for LOCALE in ${LOCALES}
do
    if [[ i18n/${LOCALE}.ts -nt i18n/latest_run ]]
    then
        echo "Processing: ${LOCALE}.ts"
        # Note we don't use pylupdate with qt .pro file approach as it is flakey
        # about what is made available.
        $LRELEASE i18n/${LOCALE}.ts
    fi
done
touch i18n/latest_run
