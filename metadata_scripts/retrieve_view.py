#!/usr/bin/env python3
import json
import sys
import time

from fairspace_api.api import FairspaceApi, Page


def display_config(config):
    print('Fetching view config')

    print('Config')
    print('=======')
    print(json.dumps(config, indent=2))
    print()


def display_page(page: Page):
    if page.totalElements is not None:
        print(f'Displaying {len(page.rows)} / {page.totalElements:,} results. Page {page.page} / {page.totalPages:,}.')
    else:
        print(f'Displaying {len(page.rows)} results. Page {page.page}.')
    for row in page.rows:
        print(row)
    if page.hasNext:
        print('More results available ...')


def main():
    view = sys.argv[1] if len(sys.argv) > 1 else 'config'
    api = FairspaceApi()

    if view == 'config':
        config = api.retrieve_view_config()
        display_config(config)
        return

    print(f'Fetching {view} view')
    start = time.time()
    page = api.retrieve_view_page(view, page=1, size=20)
    duration = 1000*(time.time() - start)
    print(f'(took {duration:,.0f} ms)')
    display_page(page)

    print()
    print(f'Fetching {view} view count')
    start = time.time()
    count = api.count(view)
    duration = 1000*(time.time() - start)
    print(f'(took {duration:,.0f} ms)')
    print(f'{count.totalElements} results.')


if __name__ == '__main__':
    main()
