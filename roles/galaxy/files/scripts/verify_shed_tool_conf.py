#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Check shed_tool_conf.xml file for missing paths and incorrect
"installed_change_revision" attributes
'''
from __future__ import print_function
import argparse
import os
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("shed_tool_conf_file", default="shed_tool_conf.xml")
    args = parser.parse_args()

    tree = ET.parse(args.shed_tool_conf_file)
    root = tree.getroot()

    tool_path = root.get("tool_path")
    print(tool_path)
    tools = root.findall(".//tool")
    for tool in tools:
        # print tool.get("guid")
        filepath = os.path.join(tool_path, tool.get('file'))
        installed_changeset_revision = \
            tool.find("installed_changeset_revision").text
        if filepath.find(installed_changeset_revision) == -1:
            print("Installed changset revision: '%s' does not match filepath: "
                  "'%s'" % (installed_changeset_revision, filepath))
        if not os.path.exists(filepath):
            print("Filepath: '%s' does not exist!")

if __name__ == "__main__":
    main()
