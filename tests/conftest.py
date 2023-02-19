import asyncio
import os

import pytest
from playwright.async_api import async_playwright


def pytest_addoption(parser) -> None:
    group = parser.getgroup("playwright", "Playwright")
    group.addoption(
        "--browser",
        action="append",
        default=[],
        help="Browsers which should be used. By default on all the browsers.",
    )
    group.addoption(
        "--browser-channel",
        action="store",
        default=None,
        help="Browser channel to be used.",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run tests in headed mode.",
    )


def pytest_generate_tests(metafunc):
    if "browser_name" in metafunc.fixturenames:
        browsers = metafunc.config.option.browser or [
            "chromium",
            "firefox",
            "webkit",
        ]
        metafunc.parametrize("browser_name", browsers, scope="session")


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def browser_name(pytestconfig):
    return pytestconfig.getoption("browser")


@pytest.fixture(scope="session")
def browser_channel(pytestconfig):
    return pytestconfig.getoption("--browser-channel")


@pytest.fixture(scope="session")
async def playwright():
    async with async_playwright() as playwright_object:
        yield playwright_object


@pytest.fixture(scope="session")
def launch_arguments(pytestconfig):
    return {
        "headless": not (
            pytestconfig.getoption("--headed") or os.getenv("HEADFUL", False)
        ),
        "channel": pytestconfig.getoption("--browser-channel"),
    }


@pytest.fixture(scope="session")
def browser_type(playwright, browser_name: str):
    if browser_name == "chromium":
        return playwright.chromium
    if browser_name == "firefox":
        return playwright.firefox
    if browser_name == "webkit":
        return playwright.webkit


@pytest.fixture(scope="session")
async def browser_factory(launch_arguments, browser_type):
    browsers = []

    async def launch(**kwargs):
        browser = await browser_type.launch(**launch_arguments, **kwargs)
        browsers.append(browser)
        return browser

    yield launch
    for browser in browsers:
        await browser.close()


@pytest.fixture(scope="session")
async def browser(browser_factory):
    browser = await browser_factory()
    yield browser
    await browser.close()


@pytest.fixture(scope="session")
async def authenticate(browser):
    context = await browser.new_context()
    page = await context.new_page()
    # TODO: authenticate here
    await context.storage_state(path="state.json")
    await context.close()


@pytest.fixture
async def context_factory(browser):
    contexts = []

    async def launch(**kwargs):
        context = await browser.new_context(**kwargs)
        contexts.append(context)
        return context

    yield launch
    for context in contexts:
        await context.close()


@pytest.fixture
async def authenticated_context(authenticate, context_factory):
    if os.path.exists("state.json"):
        context = await context_factory(storage_state="state.json")
    else:
        context = await context_factory()
    yield context
    await context.close()


@pytest.fixture
async def context(context_factory):
    context = await context_factory()
    yield context
    await context.close()


@pytest.fixture
async def authenticated_page(authenticated_context):
    page = await authenticated_context.new_page()
    yield page
    await page.close()


@pytest.fixture
async def page(context):
    page = await context.new_page()
    yield page
    await page.close()
