#!/usr/bin/env python
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.#
"""Intellij URL Provider."""

from __future__ import absolute_import

import urllib2
import xml.etree.cElementTree as ET

from autopkglib import Processor, ProcessorError

__all__ = ["IntellijURLProvider"]

intellij_version_url = "https://www.jetbrains.com/updates/updates.xml"


class IntellijURLProvider(Processor):
    """Provide URL for latest Intellij IDEA build."""

    description = "Provides URL and version for the latest release of Intellij."
    input_variables = {
        "base_url": {
            "required": False,
            "description": (
                "Default is https://www.jetbrains.com/updates/updates.xml"
            ),
        },
        "edition": {
            "required": False,
            "description": (
                'Either "C" for "Community" or "U" for "Ultimate" '
                'edition. Defaults to "C".'
            ),
        },
    }
    output_variables = {"url": {"description": "URL to the latest release of Intellij"}}

    __doc__ = description

    def get_intellij_version(self, intellij_version_url):
        """Retrieve version number from XML."""
        # Read XML
        try:
            req = urllib2.Request(intellij_version_url)
            f = urllib2.urlopen(req)
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (intellij_version_url, e))
        # Search for download link.
        root = ET.fromstring(html)
        # Use XPath to select the IntelliJ node; will always
        # select the first instance which *should* be the
        # latest version.
        latest_version = root.find(
            "./product[@name='IntelliJ IDEA']/"
            "channel[@name='IntelliJ IDEA RELEASE']//"
        )
        # Return version number
        return str(latest_version.attrib["version"])

    def main(self):
        """Main function."""
        # Determine values.
        version_url = self.env.get("version_url", intellij_version_url)
        version = self.get_intellij_version(version_url)
        download_url = "https://download.jetbrains.com/idea/ideaI%s-%s.dmg" % (
            self.env.get("edition", "C"),
            version,
        )

        self.env["url"] = download_url
        self.output("URL: %s" % self.env["url"])


if __name__ == "__main__":
    processor = IntellijURLProvider()
    processor.execute_shell()
