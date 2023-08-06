#!/bin/sh


# TODO: Add firefox support in prepare()

SCRIPT_PATH="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P)"
install="install"
build="build"
build_rippled_opt="false"
get_rippled_version_opt="false"
run_unittests_opt="false"
stop_network_opt="false"
start_network_opt="false"
validate_network_opt="false"
launch_explorer_opt="false"
install_mode="${build}"
rippled_repo="${HOME}/rippled"
LOG_BASE_DIR="${HOME}/logs"
LOG_DIR="${LOG_BASE_DIR}/logs_$(date +%Y%m%d_%H%M%S)"
SCRIPT_HELPER="${SCRIPT_PATH}/lib/setup_helper.sh"
WORK_DIR="/tmp/work_dir"
ALT_HOST_SCRIPT_DIR="/tmp/network_setup"
filtered_unittests_to_run=""

trap cleanup EXIT


usage() {
  echo ""
  echo "Usage: $0 [Optional parameters]"
  echo "  --installMode <${install}/${build}> (default: ${install_mode})"
  echo "  --buildRippled (Build rippled)"
  echo "  --rippledVersion (Get rippled version)"
  echo "  --runUnittests (Run rippled unittests)"
  echo "  --rippledRepo <Path to rippled repo (default: ${rippled_repo})>"
  echo "  --networkStart (Start local rippled network)>"
  echo "  --networkStop (Stop local rippled network)>"
  echo "  --networkStatus (Get local rippled network status)>"

  exit 1
}

cleanup() {
  /bin/rm -rf "${WORK_DIR}" "${ALT_HOST_SCRIPT_DIR}"
}

prepare_workspace() {
  if [ "${build_rippled_opt}" = "true" ]; then
    if [ ! -d "${rippled_repo}" ]; then
      echo "rippled repo '${rippled_repo}' not found. Check help"
      exit 1
    fi
    echo "Log directory: ${LOG_DIR}"
    mkdir -p "${LOG_DIR}" "${WORK_DIR}"
  fi

  rippled_db_dirs="$HOME/rippled_db/rippled_1 \
                  $HOME/rippled_db/rippled_2 \
                  $HOME/rippled_db/rippled_3 \
                  $HOME/rippled_db/rippled_4 \
                  $HOME/rippled_db/rippled_5"
  rippled_log_dirs="$HOME/rippled_log/rippled_1 \
                  $HOME/rippled_log/rippled_2 \
                  $HOME/rippled_log/rippled_3 \
                  $HOME/rippled_log/rippled_4 \
                  $HOME/rippled_log/rippled_5"
  for rippled_dir in ${rippled_db_dirs} ${rippled_log_dirs}; do
    /bin/rm -rf "${rippled_dir}"
    mkdir -p "${rippled_dir}"
    if [ ! -d "${rippled_dir}" ]; then
      parent_dir=$(dirname "${rippled_dir}")
      echo "Create '${parent_dir}' with write access"
      exit 1
    fi
  done

  host_script_dir="${SCRIPT_PATH}"
  is_script_in_home=$(echo "${PWD}" | grep "^${HOME}")
  if [ -z "${is_script_in_home}" ]; then
    /bin/cp -r "${host_script_dir}" "$(dirname "${ALT_HOST_SCRIPT_DIR}")"
    host_script_dir="${ALT_HOST_SCRIPT_DIR}"
  fi

  . "${SCRIPT_HELPER}"
}


if [ "$1" = "" ]; then
  usage
fi

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

  --buildRippled)
    build_rippled_opt="true"
    ;;

  --rippledVersion)
    get_rippled_version_opt="true"
    ;;

  --runUnittests)
    run_unittests_opt="true"
    next_param=$(echo "$2" | grep "^--")
    if [ -z "${next_param}" ]; then
      filtered_unittests_to_run="$2"
      shift
    fi
    ;;

  --networkStart)
    start_network_opt="true"
    validate_network_opt="true"
    launch_explorer_opt="true"
    ;;

  --networkStop)
    stop_network_opt="true"
    ;;

  --networkStatus)
    validate_network_opt="true"
    ;;

  --help | *)
    usage
    ;;
  esac
  shift
done

prepare_workspace
stop_network "${stop_network_opt}"
docker_build_rippled "${build_rippled_opt}" "${install_mode}" "${host_script_dir}"
docker_rippled_version "${get_rippled_version_opt}"
docker_run_unittests "${run_unittests_opt}" "${filtered_unittests_to_run}"
start_network "${start_network_opt}" "${host_script_dir}"
validate_network "${validate_network_opt}"
launch_explorer "${launch_explorer_opt}"
