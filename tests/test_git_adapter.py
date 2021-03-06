from nbdiff.adapter import git_adapter as g
from pretend import stub


def test_get_modified_notebooks_empty():
    g.subprocess = stub(check_output=lambda cmd: 'true\n'
                        if '--is-inside-work-tree' in cmd
                        else '')
    adapter = g.GitAdapter()
    result = adapter.get_modified_notebooks()
    assert result == []


def test_get_modified_notebooks_deleted():
    adapter = g.GitAdapter()

    def check_output_stub(cmd):
        if '--modified' in cmd:
            output = '''foo.ipynb
bar.ipynb
foo.txt
baz.ipynb
'''
            return output
        elif '--unmerged' in cmd:
            return ''.join([
                '100755\thash\t{i}\tfoo.ipynb\n'
                for i in [1, 2, 3]
            ])
        elif '--is-inside-work-tree' in cmd:
            return 'true\n'
        elif '--show-toplevel' in cmd:
            return '/home/user/Documents'

    def popen(*args, **kwargs):
        return stub(stdout=stub(read=lambda: ""))

    g.open = lambda fname: stub(read=lambda: "")
    g.subprocess = stub(
        check_output=check_output_stub,
        PIPE='foo',
        Popen=popen,
    )
    g.os.path.exists = lambda path: 'bar.ipynb' in path
    result = adapter.get_modified_notebooks()
    assert result[0][2] == 'bar.ipynb'
    assert len(result) == 1


def test_get_modified_notebooks():
    adapter = g.GitAdapter()

    def check_output_stub(cmd):
        if '--modified' in cmd:
            output = '''foo.ipynb
bar.ipynb
foo.txt
baz.ipynb
'''
            return output
        elif '--unmerged' in cmd:
            return ''.join([
                '100755\thash\t{i}\tfoo.ipynb\n'
                for i in [1, 2, 3]
            ])
        elif '--is-inside-work-tree' in cmd:
            return 'true\n'
        elif '--show-toplevel' in cmd:
            return '/home/user/Documents'

    def popen(*args, **kwargs):
        return stub(stdout=stub(read=lambda: ""))

    g.open = lambda fname: stub(read=lambda: "")
    g.subprocess = stub(
        check_output=check_output_stub,
        PIPE='foo',
        Popen=popen,
    )
    g.os.path.exists = lambda path: True
    result = adapter.get_modified_notebooks()
    assert result[0][2] == 'bar.ipynb'
    assert result[1][2] == 'baz.ipynb'
    assert len(result) == 2


def test_get_unmerged_notebooks_empty():
    g.subprocess = stub(check_output=lambda cmd: 'true\n'
                        if '--is-inside-work-tree' in cmd
                        else '')
    adapter = g.GitAdapter()
    result = adapter.get_unmerged_notebooks()
    assert result == []


def test_get_unmerged_notebooks():
    adapter = g.GitAdapter()

    def check_output_stub(cmd):
        if '--unmerged' in cmd:
            f1 = ''.join([
                '100755\thash\t{i}\tfoo.ipynb\n'
                for i in [1, 2, 3]
            ])
            f2 = ''.join([
                '100755\thash\t{i}\tbar.ipynb\n'
                for i in [1, 2, 3]
            ])
            f3 = ''.join([
                '100755\thash\t{i}\tfoo.py\n'
                for i in [1, 2, 3]
            ])
            return f1 + f2 + f3
        elif '--is-inside-work-tree' in cmd:
            return 'true\n'
        elif '--show-toplevel' in cmd:
            return '/home/user/Documents'

    def popen(*args, **kwargs):
        return stub(stdout=stub(read=lambda: ""))

    g.open = lambda fname: stub(read=lambda: "")
    g.subprocess = stub(
        check_output=check_output_stub,
        PIPE='foo',
        Popen=popen,
    )
    result = adapter.get_unmerged_notebooks()
    assert len(result) == 2
    assert result[0][3] == '/home/user/Documents/foo.ipynb'
    assert result[1][3] == '/home/user/Documents/bar.ipynb'
