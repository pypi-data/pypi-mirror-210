# --------------------------------------------------------------------------- #
#   Sphinx-Proofscape                                                         #
#                                                                             #
#   Copyright (c) 2022-2023 Proofscape contributors                           #
#                                                                             #
#   Licensed under the Apache License, Version 2.0 (the "License");           #
#   you may not use this file except in compliance with the License.          #
#   You may obtain a copy of the License at                                   #
#                                                                             #
#       http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                             #
#   Unless required by applicable law or agreed to in writing, software       #
#   distributed under the License is distributed on an "AS IS" BASIS,         #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#   See the License for the specific language governing permissions and       #
#   limitations under the License.                                            #
# --------------------------------------------------------------------------- #


import json

from sphinx_proofscape.lang_exts import (
    chartwidget, visit_chartwidget_html, depart_chartwidget_html,
    PfscChartRole,
    PfscChartDirective,
    PfscDefnsDirective,
)
from sphinx_proofscape.lexer import (
    MesonLexer, ProofscapeLexer, MesonBnfGrammarLexer,
)


__version__ = '0.4.0'


###############################################################################
# Standard purge & merge
# See e.g. https://www.sphinx-doc.org/en/master/development/tutorials/todo.html


def purge_chart_widgets(app, env, docname):
    if not hasattr(env, 'pfsc_all_chart_widgets'):
        return
    env.pfsc_all_chart_widgets = [w for w in env.pfsc_all_chart_widgets
                                  if w.docname != docname]


def merge_chart_widgets(app, env, docnames, other):
    if not hasattr(env, 'pfsc_all_chart_widgets'):
        env.pfsc_all_chart_widgets = []
    if hasattr(other, 'pfsc_all_chart_widgets'):
        env.pfsc_all_chart_widgets.extend(other.pfsc_all_chart_widgets)


###############################################################################


def write_widget_data(app, pagename, templatename, context, event_arg):
    """
    Inject the necessary <script> tag into a document, recording the data for
    any pfsc widgets defined on the page.
    """
    if app.builder.format != 'html':
        return
    env = app.builder.env
    if not hasattr(env, 'pfsc_all_chart_widgets'):
        env.pfsc_all_chart_widgets = []
    widget_descrips = []
    for w in env.pfsc_all_chart_widgets:
        if w.docname == pagename:
            widget_descrips.append(w.write_info_dict())
    if widget_descrips:
        body = f'\nconst pfsc_widget_data = {json.dumps(widget_descrips, indent=4)}\n'
        app.add_js_file(None, body=body)


###############################################################################


def setup(app):
    # In version 0.3.x, we defined more than just the lexers, including roles,
    # directives, etc.
    # In version 0.4.x, we define only the lexers, while everything else has
    # moved into `pise/server`.
    # In future versions, we may move everything back into this package, which
    # would then depend on a refactored `pfsc-core` package, yet to come.

    app.add_lexer('meson-grammar', MesonBnfGrammarLexer)
    app.add_lexer('meson', MesonLexer)
    app.add_lexer('proofscape', ProofscapeLexer)
    app.add_lexer('pfsc', ProofscapeLexer)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
