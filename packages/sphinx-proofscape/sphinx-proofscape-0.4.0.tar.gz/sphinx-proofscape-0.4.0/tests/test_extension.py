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
from collections import defaultdict

import pytest
from bs4 import BeautifulSoup


def get_widget_data_from_script_tag(soup):
    """
    If the HTML contains a <script> tag defining pfsc_widget_data, then parse
    the JSON and return the widget data itself.

    Otherwise return None.
    """
    intro = '\nconst pfsc_widget_data = '
    for s in soup.find_all('script'):
        if s.text.startswith(intro):
            rem = s.text[len(intro):]
            data = json.loads(rem)
            return data
    return None


def get_highlights(soup, language):
    """
    Grab all the highlight divs, for a given language.
    """
    return list(soup.find_all('div', class_=f'highlight-{language}'))


def sort_highlight_spans(hdiv):
    """
    Given a highlight div, return a dictionary mapping span classes to
    sets of strings being the inner text that occurs in spans of that class.
    """
    d = defaultdict(set)
    spans = hdiv.find_all('span')
    for span in spans:
        c = span.get('class')
        if not c or len(c) > 1:
            continue
        d[c[0]].add(span.text)
    return d


@pytest.mark.sphinx(buildername='html', freshenv=True)
def test_sphinx_build(app, status, warning):
    """
    Cf `test_spx_doc0()` in the `pise/server` project.
    That test now takes over testing on Pages A and C, while Page B is still
    tested here.
    """
    app.build()
    assert not status.read()
    assert not warning.read()

    # Page B
    # ======
    html = (app.outdir / 'pageB.html').read_text()
    soup = BeautifulSoup(html, 'html.parser')

    # Does not define pfsc_widget_data
    assert get_widget_data_from_script_tag(soup) is None

    # Get expected classes in syntax highlight modes
    hl = get_highlights(soup, 'proofscape')
    assert len(hl) == 1
    d = sort_highlight_spans(hl[0])
    #print(d)
    assert d == PAGE_B_PFSC_SYNTAX_CLASSES

    hl = get_highlights(soup, 'meson')
    assert len(hl) == 1
    d = sort_highlight_spans(hl[0])
    #print(d)
    assert d == PAGE_B_MESON_SYNTAX_CLASSES

    hl = get_highlights(soup, 'meson-grammar')
    assert len(hl) == 1
    d = sort_highlight_spans(hl[0])
    #print(d)
    assert d == PAGE_B_MESON_GRAMMAR_SYNTAX_CLASSES


PAGE_B_PFSC_SYNTAX_CLASSES = {
    'kn': {'from', 'import'},
    'n': {'spam', 'Thm', 'Pf', 'P', 'C', 'A', 'Thm.C', 'eggs', 'gh.foo.bar', 'B', 'Thm.P'},
    'k': {'get', 'From', 'deduc', 'of', 'Suppose', 'hence', 'Then', 'as'},
    'c1': {'# This is a comment.'},
    'p': {'{', '.', ',', '}'},
    'nb': {'meson', 'de', 'sy', 'asrt', 'fr', 'supp', 'en'},
    'o': {'='},
    's2': {'"""$A$"""', '"$P$"'},
    's1': {"'$C$'", "'''$B$'''"},
    's': {'"', "'"}
}


PAGE_B_MESON_SYNTAX_CLASSES = {
    'n': {'A', 'F', 'H', 'B', 'G', 'D.Y.Z', 'C.X', 'E'},
    'p': {',', '.'},
    'k': {'therefore', 'Hence', 'and', 'by', 'so', 'using'}
}


PAGE_B_MESON_GRAMMAR_SYNTAX_CLASSES = {
    'nb': {'MesonScript', 'method', 'supposition', 'nodes', 'sentence',
           'reason', 'conclusion', 'initialSentence', 'assertion'},
    'o': {')*', '*', '?', '|', ')?', '(', '::='},
    'k': {'sup', 'name', 'how', 'inf', 'modal', 'conj', 'roam', 'flow'}
}
