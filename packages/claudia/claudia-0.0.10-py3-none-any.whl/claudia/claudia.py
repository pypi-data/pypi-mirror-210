import os
import subprocess

import click
import inquirer
from inquirer.themes import GreenPassion


class SingletonClass(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonClass, cls).__new__(cls)
        return cls.instance


singleton = SingletonClass()
singleton.PROJECT_ROOT_DIR = os.path.dirname(__file__)


def set_to_js_wd():
    os.chdir("{}/javascript/".format(singleton.PROJECT_ROOT_DIR))


def set_to_py_wd():
    os.chdir("{}/python/".format(singleton.PROJECT_ROOT_DIR))


def set_to_project_root_wd():
    os.chdir(singleton.PROJECT_ROOT_DIR)


def python(client_type, network, tag, feature):
    set_to_py_wd()
    try:
        set_python_launch_vars(network, client_type)
        load_feature_files()
        launch_behave(tag, feature)
        unload_feature_files()
    except Exception as e:
        set_to_project_root_wd()
        raise e


def javascript(network, tag, feature, invalidate_cache):
    set_to_js_wd()
    try:
        if invalidate_cache != 'false':
            invalidate_cache_and_rebuild()
        elif not os.path.isdir('./node_modules'):
            first_time_build()

        set_javascript_launch_vars(network)
        load_feature_files()
        launch_cucumber(tag, feature)
        unload_feature_files()
        set_to_project_root_wd()
    except Exception as e:
        set_to_project_root_wd()
        raise e


def compose_feature_helper_message():
    message = "Feature file to be used for the test run. Allowed values are "
    features = get_feature_file_names()
    for i in range(0, len(features)):
        message += "'{}', ".format(features[i])
    message += "and 'all' and is defaulted to 'payments'. \n\nMore information: https://behave.readthedocs.io/en/latest/tutorial.html?highlight=feature#feature-files."
    return message


def get_feature_file_names():
    set_to_project_root_wd()
    files = os.listdir('./features/')
    features = []
    for i in range(0, len(files)):
        features.append(files[i].replace(".feature", ""))

    return features


@click.group()
@click.version_option(message=('%(prog)s version %(version)s'))
def main():
    """Claudia says hi! Please choose a command to perform an action. A command can have multiple sub-commands and options. Use '--help' option for more information."""


@main.command()
def demo():
    """Launch claudia in demo mode"""
    try:
        clear_screen()
        launch_wizard()
    except Exception as e:
        pass


