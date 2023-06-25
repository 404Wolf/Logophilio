from src.flashcards.renderer.converter.engine import webdriver_chrome


def convert_to_pdf(data: str, mimetype: str, width: int, height: int) -> str:
    """
    Convert a chrome preview-able file to a base-64 encoded pdf using Selenium.

    Args:
        data (str): Base64 encoded preview-able file.
        mimetype (str): The mimetype of the base64 data.
        width (float): The width of the preview-able file.
        height (float): The height of the preview-able file.

    Returns:
        str: The base64 encoded pdf.
    """
    assert isinstance(width, float)
    assert isinstance(height, float)
    webdriver_chrome.get(f"about:blank")
    webdriver_chrome.execute_cdp_cmd(
        "Emulation.setVisibleSize",
        {
            "width": width,
            "height": height,
        },
    )
    webdriver_chrome.execute_script(
        "document.body.style.margin = '0';"
        "const content = document.createElement('img');"
        f"content.src = 'data:{mimetype};base64,{data}';"
        "content.style.width = '100%';"
        "content.style.height = '100%';"
        "document.body.appendChild(content);"
    )
    pdf = webdriver_chrome.execute_cdp_cmd(
        "Page.printToPDF",
        {
            "printBackground": False,
            "landscape": False,
            "displayHeaderFooter": False,
            "scale": 1.5,
            "paperWidth": 1.75,
            "paperHeight": 2.5,
            "marginTop": 0,
            "marginBottom": 0,
            "marginLeft": 0,
            "marginRight": 0,
        },
    )
    return pdf["data"]
