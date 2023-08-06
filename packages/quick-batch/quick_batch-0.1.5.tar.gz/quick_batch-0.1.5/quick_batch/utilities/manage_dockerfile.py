from dockerfile_parse import DockerfileParser


def check_requirements_copy_and_install(dockerfile_path):
    parser = DockerfileParser()
    parser.content = open(dockerfile_path, 'r').read()

    # Check if requirements.txt is being copied
    requirements_copied = False
    for instruction in parser.structure:
        if instruction['instruction'] == 'COPY' and \
         'requirements.txt' in instruction['value']:
            requirements_copied = True
            break

    # Check if requirements.txt is being pip installed
    requirements_installed = False
    for instruction in parser.structure:
        if instruction['instruction'] == 'RUN' and \
         'requirements.txt' in instruction['value']:
            requirements_installed = True
            break

    if not requirements_copied or not requirements_installed:
        print("INFO: Adding instructions to Dockerfile to copy and "
              "install requirements.txt")
        with open(dockerfile_path, 'a') as file:
            file.write("\nRUN mkdir /usr/src/app\n")
            file.write("COPY requirements.txt /usr/src/app\n")
            file.write("RUN pip install -r /usr/src/app/requirements.txt\n")
            file.write("RUN rm -r /usr/src/app\n")
