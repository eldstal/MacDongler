#!/bin/bash
#
# Auto-generate device definitions that only differ by vid and pid
# These devices are classified based on their names, so there are bound to be some incorrect ones.
# All that means is, you may end up pretending the vid/pid of a network device is a serial device. No big deal.

SUPPORT=$(dirname "${BASH_SOURCE}")
GEN="${SUPPORT}/device-gen/make-device-db"
DB=$(cd "${SUPPORT}/../devices" && pwd)


mkdir -p "${DB}/hid/keyboard"
"${GEN}" --usb-id-file /tmp/usb.ids --template "keyboard" --name-prefix "kbd" --vendor-regex ".*" --product-regex "keyboard|keypad|numpad" > ${DB}/hid/keyboard/kbd-auto.json5

#mkdir -p "${DB}/hid/mouse"
#"${GEN}" --usb-id-file /tmp/usb.ids --template "mouse" --name-prefix "mouse" --vendor-regex ".*" --product-regex "mouse|trackpad|trackball|trackpoint|pointer|" > ${DB}/hid/mouse/mouse-auto.json5

#mkdir -p "${DB}/storage/msc"
#"${GEN}" --usb-id-file /tmp/usb.ids --template "msc-2.0" --name-prefix "msc" --vendor-regex ".*" --product-regex "flash|datatrave|cruzer|drive|fd device|[^t]card reader|securedigital|microsd|sd card" > ${DB}/storage/msc/msc-auto.json5

mkdir -p "${DB}/serial/acm"
"${GEN}" --usb-id-file /tmp/usb.ids --template "acm-2.0" --name-prefix "acm" --vendor-regex ".*" --product-regex "serial|(^acm)|( acm )|cdc acm|((rs|tia|eia)-?(232|422|423485))" > ${DB}/serial/acm/acm-auto.json5

mkdir -p "${DB}/serial/acm"
"${GEN}" --usb-id-file /tmp/usb.ids --template "acm-2.0" --name-prefix "acm" --vendor-regex ".*" --product-regex "modem" > ${DB}/serial/acm/modem-auto.json5

mkdir -p "${DB}/net/ecm"
"${GEN}" --usb-id-file /tmp/usb.ids --template "ecm-2.0" --name-prefix "ecm" --vendor-regex ".*" --product-regex "network|ethernet|lan|gigabit" > ${DB}/net/ecm/ecm-auto.json5

mkdir -p "${DB}/net/rndis"
"${GEN}" --usb-id-file /tmp/usb.ids --template "rndis-2.0" --name-prefix "rndis" --vendor-regex ".*" --product-regex "network|ethernet|lan|rndis|802\.11|wireless" > ${DB}/net/rndis/rndis-auto.json5
