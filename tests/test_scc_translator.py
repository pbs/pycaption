from pycaption.scc.translator import translate_scc


class TestSCCTranslator:

    def test_successful_translation(
            self, sample_scc_pop_on, sample_translated_scc_success):
        result = translate_scc(sample_scc_pop_on)

        assert sample_translated_scc_success == result

    def test_no_brackets(
            self, sample_scc_pop_on, sample_translated_scc_no_brackets):
        result = translate_scc(sample_scc_pop_on, brackets=None)

        assert sample_translated_scc_no_brackets == result

    def test_custom_brackets(
            self, sample_scc_pop_on, sample_translated_scc_custom_brackets):
        result = translate_scc(sample_scc_pop_on, brackets="{}")

        assert sample_translated_scc_custom_brackets == result

    def test_commands_not_found(self, sample_scc_with_unknown_commands,
                                sample_translated_scc_commands_not_found):
        result = translate_scc(sample_scc_with_unknown_commands)

        assert sample_translated_scc_commands_not_found == result

    def test_special_and_extended_characters(
            self, sample_scc_special_and_extended_characters,
            sample_translated_scc_special_and_extended_characters):
        result = translate_scc(sample_scc_special_and_extended_characters)

        assert sample_translated_scc_special_and_extended_characters == result