def launch_wizard():
    relaunch_wizard = True
    questions = [
        inquirer.List(
            "wizard",
            message="Welcome to Claudia Demo! Please use ↑ ↓ and ↵ keys to choose an option. Current Selection",
            # choices=[
            #     "List e2e features",
            #     "List system requirements (prerequisites)",
            #     "Build Rippled from local code",
            #     "Install Rippled",
            #     "Print already built/installed Rippled version",
            #     "Start local network",
            #     "Check local network status",
            #     "Stop local network",
            #     "Run e2e tests",
            #     "Run unit tests",
            #     "Exit"
            # ],
            choices=[
                "Build Rippled from local code",
                "Install Rippled",
                "Print already built/installed Rippled version",
                "Start local network",
                "Check local network status",
                "Stop local network",
                "Run e2e tests",
                "Run unit tests",
                "List e2e features",
                "List system requirements (prerequisites)",
                "Exit"
            ],
        ),
    ]

    selection_text = inquirer.prompt(questions)['wizard']

    if (selection_text == 'List e2e features'):
        print("\nIn order to '{}', run: 'claudia list e2e-features'".format(selection_text))
        if (get_confirmation("Are you sure you want to run this command?")):
            relaunch_wizard = False
            clear_screen()
            print("{}:\n".format(selection_text))
            launch_command_e2e_features()
    elif (selection_text == 'List system requirements (prerequisites)'):
        print("\nIn order to '{}', run: 'claudia list system-requirements'".format(selection_text))
        if (get_confirmation("Are you sure you want to run this command?")):
            relaunch_wizard = False
            clear_screen()
            print("{}:\n".format(selection_text))
            launch_command_system_requirements()
    elif (selection_text == 'Build Rippled from local code'):
        print("\nIn order to '{}', run: 'claudia rippled build --repo <absolute_path_to_local_repo>'".format(
            selection_text))
        if (get_confirmation("Are you sure you want to run this command?")):
            relaunch_wizard = False
            repo_path = get_valid_repo_path()
            if (repo_path == "" or repo_path.replace("'", "").replace('"', '').lower() == 'back'):
                relaunch_wizard = True
            else:
                clear_screen()
                print("{}:\n".format(selection_text))
                launch_command_build(repo_path)
    elif (selection_text == 'Install Rippled'):
        print("\nIn order to '{}', run: 'claudia rippled install'".format(selection_text))
        if (get_confirmation("Are you sure you want to run this command?")):
            relaunch_wizard = False
            clear_screen()
            print("{}:\n".format(selection_text))
            launch_command_rippled_install()
    elif (selection_text == 'Print already built/installed Rippled version'.format(selection_text)):
        print("\nIn order to '{}', run: 'claudia rippled version'".format(selection_text))
        if (get_confirmation("Are you sure you want to run this command?")):
            relaunch_wizard = False
            clear_screen()
            print("{}:\n".format(selection_text))
            launch_command_rippled_version()
    elif (selection_text == 'Start local network'):
        print("\nIn order to '{}', run: 'claudia network start --repo <absolute_path_to_local_repo>'".format(
            selection_text))
        if (get_confirmation("Are you sure you want to run this command?")):
            relaunch_wizard = False
            repo_path = get_valid_repo_path()
            if (repo_path == "" or repo_path.replace("'", "").replace('"', '').lower() == 'back'):
                relaunch_wizard = True
            else:
                clear_screen()
                print("{}:\n".format(selection_text))
                launch_command_network_start(repo_path)
    elif (selection_text == 'Check local network status'):
        print("\nIn order to '{}', run: 'claudia network status'".format(selection_text))
        if (get_confirmation("Are you sure you want to run this command?")):
            relaunch_wizard = False
            clear_screen()
            print("{}:\n".format(selection_text))
            launch_command_network_status()
    elif (selection_text == 'Stop local network'):
        print("\nIn order to '{}', run: 'claudia network stop'".format(selection_text))
        if (get_confirmation("Are you sure you want to run this command?")):
            relaunch_wizard = False
            clear_screen()
            print("{}:\n".format(selection_text))
            launch_command_network_stop()
    elif (selection_text == 'Run e2e tests'):
        print("\nIn order to '{}', run: 'claudia run e2etests'".format(selection_text))
        if (get_confirmation("Are you sure you want to run this command?")):
            relaunch_wizard = False
            clear_screen()
            print("{}:\n".format(selection_text))
            client_type = 'websocket'
            invalidate_cache = 'false'
            feature_files = get_feature_file_names()
            feature_files.append('all')
            lib = inquirer.prompt(
                [inquirer.List("confirmation", message="Please choose library type. Current Selection",
                               choices=["py", "js"], default="py")],
                theme=GreenPassion()
            )['confirmation']

            if (lib == 'py'):
                client_type = inquirer.prompt(
                    [inquirer.List("confirmation", message="Please choose client type. Current Selection",
                                   choices=["websocket", "jsonrpc"], default="websocket")],
                    theme=GreenPassion()
                )['confirmation']
            network = inquirer.prompt(
                [inquirer.List("confirmation", message="Please choose network type. Current Selection",
                               choices=["local", "devnet", "testnet"], default="local")],
                theme=GreenPassion()
            )['confirmation']

            tag = inquirer.prompt(
                [inquirer.List("confirmation", message="Please choose tag. Current Selection",
                               choices=['smoke', 'regression', 'time_intensive'], default="smoke")],
                theme=GreenPassion()
            )['confirmation']

            feature = inquirer.prompt(
                [inquirer.List("confirmation", message="Please choose network type. Current Selection",
                               choices=feature_files, default="payments")],
                theme=GreenPassion()
            )['confirmation']

            if (lib == 'js'):
                invalidate_cache = inquirer.prompt(
                    [inquirer.List("confirmation", message="Please choose if you would like to destroy cache, if any. Current Selection",
                                   choices=["false", "true"], default="false")],
                    theme=GreenPassion()
                )['confirmation']

            print("ready!")
            launch_command_run_e2e_tests(lib, client_type, network, tag, feature, invalidate_cache)
    elif (selection_text == 'Run unit tests'):
        print("\nIn order to '{}', run: 'claudia run unittests'".format(selection_text))
        if (get_confirmation("Are you sure you want to run this command?")):
            relaunch_wizard = False
            print("{}:\n".format(selection_text))
            testname = get_testname()
            if (testname.replace("'", "").replace('"', '').lower() == 'back'):
                relaunch_wizard = True
            else:
                launch_command_run_unit_tests(testname)
    elif (selection_text == 'Exit'):
        print("Thank you for using Claudia demo. Bye!")
        return

    if (relaunch_wizard):
        clear_screen()
        launch_wizard()
    else:
        if (get_confirmation("Would you like to continue with the demo?")):
            clear_screen()
            launch_wizard()
        else:
            print("Thank you for using Claudia demo. Bye!")


