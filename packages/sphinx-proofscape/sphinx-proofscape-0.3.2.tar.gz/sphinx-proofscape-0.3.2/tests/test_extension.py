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


def get_chart_widget_anchors(soup):
    """
    Get the list of any and all <a> tags having class `chartWidget`.
    """
    return list(soup.find_all('a', class_='chartWidget'))


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


@pytest.mark.sphinx(confoverrides={
    'pfsc_repopath': 'test.foo.doc2',
    'pfsc_import_repos.gh.foo.bar': '1.2.4',
    # 'pygments_style': 'github-dark',
}, freshenv=True)
def test_conf_overrides(app, status, warning):
    app.build()
    assert not status.read()
    assert not warning.read()

    # Page A
    # ======
    html = (app.outdir / 'pageA.html').read_text()
    soup = BeautifulSoup(html, 'html.parser')

    # The repopath was changed to test.foo.doc2:
    A = get_chart_widget_anchors(soup)
    assert 'test-foo-doc2-_sphinx-pageA-w0_WIP' in A[0].get('class')

    # The version of gh.foo.bar was changed to 1.2.4:
    wd = get_widget_data_from_script_tag(soup)
    # print('\n', json.dumps(wd[0], indent=4))
    assert wd[0]["versions"]["gh.foo.bar"] == "v1.2.4"


# Note: Using `freshenv` since we need to rebuild, expecting different output
# than we got when we tested overriding config vars above.
@pytest.mark.sphinx(buildername='html', freshenv=True)
def test_sphinx_build(app, status, warning):
    app.build()
    assert not status.read()
    assert not warning.read()

    # Page A
    # ======
    html = (app.outdir / 'pageA.html').read_text()
    soup = BeautifulSoup(html, 'html.parser')

    # Have exactly one chart widget anchor tag, and it has a class encoding its UID.
    A = get_chart_widget_anchors(soup)
    assert len(A) == 1
    assert 'test-foo-doc-_sphinx-pageA-w0_WIP' in A[0].get('class')

    # Defines the expected pfsc_widget_data
    wd = get_widget_data_from_script_tag(soup)
    assert len(wd) == 1
    #print('\n', json.dumps(wd[0], indent=4))
    assert wd[0] == {
        "view": [
            "gh.foo.bar.H.ilbert.ZB.Thm168.Pf"
        ],
        "versions": {
            "gh.foo.bar": "v1.2.3"
        },
        "pane_group": "test.foo.doc@WIP._sphinx.pageA:CHART:",
        "src_line": 10,
        "type": "CHART",
        "uid": "test-foo-doc-_sphinx-pageA-w0_WIP",
        "version": "WIP",
        "widget_libpath": "test.foo.doc._sphinx.pageA.w0"
    }

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


    # Page C
    # ======
    html = (app.outdir / 'foo/pageC.html').read_text()
    soup = BeautifulSoup(html, 'html.parser')

    # Get the expected anchor tags:
    A = get_chart_widget_anchors(soup)
    for i, (a, expected_label) in enumerate(zip(A, PAGE_C_WIDGETS_LABELS)):
        assert f'test-foo-doc-_sphinx-foo-pageC-w{i}_WIP' in a.get('class')
        assert a.text == expected_label

    # Get the expected pfsc_widget_data:
    wd = get_widget_data_from_script_tag(soup)
    #print('\n', json.dumps(wd, indent=4))
    assert wd == PAGE_C_WIDGET_DATA


PAGE_C_WIDGETS_LABELS = [
    'chart widget',
    'chart widgets',
    'substitutions',
    'one-line color definition',
    'color defn with repeated LHS, plus use of update',
]


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


PAGE_C_WIDGET_DATA = [
    {
        "view": [
            "gh.foo.bar.H.ilbert.ZB.Thm168.Pf"
        ],
        "versions": {
            "gh.foo.bar": "v1.2.3"
        },
        "pane_group": "test.foo.doc@WIP._sphinx.foo.pageC:CHART:",
        "src_line": 12,
        "type": "CHART",
        "uid": "test-foo-doc-_sphinx-foo-pageC-w0_WIP",
        "version": "WIP",
        "widget_libpath": "test.foo.doc._sphinx.foo.pageC.w0"
    },
    {
        "view": [
            "gh.foo.bar.H.ilbert.ZB.Thm168.Thm"
        ],
        "versions": {
            "gh.foo.bar": "v1.2.3"
        },
        "pane_group": "test.foo.doc@WIP._sphinx.foo.pageC:CHART:",
        "src_line": 14,
        "type": "CHART",
        "uid": "test-foo-doc-_sphinx-foo-pageC-w1_WIP",
        "version": "WIP",
        "widget_libpath": "test.foo.doc._sphinx.foo.pageC.w1"
    },
    {
        "on_board": [
            "gh.foo.spam.H.ilbert.ZB.Thm168.X1"
        ],
        "off_board": [
            "gh.foo.spam.H.ilbert.ZB.Thm168.X2"
        ],
        "view": [
            "gh.foo.bar.H.ilbert.ZB.Thm168.Thm.A10",
            "gh.foo.bar.H.ilbert.ZB.Thm168.Pf.A10",
            "gh.foo.bar.H.ilbert.ZB.Thm168.Pf.A20"
        ],
        "color": {
            ":olB": [
                "gh.foo.bar.H.ilbert.ZB.Thm168.Pf.A10",
                "gh.foo.bar.H.ilbert.ZB.Thm168.Pf.A20"
            ],
            ":bgG": [
                "gh.foo.bar.H.ilbert.ZB.Thm168.Thm.A10"
            ]
        },
        "versions": {
            "gh.foo.spam": "WIP",
            "gh.foo.bar": "v1.2.3"
        },
        "pane_group": "test.foo.doc@WIP._sphinx.foo.pageC:CHART:",
        "src_line": 28,
        "type": "CHART",
        "uid": "test-foo-doc-_sphinx-foo-pageC-w2_WIP",
        "version": "WIP",
        "widget_libpath": "test.foo.doc._sphinx.foo.pageC.w2"
    },
    {
        "view": [
            "gh.foo.bar.H.ilbert.ZB.Thm168.Pf"
        ],
        "color": {
            ":olB": [
                "gh.foo.bar.H.ilbert.ZB.Thm168.Pf.A10",
                "gh.foo.bar.H.ilbert.ZB.Thm168.Pf.A20"
            ]
        },
        "versions": {
            "gh.foo.bar": "v1.2.3"
        },
        "pane_group": "test.foo.doc@WIP._sphinx.foo.pageC:CHART:",
        "src_line": 36,
        "type": "CHART",
        "uid": "test-foo-doc-_sphinx-foo-pageC-w3_WIP",
        "version": "WIP",
        "widget_libpath": "test.foo.doc._sphinx.foo.pageC.w3"
    },
    {
        "color": {
            ":bgG": [
                "gh.foo.bar.H.ilbert.ZB.Thm168.Pf.A10",
                "gh.foo.bar.H.ilbert.ZB.Thm168.Pf.A20",
                "gh.foo.bar.H.ilbert.ZB.Thm168.Thm.A10"
            ],
            ":update": True
        },
        "versions": {
            "gh.foo.bar": "v1.2.3"
        },
        "pane_group": "test.foo.doc@WIP._sphinx.foo.pageC:CHART:",
        "src_line": 40,
        "type": "CHART",
        "uid": "test-foo-doc-_sphinx-foo-pageC-w4_WIP",
        "version": "WIP",
        "widget_libpath": "test.foo.doc._sphinx.foo.pageC.w4"
    }
]
