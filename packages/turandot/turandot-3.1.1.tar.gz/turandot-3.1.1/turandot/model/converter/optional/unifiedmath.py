import re
from turandot.model import OptionalConverter, ConversionJob, ConfigDict


class UnifiedMathMarker(OptionalConverter):
    """Optional processor to convert JS style Katex fences to Python Markdown compatible fences"""

    LATEX_PATTERN = '(^\$\$$)([^\$]+)(^\$\$$)'
    GITHUB_MARKERS = ['```math', '```']

    def check_config(self, config: dict) -> bool:
        return bool(
            self.conversion_job.config.get_key(['opt_processors', 'unified_math_block_marker', 'enable'], default=False)
        )

    def process_step(self) -> ConversionJob:
        self.conversion_job.current_step.content = UnifiedMathMarker._static_conversion(self.conversion_job.current_step.content)
        return self.conversion_job

    @staticmethod
    def _static_conversion(fulltext: str) -> str:
        """Find regex matches for JS Katex fences and convert them"""
        flagged_pattern = re.compile('(^\$\$$)([^\$]+)(^\$\$$)', flags=re.MULTILINE)
        while True:
            stack = re.finditer(flagged_pattern, fulltext)
            if (needle := next(stack, None)) is None:
                break
            fulltext = UnifiedMathMarker._process_latex_match(needle, fulltext)
        return fulltext

    @staticmethod
    def _process_latex_match(match: re.Match, fulltext: str) -> str:
        """Process a found fence match"""
        pre = fulltext[:match.start()]
        math = fulltext[match.start() + 2:match.end() - 2]
        post = fulltext[match.end():]
        return pre + UnifiedMathMarker.GITHUB_MARKERS[0] + math + UnifiedMathMarker.GITHUB_MARKERS[1] + post
