def on_page_markdown(markdown, page, config, files):
    page.file.name = page.file.name.lower()
    
    page.file.url = page.file.url.lower()
    page.file.dest_uri = page.file.dest_uri.lower()
    page.file.abs_dest_path = page.file.abs_dest_path.lower()

    return markdown