"""Constants for the Beszel integration."""
from homeassistant.const import Platform

DOMAIN = "beszel"

CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

PLATFORMS = [Platform.SENSOR]

DEFAULT_UPDATE_INTERVAL_SECONDS = 60

# Attribute names from Beszel API (SystemInfo)
ATTR_HOSTNAME = "h"
ATTR_KERNEL_VERSION = "k"
ATTR_CPU_PERCENT_INFO = "cpu" # System-wide CPU from info, distinct from stats
ATTR_THREADS = "t"
ATTR_CORES = "c"
ATTR_CPU_MODEL = "m"
ATTR_UPTIME = "u"
ATTR_MEM_PERCENT_INFO = "mp" # System-wide Mem % from info
ATTR_DISK_PERCENT_INFO = "dp" # System-wide Disk % from info
ATTR_BANDWIDTH_MB = "b"
ATTR_AGENT_VERSION = "v"
ATTR_PODMAN = "p"
ATTR_GPU_PERCENT_INFO = "g" # System-wide GPU % from info
ATTR_DASHBOARD_TEMP = "dt"
ATTR_OS = "os"

# Attribute names from Beszel API (SystemStats)
ATTR_CPU_PERCENT = "cpu"
ATTR_CPU_MAX_PERCENT = "cpum"
ATTR_MEM_TOTAL_GB = "m"
ATTR_MEM_USED_GB = "mu"
ATTR_MEM_PERCENT = "mp"
ATTR_MEM_BUFF_CACHE_GB = "mb"
ATTR_MEM_ZFS_ARC_GB = "mz"
ATTR_SWAP_TOTAL_GB = "s"
ATTR_SWAP_USED_GB = "su"
ATTR_SWAP_PERCENT = "sp" # Placeholder, confirm actual API key if different
ATTR_DISK_TOTAL_GB = "d"
ATTR_DISK_USED_GB = "du"
ATTR_DISK_PERCENT = "dp"
ATTR_DISK_READ_PS_MB = "dr"
ATTR_DISK_WRITE_PS_MB = "dw"
ATTR_DISK_READ_MAX_PS_MB = "drm"
ATTR_DISK_WRITE_MAX_PS_MB = "dwm"
ATTR_NET_SENT_PS_MB = "ns"
ATTR_NET_RECV_PS_MB = "nr"
ATTR_NET_SENT_MAX_PS_MB = "nsm"
ATTR_NET_RECV_MAX_PS_MB = "nrm"
ATTR_TEMPERATURES = "t"
ATTR_EXTRA_FS = "efs"
ATTR_GPU_DATA = "g"

# For GPUData
ATTR_GPU_NAME = "n"
ATTR_GPU_MEM_USED_MB = "mu"
ATTR_GPU_MEM_TOTAL_MB = "mt"
ATTR_GPU_USAGE_PERCENT = "u"
ATTR_GPU_POWER_W = "p"

# For ExtraFsStats
ATTR_FS_DISK_TOTAL_GB = "d"
ATTR_FS_DISK_USED_GB = "du"
ATTR_FS_DISK_PERCENT = "dp" # Placeholder, confirm actual API key if different
ATTR_FS_DISK_READ_PS_MB = "r"
ATTR_FS_DISK_WRITE_PS_MB = "w"
ATTR_FS_MAX_DISK_READ_PS_MB = "rm"
ATTR_FS_MAX_DISK_WRITE_PS_MB = "wm"
