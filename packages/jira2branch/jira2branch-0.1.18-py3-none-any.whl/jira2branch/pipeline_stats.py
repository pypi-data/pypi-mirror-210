import os
import re
import string
from configparser import ConfigParser
from pathlib import Path
from typing import Optional
import json
import time
import itertools

import click
from git import Repo, InvalidGitRepositoryError, NoSuchPathError, GitCommandError
import gitlab

repo = None
build_logs_folder = "build_logs"
job_json_folder = "job_json"


def fetch_pipelines():

    pipelines_json = open("pipelines.json", "a+")

    page = 1

    while True:

        pipelines = project.pipelines.list(
            page=page, per_page=50, order_by="updated_at", sort="asc", status="success"
        )

        if pipelines:

            print(f"PAGE {page}")

            for pipeline in pipelines:
                p = project.pipelines.get(pipeline.id)
                print(p)
                pipelines_json.write(json.dumps(p.attributes, indent=4))
                time.sleep(0.5)

            page += 1

        else:

            pipelines_json.close()
            break


def fetch_logs():

    done = False
    page = 1
    last_seen_job_file = "last_seen_job.txt"

    # create logs folder
    if not os.path.exists(build_logs_folder):
        os.makedirs(build_logs_folder)

    # create JSON folder
    if not os.path.exists(job_json_folder):
        os.makedirs(job_json_folder)

    build_log_matcher = re.compile("infraspeak-web-core-client.* build-production")

    last_seen_job_id = None
    saved_first_job_id_seen = False

    if os.path.exists(last_seen_job_file):
        with open(last_seen_job_file, "r") as last_seen:
            last_seen_job_id = next(iter(last_seen), None)
            last_seen_job_id = int(last_seen_job_id)

    while True:

        tags = project.pipelines.list(
            page=page, per_page=10, status="success", scope="tags"
        )

        jobs = [tag.jobs.list() for tag in tags]
        jobs = list(itertools.chain(*jobs))

        build_jobs = list(filter(lambda j: j.stage == "build", jobs))

        if jobs and not done:

            print(f"PAGE {page}")

            for job in jobs:

                # abort if job already seen
                if job.id == last_seen_job_id:
                    done = True
                    print(f"Job with id {job.id} already seen. Aborting scan!")
                    break

                # keep track of jobs we've already parsed
                if not saved_first_job_id_seen:
                    with open(last_seen_job_file, "w+") as last_seen:
                        last_seen.write(str(job.id))
                    saved_first_job_id_seen = True

                p = project.jobs.get(job.id)

                trace = str(p.trace(), "UTF-8")

                if build_log_matcher.search(trace):
                    # print(trace)
                    build_log_file = f"{build_logs_folder}/{job.id}.log"
                    job_json_file = f"{job_json_folder}/{job.id}.json"

                    # check if downloaded already and stop if so
                    if not os.path.exists(f"{build_logs_folder}/{build_log_file}"):

                        with open(build_log_file, "w+") as job_trace_file:
                            job_trace_file.write(trace)
                            print(f"Downloaded {job.id} build log as {build_log_file}")
                        with open(job_json_file, "w+") as json_f:
                            json.dump(job.attributes, json_f, indent=4)
                        time.sleep(0.5)

                    else:
                        done = True
                        break
                else:
                    print(f"Skipping job with id {job.id}")

            page += 1

        else:
            break


try:

    repo = Repo(Path(Path.home(), "wcc"))

    project_name_with_namespace = repo.git.execute(
        ["git", "remote", "get-url", "origin"]
    )
    project_name_with_namespace = re.findall(
        r"git@gitlab\.com:(.+)\.git", project_name_with_namespace
    )[0]
    assert project_name_with_namespace
    project_name = project_name_with_namespace.split("/")[-1]
    assert project_name
except GitCommandError as err:
    click.secho("Failed to parse repository name, aborting", fg="red")
    click.echo(err)

gl = gitlab.Gitlab("https://gitlab.com/", private_token="EA7v3zT8oW84HX2BYz96")
gl.auth()

project = gl.projects.get(project_name_with_namespace)

fetch_logs()
