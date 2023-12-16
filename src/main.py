import logging
import re

from urllib.parse import urljoin
import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm
from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL, EXPECTED_STATUS
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag, get_soup


def whats_new(session):
    """Парсер информации из статей о нововведениях в Python."""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    soup = BeautifulSoup(response.text, 'lxml')
    main_div = find_tag(soup, 'section', {'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', {'class': 'toctree-wrapper'})
    sections = div_with_ul.find_all('li', {'class': 'toctree-l1'})

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    if response is None:
        return

    for section in tqdm(sections):
        sector_tag = section.find('a')
        version_link = urljoin(whats_new_url, sector_tag['href'])
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')

        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    """Парсер статусов версий Python."""
    response = get_response(session, MAIN_DOC_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    """Парсер, который скачивает архив документации Python."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    soup = BeautifulSoup(response.text, 'lxml')
    main_div = find_tag(soup, 'div', {'role': 'main'})
    sec_div = find_tag(main_div, 'table', {'class': 'docutils'})
    url = find_tag(sec_div, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    abs_url = urljoin(downloads_url, url['href'])
    filename = abs_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(abs_url)

    if response is None:
        return

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    """Парсинг документов PEP."""
    soup = get_soup(session, PEP_URL)
    main_tag = find_tag(soup, 'section', {'id': 'numerical-index'})
    tbody_tag = find_tag(main_tag, 'tbody')
    peps_row = tbody_tag.find_all('tr')
    status_sum = {}
    total_peps = 0
    result = [('Статус', 'Количество')]
    for i in peps_row:
        total_peps += 1
        data = list(find_tag(i, 'abbr').text)
        preview_status = data[1:][0] if len(data) > 1 else ''
        url = urljoin(PEP_URL, find_tag(i, 'a', attrs={
            'class': 'pep reference internal'})['href'])
        soup = get_soup(session, url)
        table_info = find_tag(soup, 'dl',
                              attrs={'class': 'rfc2822 field-list simple'})
        status_pep_page = table_info.find(
            string='Status').parent.find_next_sibling('dd').string
        if status_pep_page in status_sum:
            status_sum[status_pep_page] += 1
        if status_pep_page not in status_sum:
            status_sum[status_pep_page] = 1
        if status_pep_page not in EXPECTED_STATUS[preview_status]:
            error_message = (f'Несовпадающие статусы:\n'
                             f'{url}\n'
                             f'Статус в карточке: {status_pep_page}\n'
                             f'Ожидаемые статусы: '
                             f'{EXPECTED_STATUS[preview_status]}')
            logging.warning(error_message)
    result.extend(status_sum.items())
    result.append(('Total', total_peps))
    return result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