def get_valid_repo_path():
    input_path = [
        inquirer.Text('repo path',
                      message="Please enter the absolute path to the rippled repo. Type 'back' or simply press ↵ (return) key to skip and go back to main menu.")
    ]
    full_repo_path = inquirer.prompt(input_path)['repo path']
    if full_repo_path == "" or full_repo_path == "back":
        pass
    else:
        if not os.path.isabs(full_repo_path) or not os.path.exists(full_repo_path):
            print(
                "Rippled repository path '{}' is not correct. Please provide correct absolute path!".format(
                    full_repo_path))
            return get_valid_repo_path()

    return full_repo_path


def get_testname():
    testname = [
        inquirer.Text('testname',
                      message="Please enter name test name. Press ↵ (return) key to include run everything. Type 'back' to skip and go back to main menu.")
    ]
    return inquirer.prompt(testname)['testname']


def get_confirmation(confirmation_message):
    q = [inquirer.List("confirmation", message=confirmation_message, choices=["Yes", "No"], default="No")]
    answer = inquirer.prompt(q, theme=GreenPassion())['confirmation']
    if (answer == 'Yes'):
        return_value = True
    else:
        return_value = False
    return return_value


def clear_screen():
    if os.name == 'posix':
        os.system('clear')
    elif os.name == 'nt':
        os.system('cls')


@main.group()
def rippled():
    """Build or install rippled"""


@main.group()
def network():
    """Setup Rippled Network"""


@main.group()
@click.pass_context
def run(context):
    """Run XRPL automated tests"""


@main.group()
def list():
    """List supported options"""


@list.command()
def e2e_features():
    """List all supported features to be tested"""
    launch_command_e2e_features()


def launch_command_e2e_features():
    set_to_project_root_wd()
    features = os.listdir('./features/')
    message = "Following features were found:\n"
    for i in range(0, len(features)):
        message += "   - {}\n".format(features[i].replace(".feature", ""))
    click.echo(message)


@list.command()
def system_requirements():
    """List all system requirements before continuing further with claudia"""
    launch_command_system_requirements()


def launch_command_system_requirements():
    message = """
    1. Common requirements:
        - Python3
        - pip
        - docker
    2. Pull down a fresh copy of rippled code base from https://github.com/XRPLF/rippled
    3. Optional: Following depedencies are only required if you intend to run Javascript tests:
        - node
        - npm
    
        More detailed information can be found under the 'General prerequisite' section here: https://pypi.org/project/claudia
    """
    click.echo(message)


@rippled.command()
@click.option('--repo', required=True, help="The path to a local rippled repo")
def build(repo):
    """Build rippled from source"""
    if not os.path.isabs(repo) or not os.path.exists(repo):
        click.echo(
            " - ERROR: Rippled repository path '{}' is not correct. Please provide correct absolute path!".format(repo))
        return
    launch_command_build(repo)


def launch_command_build(repo):
    set_to_project_root_wd()
    command = "sh network_setup/setup.sh --buildRippled --rippledRepo {}".format(repo)
    subprocess.call(command, shell=True)


@rippled.command()
def version():
    """View rippled version info"""
    launch_command_rippled_version()


def launch_command_rippled_version():
    set_to_project_root_wd()
    command = "sh network_setup/setup.sh --rippledVersion"
    subprocess.call(command, shell=True)


@rippled.command()
def install():
    """Install rippled packages"""
    launch_command_rippled_install()


