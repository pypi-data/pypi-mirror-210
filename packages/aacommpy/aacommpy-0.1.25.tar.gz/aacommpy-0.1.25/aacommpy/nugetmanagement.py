import os
import shutil
import subprocess

def download_nuget(version: str = "", update: bool = False) -> None:
    nuget_path = os.path.join(os.path.dirname(__file__), 'aacommpyDownloader-main', 'nuget.exe')
    installed = False
    for dirname in os.listdir(os.path.dirname(nuget_path)):
        if dirname.startswith('Agito.AAComm.') and os.path.isdir(os.path.join(os.path.dirname(nuget_path), dirname)):
            installed = True
            old_version = dirname.split('.')[2:]
            old_version = '.'.join(old_version)
            break
    if update and installed:
        shutil.rmtree(os.path.join(os.path.dirname(nuget_path), f'Agito.AAComm.{old_version}'))
    nuget_cmd = [nuget_path, 'install', 'Agito.AAComm', '-OutputDirectory', os.path.join(os.path.dirname(nuget_path)), '-Source', 'https://api.nuget.org/v3/index.json']
    if version != "":
        nuget_cmd.extend(['-Version', version])
    subprocess.run(nuget_cmd, check=True)
    for dirname in os.listdir(os.path.dirname(nuget_path)):
        if dirname.startswith('Agito.AAComm.') and os.path.isdir(os.path.join(os.path.dirname(nuget_path), dirname)):
            new_version = dirname.split('.')[2:]
            new_version = '.'.join(new_version)
            source_dir = os.path.join(os.path.dirname(nuget_path), f'Agito.AAComm.{new_version}/build/AACommServer')
            dest_dir = os.path.dirname(__file__)
            shutil.copy2(os.path.join(source_dir, 'AACommServer.exe'), dest_dir)
            shutil.copy2(os.path.join(source_dir, 'AACommServerAPI.dll'), dest_dir)
            source_dir2 = os.path.join(os.path.dirname(nuget_path), f'Agito.AAComm.{new_version}/lib/net5.0')
            shutil.copy2(os.path.join(source_dir2, 'AAComm.dll'), dest_dir)
            break
    return None
def nuget_version() -> str:
    nuget_path = os.path.join(os.path.dirname(__file__), 'aacommpyDownloader-main', 'nuget.exe')
    installed = False
    latest_version = None
    for dirname in os.listdir(os.path.dirname(nuget_path)):
        if dirname.startswith('Agito.AAComm.') and os.path.isdir(os.path.join(os.path.dirname(nuget_path), dirname)):
            installed = True
            version = dirname.split('.')[2:]
            latest_version = '.'.join(version)
            print(f"The installed version of Agito.AAComm is {latest_version}.")
            break

    if not installed:
        raise RuntimeError('Agito.AAComm package is not installed.')
    
    return latest_version
def update_nuget() -> None:
    download_nuget(update=True)
    return None
def dotnetfw(version: str = "net40") -> None:
    latest_version = nuget_version()
    source_dir = os.path.join(os.path.dirname(__file__), 'aacommpyDownloader-main', f'Agito.AAComm.{latest_version}')
    dest_dir = os.path.dirname(__file__)    
    if version == "net5.0":
        source_dir = os.path.join(source_dir, 'lib', 'net5.0')
    elif version == "net40":
        source_dir = os.path.join(source_dir, 'lib', 'net40')
    elif version == "net46":
        source_dir = os.path.join(source_dir, 'lib', 'net46')
    elif version == "net48":
        source_dir = os.path.join(source_dir, 'lib', 'net48')
    elif version == "netcoreapp3.1":
        source_dir = os.path.join(source_dir, 'lib', 'netcoreapp3.1')
    else:
        raise ValueError("Invalid .NET framework version specified.")    
    dll_path = os.path.join(source_dir, 'AAComm.dll')
    if not os.path.isfile(dll_path):
        raise FileNotFoundError(f"Could not find AAComm.dll in {source_dir}.")
    shutil.copy2(dll_path, dest_dir)
    print(f"The current .NET framework target of AAComm is {version}")
    return None
def get_dotnet_versions():
    try:
        result = subprocess.run(['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP'], capture_output=True, text=True, check=True)
        output_lines = result.stdout.strip().split('\n')
        versions = []
        for line in output_lines:
            if '\\NDP\\v' in line:
                version = line.split('\\')[-1][1:]
                versions.append(version)
        return versions
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while retrieving .NET Framework versions: {e}")
        return []

def check_dotnet_versions():
    target_versions = ["4.0", "4.6", "4.8", "5.0"]
    dotnet_versions = get_dotnet_versions()
    matching_versions = [dotnetfw_from_dotnet_version(version) for version in target_versions if version in dotnet_versions]

    if not matching_versions:
        print("No proper .NET Framework versions found.")
        print("Please install one of the following .NET Framework versions:")
        for version in target_versions:
            print(version)
    else:
        print("Installed Dotnet framework versions which can be used with AAComm:")
        for version in matching_versions:
            print(version)

    return matching_versions

def dotnetfw_from_dotnet_version(dotnet_version):
    version_mapping = {
        "4.0": "net40",
        "4.6": "net46",
        "4.8": "net48",
        "5.0": "net5.0"
    }

    return version_mapping.get(dotnet_version)