from __future__ import print_function

import sys
import os.path
import argparse

db_shell_path = __file__
new_path = [ os.path.join( os.path.dirname( db_shell_path ), os.path.pardir,  "lib" ) ]
new_path.extend( sys.path[1:] )  # remove scripts/ from the path
sys.path = new_path

from galaxy.model.orm.scripts import get_config
db_url = get_config( sys.argv )['db_url']

from galaxy.model.tool_shed_install.mapping import init
sa_session = init( db_url ).context
from galaxy.model.tool_shed_install import *


def get_tool(names):
    query = sa_session.query(ToolShedRepository).filter(
        ToolShedRepository.name.in_(names),
        ToolShedRepository.deleted==True,
        ToolShedRepository.uninstalled==True,
    ).order_by(
        ToolShedRepository.tool_shed,
        ToolShedRepository.name,
        ToolShedRepository.owner,
        ToolShedRepository.changeset_revision,
    )

    return query


def get_uninstalled_tools():
    query = sa_session.query(ToolShedRepository).filter(
        ToolShedRepository.deleted==True,
        ToolShedRepository.uninstalled==True,
    ).order_by(
        ToolShedRepository.tool_shed,
        ToolShedRepository.name,
        ToolShedRepository.owner,
        ToolShedRepository.changeset_revision,
    )

    return query


def print_tool(tool):
    print(
        "\033[1mToolshed\033[0m", tool.tool_shed,
        " \033[1mName\033[0m", tool.name,
        " \033[1mOwner\033[0m", tool.owner,
        " \033[1mRevision\033[0m", tool.changeset_revision,
        " \033[1mLastChange\033[0m", tool.update_time,
    )

def prompt_removal(default_msg="Remove this tool? (y/N) "):
    YES = ("y", "Y", "yes", "Yes")
    NO = ("n", "N", "no", "No", "")

    while True:
        remove = raw_input(default_msg)
        if not (remove in YES or remove in NO):
            print("Invalid choice, enter Yes or No")
            continue
        else:
            remove = remove in YES
            break

    return remove


def purge_from_db(tool, args, counter):
    def do_action(model, *element):
        counter.action += 1


        if args.dryrun:
            if args.verbose:
                print("Would have purged", model, "with id:", *element)

            return False
        else:
            if args.verbose:
                print("Purging", model, "id:", *element)

            return True

    print_tool(tool)

    if args.prompt:
        if not prompt_removal():
            # Response was negative so not removing
            # Don't count the tool as purged either
            print("\033[1mNot removing.\033[0m")
            return

    # Relations between ToolShedRepository and other models
    #
    # ToolShedRepository.id:
    #   ToolDependency.tool_shed_repository_id
    #   RepositoryDependency.tool_shed_repository_id
    #   RepositoryRepositoryDependencyAssociation.tool_shed_repository_id
    #   ToolVersion.tool_shed_repository_id
    #
    # ToolVersion.id
    #   ToolVersionAssociation.tool_id
    #   ToolVersionAssociation.parent_id
    #
    # RepositoryDependency.id
    #   RepositoryRepositoryDependencyAssociation.repository_dependency_id

    tool_versions = (sa_session.query(ToolVersion)
                               .filter(ToolVersion.tool_shed_repository_id==ToolShedRepository.id)
                               .filter(ToolShedRepository.id==tool.id)
                     )

    previous_associations = set()

    for tool_version in tool_versions:
        # Deleting based on ToolVersionAssociation.parent_id and based on ToolVersionAssociation.tool_id
        associations = (sa_session.query(ToolVersionAssociation)
                                  .filter(
                                      (ToolVersionAssociation.parent_id==ToolVersion.id) |
                                      (ToolVersionAssociation.tool_id==ToolVersion.id)
                                  )
                                  .filter(ToolVersion.id==tool_version.id)
                        )
        
        for association in associations:
            if association not in previous_associations:
                # Keep track of deleted objects so we don't try to remove them multiple times
                previous_associations.add(association)

                if do_action("ToolVersionAssociation", association.id):
                    sa_session.delete(association)

        # Deleting based on ToolVersion.tool_shed_repository_id
        if do_action("ToolVersion", tool_version.id):
            sa_session.delete(tool_version)

    repository_deps = (sa_session.query(RepositoryDependency)
                                 .filter(RepositoryDependency.tool_shed_repository_id==ToolShedRepository.id)
                                 .filter(ToolShedRepository.id==tool.id)
                       )

    for repo_dep in repository_deps:
        repo_repo_dep_associations = (sa_session.query(RepositoryRepositoryDependencyAssociation)
                                                .filter(RepositoryRepositoryDependencyAssociation.repository_dependency_id==RepositoryDependency.id)
                                                .filter(RepositoryDependency.id==repo_dep.id)
                                      )

        # Deleting based on RepositoryRepositoryDependencyAssociation.repository_dependency_id
        for rrda in repo_repo_dep_associations:
            if do_action("RepositoryRepositoryDependencyAssociation", rrda.id):
                sa_session.delete(rrda)

        # Deleting based on RepositoryDependency.tool_shed_repository_id
        if do_action("RepositoryDependency", repo_dep.id):
            sa_session.delete(repo_dep)


    tool_deps = (sa_session.query(ToolDependency)
                           .filter(ToolDependency.tool_shed_repository_id==ToolShedRepository.id)
                           .filter(ToolShedRepository.id==tool.id)
                 )

    # Deleting based on ToolDependency.tool_shed_repository_id
    for tool_dep in tool_deps:
        if do_action("ToolDependency", tool_dep.id, tool_dep.name):
            sa_session.delete(tool_dep)

    # Deleting the ToolShedRepository itself
    if do_action("ToolShedRepository", tool.id, tool.name):
        sa_session.delete(tool)

    # Ensure changes are pushed to DB
    sa_session.flush()

    counter.tool += 1
    return


def parse_args():
    parser = argparse.ArgumentParser(description="This script can be used to remove/purge "
                                     "tools/dependencies from the DB that are in uninstalled state")
    parser.add_argument("tool_names", nargs="*",
                        help="Name of the tool(s) as shown in the admin interface")
    parser.add_argument("--dryrun", action="store_true",
                        help="Run without changing the database")
    parser.add_argument("--noprompt", dest="prompt", action="store_false",
                        help="Do not ask confirmation before deleting (know what you are doing!)")
    parser.add_argument("--verbose", action="store_true",
                        help="Print more information about what is being done")

    return parser.parse_args()


class Counter(object):
    def __init__(self):
        self.tool = 0
        self.action = 0


def main():
    args = parse_args()

    if not args.prompt:
        print("Running in no-prompt mode")

    if args.dryrun:
        print("Running in dry-run mode (and forcing no-prompt mode)")
        args.prompt = False

    if args.tool_names:
        tools = get_tool(args.tool_names)
    else:
        if args.prompt:
            if not prompt_removal("\033[1mWarning no tool specified, are you sure you want to purge all uninstalled tools?\033[0m (y/N) "):
                print("\033[1mNot removing anything.\033[0m")
                return

        tools = get_uninstalled_tools()

    counter = Counter()

    for tool in tools:
        purge_from_db(tool, args=args, counter=counter)

    if args.dryrun:
        print("\033[1mWould have purged", counter.tool, "tool(s) totalling",
              counter.action, "database deletion(s).\033[0m")
    else:
        print("\033[1mPurged", counter.tool, "tool(s) totalling",
              counter.action, "database deletion(s).\033[0m")


if __name__ == "__main__":
    main()