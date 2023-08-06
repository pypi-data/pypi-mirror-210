import abc
from pathlib import Path

import datalad_catalog.constants as cnst
from datalad_catalog.utils import read_json_file, get_entry_points
from datalad.support.exceptions import InsufficientArgumentsError


class TranslatorBase(metaclass=abc.ABCMeta):
    """
    Translator base class providing internal methods for matching
    incoming metadata to a translator that inherits from this base class,
    as well as the following abstract methods that should be overridden
    by the inheriting class:
        match()
        translate()
    """

    @classmethod
    @abc.abstractmethod
    def match(
        cls, source_name: str, source_version: str, source_id: str = None
    ) -> bool:
        """
        Report the result of matching criteria applied to the translator

        This tests whether the inherited translator can be used to translate
        metadata output from a specific source.

        Current criteria include extractor name and extractor version,
        and the catalog schema version
        """
        raise NotImplementedError

    @abc.abstractmethod
    def translate(self, metadata):
        """
        Translate incoming metadata to the current catalog schema

        This method contains the logic for translating an incoming metadata
        object to the catalog schema (version-specific).
        """
        raise NotImplementedError

    @classmethod
    def get_current_schema_version(self) -> str:
        """
        Retrieves schema version of current package installation
        """
        # Setup schema parameters
        package_path = Path(__file__).resolve().parent
        schema_dir = package_path / "schema"
        schema_path = schema_dir / str("jsonschema_catalog.json")
        schema = read_json_file(schema_path)
        return schema.get(cnst.VERSION)


class TranslatorNotFoundError(InsufficientArgumentsError):
    pass


class Translate(object):
    """
    Class responsible for executing translation of an extracted metadata record,
    including finding a matching class (base class TranslatorBase) and running
    metadata translation.
    """

    def __init__(
        self, meta_record: dict = None, translators: dict = None
    ) -> None:
        """"""
        self.meta_record = meta_record
        if self.meta_record is None:
            raise ValueError("No metadata record provided")
        self.available_translators = translators
        if self.available_translators is None:
            raise ValueError("No translators provided")
        self.match_translator()

    def match_translator(self):
        """Match an extracted metadata record with an appropriate translator

        Parameters
        ----------
        meta_record : dict
            A dictionary containing metadata that was extracted from a file or dataset
            using datalad-metalad

        Returns
        ------
        TranslatorBase
            The first matched translator instance of base class TranslatorBase
        """
        # First get source name and version from record
        source_name = self.meta_record.get(cnst.EXTRACTOR_NAME)
        source_version = self.meta_record.get(cnst.EXTRACTOR_VERSION)
        matched_translators = []
        for (
            translator_name,
            translator_dict,
        ) in self.available_translators.items():
            translator_class = translator_dict["loader"]()
            translator_instance = translator_class()
            if translator_instance.match(source_name, source_version):
                # break on first match
                matched_translators.append(translator_instance)
                break
        # Raise error if there was no match
        if not matched_translators:
            self.translator = None
            raise TranslatorNotFoundError(
                f"Metadata translator not found for metadata source \
{source_name} and version {source_version}"
            )
        # if for some reason more than one entry points are returned, select first one
        self.translator = matched_translators[0]

    def run_translator(self):
        """"""
        return self.translator.translate(self.meta_record)


def get_translators(include_load_error: bool = False) -> dict:
    """Return all translators known to the current installation

    Parameters
    ----------
    include_load_error: bool
        Set to True if entry points with load errors should be included
        in the returned dictionary (default is False)

    Returns
    -------
    translator_eps : dict
        A dictionary of translator entry points with no load_errors
    """
    translator_dict = get_entry_points("datalad.metadata.translators")
    translator_eps = translator_dict
    # Include all translator entrypoints vs only those without load errors
    if include_load_error:
        translator_eps = {
            name: translator_dict[name]
            for name in translator_dict.keys()
            if translator_dict[name]["load_error"] is None
        }
    # Raise error if no translators found
    if not bool(translator_eps):
        raise TranslatorNotFoundError(f"No metadata translators were found")
    return translator_eps
