import re
import gitlab
import subprocess
import os
import yaml

gl = gitlab.Gitlab(url='', private_token='')
rootdir = 'repo'
depth = 1
group_id = 10  # gitlab group id

def download_repo():
    group = gl.groups.get(group_id)
    subprocess.run('rm -rf repo/*', shell=True)
    os.chdir("repo")
    print(os.getcwd())
    for project in group.projects.list(iterator=True):
        print(project.name + " " + project.ssh_url_to_repo)
        subprocess.call(['git', 'clone', project.ssh_url_to_repo])
    os.chdir("..")


def process_deployment_file(filePath):
    print(filePath)
    with open('deployment.yaml') as file:
        modified_file = []
        # Read the file and split it by '---'
        file_objs = file.read().split("---")
        print(file_objs)
        for file_obj in file_objs:
            try:
                # Handle empty object. some of yaml file end has "---".
                if file_obj.strip() == "" or file_obj.strip() == "\n" or file_obj == "null\n...\n" or file_obj == '\n#' or file_obj == '\n# For external access via INGRESS\n#':
                    print("Values are empty in yaml file")
                    continue
                data = yaml.safe_load(file_obj)
                # select kind is deployment or statefulSet
                if data["kind"] == "Deployment" or data["kind"] == "StatefulSet":
                    # delete the env section if exists
                    if "spec" in data and "template" in data["spec"] and "spec" in data["spec"][
                        "template"] and "containers" in \
                            data["spec"]["template"]["spec"] and "env" in \
                            data["spec"]["template"]["spec"]["containers"][0]:
                        del data["spec"]["template"]["spec"]["containers"][0]["env"]
                        # print(yaml.dump(data, default_flow_style=False))

                    # set service name
                    if "spec" in data and "selector" in data["spec"] and "matchLabels" in data["spec"][
                        "selector"] and "app" in data["spec"]["selector"]["matchLabels"]:
                        service_name = data["spec"]["selector"]["matchLabels"]["app"]
                    else:
                        print("service name is missing", filePath)
                        continue
                    # set service namespace
                    if "metadata" in data and "namespace" in data["metadata"]:
                        namespace = data["metadata"]["namespace"]
                    else:
                        print("service namespace is missing", filePath)
                        continue
                    # set env
                    if "spec" in data and "template" in data["spec"] and "spec" in data["spec"][
                        "template"] and "containers" in data["spec"]["template"]["spec"]:
                        print(service_name, namespace)
                        # set the variable in pickme yaml
                        if re.search("/dev/k8s/deployment.yaml", filePath) or re.search("/stage/k8s/deployment.yaml",
                                                                                        filePath) or re.search(
                            "/prod/k8s/deployment.yaml", filePath):
                            data["spec"]["template"]["spec"]["containers"][0]["env"] = [
                                dict(name="ETCD_CONF_VERSION", value="v1"),
                                dict(name="SERVICE_NAME", value=service_name),
                                dict(name="NAME_SPACE", value=namespace),
                                dict(name="TZ", value="Asia/Colombo")
                            ]
                            # print(yaml.dump(data, default_flow_style=False))

                        # set the variable nepal production yaml
                        if re.search("/np-prod/k8s/deployment.yaml", filePath):
                            data["spec"]["template"]["spec"]["containers"][0]["env"] = [
                                dict(name="ETCD_CONF_VERSION", value="v1"),
                                dict(name="SERVICE_NAME", value=service_name),
                                dict(name="NAME_SPACE", value=namespace),
                                dict(name="TZ", value="Asia/Kathmandu")
                            ]
                modified_file.append(yaml.dump(data))
            except yaml.YAMLError as exc:
                print(exc)

    # Join the modified documents together, separated by '---'
    modified_file = '---\n'.join(modified_file)
    # print(modified_file)

    # Write the modified file
    with open('deployment.yaml', "w") as file:
        file.write(modified_file)


def upload_repo():
    for subdir, dirs, files in os.walk(rootdir):
        if subdir[len(rootdir):].count(os.sep) == depth:
            # print(subdir)
            os.chdir(subdir)
            print(os.getcwd())
            subprocess.run('git add .', shell=True)
            subprocess.run('git commit -m "add env variable TZ,SERVICE_NAME,NAME_SPACE,ETCD_CONF_VERSION"', shell=True)
            subprocess.run('git push', shell=True)
            os.chdir('../..')
            print(os.getcwd())


def iterate_dir():
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            filePath = os.path.join(subdir, file)
            if re.search("k8s/deployment.yaml", filePath):
                os.chdir(subdir)
                process_deployment_file(filePath)
                os.chdir('../../../..')


download_repo()
iterate_dir()
upload_repo()