def launch_command_rippled_install():
    click.echo("Currently not supported")


@network.command()
@click.option('--repo', required=True,
              help="The path to a local rippled repo")
def start(repo):
    """Start a new rippled network"""
    if not os.path.isabs(repo) or not os.path.exists(repo):
        click.echo(
            " - ERROR: Rippled repository path '{}' is not correct. Please provide correct absolute path!".format(repo))
        return
    launch_command_network_start(repo)


def launch_command_network_start(repo):
    set_to_project_root_wd()
    command = "sh ./network_setup/setup.sh --networkStart  --rippledRepo {}".format(repo)
    subprocess.call(command, shell=True)


@network.command()
def stop():
    """Stop rippled network"""
    launch_command_network_stop()


def launch_command_network_stop():
    set_to_project_root_wd()
    command = "sh ./network_setup/setup.sh --networkStop"
    subprocess.call(command, shell=True)


@network.command()
def status():
    """rippled network status"""
    launch_command_network_status()


def launch_command_network_status():
    set_to_project_root_wd()
    command = "sh ./network_setup/setup.sh --networkStatus"
    subprocess.call(command, shell=True)


def print_explorer_message(network):
    url = ""
    if network == 'testnet':
        url = "https://testnet.xrpl.org"
    elif network == 'devnet':
        url = "https://devnet.xrpl.org"
    else:
        url = "https://custom.xrpl.org/localhost:6001"

    click.echo("INFO: Navigate to '{}' to view explorer.\n".format(url))


@run.command()
@click.pass_context
@click.option('--lib', default='py',
              help="The type of client library to be used for running the tests. Allowed values are 'py' and 'js' and is defaulted to 'py'.  \n\nMore information: https://xrpl.org/client-libraries.html#client-libraries")
@click.option('--client_type', default='websocket',
              help="The type of client to be used. This flag should only be used with 'py' library. Allowed values are 'websocket' and 'jsonrpc' and is defaulted to 'websocket'.  \n\nMore information: https://xrpl.org/get-started-using-http-websocket-apis.html#differences-between-json-rpc-and-websocket")
@click.option('--network', default='local',
              help="The type of network to be used. Allowed values are 'devnet', 'testnet', and 'local' and is defaulted to 'local'.  \n\nMore information: https://xrpl.org/get-started-using-http-websocket-apis.html#differences-between-json-rpc-and-websocket")
@click.option('--tag', default='smoke',
              help="Tag name of the all the tests to be included in the test run. Allowed values are 'smoke', 'regression' and 'time_intensive' and is defaulted to 'smoke'.  \n\nMore information: https://behave.readthedocs.io/en/latest/tag_expressions.html")
@click.option('--feature', default='payments',
              help=compose_feature_helper_message())
@click.option('--invalidate_cache', default='false',
              help="Forces ignoring cache, and reinstalling dependencies. This flag should only be used with 'js library. Allowed values are 'true' and 'false' and is defaulted to 'false'.")
def e2etests(context, lib, client_type, network, tag, feature, invalidate_cache):
    """Launch XRPL Automated tests using XRPL library client"""
    launch_command_run_e2e_tests(lib, client_type, network, tag, feature, invalidate_cache)


def launch_command_run_e2e_tests(lib, client_type, network, tag, feature, invalidate_cache):
    if (lib == 'py'):
        if (invalidate_cache != 'false'):
            raise Exception("--invalidate_cache flag is supported not with {} library client.".format(lib))
        print_explorer_message(network)
        python(client_type, network, tag, feature)
    elif (lib == 'js'):
        if (client_type != 'websocket'):
            raise Exception("Client Type {} is not supported with {} library client.".format(client_type, lib))
        print_explorer_message(network)
        javascript(network, tag, feature, invalidate_cache)
    else:
        raise Exception("Invalid library type: {}".format(lib))


@run.command()
@click.option('--testname', default='everything',
              help="The unit test which needs to be selected. If not provided, all tests are selected.")
def unittests(testname):
    """Launch Rippled Unit tests"""
    launch_command_run_unit_tests(testname)


def launch_command_run_unit_tests(testname):
    set_to_project_root_wd()
    if (testname == ''):
        command = "sh network_setup/setup.sh --runUnittests"
    else:
        command = "sh network_setup/setup.sh --runUnittests {}".format(testname)
    subprocess.call(command, shell=True)


