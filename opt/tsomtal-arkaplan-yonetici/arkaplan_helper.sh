#!/bin/bash
if [ "$(id -u)" -ne 0 ]; then
  exit 126 
fi
ACTION="$1"
FILE_URI="$2"
DCONF_DIR="/etc/dconf/db/local.d"
LOCKS_DIR="${DCONF_DIR}/locks"
PROFILE_FILE="/etc/dconf/profile/user"
mkdir -p "$LOCKS_DIR"
cat > "$PROFILE_FILE" << EOF
user-db:user
system-db:local
system-db:pardus
system-db:gdm
EOF
case "$ACTION" in
  lock)
    if [ -z "$FILE_URI" ]; then
      exit 1
    fi
    printf "[org/gnome/desktop/background]\npicture-uri='%s'\npicture-uri-dark='%s'\npicture-options='zoom'\n" "$FILE_URI" "$FILE_URI" > "${DCONF_DIR}/00-arkaplan-ayari"
    cat > "${LOCKS_DIR}/arkaplan-kilidi" << EOF
/org/gnome/desktop/background/picture-uri
/org/gnome/desktop/background/picture-uri-dark
/org/gnome/desktop/background/picture-options
EOF
    dconf update
    ;;
  unlock)
    rm -f "${DCONF_DIR}/00-arkaplan-ayari"
    rm -f "${LOCKS_DIR}/arkaplan-kilidi"
    dconf update
    ;;
  *)
    exit 2
    ;;
esac
exit 0
