from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from benchling_api_client.v2.stable.client import Client

from benchling_sdk.helpers.client_helpers import v2_beta_client
from benchling_sdk.helpers.retry_helpers import RetryStrategy
from benchling_sdk.services.v2.base_service import BaseService

if TYPE_CHECKING:
    from benchling_sdk.services.v2.beta.v2_beta_aa_sequence_service import V2BetaAaSequenceService
    from benchling_sdk.services.v2.beta.v2_beta_app_service import V2BetaAppService
    from benchling_sdk.services.v2.beta.v2_beta_custom_entity_service import V2BetaCustomEntityService
    from benchling_sdk.services.v2.beta.v2_beta_dna_oligo_service import V2BetaDnaOligoService
    from benchling_sdk.services.v2.beta.v2_beta_dna_sequence_service import V2BetaDnaSequenceService
    from benchling_sdk.services.v2.beta.v2_beta_entity_service import V2BetaEntityService
    from benchling_sdk.services.v2.beta.v2_beta_entry_service import V2BetaEntryService
    from benchling_sdk.services.v2.beta.v2_beta_rna_oligo_service import V2BetaRnaOligoService
    from benchling_sdk.services.v2.beta.v2_beta_worklist_service import V2BetaWorklistService


class V2BetaService(BaseService):
    """
    V2-beta.

    Beta endpoints have different stability guidelines than other stable endpoints.

    See https://benchling.com/api/v2-beta/reference
    """

    _aa_sequence_service: Optional[V2BetaAaSequenceService]
    _app_service: Optional[V2BetaAppService]
    _custom_entity_service: Optional[V2BetaCustomEntityService]
    _dna_oligo_service: Optional[V2BetaDnaOligoService]
    _dna_sequence_service: Optional[V2BetaDnaSequenceService]
    _entity_service: Optional[V2BetaEntityService]
    _entry_service: Optional[V2BetaEntryService]
    _rna_oligo_service: Optional[V2BetaRnaOligoService]
    _worklist_service: Optional[V2BetaWorklistService]
    _beta_client: Client

    def __init__(self, client: Client, retry_strategy: RetryStrategy = RetryStrategy()):
        """
        Initialize a v2-beta service.

        :param client: Underlying generated Client.
        :param retry_strategy: Retry strategy for failed HTTP calls
        """
        super().__init__(client, retry_strategy)
        self._beta_client = v2_beta_client(self.client)
        self._aa_sequence_service = None
        self._app_service = None
        self._custom_entity_service = None
        self._dna_sequence_service = None
        self._dna_oligo_service = None
        self._entity_service = None
        self._entry_service = None
        self._rna_oligo_service = None
        self._worklist_service = None

    @property
    def aa_sequences(self) -> V2BetaAaSequenceService:
        """
        V2-Beta AA Sequences.

        AA Sequences are the working units of cells that make everything run (they help make structures, catalyze
        reactions and allow for signaling - a kind of internal cell communication). On Benchling, these are comprised
        of a string of amino acids and collections of other attributes, such as annotations.

        See https://benchling.com/api/v2-beta/reference#/AA%20Sequences
        """
        if self._aa_sequence_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_aa_sequence_service import V2BetaAaSequenceService

            self._aa_sequence_service = V2BetaAaSequenceService(self._beta_client, self.retry_strategy)
        return self._aa_sequence_service

    @property
    def apps(self) -> V2BetaAppService:
        """
        V2-Beta Apps.

        Create and manage Apps on your tenant.

        https://benchling.com/api/v2-beta/reference?stability=not-available#/Apps
        """
        if self._app_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_app_service import V2BetaAppService

            self._app_service = V2BetaAppService(self._beta_client, self.retry_strategy)
        return self._app_service

    @property
    def custom_entities(self) -> V2BetaCustomEntityService:
        """
        V2-Beta Custom Entities.

        Benchling supports custom entities for biological entities that are neither sequences or proteins. Custom
        entities must have an entity schema set and can have both schema fields and custom fields.

        See https://benchling.com/api/v2-beta/reference#/Custom%20Entities
        """
        if self._custom_entity_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_custom_entity_service import V2BetaCustomEntityService

            self._custom_entity_service = V2BetaCustomEntityService(self._beta_client, self.retry_strategy)
        return self._custom_entity_service

    @property
    def dna_oligos(self) -> V2BetaDnaOligoService:
        """
        V2-Beta DNA Oligos.

        DNA Oligos are short linear DNA sequences that can be attached as primers to full DNA sequences. Just like other
        entities, they support schemas, tags, and aliases.

        See https://benchling.com/api/v2-beta/reference#/DNA%20Oligos
        """
        if self._dna_oligo_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_dna_oligo_service import V2BetaDnaOligoService

            self._dna_oligo_service = V2BetaDnaOligoService(self._beta_client, self.retry_strategy)
        return self._dna_oligo_service

    @property
    def dna_sequences(self) -> V2BetaDnaSequenceService:
        """
        V2-Beta DNA Sequences.

        DNA sequences are the bread and butter of the Benchling Molecular Biology suite. On Benchling, these are
        comprised of a string of nucleotides and collections of other attributes, such as annotations and primers.

        See https://benchling.com/api/v2-beta/reference#/DNA%20Sequences
        """
        if self._dna_sequence_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_dna_sequence_service import V2BetaDnaSequenceService

            self._dna_sequence_service = V2BetaDnaSequenceService(self._beta_client, self.retry_strategy)
        return self._dna_sequence_service

    @property
    def entities(self) -> V2BetaEntityService:
        """
        V2-Beta Entities.

        Entities include DNA and AA sequences, oligos, molecules, custom entities, and
        other biological objects in Benchling. Entities support schemas, tags, and aliases,
        and can be registered.

        See https://benchling.com/api/v2-beta/reference#/Entities
        """
        if self._entity_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_entity_service import V2BetaEntityService

            self._entity_service = V2BetaEntityService(self._beta_client, self.retry_strategy)
        return self._entity_service

    @property
    def entries(self) -> V2BetaEntryService:
        """
        V2-Beta Entries.

        Entries are rich text documents that allow you to capture all of your experimental data in one place.

        https://benchling.com/api/v2-beta/reference#/Entries
        """
        if self._entry_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_entry_service import V2BetaEntryService

            self._entry_service = V2BetaEntryService(self._beta_client, self.retry_strategy)
        return self._entry_service

    @property
    def rna_oligos(self) -> V2BetaRnaOligoService:
        """
        V2-Beta RNA Oligos.

        RNA Oligos are short linear RNA sequences that can be attached as primers to full DNA sequences. Just like other
        entities, they support schemas, tags, and aliases.

        See https://benchling.com/api/v2-beta/reference#/RNA%20Oligos
        """
        if self._rna_oligo_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_rna_oligo_service import V2BetaRnaOligoService

            self._rna_oligo_service = V2BetaRnaOligoService(self._beta_client, self.retry_strategy)
        return self._rna_oligo_service

    @property
    def worklists(self) -> V2BetaWorklistService:
        """
        V2-Beta Worklists.

        Worklists are a convenient way to organize items for bulk actions, and are complementary to folders and
        projects.

        See https://benchling.com/api/v2-beta/reference#/Worklists
        """
        if self._worklist_service is None:
            from benchling_sdk.services.v2.beta.v2_beta_worklist_service import V2BetaWorklistService

            self._worklist_service = V2BetaWorklistService(self._beta_client, self.retry_strategy)
        return self._worklist_service
