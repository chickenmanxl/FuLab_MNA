import os

# Define the path to your site-packages directory
site_packages_dir = 'E:\\programs\\Fu_Lab\\vgrampy\\fuvenv\\Lib\\site-packages'

# List of packages from requirements.txt
required_packages = [
    'matplotlib', 'numpy', 'pandas', 'customtkinter', 'pyserial', 'time'
]

# Collect files from site-packages that match required packages
datas = []
for package in required_packages:
    package_path = os.path.join(site_packages_dir, package)
    if os.path.exists(package_path):
        if os.path.isdir(package_path):
            package_files = [(os.path.join(package_path, f), os.path.join(package, f)) for f in os.listdir(package_path)]
            datas.extend(package_files)
        else:
            datas.append((package_path, package))
print(datas)