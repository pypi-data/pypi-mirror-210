#!/bin/sh

OS_NAME="$(uname -s)"
OS_ARCH="$(uname -p)"
PYTHON_VERSION=3.9
cmake_version=3.22.3
gcc_version=10
abi_version=11
cppstd=20

DOCKER_IMAGE="ubuntu:22.04"
RIPPLED_NODE_CONTAINER_NAME=rippled_node
RIPPLED_BUILD_CONTAINER_NAME=rippled_build
MAC_CHROME_BROWSER="/Applications/Google Chrome.app"
LINUX_CHROME_BROWSER="chrome"
EXPLORER_URL="https://custom.xrpl.org/localhost:6001"

BUILD_DIR_NAME="linux_build"
CONFIGS_DIR_NAME="configs"
CONTAINER_HOME="/root"
RIPPLED_BUILD_CONTAINER_SCRIPT_DIR="${CONTAINER_HOME}/network_setup"
RIPPLED_BUILD_CONTAINER_LOG_DIR="${CONTAINER_HOME}/logs"
RIPPLED_BUILD_CONTAINER_BUILD_SCRIPT="${RIPPLED_BUILD_CONTAINER_SCRIPT_DIR}/lib/build_rippled.sh"
RIPPLED_BUILD_CONTAINER_RIPPLED_HOME="${CONTAINER_HOME}/rippled"
RIPPLED_BUILD_CONTAINER_RIPPLED_EXEC="${RIPPLED_BUILD_CONTAINER_RIPPLED_HOME}/${BUILD_DIR_NAME}/rippled"
RIPPLED_NODE_DOCKER_FILE="${SCRIPT_PATH}"
NETWORK_VALIDATION_SCRIPT="${SCRIPT_PATH}/lib/validate_network.py"
DOCKER_NETWORK_CONFIG="${SCRIPT_PATH}/lib/rippled_network.yml"
rippled_build_path="${rippled_repo}/${BUILD_DIR_NAME}"
rippled_exec="${rippled_build_path}/rippled"
package_versions_log="${LOG_DIR}/package_versions.log"


exit_on_error() {
  exit_code=$1
  if [ "${exit_code}" -ne 0 ]; then
    echo "Exit code: $exit_code"
    exit "${exit_code}"
  fi
}

rippled_exec_not_found() {
  echo "rippled binary '${rippled_exec}' not found"
  echo " - Is rippled built successfully?"
  echo " - Is the path to rippled repo correct?"
  exit 1
}

is_rippled_built_successfully() {
  docker exec ${RIPPLED_BUILD_CONTAINER_NAME} "${RIPPLED_BUILD_CONTAINER_RIPPLED_EXEC}" --version > /dev/null 2>&1
  if [ "$?" -ne 0 ]; then
    echo "Error: 'rippled' not built successfully"
    exit 1
  fi
}

install_os_packages() {
  echo "- Install OS packages"
  time_now="$(date +%Y%m%d_%H%M%S)"
  log_file="${LOG_DIR}/${time_now}_prerequisite.log"

  apt -y update >>"${log_file}" 2>&1 && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata >>"${log_file}" 2>&1 && \
  apt -y install sysstat dnsutils net-tools vim apt-transport-https ca-certificates >>"${log_file}" 2>&1 && \
  apt -y install wget gnupg apt-utils docker docker-compose >>"${log_file}" 2>&1 && \
  apt -y install software-properties-common >>"${log_file}" 2>&1 && \
  add-apt-repository -y ppa:deadsnakes/ppa >>"${log_file}" 2>&1 && \
  apt update >>"${log_file}" 2>&1 && \
  apt -y install python${PYTHON_VERSION} python3-pip >>"${log_file}" 2>&1
  exit_on_error $?
  update-alternatives --install /usr/local/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 3 > /dev/null 2>&1
  exit_on_error $?

  python3 --version >> "${package_versions_log}" 2>&1
  exit_on_error $?
}

update_gcc() {
  echo "- Update gcc"
  time_now="$(date +%Y%m%d_%H%M%S)"
  log_file="${LOG_DIR}/${time_now}_gcc.log"

  apt-get -y update >> "${log_file}" 2>&1 && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata >>"${log_file}" 2>&1 && \
  apt-get -y dist-upgrade >> "${log_file}" 2>&1 && \
  apt-get -y install build-essential software-properties-common >> "${log_file}" 2>&1 && \
  add-apt-repository -y ppa:ubuntu-toolchain-r/test >> "${log_file}" 2>&1 && \
  apt-get -y update >> "${log_file}" 2>&1

  update-alternatives --force --remove-all gcc >> "${log_file}" 2>&1
  apt-get -o Dpkg::Options::="--force-confnew" -y install gcc-${gcc_version} g++-${gcc_version} >> "${log_file}" 2>&1 && \
  update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-${gcc_version} 60 --slave /usr/bin/g++ g++ /usr/bin/g++-${gcc_version} >> "${log_file}" 2>&1 && \
  update-alternatives --config gcc >> "${log_file}" 2>&1
  exit_on_error $?

  gcc --version >> "${package_versions_log}" 2>&1
  exit_on_error $?
}

