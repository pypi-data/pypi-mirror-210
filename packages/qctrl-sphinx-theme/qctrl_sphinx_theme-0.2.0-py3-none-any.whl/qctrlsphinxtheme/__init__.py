# Copyright 2023 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""Q-CTRL Sphinx Theme"""
from os import path

__version__ = "0.2.0"
__author__ = "Q-CTRL <support@q-ctrl.com>"

# See https://www.sphinx-doc.org/en/master/development/theming.html#distribute-your-theme-as-a-python-package
def setup(app):
    app.add_html_theme(
        "qctrl_sphinx_theme", path.abspath(path.dirname(__file__))
    )
