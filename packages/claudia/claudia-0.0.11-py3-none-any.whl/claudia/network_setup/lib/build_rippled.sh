#!/bin/sh

SCRIPT_PATH="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P)"
OS_NAME="$(uname -s)"
install="install"
build="build"
install_mode="${build}"
rippled_repo="${HOME}/rippled"
LOG_BASE_DIR="${HOME}/logs"
LOG_DIR="${LOG_BASE_DIR}/logs_$(date +%Y%m%d_%H%M%S)"
WORK_DIR="/tmp/work_dir"
use_existing_log_dir="false"

trap cleanup EXIT


usage() {
  echo ""
  echo "Usage: $0 [Optional parameters]"
  echo "  --installMode <${install}, ${build}> (default: ${install_mode})"
  echo "  --localRippledRepo <path to rippled repo (default: ${rippled_repo})>"

  exit 1
}

cleanup() {
  if [ -d "${WORK_DIR}" ]; then
    /bin/rm -rf "${WORK_DIR}"
  fi
}

prepare_workspace() {
  if [ "$(id -u)" -ne "0" ] ; then
    echo "This script must be executed with root privileges"
    exit 1
  fi

  if [ "${OS_NAME}" != "Linux" ]; then
    echo "Unsupported distro!"
    exit 1
  fi

  if [ ! -d "${rippled_repo}" ]; then
    echo "rippled repo '${rippled_repo}' not found. Check help"
    exit 1
  fi

  mkdir -p "${WORK_DIR}"
  if [ "${use_existing_log_dir}" != "true" ]; then
    echo "Log directory: ${LOG_DIR}"
    mkdir -p "${LOG_DIR}"
  fi

  . "${SCRIPT_PATH}/setup_helper.sh"
}



while [ "$1" != "" ]; do
  case $1 in
  --rippledRepo)
    shift
    rippled_repo="${1:-$rippled_repo}"
    ;;

  --installMode)
    shift
    install_mode="${1:-$install_mode}"
    ;;

  --logDir)
    shift
    use_existing_log_dir="true"
    LOG_DIR="${LOG_BASE_DIR}/$(basename "$1")"
    ;;

  --help | *)
    usage
    ;;
  esac
  shift
done

prepare_workspace
install_prerequisites
build_rippled "${install_mode}" "${rippled_repo}"
