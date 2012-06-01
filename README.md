After installing nltk, the appropriate Punkt tokenizer info must be downloaded.

Suggested usage:

import SAMI
sami = SAMIUtility(url='<SAMI url>')
sami.get_transcript()
sami.get_dfxp()