# list discovered distros (from data/quotes/*.json)
distro-says list

# show a specific distro
distro-says show ubuntu

# detect from /etc/os-release
distro-says show --auto

# random pick
distro-says random

# JSON output (for piping/scripting)
distro-says show ubuntu --json

# disable ASCII art
distro-says show ubuntu --no-ascii
