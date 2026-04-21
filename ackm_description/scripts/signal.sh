#!/bin/bash



WORLD="default"
POSE='position: {x: 0, y: -1.55, z: 1.2},
orientation: {x: 0, y: 0, z: 0.7071, w: 0.7071}'

STATE_FILE="/tmp/gz_panel_state"

if [ "$1" == "-clean" ]; then
    rm -f "$STATE_FILE"
    echo "STATE limpo"
    exit 0
fi

get_id_by_name() {
    local name="$1"

    gz topic -e -t /world/$WORLD/pose/info \
    | awk -v n="$name" '
        $0 ~ "name: \""n"\"" {found=1}
        found && $1=="id:" {
            if ($2 ~ /^[0-9]+$/) {
                print $2
                exit
            }
        }
    '
}

create_panel() {
    local name="$1"

    gz service -s /world/$WORLD/create \
    --reqtype gz.msgs.EntityFactory \
    --reptype gz.msgs.Boolean \
    --timeout 3000 \
    --req "sdf_filename: \"model://ackm_description/models/$name\",
           name: \"$name\",
           pose: {$POSE}"
}

remove_by_id() {
    local id="$1"

    gz service -s /world/$WORLD/remove \
    --reqtype gz.msgs.Entity \
    --reptype gz.msgs.Boolean \
    --timeout 3000 \
    --req "id: $id"
}

# -------- MAIN --------

NEW_PANEL="$1"

if [ -z "$NEW_PANEL" ]; then
    echo "uso: $0 videopanelX"
    exit 1
fi


if [ -f "$STATE_FILE" ]; then
    OLD_ID=$(cat "$STATE_FILE")
    echo "no ficheiro: $OLD_ID"
else
    # tenta obter id do painel inicial (videopanel3)
    for i in {1..10}; do
        OLD_ID=$(get_id_by_name "videopanel3")
        [[ "$OLD_ID" =~ ^[0-9]+$ ]] && break
        sleep 0.2
    done

    # guarda se encontrou
    if [[ "$OLD_ID" =~ ^[0-9]+$ ]]; then
        echo "$OLD_ID" > "$STATE_FILE"
    else
        echo "WARN: não consegui obter id inicial de videopanel3"
        OLD_ID=""
    fi
fi

# cria novo
create_panel "$NEW_PANEL"

# espera o ID aparecer
sleep 0.5
NEW_ID=$(get_id_by_name "$NEW_PANEL")

# remove antigo
if [ ! -z "$OLD_ID" ]; then
    remove_by_id "$OLD_ID"
fi

# guarda novo id
echo "$NEW_ID" > "$STATE_FILE"

echo "OK: $NEW_PANEL (id=$NEW_ID), removed old id=$OLD_ID"
