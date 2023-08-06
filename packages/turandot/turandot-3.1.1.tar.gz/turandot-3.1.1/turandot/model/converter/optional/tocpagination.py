from bs4 import BeautifulSoup
from turandot.model import OptionalConverter, ConversionJob


class TocPaginationContainers(OptionalConverter):
    """Optional converter to wrap page numbers in TOC into additional tags for easier styling"""

    def check_config(self, config: dict) -> bool:
        return bool(self.conversion_job.config.get_key(['opt_processors', 'toc_pagination_containers', 'enable'], default=False))

    def process_step(self) -> ConversionJob:
        soup = BeautifulSoup(self.conversion_job.current_step.content, features="html5lib")
        toc_tag = soup.find("div", {'class': 'toc'})
        if toc_tag is not None:
            toc_links = toc_tag.findChildren("a", recursive=True)
            for i in toc_links:
                container = soup.new_tag("a")
                container['href'] = i['href']
                container['class'] = "tocpagenr"
                i.insert_after(container)
        self.conversion_job.current_step.content = str(soup)
        return self.conversion_job