install_cmake() {
  echo "- Install cmake"
  time_now="$(date +%Y%m%d_%H%M%S)"
  log_file="${LOG_DIR}/${time_now}_cmake_install.log"

  cmake_script="cmake-${cmake_version}-Linux-${OS_ARCH}.sh"
  wget -q -P "${WORK_DIR}" https://github.com/Kitware/CMake/releases/download/v"${cmake_version}"/"${cmake_script}"
  exit_on_error $?
  sh "${WORK_DIR}/${cmake_script}" --prefix=/usr/local --exclude-subdir >> "${log_file}" 2>&1

  cmake --version >> "${package_versions_log}" 2>&1
  exit_on_error $?
}

install_conan() {
  echo "- Install conan"
  time_now="$(date +%Y%m%d_%H%M%S)"
  log_file="${LOG_DIR}/${time_now}_conan_setup.log"

  pip install --upgrade 'conan<2' > "${log_file}" 2>&1
  conan profile new default --detect >> "${log_file}" 2>&1
  conan profile update settings.compiler.cppstd=${cppstd} default >> "${log_file}" 2>&1
  conan profile update settings.compiler.libcxx=libstdc++${abi_version} default >> "${log_file}" 2>&1
  conan profile show default >> "${package_versions_log}" 2>&1
  exit_on_error $?

  conan --version >> "${package_versions_log}" 2>&1
  exit_on_error $?
}

install_prerequisites() {
  install_os_packages
  update_gcc
  install_cmake
  install_conan
}

build_rippled() {
  install_mode="$1"
  rippled_repo="$2"
  echo "- Rippled ${install_mode}"
  time_now="$(date +%Y%m%d_%H%M%S)"
  log_file="${LOG_DIR}/${time_now}_rippled_install.log"

  CWD=$(pwd)
  cd "${rippled_repo}" || exit
  time_now="$(date +%Y%m%d_%H%M%S)"
  conan export external/snappy snappy/1.1.9@ > "${LOG_DIR}/${time_now}_snappy.log" 2>&1
  conan export external/soci soci/4.0.3@ > "${LOG_DIR}/${time_now}_soci.log" 2>&1
  exit_on_error $?

  rm -rf "${rippled_build_path}" ; mkdir -p "${rippled_build_path}" ; cd "${rippled_build_path}" || exit
  time_now="$(date +%Y%m%d_%H%M%S)"
  conan install .. --output-folder . --build missing --settings build_type=Release > "${LOG_DIR}/${time_now}_conan_install.log" 2>&1
  exit_on_error $?

  time_now="$(date +%Y%m%d_%H%M%S)"
  cmake -DCMAKE_TOOLCHAIN_FILE:FILEPATH=build/generators/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=Release .. > "${LOG_DIR}/${time_now}_cmake.log" 2>&1
  exit_on_error $?

  time_now="$(date +%Y%m%d_%H%M%S)"
  cmake --build . -- -j $(( $(nproc) / 2)) >> "${LOG_DIR}/${time_now}_cmake_build.log" 2>&1
  exit_on_error $?
  cd "${CWD}" || exit
}

docker_build_rippled() {
  build_rippled_opt="$1"
  install_mode="$2"
  host_script_dir="$3"
  if [ "${build_rippled_opt}" = "true" ]; then
    if [ ! -f "${rippled_repo}/src/ripple/protocol/Feature.h" ]; then
      echo "${rippled_repo} doesn't seem to be a valid rippled repository"
      exit 1
    fi

    echo "- Docker build rippled"
    if [ ! "$(docker ps -aq --filter name=${RIPPLED_BUILD_CONTAINER_NAME})" ]; then
      docker run \
        --name "${RIPPLED_BUILD_CONTAINER_NAME}" -i -d \
        -v "${rippled_repo}":"${RIPPLED_BUILD_CONTAINER_RIPPLED_HOME}" \
        -v "${host_script_dir}":"${RIPPLED_BUILD_CONTAINER_SCRIPT_DIR}" \
        -v "${LOG_BASE_DIR}":"${RIPPLED_BUILD_CONTAINER_LOG_DIR}" \
        "${DOCKER_IMAGE}" > /dev/null 2>&1
    elif [ "$(docker ps -aq --filter name=${RIPPLED_BUILD_CONTAINER_NAME} --filter status=exited)" ]; then
      docker start "${RIPPLED_BUILD_CONTAINER_NAME}"
    fi

    docker exec ${RIPPLED_BUILD_CONTAINER_NAME} \
      sh "${RIPPLED_BUILD_CONTAINER_BUILD_SCRIPT}" --installMode "${install_mode}" --logDir "${LOG_DIR}"

    exit_on_error $?
  fi
}

