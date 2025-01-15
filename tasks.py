from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    open_robot_order_website()
    orders = get_orders()
    fill_form_orders(orders)
    archive_receipts()

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/")
    page = browser.page()
    page.click("text=Order your robot!")
    page.click("text=OK")
    

def get_orders():
    """Downloads CSV file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    csv_file = Tables()
    orders = csv_file.read_table_from_csv("orders.csv")
    return orders

def fill_form_orders(orders):
    for order in orders:
        page = browser.page()
        page.select_option("#head", order["Head"])
        page.click('id=id-body-{0}'.format(order["Body"]))
        page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
        page.fill("#address", order["Address"])
        page.click("id=order")
        error_displayed = page.query_selector("div[class='alert alert-danger']")
        while  error_displayed:
            page.click("id=order")
            error_displayed = page.query_selector("div[class='alert alert-danger']")
        pdf_order_path = store_receipt_as_pdf(order["Order number"])
        robot_preview=screenshot_robot(order["Order number"])
        embed_screenshot_to_receipt(robot_preview, pdf_order_path)
        page.click("id=order-another")
        page.click("text=OK")
        

def store_receipt_as_pdf(order_number):
       page = browser.page()
       receipt_html = page.locator("#receipt").inner_html()
       pdf = PDF()
       pdf_order_path="output/receipts/{0}.pdf".format(order_number)
       pdf.html_to_pdf(receipt_html, pdf_order_path)
       return pdf_order_path

def screenshot_robot(order_number):
    page = browser.page()
    page.locator('#robot-preview-image').screenshot(path="output/screenshots/{0}.png".format(order_number))
    screenshotrobot="{0}.png".format(order_number)
    return screenshotrobot

def embed_screenshot_to_receipt(screenshot, pdf_order_path):
    pdf= PDF()
    screenshotpath=["output/screenshots/{0}".format(screenshot)]
    pdf.add_files_to_pdf(files=screenshotpath, target_document=pdf_order_path, append=True)

def archive_receipts():
    archive= Archive()
    archive.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")