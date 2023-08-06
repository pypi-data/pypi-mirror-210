# pylint: disable=missing-module-docstring,missing-function-docstring

import argparse
from pathlib import Path
from shlex import split as argv

import aiohttp
from aioresponses import aioresponses

from xsget import __version__
from xsget.xsget import (
    extract_urls,
    fetch_url_by_aiohttp,
    http_headers,
    url_to_filename,
)

DEFAULT_URL = "http://localhost"


def test_repo_urls_in_help_message(script_runner):
    ret = script_runner.run(*argv("xsget -h"))
    assert "  website: https://github.com/kianmeng/xsget" in ret.stdout
    assert "  issues: https://github.com/kianmeng/xsget/issues" in ret.stdout


def test_required_url(script_runner):
    ret = script_runner.run(*argv("xsget"))
    assert (
        "xsget: error: the following arguments are required: URL" in ret.stderr
    )


def test_invalid_url(script_runner):
    ret = script_runner.run(*argv("xsget example.com"))
    assert "error: invalid url: example.com" in ret.stdout


def test_range_in_url(script_runner):
    ret = script_runner.run(*argv(f"xsget -d -t {DEFAULT_URL}/[1-2].html"))
    logs = [
        f"INFO: xsget.xsget: Found url: {DEFAULT_URL}/1.html",
        f"INFO: xsget.xsget: Found url: {DEFAULT_URL}/2.html",
    ]
    for log in logs:
        assert log in ret.stdout


def test_leading_range_in_url(script_runner):
    ret = script_runner.run(*argv(f"xsget -d -t {DEFAULT_URL}/a0[1-2].html"))
    logs = [
        f"INFO: xsget.xsget: Found url: {DEFAULT_URL}/a01.html",
        f"INFO: xsget.xsget: Found url: {DEFAULT_URL}/a02.html",
    ]
    for log in logs:
        assert log in ret.stdout


def test_raise_exception_for_invalid_range_in_url(script_runner):
    ret = script_runner.run(*argv(f"xsget -d -t {DEFAULT_URL}/[2-1].html"))
    logs = [
        "ERROR: xsget.xsget: error: invalid url range, start: 2, end: 1",
        "RuntimeError: invalid url range, start: 2, end: 1",
    ]
    for log in logs:
        assert log in ret.stdout


def test_generating_default_config_file(script_runner):
    ret = script_runner.run(*argv(f"xsget {DEFAULT_URL} -g"))
    assert "Create config file: xsget.toml" in ret.stdout
    assert (
        "Cannot connect to host localhost:80 "
        "ssl:default [Connect call failed ('127.0.0.1', 80)]" in ret.stdout
    )


def test_generating_default_config_file_with_existing_found(script_runner):
    _ = script_runner.run(*argv(f"xsget {DEFAULT_URL} -g"))
    ret = script_runner.run(*argv(f"xsget {DEFAULT_URL} -g"))
    assert "Existing config file found: xsget.toml" in ret.stdout


def test_version(script_runner):
    ret = script_runner.run(*argv("xsget -V"))
    assert f"xsget {__version__}" in ret.stdout


def test_url_to_filename():
    expected = [
        ("http://a.com", "index.html"),
        ("http://a.com/", "index.html"),
        ("http://a.com/123", "123.html"),
        ("http://a.com/123/456", "456.html"),
        ("http://a.com/123/456/789", "789.html"),
        ("http://a.com/123.html", "123.html"),
    ]
    for url, filename in expected:
        assert url_to_filename(url) == filename

    expected = [
        ("http://a.com/123?id=aaa", "id", "aaa.html"),
        ("http://a.com/456.php?tid=abc", "tid", "abc.html"),
    ]
    for url, url_param, filename in expected:
        assert url_to_filename(url, url_param) == filename


def test_extract_urls():
    html = """
        <html>
        <body>
        <div class="toc">
            <a href="http://a.com/123"/>a</a>
            <a href="http://a.com/123/789.html"/>b</a>
            <a href="//a.com/987"/>c</a>
            <a href="/123/456"/>d</a>
            <a href="/123/654.html"/>e</a>
        </div>
        </body>
        </html>
    """

    expected_urls = [
        "http://a.com/123",
        "http://a.com/123/789.html",
        "http://a.com/987",
        "http://a.com/123/456",
        "http://a.com/123/654.html",
    ]

    css_paths = [
        "html body div.toc a",
        "html body div a",
        "body div.toc a",
        "div.toc a",
        "div a",
        "a",
    ]
    for css_path in css_paths:
        config = argparse.Namespace(
            url="http://a.com/123", link_css_path=css_path
        )
        assert extract_urls(html, config) == expected_urls


def test_user_agent():
    user_agent = http_headers()["User-Agent"]
    assert "Mozilla/5.0" in user_agent


async def test_fetch_url_by_aiohttp(tmpdir):
    session = aiohttp.ClientSession()
    with aioresponses() as mocked:
        config = argparse.Namespace(url_param_as_filename="")
        mocked.get(DEFAULT_URL, status=200, body="test")

        resp = await fetch_url_by_aiohttp(session, DEFAULT_URL, config)
        assert resp.status == 200
        mocked.assert_called_once_with(DEFAULT_URL)

        with open(Path(tmpdir, "index.html"), encoding="utf8") as file:
            assert file.read() == "test"

        await session.close()