start_network() {
  start_network_opt="$1"
  host_script_dir="$2"
  if [ "${start_network_opt}" = "true" ]; then
    if [ -f "${rippled_exec}" ]; then
      echo "- Setup network"

      docker rm $(docker ps --filter name=${RIPPLED_NODE_CONTAINER_NAME} --filter status=exited -q) > /dev/null 2>&1
      docker build --quiet -t ${RIPPLED_NODE_CONTAINER_NAME} "${RIPPLED_NODE_DOCKER_FILE}" > /dev/null 2>&1

      export RIPPLED_BUILD_DIR="${rippled_build_path}"
      export RIPPLED_CONFIG_DIR="${host_script_dir}/${CONFIGS_DIR_NAME}"
      docker-compose -f "${DOCKER_NETWORK_CONFIG}" down > /dev/null 2>&1
      docker-compose -f "${DOCKER_NETWORK_CONFIG}" up -d > /dev/null 2>&1
    else
      rippled_exec_not_found
    fi
  fi
}

stop_network() {
  stop_network_opt="$1"
  if [ "${stop_network_opt}" = "true" ]; then
    echo "- Stop network"

    docker-compose -f "${DOCKER_NETWORK_CONFIG}" down > /dev/null 2>&1
    docker ps --filter name=${RIPPLED_NODE_CONTAINER_NAME}
  fi
}

validate_network() {
  validate_network_opt="$1"
  if [ "${validate_network_opt}" = "true" ]; then
    echo "- Validate network"
    python3 "${NETWORK_VALIDATION_SCRIPT}"
    exit_on_error $?
  fi
}

launch_explorer() {
  launch_explorer_opt="$1"
  if [ "${launch_explorer_opt}" = "true" ]; then
    if [ "${OS_NAME}" = "Linux" ]; then
      WEB_BROWSER="${LINUX_CHROME_BROWSER}"
    else
      WEB_BROWSER="${MAC_CHROME_BROWSER}"
    fi
    browser_name=$(echo "${WEB_BROWSER}" | awk '{ print $NF }')
    echo "- Launch Explorer (${browser_name}): ${EXPLORER_URL}"

    if [ -d "${WEB_BROWSER}" ] || [ -f "${WEB_BROWSER}" ]; then
      /usr/bin/open -a "${WEB_BROWSER}" "${EXPLORER_URL}"
      echo ""
    fi
  fi
}

docker_run_unittests() {
  run_unittests_opt="$1"
  filtered_unittests_to_run="$2"
  if [ "${run_unittests_opt}" = "true" ]; then
    echo "- Run unittests"

    if [ ! "$(docker ps -aq --filter name=${RIPPLED_BUILD_CONTAINER_NAME})" ]; then
      docker run \
        --name "${RIPPLED_BUILD_CONTAINER_NAME}" -i -d \
        -v "${rippled_repo}":"${RIPPLED_BUILD_CONTAINER_RIPPLED_HOME}" \
        -v "${host_script_dir}":"${RIPPLED_BUILD_CONTAINER_SCRIPT_DIR}" \
        -v "${LOG_BASE_DIR}":"${RIPPLED_BUILD_CONTAINER_LOG_DIR}" \
        "${DOCKER_IMAGE}" > /dev/null 2>&1
    elif [ "$(docker ps -aq --filter name=${RIPPLED_BUILD_CONTAINER_NAME} --filter status=exited)" ]; then
      docker start "${RIPPLED_BUILD_CONTAINER_NAME}"
    fi

    is_rippled_built_successfully
    docker exec ${RIPPLED_BUILD_CONTAINER_NAME} "${RIPPLED_BUILD_CONTAINER_RIPPLED_EXEC}" --unittest "${filtered_unittests_to_run}"
    exit_on_error $?
  fi
}

docker_rippled_version() {
  get_rippled_version_opt="$1"
  if [ "${get_rippled_version_opt}" = "true" ]; then
    is_rippled_built_successfully
    docker exec ${RIPPLED_BUILD_CONTAINER_NAME} "${RIPPLED_BUILD_CONTAINER_RIPPLED_EXEC}" --version
    exit_on_error $?
  fi
}
