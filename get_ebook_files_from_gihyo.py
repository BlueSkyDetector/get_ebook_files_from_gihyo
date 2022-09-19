#!/usr/bin/env python3

from playwright.sync_api import Playwright, sync_playwright, Page, TimeoutError
import re
import os
import argparse
import configparser
from logging import Logger, getLogger, StreamHandler, INFO

parser: argparse.ArgumentParser
conf: configparser.ConfigParser
download_directory: str
headless: bool

logger: Logger = getLogger()
logger.addHandler(StreamHandler())
logger.setLevel(INFO)


def parse_conf(conf_path: str):
    conf: configparser.ConfigParser = configparser.ConfigParser()
    if os.path.exists(conf_path):
        conf.read(conf_path)
    else:
        raise ValueError("conf file is not readable.")
    return conf


def load_my_page(context) -> Page:
    # Open new page
    page = context.new_page()

    # Go to https://gihyo.jp/dp
    page.goto("https://gihyo.jp/dp")

    # Click to open login modal
    page.locator("text=ログイン").click()
    page.locator("[placeholder=\"メールアドレス\"]").click()
    page.locator("[placeholder=\"メールアドレス\"]").fill(conf['login']['email'])
    page.locator("[placeholder=\"パスワード\"]").click()
    page.locator("[placeholder=\"パスワード\"]").fill(conf['login']['password'])
    page.locator("input:has-text(\"ログイン\")").click()

    # Click to go to my page
    page.locator("text=マイページ").click()
    page.wait_for_url("https://gihyo.jp/dp/my-page")
    return page


def download_ebook_file(page, ebook_title, file_ext, link_text) -> bool:
    ebook_filename = "{}.{}".format(ebook_title, file_ext)
    is_succeeded = True
    page.set_default_timeout(timeout=3000)
    # Click for download
    if not os.path.exists(os.path.join(download_directory, ebook_filename)):
        try:
            with page.expect_download() as download_info:
                with page.expect_popup() as popup_info:
                    page.locator("a", has_text=link_text).click()
                page1 = popup_info.value
            download = download_info.value
            download.save_as(os.path.join(download_directory, ebook_filename))
            logger.info(ebook_filename)

            # Close page
            page1.close()
        except TimeoutError:
            is_succeeded = False
            logger.info('timeout: {}'.format(ebook_filename))
            logger.info('retrying...')
    page.set_default_timeout(timeout=30000)
    return is_succeeded


def download_ebook_files(page, ebook_title, is_epub_to_download, is_pdf_to_download) -> bool:
    is_succeeded: bool = True
    if is_epub_to_download is False:
        pass
    elif not download_ebook_file(page=page,
                                 ebook_title=ebook_title,
                                 file_ext='epub',
                                 link_text='EPUBダウンロード'):
        is_succeeded = False
    if is_pdf_to_download is False:
        pass
    elif not download_ebook_file(page=page,
                                 ebook_title=ebook_title,
                                 file_ext='pdf',
                                 link_text='PDFダウンロード'):
        is_succeeded = False

    # Click text=閉じる
    page.locator("text=閉じる").click()
    return is_succeeded


def run(playwright: Playwright, ebook_title_regex) -> None:
    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context()
    page = load_my_page(context)
    paging_number = 1

    while True:
        # Find all matched ebooks
        elements = page.locator("li")\
            .filter(has=page.locator("p", has_text=re.compile(ebook_title_regex)))\
            .filter(has=page.locator("li", has_text=re.compile("PDF|EPUB")))
        for i in range(elements.count()):
            while True:
                # Open each ebook modal to download
                target_locator = elements.nth(i)
                title_element = target_locator.locator("//a/p[@class='title']")
                ebook_title = title_element.inner_text().replace(' ', '_').replace('\n', '_')
                is_epub_to_download: bool = False
                is_pdf_to_download: bool = False
                if target_locator.filter(has=page.locator("//a/ul/li[@class='epub']")).count() and\
                   not os.path.exists(os.path.join(download_directory, "{}.epub".format(ebook_title))):
                    is_epub_to_download = True
                if target_locator.filter(has=page.locator("//a/ul/li[@class='pdf']")).count() and\
                   not os.path.exists(os.path.join(download_directory, "{}.pdf".format(ebook_title))):
                    is_pdf_to_download = True
                if is_epub_to_download is False and is_pdf_to_download is False:
                    break
                title_element.click()
                if download_ebook_files(page, ebook_title, is_epub_to_download, is_pdf_to_download):
                    break

        next_page_elements = page.locator("//a[@class='next']")
        if next_page_elements.count():
            next_page_elements.nth(0).click()
            logger.info('next page...')
            paging_number += 30
            page.locator("//li[@class='paging-number' and text()='{}']".format(paging_number)).wait_for()
        else:
            break

    # Close page
    page.close()

    # ---------------------
    context.close()
    browser.close()


def main():
    script_dir: str = os.path.dirname(os.path.realpath(__file__))
    global parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf',
                        action='store',
                        default=script_dir + '/get_ebook_files_from_gihyo.conf',
                        help='conf file path (default: %s/get_ebook_files_from_gihyo.conf)' % script_dir)
    parser.add_argument('-s', '--show_browser', action='store_true', default=False)
    parser.add_argument('-d', '--download_directory', action='store', required=True)
    parser.add_argument('-t', '--title_of_ebooks', action='store', default='',
                        help='title of ebooks in regular expression (for example: "Software Design .*月号")')
    args: argparse.Namespace = parser.parse_args()
    global headless
    headless = not args.show_browser
    global download_directory
    download_directory = args.download_directory
    global conf
    conf = parse_conf(args.conf)

    with sync_playwright() as playwright:
        run(playwright, args.title_of_ebooks)


if __name__ == '__main__':
    main()
