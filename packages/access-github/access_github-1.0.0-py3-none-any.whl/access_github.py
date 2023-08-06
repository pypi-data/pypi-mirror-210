#!/usr/bin/env python
# access_github.py
import argparse
import base64

import requests


def get_tree(token, url):
    repo_api_url = get_repo_api_url(url)
    headers = get_headers_with_authorization_and_version(token)
    response = requests.get(f"{repo_api_url}/branches/main", headers=headers)
    response_json = response.json()
    latest_commit_sha = response_json['commit']['sha']

    tree_url = f"{repo_api_url}/git/trees/{latest_commit_sha}?recursive=1"
    response = requests.get(tree_url, headers=headers)
    tree = response.json()
    return tree


def read_file(token, url, path):
    repo_api_url = get_repo_api_url(url)
    file_url = f"{repo_api_url}/contents/{path}"
    headers = get_headers_with_authorization(token)
    response = requests.get(file_url, headers=headers)
    content = response.json()
    return content


def update_file(token, name, email, url, path, content):
    repo_api_url = get_repo_api_url(url)
    file_url = f"{repo_api_url}/contents/{path}"
    headers = get_headers_with_authorization_and_version(token)
    response = requests.get(file_url, headers=headers)

    if response.status_code == 200:
        response = update_existing_file(file_url, content, email, headers, name, response)

    return response.json()


def create(token, name, email, url, path, content=None, is_folder=False):  # 添加 content 參數
    repo_api_url = get_repo_api_url(url)
    headers = get_headers_with_authorization_and_version(token)
    file_url = f"{repo_api_url}/contents/{path}"

    if content is None:  # 新增這個條件判斷
        content = ""

    create_data = get_create_data(name, email, content)  # 將 content 傳遞給 get_create_data 函數

    if is_folder:
        path += "/.gitkeep"

    response = requests.put(file_url, json=create_data, headers=headers)
    return response.json()


def delete(token, url, path, is_folder=False):
    repo_api_url = get_repo_api_url(url)
    headers = get_headers_with_authorization_and_version(token)

    if is_folder:
        return delete_folder(repo_api_url, headers, path)
    else:
        return delete_file(repo_api_url, headers, path)


def main():
    parser = get_arg_parser()
    args = parser.parse_args()

    operations = {
        "get_tree": get_tree,
        "read_file": read_file,
        "update_file": update_file,
        "create": create,
        "delete": delete,
        "create_or_update_github_action": create_or_update_github_action,
        "dispatch_github_action": dispatch_github_action,
    }

    operation = operations[args.operation]
    required_args = operation.__code__.co_varnames[:operation.__code__.co_argcount]

    operation_args = {k: v for k, v in vars(args).items() if k in required_args and v is not None}

    if args.operation == "create" and args.content:
        operation_args["content"] = args.content

    if args.operation == "get_tree":  # Add these lines
        operation_args["repo_api_url"] = get_repo_api_url(args.url)
        operation_args["headers"] = get_headers_with_authorization_and_version(args.token)

    result = operation(**operation_args)
    print(result)


def update_existing_file(file_url, content, email, headers, name, response):
    file_data = response.json()
    sha = file_data["sha"]
    update_data = get_update_data(name, email, content, sha)
    response = requests.put(file_url, json=update_data, headers=headers)
    return response


def get_repo_api_url(url):
    if url[-4:] == '.git':
        url = url[0:-4]
    return url.replace("https://github.com", "https://api.github.com/repos")


def get_headers_with_authorization(token):
    return {"Authorization": f"token {token}"}


def get_headers_with_authorization_and_version(token):
    headers = get_headers_with_authorization(token)
    headers.update({
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    return headers


def get_create_data(name, email, content):  # 添加 content 參數
    return get_commit_data("Create file or folder", name, email, content)  # 將 content 傳遞給 get_commit_data 函數


def get_commit_data(message, name, email, content):
    return {
        "message": message,
        "author": {"name": name, "email": email},
        "committer": {"name": name, "email": email},
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
    }


def get_update_data(name, email, content, sha):
    data = get_commit_data("Update file", name, email, content)
    data["sha"] = sha
    return data


def delete_folder(repo_api_url, headers, path):
    tree = get_tree(repo_api_url, headers)
    paths_to_delete = sorted((item["path"] for item in tree["tree"] if item["path"].startswith(path)),
                             key=lambda x: x.count('/'), reverse=True)

    for path_to_delete in paths_to_delete:
        delete_specific_file(repo_api_url, headers, path_to_delete)

    return {"status": "success", "message": f"Deleted folder {path}"}


def delete_file(repo_api_url, headers, path):
    delete_specific_file(repo_api_url, headers, path)
    return {"status": "success", "message": f"Deleted file {path}"}


def delete_specific_file(repo_api_url, headers, path_to_delete):
    file_url = f"{repo_api_url}/contents/{path_to_delete}"
    response = requests.get(file_url, headers=headers)
    file_data = response.json()
    sha = file_data["sha"] if isinstance(file_data, dict) else file_data[0]["sha"]
    delete_data = {"message": f"Delete {path_to_delete}", "sha": sha}
    requests.delete(file_url, json=delete_data, headers=headers)


def get_tree(repo_api_url, headers):
    tree_url = f"{repo_api_url}/git/trees/main?recursive=1"
    response = requests.get(tree_url, headers=headers)
    return response.json()


def create_or_update_github_action(token, url, path, content):
    existing_file = read_file(token, url, path)
    if 'message' in existing_file and existing_file['message'] == 'Not Found':
        create(token, 'GitHub Actions Bot', 'actions@github.com', url, path, content)
    else:
        return update_file(token, 'GitHub Actions Bot', 'actions@github.com', url, path, content)


def dispatch_github_action(token, url, workflow_yml_filename, event_type=None, client_payload=None):
    repo_api_url = get_repo_api_url(url)
    headers = get_headers_with_authorization_and_version(token)
    dispatch_url = f"{repo_api_url}/actions/workflows/{workflow_yml_filename}/dispatches"

    data = {
        'ref': 'main',
        'inputs': {}
    }

    if event_type:
        data['inputs']['event_type'] = event_type
    if client_payload:
        data['inputs']['client_payload'] = client_payload

    response = requests.post(dispatch_url, json=data, headers=headers)
    return response.text


def get_arg_parser():
    parser = argparse.ArgumentParser(description="Access GitHub")
    parser.add_argument("operation",
                        choices=["get_tree",
                                 "read_file",
                                 "update_file",
                                 "create",
                                 "delete",
                                 "create_or_update_github_action",
                                 "dispatch_github_action"])
    parser.add_argument("--token", type=str, required=True)
    parser.add_argument("--url", type=str, required=True)
    parser.add_argument("--path", type=str)
    parser.add_argument("--content", type=str)
    parser.add_argument("--is_folder", action="store_true")
    parser.add_argument("--name", type=str)
    parser.add_argument("--email", type=str)
    parser.add_argument("--workflow_yml_filename", type=str)
    parser.add_argument("--event_type", type=str)
    parser.add_argument("--client_payload", type=str)
    return parser


if __name__ == "__main__":
    main()
