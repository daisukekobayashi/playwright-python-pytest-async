import pytest


@pytest.mark.asyncio
async def test_unauthenticated_page(page):
    URL = "https://playwright.dev/python/"
    await page.goto(URL)
    assert page.url == URL


@pytest.mark.asyncio
async def test_authenticated_page(authenticated_page):
    URL = "https://playwright.dev/python/"
    await authenticated_page.goto(URL)
    assert authenticated_page.url == URL
