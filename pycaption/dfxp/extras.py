# We thought about making pycaption.base objects immutable. This would be nice
# in a lot of cases, but since the transformations on them could be quite
# complex, the deepcopy method is good enough sometimes.
from copy import deepcopy

from .base import DFXPWriter, DFXP_DEFAULT_REGION


class SinglePositioningDFXPWriter(DFXPWriter):
    """A dfxp writer, that ignores all positioning, using a single provided value
    """
    def __init__(self, default_positioning=DFXP_DEFAULT_REGION,
                 *args, **kwargs):
        super(SinglePositioningDFXPWriter, self).__init__(*args, **kwargs)
        self.default_positioning = default_positioning

    def write(self, captions_set, force=u''):
        """Writes a DFXP file using the positioning provided in the initializer

        :type captions_set: pycaption.base.CaptionSet
        :param force: only write this language, if available in the CaptionSet
        :rtype: unicode
        """
        captions_set = self._create_single_positioning_caption_set(
            captions_set, self.default_positioning)

        return super(SinglePositioningDFXPWriter, self).write(captions_set, force)  # noqa

    @staticmethod
    def _create_single_positioning_caption_set(captions_set, positioning):
        """Return a caption where all the positioning information was
        replaced from positioning

        :type captions_set: pycaption.base.CaptionSet
        :rtype: pycaption.base.CaptionSet
        """
        # If SinglePositioningDFXPWriter would modify the state of the caption
        # set, any writer using the same caption_set thereafter would be
        # affected. At the moment we know we don't use any other writers, but
        # this is important and mustn't be neglected
        captions_set = deepcopy(captions_set)

        captions_set.layout_info = positioning

        for lang in captions_set.get_languages():
            captions_set.set_layout_info(lang, positioning)

            caption_list = captions_set.get_captions(lang)
            for caption in caption_list:
                caption.layout_info = positioning

                for node in caption.nodes:
                    if hasattr(node, 'layout_info'):
                        node.layout_info = positioning

        return captions_set