# @run.command()
# @click.pass_context
# @click.argument("text")
# def customcommand(context, text):
#     """Run a debug command"""
#     click.echo("Running command: {}".format(text))
#     subprocess.call(text, shell=True)


def invalidate_cache_and_rebuild():
    click.echo("Invalidating cache...")
    os.popen('rm -rf ./node_modules')
    install_js_dependencies_if_needed()


def first_time_build():
    click.echo("Need to install missing dependencies. It is a one time action. Please wait...")
    install_js_dependencies_if_needed()


def set_python_launch_vars(network, client_type):
    if network == "local":
        if client_type == "websocket":
            connectionScheme = "ws"
            connectionURL = "127.0.0.1:6001"
            connectionType = "websocket"
        elif client_type == "jsonrpc":
            connectionScheme = "http"
            connectionURL = "127.0.0.1:5001"
            connectionType = "jsonrpc"
        else:
            raise Exception("{} is not a valid client_type".format(client_type))
    elif network == "devnet":
        if client_type == "websocket":
            connectionScheme = "wss"
            connectionURL = "s.devnet.rippletest.net:51233"
            connectionType = "websocket"
        elif client_type == "jsonrpc":
            connectionScheme = "https"
            connectionURL = "s.devnet.rippletest.net:51234"
            connectionType = "jsonrpc"
        else:
            raise Exception("{} is not a valid client_type".format(client_type))
    elif network == "testnet":
        if client_type == "websocket":
            connectionScheme = "wss"
            connectionURL = "s.altnet.rippletest.net:51233"
            connectionType = "websocket"
        elif client_type == "jsonrpc":
            connectionScheme = "https"
            connectionURL = "s.altnet.rippletest.net:51234"
            connectionType = "jsonrpc"
        else:
            raise Exception("{} is not a valid client_type".format(client_type))
    else:
        raise Exception("{} is not a valid network".format(network))

    os.environ['CONNECTION_SCHEME'] = connectionScheme
    os.environ['CONNECTION_URL'] = connectionURL
    os.environ['CONNECTION_TYPE'] = connectionType
    click.echo("Setting CONNECTION_SCHEME='{}', CONNECTION_URL='{}' and CONNECTION_TYPE='{}'".format(connectionScheme,
                                                                                                     connectionURL,
                                                                                                     connectionType))


def set_javascript_launch_vars(network):
    if network == "local":
        connectionScheme = "ws"
        connectionURL = "127.0.0.1:6001"
        connectionType = "websocket"
    elif network == "devnet":
        connectionScheme = "wss"
        connectionURL = "s.devnet.rippletest.net:51233"
        connectionType = "websocket"
    elif network == "testnet":
        connectionScheme = "wss"
        connectionURL = "s.altnet.rippletest.net:51233"
        connectionType = "websocket"
    else:
        raise Exception("{} is not a valid network".format(network))

    os.environ['CONNECTION_SCHEME'] = connectionScheme
    os.environ['CONNECTION_URL'] = connectionURL
    os.environ['CONNECTION_TYPE'] = connectionType
    click.echo("Setting CONNECTION_SCHEME='{}', CONNECTION_URL='{}' and CONNECTION_TYPE='{}'".format(connectionScheme,
                                                                                                     connectionURL,
                                                                                                     connectionType))


def load_feature_files():
    unload_feature_files()
    os.popen("cp -fr ../features/*.feature ./features")


def unload_feature_files():
    os.popen("rm -rf ./features/*.feature")


def launch_behave(tag, feature):
    if feature == "all":
        command = "behave --no-skipped --tags={}".format(tag)
    else:
        command = "behave --no-skipped --tags={} ./features/{}.feature".format(tag, feature)
    os.system(command)


def install_js_dependencies_if_needed():
    command = "sh ./runSetup"
    subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def launch_cucumber(tag, feature):
    if feature == "all":
        command = "npx cucumber-js --format @cucumber/pretty-formatter --tags @{}".format(tag)
    else:
        command = "npx cucumber-js --format @cucumber/pretty-formatter --tags @{} ./features/{}.feature".format(tag,
                                                                                                                feature)
    subprocess.call(command, shell=True)


if __name__ == '__main__':
    main(context, obj={})
