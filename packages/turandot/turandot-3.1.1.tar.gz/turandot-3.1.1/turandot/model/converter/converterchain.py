from turandot import TurandotConversionException
from turandot.model import ConverterBase, GatherData, CopyTemplate, ConversionAlgorithm, ConvertToHtml, OptionalStage, ApplyTemplate, WeasyprintToPdf
from turandot.model.converter.optional import UnifiedMathMarker, TocPaginationContainers


class ConverterChain:

    @staticmethod
    def build_chain(alg: ConversionAlgorithm) -> ConverterBase:
        """Build a chain of converter for a specified algorithm"""
        if alg == ConversionAlgorithm.WEASYPRINT:
            return ConverterChain._build_weasyprint()
        raise TurandotConversionException("Unknown conversion algorithm")

    @staticmethod
    def _build_weasyprint() -> ConverterBase:
        """Build Weasyprint PDF conversion algorithm chain"""
        chain = GatherData()
        chain.chain_append(CopyTemplate())
        html = ConvertToHtml()
        html.register_optional(UnifiedMathMarker(), OptionalStage.PRE)
        chain.chain_append(html)
        tmpl = ApplyTemplate()
        tmpl.register_optional(TocPaginationContainers(), OptionalStage.POST)
        chain.chain_append(tmpl)
        chain.chain_append(WeasyprintToPdf())
        return chain
